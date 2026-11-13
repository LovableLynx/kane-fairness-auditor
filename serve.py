"""Single web service for hosting: all three hiring tools + the dashboard under one domain.

    /talentscreen/   target A      /hirelens/   target B
    /quickmatch/     target C      /dashboard/  audit results

Local:  python serve.py              (http://127.0.0.1:8000)
Host:   gunicorn serve:app --workers 1 --threads 8 --bind 0.0.0.0:$PORT
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # Flask resolves templates relative to the module file
    spec.loader.exec_module(mod)
    return mod.app


APPS = {
    "talentscreen": ("TalentScreen", "Drop a CV, get SHORTLIST or REJECT. Target A: contains planted bias."),
    "hirelens": ("HireLens", "Applicant tracker with role-fit percentages. Target B: fair model."),
    "quickmatch": ("QuickMatch", "Three-step wizard using the open-source all-MiniLM-L6-v2 model. Target C: black box."),
    "dashboard": ("Audit dashboard", "Verdicts, CV twins, placebo gaps and impact ratios for every tool."),
}

landing = Flask(__name__)


@landing.get("/")
def home():
    cards = "".join(
        f'<a href="/{k}/"><b>{t}</b><span>{d}</span></a>' for k, (t, d) in APPS.items())
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Kane Fairness Auditor</title>
<style>
:root{{--bg:#f6f5f1;--ink:#16181d;--muted:#666a73;--line:#e2e0d8;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111317;--ink:#eceef2;--muted:#9aa0ab;--line:#262a32;--card:#181b21}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
main{{max-width:880px;margin:0 auto;padding:40px 16px}} h1{{margin:0 0 6px}} p{{color:var(--muted)}}
.g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:22px}}
a{{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;color:inherit;text-decoration:none}}
a:hover{{border-color:var(--muted)}} a b{{display:block;font-size:18px;margin-bottom:4px}} a span{{color:var(--muted);font-size:14px}}
</style></head><body><main>
<h1>Kane Fairness Auditor</h1>
<p>Bias audits for AI hiring tools, run through each tool's own interface by Kane CLI using CV twins and a placebo control.
Sample CVs: <a style="display:inline;padding:0;border:0;background:none;text-decoration:underline" href="https://github.com/LovableLynx/kane-fairness-auditor/tree/main/data/cvs">data/cvs</a>.</p>
<div class="g">{cards}</div></main></body></html>"""


@landing.get("/healthz")
def healthz():
    return {"ok": True}


app = DispatcherMiddleware(landing, {
    "/talentscreen": load("talentscreen_app", "targets/talentscreen/app.py"),
    "/hirelens": load("hirelens_app", "targets/hirelens/app.py"),
    "/quickmatch": load("quickmatch_app", "targets/quickmatch/app.py"),
    "/dashboard": load("dashboard_app", "dashboard/app.py"),
})

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple("127.0.0.1", int(os.environ.get("PORT", 8000)), app, threaded=True)
