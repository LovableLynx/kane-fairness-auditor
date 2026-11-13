"""HireScore -- a deliberately simple AI screening portal used as the system under test.

Run:  HIRESCORE_MODEL=fair python app/app.py
      (models: fair | gender_biased | ethnicity_biased)
"""
import json
import os
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

import scoring

ROOT = Path(__file__).resolve().parents[1]
app = Flask(__name__)
CANDIDATES = {c["id"]: c for c in scoring.load_candidates()}


def latest_audit() -> dict | None:
    p = ROOT / "reports" / "audit.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


@app.context_processor
def inject_globals():
    return {"model_name": scoring.model_name(), "audit": latest_audit()}


@app.get("/")
def index():
    return render_template("index.html", candidates=CANDIDATES.values())


@app.get("/candidate/<int:cid>")
def candidate(cid: int):
    c = CANDIDATES.get(cid) or abort(404)
    f = c["features"]
    return render_template(
        "candidate.html",
        c=c,
        genders=scoring.GENDERS,
        ethnicities=scoring.ETHNICITIES,
        current_gender=scoring.label_for(f[scoring.COL_GENDER], scoring.GENDERS),
        current_ethnicity=scoring.label_for(f[scoring.COL_ETHNICITY], scoring.ETHNICITIES),
    )


@app.post("/candidate/<int:cid>/score")
def score_candidate(cid: int):
    c = CANDIDATES.get(cid) or abort(404)
    gender = request.form.get("gender", "")
    ethnicity = request.form.get("ethnicity", "")
    if gender not in scoring.GENDERS or ethnicity not in scoring.ETHNICITIES:
        abort(400)
    s = scoring.score(c["features"], gender, ethnicity)
    return render_template(
        "result.html",
        c=c,
        gender=gender,
        ethnicity=ethnicity,
        score=s,
        shortlisted=s >= scoring.SHORTLIST_THRESHOLD,
    )


@app.get("/api/score/<int:cid>")
def api_score(cid: int):
    """JSON twin of the form flow -- used by `audit.py --direct` for cheap dry runs."""
    c = CANDIDATES.get(cid) or abort(404)
    gender = request.args.get("gender", "")
    ethnicity = request.args.get("ethnicity", "")
    if gender not in scoring.GENDERS or ethnicity not in scoring.ETHNICITIES:
        abort(400)
    return {"candidate": cid, "gender": gender, "ethnicity": ethnicity,
            "score": round(scoring.score(c["features"], gender, ethnicity), 3)}


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/healthz")
def healthz():
    return {"ok": True, "model": scoring.model_name()}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5055)), debug=False)
