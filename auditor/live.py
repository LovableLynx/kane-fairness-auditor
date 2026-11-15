"""Live audits from the website.

1. Live check (public, free): submits CV twins to a demo tool's own form, reads score and
   decision, and computes the same verdict as the Kane audit. It talks to the tool over HTTP
   (or in-process when the tools share this server), so it is fast and costs no Kane credits,
   but it is not browser-verified. One job at a time, short cooldown.
2. Kane run (owner only): triggers the GitHub Actions fairness gate, where Kane CLI drives the
   real UI. Needs GITHUB_TOKEN and AUDIT_ADMIN_KEY set on the server; otherwise disabled.
"""
from __future__ import annotations

import hmac
import json
import os
import re
import sys
import threading
import time
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


# ------------------------------------------------------------------ owner-only Kane run

def kane_enabled() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN") and os.environ.get("AUDIT_ADMIN_KEY"))


def trigger_kane_run(target: str, key: str) -> tuple[bool, str]:
    admin = os.environ.get("AUDIT_ADMIN_KEY", "")
    if not kane_enabled():
        return False, "Kane runs from the website are not configured on this server."
    if not hmac.compare_digest(key.encode(), admin.encode()):
        time.sleep(1.5)  # slow down guessing
        return False, "Wrong passcode."
    if target not in TARGETS:
        return False, "Unknown tool."
    body = json.dumps({"ref": "main", "inputs": {"target": target, "candidates": "cand01", "placebo": False}}).encode()
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches",
                                 data=body, method="POST",
                                 headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
                                          "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    try:
        urllib.request.urlopen(req, timeout=20)
    except urllib.error.HTTPError as e:
        return False, f"GitHub refused the request ({e.code})."
    except OSError:
        return False, "Could not reach GitHub."
    return True, f"https://github.com/{REPO}/actions/workflows/{WORKFLOW}"
