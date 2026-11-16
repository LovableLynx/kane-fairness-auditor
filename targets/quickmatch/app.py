"""QuickMatch -- target C. A three-step wizard (role -> CV -> review) that ranks a CV by
semantic similarity to the job description using an off-the-shelf open-source
embedding model (sentence-transformers/all-MiniLM-L6-v2 via fastembed).

We did not train this model and we do not know how it treats names: it is the
genuine black box in the demo. The CV is embedded as-is, name included, the way
many "AI match score" features work.

    python targets/quickmatch/app.py     # port 5103
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import threading
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding
from flask import Flask, abort, redirect, render_template, request, url_for

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from shared.hardening import BoundedStore, harden  # noqa: E402
from shared.samples import samples  # noqa: E402

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

def _jd(title: str, body: str) -> str:
    return (f"{title}. {body} Strong communication skills and the ability to work across teams are important. "
            "Additional languages are a plus. A recommendation from a previous employer is welcome.")


ROLES = {  # the first role is the default; the fairness audit uses "data-analyst"
    "data-analyst": {"title": "Data Analyst", "emoji": "📊", "team": "Insights",
        "jd": ("Data Analyst. We are hiring a data analyst to turn business data into insight. "
               "You will build reports and dashboards, analyse trends, and present findings to stakeholders. "
               "Requirements: a degree in a quantitative field, several years of professional experience in "
               "analytics or a related role, strong communication skills, and the ability to work across teams. "
               "Additional languages are a plus. A recommendation from a previous employer is welcome.")},
    "software-engineer": {"title": "Software Engineer", "emoji": "💻", "team": "Platform",
        "jd": _jd("Software Engineer", "We are hiring a software engineer to build and maintain reliable web services. "
                  "You will write well-tested Python and SQL, review code and improve our delivery pipeline. "
                  "Requirements: a degree in computer science or a related field and several years of professional engineering experience.")},
    "project-manager": {"title": "Project Manager", "emoji": "🗂️", "team": "Delivery",
        "jd": _jd("Project Manager", "We are hiring a project manager to lead cross-functional delivery of business projects. "
                  "You will plan work, manage risks and budgets, and run stakeholder reviews. "
                  "Requirements: a degree and several years of project management experience.")},
    "accountant": {"title": "Accountant", "emoji": "🧾", "team": "Finance",
        "jd": _jd("Accountant", "We are hiring an accountant to prepare management accounts and support audits. "
                  "You will reconcile ledgers, close the books each month and improve finance processes. "
                  "Requirements: a degree in accounting or finance and several years of professional experience.")},
    "marketing-specialist": {"title": "Marketing Specialist", "emoji": "📣", "team": "Growth",
        "jd": _jd("Marketing Specialist", "We are hiring a marketing specialist to plan and run multi-channel campaigns. "
                  "You will analyse campaign performance, manage content and run experiments. "
                  "Requirements: a degree and several years of marketing experience.")},
    "nurse": {"title": "Registered Nurse", "emoji": "🩺", "team": "Patient care",
        "jd": _jd("Registered Nurse", "We are hiring a nurse to deliver safe, compassionate patient care on a busy ward. "
                  "You will keep accurate clinical records, support audits and mentor students. "
                  "Requirements: a nursing qualification and several years of clinical experience.")},
    "teacher": {"title": "Teacher", "emoji": "📚", "team": "Education",
        "jd": _jd("Teacher", "We are hiring a teacher to plan and deliver engaging lessons and track student progress. "
                  "You will use assessment data, lead curriculum work and communicate with parents. "
                  "Requirements: a degree, a teaching qualification and several years of classroom experience.")},
}

app = Flask(__name__)
harden(app)
_ids = itertools.count(1)
DRAFTS: BoundedStore = BoundedStore(300)
# Model files live inside the project so a host can download them at build time.
CACHE_DIR = os.environ.get("FASTEMBED_CACHE", str(ROOT / ".fastembed_cache"))
CUTOFF_FILE = ROOT / "data" / "quickmatch_cutoff.json"

_lock = threading.Lock()
_embedder: TextEmbedding | None = None
_jd_vec: dict[str, np.ndarray] = {}


def embedder() -> TextEmbedding:
    """Load the model on first use, so the web server starts fast on small hosts."""
    global _embedder
    with _lock:
        if _embedder is None:
            _embedder = TextEmbedding(MODEL_ID, cache_dir=CACHE_DIR, threads=1)
    return _embedder


def embed(texts: list[str]) -> np.ndarray:
    v = np.array(list(embedder().embed(texts)))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def jd_vec(role: str) -> np.ndarray:
    if role not in _jd_vec:
        _jd_vec[role] = embed([ROLES[role]["jd"]])[0]
    return _jd_vec[role]


def similarity(cv_text: str, role: str) -> float:
    return float(embed([cv_text])[0] @ jd_vec(role))


def calibrate(write: bool = False) -> dict[str, float]:
    """Shortlist cutoff per role = median similarity of an independent calibration pool
    (data/calibration.json: CVs never used in any audit) against that role's job description,
    so about half of the pool passes for every role. Cached in data/quickmatch_cutoff.json;
    `python targets/quickmatch/app.py --calibrate` refreshes it."""
    if os.environ.get("QUICKMATCH_CUTOFF"):
        return {k: float(os.environ["QUICKMATCH_CUTOFF"]) for k in ROLES}
    if CUTOFF_FILE.exists() and not write:
        data = json.loads(CUTOFF_FILE.read_text())
        cuts = data.get("cutoffs") or {"data-analyst": data["cutoff"]}
        return {k: float(cuts.get(k, cuts.get("data-analyst", 0.5))) for k in ROLES}
    pool = ROOT / "data" / "calibration.json"
    if not pool.exists():
        return {k: 0.5 for k in ROLES}
    vecs = embed(json.loads(pool.read_text()))
    cuts = {k: float(np.median(vecs @ jd_vec(k))) for k in ROLES}
    CUTOFF_FILE.write_text(json.dumps({"cutoff": cuts["data-analyst"], "cutoffs": cuts, "model": MODEL_ID,
                                       "pool": "data/calibration.json",
                                       "method": "median similarity of the calibration pool, per role"}, indent=1))
    return cuts


CUTOFFS = calibrate()
CUTOFF = CUTOFFS["data-analyst"]  # used by the audit's dev endpoint


@app.get("/")
def step_role():
    return render_template("step_role.html", roles=ROLES, step=1)


@app.post("/start")
def start():
    role = request.form.get("role")
    if role not in ROLES:
        abort(400)
    d = {"id": next(_ids), "role": role, "cv": ""}
    DRAFTS[d["id"]] = d
    return redirect(url_for("step_cv", did=d["id"]))


@app.route("/match/<int:did>/candidate", methods=["GET", "POST"])
def step_cv(did: int):
    d = DRAFTS.get(did) or abort(404)
    if request.method == "POST":
        d["cv"] = (request.form.get("candidate_cv") or "").strip()[:20000]
        if d["cv"]:
            return redirect(url_for("step_review", did=did))
    return render_template("step_cv.html", d=d, role=ROLES[d["role"]], step=2, samples=samples(),
                           error=request.method == "POST")


@app.get("/match/<int:did>/review")
def step_review(did: int):
    d = DRAFTS.get(did) or abort(404)
    if "similarity" in d:
        return redirect(url_for("result", did=did))
    if not d["cv"]:
        return redirect(url_for("step_cv", did=did))
    return render_template("step_review.html", d=d, role=ROLES[d["role"]], step=3)


@app.post("/match/<int:did>/run")
def run_match(did: int):
    d = DRAFTS.get(did) or abort(404)
    if "similarity" in d:
        return redirect(url_for("result", did=did))
    if not d["cv"]:
        return redirect(url_for("step_cv", did=did))
    d["similarity"] = similarity(d["cv"], d["role"])
    d["recommended"] = d["similarity"] >= CUTOFFS[d["role"]]
    d["cv"] = ""  # data minimisation: the CV text is not kept once it has been scored
    return redirect(url_for("result", did=did))


@app.get("/match/<int:did>")
def result(did: int):
    d = DRAFTS.get(did) or abort(404)
    if "similarity" not in d:
        return redirect(url_for("step_review", did=did))
    return render_template("result.html", d=d, role=ROLES[d["role"]], cutoff=CUTOFFS[d["role"]], step=4)


@app.post("/api/match")
def api_match():
    """Dev-only shortcut used by the auditor's --direct dry runs."""
    cv_text = request.form.get("candidate_cv", "")
    s = similarity(cv_text, "data-analyst")
    return (f"<p>Similarity score: {s:.3f}</p>"
            f"<p>Verdict: {'Recommended for interview' if s >= CUTOFF else 'Not recommended'}</p>")


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/healthz")
def healthz():
    return {"ok": True, "target": "quickmatch", "model": MODEL_ID, "cutoff": round(CUTOFF, 4)}


if __name__ == "__main__":
    if "--calibrate" in sys.argv:
        print(f"cutoffs = {calibrate(write=True)} -> {CUTOFF_FILE}")
    elif "--download" in sys.argv:
        embedder()
        print(f"model cached in {CACHE_DIR}")
    else:
        app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5103)))
