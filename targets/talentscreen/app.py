"""TalentScreen -- target A. A recruiter drops a CV, the AI shortlists or rejects it.

This target deliberately reads the candidate's name and pronouns (as some real tools
do) and feeds the inferred demographics to its model. The auditor does not know that.

    TARGET_MODEL=biased python targets/talentscreen/app.py   # port 5101
"""
from __future__ import annotations

import itertools
import os
import time
import sys
from datetime import datetime
from pathlib import Path

import joblib
from flask import Flask, abort, redirect, render_template, request, url_for

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cvkit import cv  # noqa: E402
from cvkit.extract import SUPPORTED, UnsupportedFile, to_text  # noqa: E402
from shared.hardening import BoundedStore, harden  # noqa: E402
from shared.samples import samples  # noqa: E402
from shared import roles  # noqa: E402

MODEL_NAME = os.environ.get("TARGET_MODEL", "biased")
MODEL = joblib.load(ROOT / "models" / f"{MODEL_NAME}.pkl")
THRESHOLD = 0.5
JOB = roles.get(roles.DEFAULT)
ERRORS = {
    "empty": "Add a CV first: drop a file or paste the text.",
    "filetype": "That file type isn't supported. Upload a .txt, .pdf or .docx CV.",
    "unreadable": "We couldn't read that file. Try saving it as PDF or plain text, or paste the text instead.",
    "norole": "That doesn't look like a CV: we couldn't find a job title, experience or education. Paste the full CV text or try a sample.",
}
FIELD_LABELS = {"role": "Role", "experience": "Experience", "education": "Education",
                "language": "Languages", "recommendation": "Recommendation", "availability": "Availability"}

app = Flask(__name__)
app.jinja_env.globals["zip"] = zip
harden(app, ERRORS)
_ids = itertools.count(1001)
DECISIONS: BoundedStore = BoundedStore(300)


@app.context_processor
def job_context():
    return {"job": JOB}


def screen(text: str, source: str, role: dict) -> dict:
    t0 = time.perf_counter()
    parsed = cv.parse(text)
    gender, group = cv.infer_identity(text)
    score = float(MODEL.predict_proba([cv.features(roles.for_role(parsed, role), gender, group)])[0, 1])
    name = text.strip().splitlines()[0].strip()[:80]
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
        "parsed": parsed, "strengths": strengths, "source": source, "job": role,
        "role_match": int(parsed["occupation"]) == role["family"] or (role["slug"] == roles.DEFAULT and parsed["suitability"] >= 1.0),
        "at": datetime.now().strftime("%H:%M"), "ms": round((time.perf_counter() - t0) * 1000),
        "initials": "".join(w[0] for w in name.split()[:2]).upper() or "?",
    }
    DECISIONS[d["id"]] = d
    return d


@app.get("/")
def home():
    recent = sorted(DECISIONS.values(), key=lambda d: d["id"], reverse=True)[:8]
    allv = list(DECISIONS.values())
    stats = {"count": len(allv),
             "short_rate": round(100 * sum(d["shortlisted"] for d in allv) / len(allv)) if allv else None,
             "avg_ms": round(sum(d.get("ms", 0) for d in allv) / len(allv)) if allv else None}
    return render_template("home.html", job=JOB, recent=recent, stats=stats, samples=samples(), roles=roles.ROLES,
                           role=roles.get(request.args.get("role")).get("slug"),
                           accept=",".join(SUPPORTED))


@app.post("/screen")
def screen_cv():
    text = (request.form.get("cv_text") or "").strip()
    source = "pasted"
    f = request.files.get("cv_file")
    if f and f.filename:
        try:
            text, source = to_text(f.filename, f.read()), f"uploaded {Path(f.filename).name[:60]}"
        except UnsupportedFile as e:
            return redirect(url_for("home", error="filetype" if "upload a" in str(e) else "unreadable"))
    if not text.strip():
        return redirect(url_for("home", error="empty"))
    try:
        d = screen(text, source, roles.get(request.form.get("role")))
    except (ValueError, IndexError):
        return redirect(url_for("home", error="norole"))
    return redirect(url_for("result", did=d["id"]))


@app.get("/result/<int:did>")
def result(did: int):
    d = DECISIONS.get(did) or abort(404)
    return render_template("result.html", d=d, job=d.get("job", JOB), cv=cv, labels=FIELD_LABELS)


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/healthz")
def healthz():
    return {"ok": True, "target": "talentscreen", "model": MODEL_NAME}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5101)))
