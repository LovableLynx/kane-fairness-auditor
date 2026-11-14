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


def lab_data(reports: dict) -> dict | None:
    """Everything the interactive Twin Lab needs: per candidate, every name variant with
    its CV text and what each tool decided (from the published audit results)."""
    keys = [k for k in TOOLS if k in reports]
    if len(keys) < 3:
        return None
    by_tool = {k: {c["candidate"]: c for c in reports[k]["candidates"]} for k in keys}
    cands = []
    for cand in by_tool[keys[0]]:
        if not all(cand in by_tool[k] for k in keys):
            continue
        variants = []
        for t in by_tool[keys[0]][cand]["twins"]:
            entry = {"gender": t["gender"], "group": t["group"], "slot": t["slot"], "name": t["name"], "tools": {}}
            for k in keys:
                m = next((x for x in by_tool[k][cand]["twins"]
                          if (x["gender"], x["group"], x["slot"]) == (t["gender"], t["group"], t["slot"])), None)
                if m is None or m["score"] is None:
                    break
                entry["tools"][k] = {"score": round(m["score"], 3), "selected": bool(m["selected"])}
            else:
                try:
                    entry["cv"] = (ROOT / t["file"]).read_text(encoding="utf-8")[:900]
                except (OSError, KeyError):
                    entry["cv"] = ""
                variants.append(entry)
        if len(variants) >= 4:
            swing = max(v["tools"]["quickmatch"]["score"] for v in variants) - min(v["tools"]["quickmatch"]["score"] for v in variants)
            cands.append({"id": cand, "variants": variants, "swing": swing})
    if not cands:
        return None
    start = max(range(len(cands)), key=lambda i: cands[i]["swing"])
    try:
        qm_cut = float(json.loads((ROOT / "data" / "quickmatch_cutoff.json").read_text())["cutoff"])
    except (OSError, ValueError, KeyError):
        qm_cut = 0.5
    # Bar scale and shortlist cutoff per tool (similarity scores live on a smaller range).
    scale = {"talentscreen": (1.0, 0.5), "hirelens": (1.0, 0.5), "quickmatch": (0.5, qm_cut)}
    return {"tools": [{"key": k, "name": TOOLS[k]["name"], "role": TOOLS[k]["role"],
                       "max": scale.get(k, (1.0, 0.5))[0], "cutoff": scale.get(k, (1.0, 0.5))[1]} for k in keys],
            "candidates": cands, "start": start}


def terminal_lines(reports: dict) -> list[dict] | None:
    """A gate run rendered as terminal lines, using values from the published TalentScreen audit."""
    r = reports.get("talentscreen")
    if not r or not r.get("candidates"):
        return None
    c = r["candidates"][0]
    lines = [{"k": "cmd", "t": "python audit/gate.py --target talentscreen"},
             {"k": "dim", "t": "== talentscreen up · Kane gets one line: \"Submit the CV for screening…\" =="},
             {"k": "dim", "t": f"kane-cli run … --agent --headless   # {c['candidate']}, {len(c['twins'])} CVs"}]
    for t in c["twins"]:
        if t["score"] is None:
            continue
        tag = "placebo" if t["slot"] else f"{t['gender'][0].upper()}·{t['group']}"
        lines.append({"k": "ok" if t["selected"] else "no",
                      "t": f"{t['name']:<20} {tag:<8} {t['score']:.3f}  {'SHORTLIST' if t['selected'] else 'REJECT'}"})
    lines += [{"k": "verdict", "t": f"VERDICT {r['verdict']}"}]
    lines += [{"k": "dim", "t": f"  - {x}"} for x in r.get("reasons", [])[:2]]
    blocked = r["verdict"] != "PASS"
    lines += [{"k": "no" if blocked else "ok",
               "t": "== DEPLOY BLOCKED: fairness audit failed ==" if blocked else "== DEPLOY ALLOWED =="},
              {"k": "cmd", "t": "echo $?"}, {"k": "out", "t": "1" if blocked else "0"}]
    return lines


@app.context_processor
def globals_():
    return {"REPO": REPO, "TOOLS": TOOLS, "TOOL_URLS": TOOL_URLS}


@app.get("/")
def landing():
    reports = load_reports()
    return render_template("landing.html", reports=reports, study=load_study(),
                           twins=hero_twins(reports), lab=lab_data(reports),
                           term=terminal_lines(reports), page="home")


@app.get("/results")
def results():
    return render_template("results.html", reports=load_reports(), page="results")


@app.get("/results/<name>")
def result(name: str):
    r = load_reports().get(name) or abort(404)
    bar_max = 0.5 if name == "quickmatch" else 1.0  # similarity scores sit on a smaller range
    return render_template("result.html", r=r, tool=TOOLS.get(name, {}), bar_max=bar_max, page="results")


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
