"""Sample CVs for the demo tools' "Try a sample" buttons: twins of the same candidate."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def samples() -> list[dict]:
    """Two twins (identical qualifications, different name) plus one long CV, from the published set."""
    try:
        cand = {c["candidate"]: c for c in json.loads((ROOT / "data" / "cvs" / "manifest.json").read_text())}["cand01"]
    except (OSError, KeyError, json.JSONDecodeError):
        return []
    out = []
    for gender, group, length, label in (("male", "A", "short", "Sample A"), ("female", "C", "short", "Sample B (twin of A)"),
                                         ("male", "A", "long", "Long CV")):
        v = next((v for v in cand["variants"] if v["gender"] == gender and v["group"] == group
                  and v["slot"] == 0 and v["length"] == length), None)
        if v:
            try:
                out.append({"label": label, "name": v["name"], "text": (ROOT / v["file"]).read_text(encoding="utf-8")})
            except OSError:
                pass
    return out
