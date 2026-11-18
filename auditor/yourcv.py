"""Twin your own CV: a free spot check on the website (Python only: no Kane, no credits).

The visitor's CV is rewritten under eight test names (4 demographic twins + 4 placebo names from the
same groups, exactly as in the audit): only the name, the email address and he/she pronouns change.
Every version is then submitted to each demo tool through the tool's own form, in-process, and the
score and decision are read off the tool's own result page, the same path the audit's dry run uses.

Privacy: the CV is held in memory only for the few seconds the check takes. Each tool's stored copy
is deleted as soon as its score is read. The CV versions are handed to the visitor's browser once (to show
them side by side) and then dropped; the scores are forgotten after ten minutes. Nothing is sent to Kane, GitHub or TestMu.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import threading
import time
import uuid
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "audit"))
import twin_audit as ta  # noqa: E402
from cvkit import cv  # noqa: E402

TARGETS = json.loads((ROOT / "audit" / "targets.json").read_text(encoding="utf-8"))
TOOL_ORDER = ["talentscreen", "hirelens", "quickmatch"]
TOOL_FILES = {k: f"targets/{k}/app.py" for k in TOOL_ORDER}
STORES = {"talentscreen": "DECISIONS", "hirelens": "APPLICANTS"}  # where a tool keeps a submission
MAX_CHARS = 20000
HEADER = re.compile(r"(?i)^\s*(curriculum\s+vitae|resume|résumé|cv)\s*:?\s*$")
NAME_WORD = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]*$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
SAMPLE = {"candidate": "cand02", "length": "short"}  # the CV from the Kane-verified QuickMatch story

_lock = threading.Lock()
_jobs: dict[str, dict] = {}
_modules: dict[str, object] = {}
_mod_lock = threading.Lock()


class CVError(ValueError):
    """A problem the visitor can fix, worded for them."""


# ------------------------------------------------------------------ twins

def find_name(text: str) -> tuple[str, list[str]]:
    """Return the candidate's name and the CV lines, with the name on the first line (as the tools expect)."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    while lines and (not lines[0].strip() or HEADER.match(lines[0])):
        lines.pop(0)  # a "Curriculum Vitae" heading above the name
    if not lines:
        raise CVError("The CV looks empty.")
    head = re.split(r"\s+[|•·–—-]\s+|,|\t", lines[0].strip())[0].strip()
    words = head.split()
    if not 2 <= len(words) <= 4 or not all(NAME_WORD.match(w) for w in words):
        raise CVError("Put your full name on the first line of the CV (for example \"Ada Obi\"), then try again.")
    return head, lines


def swap_pronouns(text: str, gender: str) -> str:
    if gender == "female":
        pairs = [("He", "She"), ("he", "she"), ("Himself", "Herself"), ("himself", "herself"),
                 ("His", "Her"), ("his", "her"), ("Him", "Her"), ("him", "her"), ("Mr", "Ms")]
    else:
        pairs = [("She", "He"), ("she", "he"), ("Herself", "Himself"), ("herself", "himself"),
                 ("Her", "His"), ("her", "his"), ("Mrs", "Mr"), ("Ms", "Mr"), ("Miss", "Mr")]
    table = dict(pairs)
    return re.sub(r"\b(" + "|".join(re.escape(a) for a, _ in pairs) + r")\b", lambda m: table[m.group(1)], text)


def make_twin(name: str, lines: list[str], first: str, last: str, gender: str) -> str:
    """The same CV under another name: name, email and pronouns change, nothing else."""
    old_first = name.split()[0]
    new_name = f"{first} {last}"
    if name.isupper():
        new_name = new_name.upper()
    head = lines[0].strip()
    body = "\n".join(lines[1:])
    email = f"{first}.{last}@example.com".lower().replace("'", "")
    body = EMAIL.sub(email, body)
    body = re.sub(re.escape(name), lambda _: new_name, body, flags=re.IGNORECASE)
    body = re.sub(rf"\b{re.escape(old_first)}\b", lambda _: first, body)
    body = swap_pronouns(body, gender)
    head = new_name + EMAIL.sub(email, head[len(name):])
    return head + ("\n" + body if body else "")


def identities(text: str) -> list[dict]:
    """Eight test identities: (male, female) x (group A, group C), two names each (slot 1 = placebo)."""
    seed = zlib.crc32(text.encode("utf-8")) % 9
    out = []
    for slot in (0, 1):
        for who in cv.identities_for(seed, slot):
            out.append({"gender": who.gender, "group": who.group, "slot": slot, "first": who.first, "last": who.last})
    return out


def sample_cv() -> tuple[str, list[dict]]:
    """A fictional CV from the audit, with the audit's own eight names for it."""
    cand = {c["candidate"]: c for c in json.loads((ROOT / "data" / "cvs" / "manifest.json").read_text())}[SAMPLE["candidate"]]
    vs = [v for v in cand["variants"] if v["length"] == SAMPLE["length"]]
    base = next(v for v in vs if v["gender"] == "male" and v["group"] == "A" and v["slot"] == 0)
    ids = [{"gender": v["gender"], "group": v["group"], "slot": v["slot"], "first": v["name"].split()[0],
            "last": " ".join(v["name"].split()[1:])} for v in sorted(vs, key=lambda v: (v["slot"], v["gender"] != "male", v["group"]))]
    return (ROOT / base["file"]).read_text(encoding="utf-8"), ids


# ------------------------------------------------------------------ tools

def tool_module(target: str):
    """The demo tool's module: the one serve.py mounted, or loaded here when the site runs on its own."""
    name = f"{target}_app"
    with _mod_lock:
        mod = sys.modules.get(name) or _modules.get(name)
        if mod is None:
            spec = importlib.util.spec_from_file_location(name, ROOT / TOOL_FILES[target])
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            _modules[name] = mod
    return mod


