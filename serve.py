"""Single web service for hosting: the auditor site at / and the three demo hiring tools.

    /               Fairness Auditor (landing, results, method, legal)
    /talentscreen/  target A      /hirelens/  target B      /quickmatch/  target C

Local:  python serve.py              (http://127.0.0.1:8000)
Host:   gunicorn serve:app --workers 1 --threads 8 --bind 0.0.0.0:$PORT
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.utils import redirect

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # Flask resolves templates and static files relative to the module file
    spec.loader.exec_module(mod)
    return mod.app


auditor = load("auditor_app", "auditor/app.py")


def legacy_dashboard(environ, start_response):
    """Old /dashboard/... links now live at /results."""
    return redirect("/results", code=301)(environ, start_response)


TOOLS = {
    "talentscreen": load("talentscreen_app", "targets/talentscreen/app.py"),
    "hirelens": load("hirelens_app", "targets/hirelens/app.py"),
    "quickmatch": load("quickmatch_app", "targets/quickmatch/app.py"),
}
# Live checks from the website call the tools in-process instead of over the network.
sys.modules["live"].TARGET_APPS.update(TOOLS)

app = DispatcherMiddleware(auditor, {
    **{f"/{k}": v for k, v in TOOLS.items()},
    "/dashboard": legacy_dashboard,
})

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple("127.0.0.1", int(os.environ.get("PORT", 8000)), app, threaded=True)
