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
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

ROLES = {
    "data-analyst": {
        "title": "Data Analyst",
        "jd": ("Data Analyst. We are hiring a data analyst to turn business data into insight. "
               "You will build reports and dashboards, analyse trends, and present findings to stakeholders. "
               "Requirements: a degree in a quantitative field, several years of professional experience in "
               "analytics or a related role, strong communication skills, and the ability to work across teams. "
               "Additional languages are a plus. A recommendation from a previous employer is welcome."),
    },
}

app = Flask(__name__)
_ids = itertools.count(1)
DRAFTS: dict[int, dict] = {}
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


def calibrate(write: bool = False) -> float:
    """Shortlist cutoff = median similarity over an independent calibration pool
    (data/calibration.json: CVs that are never used in any audit), so about half pass.
    The value is cached in data/quickmatch_cutoff.json; `python targets/quickmatch/app.py --calibrate` refreshes it."""
    if os.environ.get("QUICKMATCH_CUTOFF"):
        return float(os.environ["QUICKMATCH_CUTOFF"])
    if CUTOFF_FILE.exists() and not write:
        return float(json.loads(CUTOFF_FILE.read_text())["cutoff"])
    pool = ROOT / "data" / "calibration.json"
    if not pool.exists():
        return 0.5
    cut = float(np.median(embed(json.loads(pool.read_text())) @ jd_vec("data-analyst")))
    CUTOFF_FILE.write_text(json.dumps({"cutoff": cut, "model": MODEL_ID, "pool": "data/calibration.json"}, indent=1))
    return cut


CUTOFF = calibrate()


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
        d["cv"] = (request.form.get("candidate_cv") or "").strip()
        if d["cv"]:
            return redirect(url_for("step_review", did=did))
    return render_template("step_cv.html", d=d, role=ROLES[d["role"]], step=2,
                           error=request.method == "POST")


@app.get("/match/<int:did>/review")
def step_review(did: int):
    d = DRAFTS.get(did) or abort(404)
    if not d["cv"]:
        return redirect(url_for("step_cv", did=did))
    return render_template("step_review.html", d=d, role=ROLES[d["role"]], step=3)


@app.post("/match/<int:did>/run")
def run_match(did: int):
    d = DRAFTS.get(did) or abort(404)
    d["similarity"] = similarity(d["cv"], d["role"])
    d["recommended"] = d["similarity"] >= CUTOFF
    return redirect(url_for("result", did=did))


@app.get("/match/<int:did>")
def result(did: int):
    d = DRAFTS.get(did) or abort(404)
    if "similarity" not in d:
        return redirect(url_for("step_review", did=did))
    return render_template("result.html", d=d, role=ROLES[d["role"]], cutoff=CUTOFF, step=4)


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
        print(f"cutoff = {calibrate(write=True):.4f} -> {CUTOFF_FILE}")
    elif "--download" in sys.argv:
        embedder()
        print(f"model cached in {CACHE_DIR}")
    else:
        app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5103)))
