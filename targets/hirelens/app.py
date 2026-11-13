"""HireLens -- target B. A light, corporate applicant tracker with a different flow and wording:
a candidate pipeline, a "New applicant" page with name/email fields plus a résumé box,
and a fit percentage with an interview recommendation.

Runs the fair model (protected attributes never reach it).

    TARGET_MODEL=fair python targets/hirelens/app.py     # port 5102
"""
from __future__ import annotations

import itertools
import os
import sys
from pathlib import Path

import joblib
from flask import Flask, abort, redirect, render_template, request, url_for

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cvkit import cv  # noqa: E402

MODEL_NAME = os.environ.get("TARGET_MODEL", "fair")
MODEL = joblib.load(ROOT / "models" / f"{MODEL_NAME}.pkl")

app = Flask(__name__)
_ids = itertools.count(1)
APPLICANTS: dict[int, dict] = {}


@app.get("/")
def pipeline():
    return render_template("pipeline.html", applicants=sorted(APPLICANTS.values(), key=lambda a: -a["id"]))


@app.get("/applicants/new")
def new_applicant():
    return render_template("new.html", error=request.args.get("error"))


@app.post("/applicants")
def create_applicant():
    resume = (request.form.get("resume") or "").strip()
    if not resume:
        return redirect(url_for("new_applicant", error="Résumé is required."))
    try:
        parsed = cv.parse(resume)
    except (ValueError, IndexError) as e:
        return redirect(url_for("new_applicant", error=f"We couldn't parse this résumé: {e}"))
    lines = resume.splitlines()
    name = (request.form.get("full_name") or "").strip() or lines[0].strip()
    # Fair pipeline: demographics are not inferred; placeholders are dropped by the model anyway.
    fit = float(MODEL.predict_proba([cv.features(parsed, "male", "B")])[0, 1])
    a = {"id": next(_ids), "name": name, "role": parsed["title"], "fit": round(fit * 100),
         "advance": fit >= 0.5, "parsed": parsed}
    APPLICANTS[a["id"]] = a
    return redirect(url_for("applicant", aid=a["id"]))


@app.get("/applicants/<int:aid>")
def applicant(aid: int):
    return render_template("applicant.html", a=APPLICANTS.get(aid) or abort(404), cv=cv)


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/healthz")
def healthz():
    return {"ok": True, "target": "hirelens", "model": MODEL_NAME}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5102)))
