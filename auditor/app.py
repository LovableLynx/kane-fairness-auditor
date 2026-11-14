"""Fairness Auditor: the product site (landing, results, method, legal).

    python auditor/app.py        # http://127.0.0.1:5100
Reads published audit results from results/ (override with AUDIT_REPORTS).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from flask import Flask, abort, redirect, render_template, url_for

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shared.hardening import harden  # noqa: E402

RESULTS = Path(os.environ.get("AUDIT_REPORTS", ROOT / "results"))
REPO = "https://github.com/LovableLynx/kane-fairness-auditor"
# Where the three demo tools live. In the single-service deployment they are mounted under these paths.
TOOL_URLS = {
    "talentscreen": os.environ.get("TALENTSCREEN_URL", "/talentscreen/"),
    "hirelens": os.environ.get("HIRELENS_URL", "/hirelens/"),
    "quickmatch": os.environ.get("QUICKMATCH_URL", "/quickmatch/"),
}
TOOLS = {
    "talentscreen": {"name": "TalentScreen", "ui": "Drag-and-drop CV screener with a 0–1 match score",
                     "model": "Logistic regression trained on labels with injected bias", "role": "Known biased"},
    "hirelens": {"name": "HireLens", "ui": "Applicant tracker with role-fit percentages",
                 "model": "Logistic regression without protected attributes", "role": "Known fair"},
    "quickmatch": {"name": "QuickMatch", "ui": "Three-step wizard with a similarity score",
                   "model": "Open-source all-MiniLM-L6-v2 embeddings", "role": "Real black box"},
}

app = Flask(__name__)
harden(app)


def load_reports() -> dict[str, dict]:
    out = {}
    for p in sorted(RESULTS.glob("twin_audit_*.json")):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        r["verified"] = r.get("driver", "").startswith("Kane")
        r["verdict_class"] = r.get("verdict", "INCONCLUSIVE").split(":")[0]
        out[r["target"]] = r
    return out


def load_study() -> dict | None:
    p = RESULTS / "study_quickmatch.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def hero_twins(reports: dict) -> list[dict]:
    """Same CV, four names: what the biased and the fair tool did with each (from published results)."""
    a, b = reports.get("talentscreen"), reports.get("hirelens")
    if not a or not b:
        return []
    ta = [t for t in a["candidates"][0]["twins"] if t["slot"] == 0]
    tb = {(t["gender"], t["group"]): t for t in b["candidates"][0]["twins"] if t["slot"] == 0}
    out = []
    for t in ta:
        f = tb.get((t["gender"], t["group"]))
        if f and t["score"] is not None and f["score"] is not None:
            out.append({"name": t["name"],
                        "biased": {"score": t["score"], "selected": bool(t["selected"])},
                        "fair": {"score": f["score"], "selected": bool(f["selected"])}})
    return out


@app.context_processor
def globals_():
    return {"REPO": REPO, "TOOLS": TOOLS, "TOOL_URLS": TOOL_URLS}


@app.get("/")
def landing():
    reports = load_reports()
    return render_template("landing.html", reports=reports, study=load_study(),
                           twins=hero_twins(reports), page="home")


@app.get("/results")
def results():
    return render_template("results.html", reports=load_reports(), page="results")


@app.get("/results/<name>")
def result(name: str):
    r = load_reports().get(name) or abort(404)
    return render_template("result.html", r=r, tool=TOOLS.get(name, {}), page="results")


@app.get("/target/<name>")
def legacy_target(name: str):
    return redirect(url_for("result", name=name), code=301)


@app.get("/method")
def method():
    return render_template("method.html", study=load_study(), page="method")


@app.get("/legal")
def legal():
    return render_template("legal.html", page="legal")


@app.get("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.svg")


@app.get("/healthz")
def healthz():
    return {"ok": True, "reports": sorted(load_reports())}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5100)))
