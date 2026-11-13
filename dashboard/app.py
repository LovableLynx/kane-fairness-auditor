"""Fairness Auditor dashboard -- reads reports/twin_audit_<target>.json and shows every target.

    python dashboard/app.py      # port 5100
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, abort, render_template

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
app = Flask(__name__)


def load_reports() -> list[dict]:
    out = []
    for p in sorted(REPORTS.glob("twin_audit_*.json")):
        try:
            out.append(json.loads(p.read_text()))
        except json.JSONDecodeError:
            continue
    return out


@app.get("/")
def index():
    return render_template("index.html", reports=load_reports())


@app.get("/target/<name>")
def target(name: str):
    rep = next((r for r in load_reports() if r["target"] == name), None) or abort(404)
    return render_template("target.html", r=rep)


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5100)))
