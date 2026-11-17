"""Live audits from the website.

1. Live check (public, free): submits CV twins to a demo tool's own form, reads score and
   decision, and computes the same verdict as the Kane audit. It talks to the tool over HTTP
   (or in-process when the tools share this server), so it is fast and costs no Kane credits,
   but it is not browser-verified. One job at a time, short cooldown.
2. Kane run (public, on the project's Kane credits): triggers the GitHub Actions fairness gate, where
   Kane CLI drives the real UI for one candidate (8 CVs with placebo names). One run at a time and
   a daily cap counted on GitHub itself, so restarts cannot reset it. Needs GITHUB_TOKEN on the server.
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
import twin_audit as ta  # noqa: E402

TARGETS = json.loads((ROOT / "audit" / "targets.json").read_text(encoding="utf-8"))
MANIFEST = {c["candidate"]: c for c in json.loads((ROOT / "data" / "cvs" / "manifest.json").read_text())}
LIVE_CANDIDATES = ["cand01", "cand02", "cand03"]
COOLDOWN_S = 20
REPO = os.environ.get("GITHUB_REPO", "LovableLynx/kane-fairness-auditor")
WORKFLOW = "fairness-gate.yml"

# Set by serve.py when the tools are mounted in this same process: {"talentscreen": wsgi_app, ...}
TARGET_APPS: dict = {}

_jobs: dict[str, dict] = {}
_lock = threading.Lock()
_last_finish = [0.0]


def _submit(target: str, text: str) -> str:
    """Post one CV to the tool's own form endpoint and return the resulting page as flat text."""
    d = TARGETS[target]["direct"]
    form = {**d.get("extra", {}), d["field"]: text}
    app = TARGET_APPS.get(target)
    if app is not None:
        client = app.test_client()
        html = client.post(d["post"], data=form, follow_redirects=True).get_data(as_text=True)
    else:
        base = TARGETS[target]["url"].rstrip("/")
        html = urllib.request.urlopen(base + d["post"], data=urllib.parse.urlencode(form).encode(),
                                      timeout=90).read().decode("utf-8", "replace")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _run(job: dict) -> None:
    target = job["target"]
    d = TARGETS[target]["direct"]
    log = job["lines"]
    try:
        log.append({"k": "cmd", "t": f"live check --target {target} --candidates {','.join(LIVE_CANDIDATES)} (placebo on)"})
        runs = []
        for cid in LIVE_CANDIDATES:
            run = ta.CandidateRun(cid, ta.pick_twins(MANIFEST[cid], "short", True))
            for t in run.twins:
                flat = _submit(target, (ROOT / t.file).read_text(encoding="utf-8"))
                sm, dm = re.search(d["score_re"], flat), re.search(d["decision_re"], flat)
                t.score = ta.normalise(float(sm.group(1))) if sm else None
                t.decision = dm.group(1).strip() if dm else None
                t.selected = ta.to_selected(t.decision)
                tag = "placebo" if t.slot else f"{t.gender[0].upper()}·{t.group}"
                if t.score is None:
                    log.append({"k": "no", "t": f"{cid}  {t.name:<20} {tag:<8} could not read the result"})
                else:
                    log.append({"k": "ok" if t.selected else "no",
                                "t": f"{cid}  {t.name:<20} {tag:<8} {t.score:.3f}  {t.decision}"})
                job["done"] += 1
            run.status = "passed" if all(t.score is not None and t.selected is not None for t in run.twins) else "error"
            ta.score_candidate(run)
            runs.append(run)
        eff = ta.effects(runs)
        verdict, code, reasons = ta.decide(runs, eff, ta.impact_ratios(runs), 0.05, True)
        log.append({"k": "verdict", "t": f"VERDICT {verdict}"})
        log += [{"k": "dim", "t": f"  - {r}"} for r in reasons]
        log.append({"k": "ok" if code == 0 else "no",
                    "t": "== DEPLOY ALLOWED ==" if code == 0 else "== DEPLOY BLOCKED =="})
        job.update(verdict=verdict, code=code, status="finished")
    except Exception as e:  # noqa: BLE001 - report any failure to the page instead of crashing the worker
        log.append({"k": "no", "t": f"error: {type(e).__name__}: {e}"})
        job.update(status="error")
    finally:
        _last_finish[0] = time.time()


