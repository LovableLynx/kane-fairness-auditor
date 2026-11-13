"""TalentScreen -- target A. A recruiter drops a CV, the AI shortlists or rejects it.

This target deliberately reads the candidate's name and pronouns (as some real tools
do) and feeds the inferred demographics to its model. The auditor does not know that.

    TARGET_MODEL=biased python targets/talentscreen/app.py   # port 5101
"""
from __future__ import annotations

import itertools
import os
import sys
from datetime import datetime
from pathlib import Path

import joblib
from flask import Flask, abort, redirect, render_template, request, url_for

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cvkit import cv  # noqa: E402

MODEL_NAME = os.environ.get("TARGET_MODEL", "biased")
MODEL = joblib.load(ROOT / "models" / f"{MODEL_NAME}.pkl")
THRESHOLD = 0.5
JOB = {"title": "Data Analyst", "team": "Insights", "location": "Remote"}

app = Flask(__name__)
app.jinja_env.globals["zip"] = zip
_ids = itertools.count(1001)
DECISIONS: dict[int, dict] = {}


def screen(text: str, source: str) -> dict:
    parsed = cv.parse(text)
    gender, group = cv.infer_identity(text)
    score = float(MODEL.predict_proba([cv.features(parsed, gender, group)])[0, 1])
    name = text.strip().splitlines()[0].strip()
    strengths = []
    if parsed["years"] >= 6:
        strengths.append(f"{parsed['years']} years' experience")
    if parsed["education"] >= 0.8:
        strengths.append("postgraduate degree")
    if parsed["recommendation"]:
        strengths.append("recommendation letter")
    if sum(v >= 0.6 for v in parsed["languages"]) >= 2:
        strengths.append("multilingual")
    d = {
        "id": next(_ids), "name": name, "score": score, "shortlisted": score >= THRESHOLD,
        "parsed": parsed, "strengths": strengths, "source": source,
        "at": datetime.now().strftime("%H:%M:%S"),
    }
    DECISIONS[d["id"]] = d
    return d


@app.get("/")
def home():
    recent = sorted(DECISIONS.values(), key=lambda d: d["id"], reverse=True)[:8]
    return render_template("home.html", job=JOB, recent=recent, error=request.args.get("error"))


@app.post("/screen")
def screen_cv():
    text = (request.form.get("cv_text") or "").strip()
    source = "pasted"
    f = request.files.get("cv_file")
    if f and f.filename:
        if not f.filename.lower().endswith(".txt"):
            return redirect(url_for("home", error="Please upload a .txt CV for now."))
        text, source = f.read().decode("utf-8", errors="replace"), f"uploaded {f.filename}"
    if not text:
        return redirect(url_for("home", error="Add a CV first."))
    try:
        d = screen(text, source)
    except (ValueError, IndexError) as e:
        return redirect(url_for("home", error=f"Couldn't read that CV ({e})."))
    return redirect(url_for("result", did=d["id"]))


@app.get("/result/<int:did>")
def result(did: int):
    d = DECISIONS.get(did) or abort(404)
    return render_template("result.html", d=d, job=JOB, cv=cv)


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/healthz")
def healthz():
    return {"ok": True, "target": "talentscreen", "model": MODEL_NAME}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5101)))