def tool_meta(target: str) -> dict:
    mod = tool_module(target)
    cut = getattr(mod, "CUTOFF", None) or getattr(mod, "THRESHOLD", None) or 0.5
    return {"key": target, "cutoff": round(float(cut), 4), "max": 0.5 if target == "quickmatch" else 1.0}


def submit(target: str, text: str) -> dict:
    """Post one CV to the tool's own form, read its own result page, then delete the tool's stored copy."""
    mod = tool_module(target)
    d = TARGETS[target]["direct"]
    client = mod.app.test_client()
    resp = client.post(d["post"], data={**d.get("extra", {}), d["field"]: text})
    store_id = None
    try:
        if resp.status_code in (301, 302, 303):
            loc = resp.headers.get("Location", "")
            m = re.search(r"/(\d+)$", loc)
            if not m:  # the tool sent us back to its form: it could not read this CV
                err = re.search(r"error=(\w+)", loc)
                return {"score": None, "selected": None, "error": err.group(1) if err else "unreadable"}
            store_id = int(m.group(1))
            resp = client.get(loc)
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", resp.get_data(as_text=True)))
        sm, dm = re.search(d["score_re"], flat), re.search(d["decision_re"], flat)
        if not sm:
            return {"score": None, "selected": None, "error": "noscore"}
        decision = dm.group(1).strip() if dm else None
        return {"score": round(ta.normalise(float(sm.group(1))), 4), "decision": decision,
                "selected": ta.to_selected(decision)}
    finally:
        store = getattr(mod, STORES.get(target, ""), None)
        if store is not None and store_id is not None:
            store.pop(store_id, None)


# ------------------------------------------------------------------ jobs

def _summary(target: str, original: dict, twins: list[dict]) -> dict:
    run = ta.CandidateRun("visitor", [])
    for t in twins:
        r = t["scores"][target]
        tr = ta.TwinResult(t["gender"], t["group"], t["slot"], t["name"], "")
        tr.score, tr.selected = r.get("score"), r.get("selected")
        run.twins.append(tr)
    ta.score_candidate(run)
    scores = [t["scores"][target].get("score") for t in twins if t["scores"][target].get("score") is not None]
    return {"swing": round(max(scores) - min(scores), 4) if scores else None,
            "demo_gap": None if run.demo_gap is None else round(run.demo_gap, 4),
            "placebo_gap": None if run.placebo_gap is None else round(run.placebo_gap, 4),
            "demo_flip": run.demo_flip, "placebo_flip": run.placebo_flip,
            "flip": len({t["scores"][target].get("selected") for t in twins} - {None}) > 1,
            "readable": len(scores) == len(twins)}


def _run(job: dict, text: str, ids: list[dict] | None) -> None:
    try:
        name, lines = find_name(text)
        ids = ids or identities(text)
        job["name"] = name
        twins = [{**i, "name": f"{i['first']} {i['last']}",
                  "text": make_twin(name, lines, i["first"], i["last"], i["gender"]), "scores": {}} for i in ids]
        original = "\n".join(lines)
        job["cv"] = {"original": original, "twins": [t["text"] for t in twins]}
        job["twins"] = [{k: t[k] for k in ("name", "gender", "group", "slot")} for t in twins]
        job["tools"] = [tool_meta(k) for k in TOOL_ORDER]
        job["total"] = len(TOOL_ORDER) * (len(twins) + 1)
        job["original"] = {}
        for target in TOOL_ORDER:
            job["original"][target] = submit(target, original)
            job["done"] += 1
            for i, t in enumerate(twins):
                t["scores"][target] = submit(target, t["text"])
                job["twins"][i]["scores"] = t["scores"]
                job["done"] += 1
        job["summary"] = {k: _summary(k, job["original"][k], twins) for k in TOOL_ORDER}
        job["status"] = "finished"
    except CVError as e:
        job.update(status="error", error=str(e))
    except Exception as e:  # noqa: BLE001 - tell the page instead of crashing the worker
        job.update(status="error", error=f"Something went wrong while scoring ({type(e).__name__}). Please try again.")
    finally:
        job["finished_at"] = time.time()
        # the CV versions wait at most two minutes for the browser to collect them
        timer = threading.Timer(120, lambda: job.pop("cv", None))
        timer.daemon = True
        timer.start()


def start(text: str | None, use_sample: bool) -> tuple[dict | None, str | None]:
    ids = None
    if use_sample:
        text, ids = sample_cv()
    text = (text or "").strip()
    if not text:
        return None, "Paste your CV text or upload a file first."
    if len(text) > MAX_CHARS:
        return None, f"That CV is very long. Please keep it under {MAX_CHARS // 1000}k characters."
    with _lock:
        now = time.time()
        for k in [k for k, j in _jobs.items() if j.get("finished_at") and now - j["finished_at"] > 600]:
            _jobs.pop(k, None)  # forget finished checks after 10 minutes
        if sum(1 for j in _jobs.values() if j["status"] == "running") >= 2:
            return None, "Two checks are already running. Please try again in a few seconds."
        job = {"id": uuid.uuid4().hex, "status": "running", "done": 0, "total": 27, "sample": use_sample,
               "started": now, "finished_at": None}
        _jobs[job["id"]] = job
    threading.Thread(target=_run, args=(job, text, ids), daemon=True).start()
    return job, None


def _purge() -> None:
    now = time.time()
    with _lock:
        for k in [k for k, j in _jobs.items() if j.get("finished_at") and now - j["finished_at"] > 600]:
            _jobs.pop(k, None)  # forget finished checks after 10 minutes


def get(job_id: str) -> dict | None:
    _purge()
    return _jobs.get(job_id)