def start_live_check(target: str) -> tuple[dict | None, str | None]:
    if target not in TARGETS or "direct" not in TARGETS[target]:
        return None, "unknown tool"
    with _lock:
        running = next((j for j in _jobs.values() if j["status"] == "running"), None)
        if running and running["target"] == target:
            return running, None  # join the run already in progress for the same tool
        if running:
            return None, f"Please wait: a live check on {running['target']} is running. Try again in a moment."
        wait = COOLDOWN_S - (time.time() - _last_finish[0])
        if wait > 0:
            return None, f"Please wait {int(wait) + 1}s before starting another live check."
        total = sum(len(ta.pick_twins(MANIFEST[c], "short", True)) for c in LIVE_CANDIDATES)
        job = {"id": uuid.uuid4().hex[:12], "target": target, "status": "running", "lines": [],
               "done": 0, "total": total, "verdict": None, "code": None, "started": time.time()}
        for old in [k for k, j in _jobs.items() if j["status"] != "running"][:-5]:
            _jobs.pop(old, None)  # keep only a few finished jobs in memory
        _jobs[job["id"]] = job
    threading.Thread(target=_run, args=(job,), daemon=True).start()
    return job, None


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


# ------------------------------------------------------------------ public Kane run (GitHub Actions)

KANE_DAILY_CAP = int(os.environ.get("KANE_DAILY_CAP", "8"))
_kane_lock = threading.Lock()
_status_cache: dict = {"t": 0.0, "data": None}


def kane_enabled() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN"))


def _gh(path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}{path}",
                                 data=json.dumps(body).encode() if body is not None else None,
                                 method="POST" if body is not None else "GET",
                                 headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                                          "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
    return json.loads(raw) if raw else {}


def _recent_runs() -> list[dict]:
    since = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 86400))
    data = _gh(f"/actions/workflows/{WORKFLOW}/runs?event=workflow_dispatch&per_page=50&created=%3E%3D{since}")
    return data.get("workflow_runs", [])


def kane_status() -> dict:
    """Latest web-triggered Kane run and how many are left today (cached 10 s)."""
    if not kane_enabled():
        return {"enabled": False}
    if time.time() - _status_cache["t"] < 10 and _status_cache["data"]:
        return _status_cache["data"]
    try:
        runs = _recent_runs()
    except (OSError, ValueError):
        return {"enabled": True, "error": "Could not reach GitHub."}
    latest = runs[0] if runs else None
    data = {"enabled": True, "left_today": max(0, KANE_DAILY_CAP - len(runs)), "cap": KANE_DAILY_CAP,
            "latest": latest and {"title": latest.get("display_title") or latest.get("name"),
                                  "status": latest.get("status"), "conclusion": latest.get("conclusion"),
                                  "url": latest.get("html_url"), "created": latest.get("created_at")}}
    _status_cache.update(t=time.time(), data=data)
    return data


def trigger_kane_run(target: str, candidate: str) -> tuple[bool, str]:
    if not kane_enabled():
        return False, "Kane runs from the website are not configured on this server."
    if target not in TARGETS:
        return False, "Unknown tool."
    if candidate not in MANIFEST:
        return False, "Unknown candidate."
    with _kane_lock:
        try:
            runs = _recent_runs()
        except (OSError, ValueError):
            return False, "Could not reach GitHub."
        if any(r.get("status") != "completed" for r in runs):
            return False, "A Kane run is already in progress. Watch it below, then try again."
        if len(runs) >= KANE_DAILY_CAP:
            return False, f"Today's {KANE_DAILY_CAP} Kane runs are used up. Try again tomorrow."
        try:
            _gh(f"/actions/workflows/{WORKFLOW}/dispatches",
                {"ref": "main", "inputs": {"target": target, "candidates": candidate, "placebo": True}})
        except urllib.error.HTTPError as e:
            return False, f"GitHub refused the request ({e.code})."
        except OSError:
            return False, "Could not reach GitHub."
        _status_cache["t"] = 0.0
    return True, f"Kane is starting on {TARGETS[target].get('name', target)}, {candidate}: 8 CVs in a real browser, about 15 minutes."
