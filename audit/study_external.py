"""External replication: does QuickMatch react to names on CVs that we did not write?

Uses the 500 AI-written CVs of the AI CV Detection Dataset (Jamal Ibrahim, 2026, Hugging Face,
https://huggingface.co/datasets/jamal-ibrahim/ai-cv-detection-dataset, Apache-2.0). The CVs are downloaded at run
time and are not stored or republished here; only aggregate results are written.

For every CV, name and email placeholders are removed and a twin's name and email are put on the first lines (the same
layout as the main audit's twins). Each CV gets the same 8-twin design as the main audit, with names from
cvkit/names.py: man/woman x name group A/C, and a second same-group name (placebo) in every cell. The CV is scored
against the QuickMatch role it fits best (chosen on the name-free CV), with that role's calibrated cutoff.

    python audit/study_external.py            # writes results/study_external_ai_cvs.json
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "audit"), str(ROOT / "targets" / "quickmatch")]
from cvkit import names as N  # noqa: E402
from study import summarise  # noqa: E402
import app as qm  # noqa: E402  (QuickMatch: embedder, job descriptions, calibrated cutoffs)

URL = "https://huggingface.co/datasets/jamal-ibrahim/ai-cv-detection-dataset/resolve/main/verified_cv_dataset.csv"
SOURCE = {"dataset": "AI CV Detection Dataset", "author": "Jamal Ibrahim", "year": 2026, "publisher": "Hugging Face",
          "url": "https://huggingface.co/datasets/jamal-ibrahim/ai-cv-detection-dataset", "licence": "Apache-2.0",
          "subset": "label == ai_generated"}
NAME_PH = re.compile(r"\[(?:Full Name|Your Name|Name|First Name Last Name|Candidate Name)\]", re.I)
MAIL_PH = re.compile(r"\[(?:Email Address|Email|Your Email)\]", re.I)
RNG = np.random.default_rng(2026)
CELLS = [("male", "A"), ("female", "A"), ("male", "C"), ("female", "C")]


def load() -> list[dict]:
    raw = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "fairness-auditor-study"}), timeout=180).read()
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8", errors="replace"))))
    return [r for r in rows if r["label"] == "ai_generated"]


def twin_names() -> dict:
    """Names for one CV: per slot (0 = main, 1 = placebo) a surname per group and a first name per cell."""
    out = {}
    for slot in (0, 1):
        sur = {g: N.LAST[g][RNG.integers(len(N.LAST[g]))] for g in ("A", "C")}
        for cell in CELLS:
            out[(cell, slot)] = None, sur[cell[1]]
    for cell in CELLS:
        a, b = RNG.choice(len(N.FIRST[cell]), size=2, replace=False)
        out[(cell, 0)] = (N.FIRST[cell][a], out[(cell, 0)][1])
        out[(cell, 1)] = (N.FIRST[cell][b], out[(cell, 1)][1])
    return out


def with_name(body: str, first: str, last: str) -> str:
    mail = f"{first}.{last}@example.com".lower().replace("'", "")
    return f"{first} {last}\n{mail}\n\n{body}"


def main() -> int:
    rows = load()
    roles = list(qm.ROLES)
    jd = np.stack([qm.jd_vec(r) for r in roles])
    bodies = [MAIL_PH.sub("", NAME_PH.sub("", r["Text"])).strip() for r in rows]
    base = qm.embed(bodies)
    best = [roles[int(np.argmax(jd @ v))] for v in base]   # the job each name-free CV fits best

    texts, index = [], []
    for i, body in enumerate(bodies):
        nm = twin_names()
        for (cell, slot), (first, last) in nm.items():
            texts.append(with_name(body, first, last)); index.append((i, cell, slot))
    vecs = qm.embed(texts)
    S = np.zeros((len(rows), 2, 2, 2))   # cv, gender (m, f), group (A, C), slot
    G, E = {"male": 0, "female": 1}, {"A": 0, "C": 1}
    for (i, (g, e), slot), v in zip(index, vecs):
        S[i, G[g], E[e], slot] = float(v @ qm.jd_vec(best[i]))
    cut = np.array([qm.CUTOFFS[r] for r in best])
    D = S >= cut[:, None, None, None]

    gender_eff = (S[:, 1] - S[:, 0]).mean(axis=(1, 2))
    group_eff = (S[:, :, 1] - S[:, :, 0]).mean(axis=(1, 2))
    placebo_eff = (S[..., 1] - S[..., 0]).mean(axis=(1, 2))
    demo = S[..., 0].reshape(len(rows), 4)
    demo_abs = np.abs(demo[:, :, None] - demo[:, None, :]).max(axis=(1, 2))
    plac_abs = np.abs(S[..., 1] - S[..., 0]).max(axis=(1, 2))
    dd = D[..., 0].reshape(len(rows), 4)
    demo_flip = dd.any(axis=1) & ~dd.all(axis=1)
    plac_flip = (D[..., 1] != D[..., 0]).any(axis=(1, 2))
    near = np.abs(S[..., 0].mean(axis=(1, 2)) - cut) <= 0.02

    res = {
        "source": SOURCE, "n_cvs": len(rows), "scored_cvs": int(len(texts)), "model": qm.MODEL_ID,
        "design": "8 twins per CV: man/woman x name group A/C (Bertrand & Mullainathan names) x 2 same-group names (placebo); "
                  "each CV scored for the QuickMatch role it fits best, against that role's calibrated cutoff",
        "roles_used": {r: best.count(r) for r in roles if best.count(r)},
        "gender_effect_female_minus_male": summarise(gender_eff),
        "group_effect_C_minus_A": summarise(group_eff),
        "placebo_effect_same_group": summarise(placebo_eff),
        "mean_max_gap_demographic_swap": float(demo_abs.mean()),
        "mean_max_gap_placebo_swap": float(plac_abs.mean()),
        "decision_flip_rate_demographic": float(demo_flip.mean()),
        "decision_flip_rate_placebo": float(plac_flip.mean()),
        "share_of_cvs_shortlisted_any_name": float(D.any(axis=(1, 2, 3)).mean()),
        "share_near_cutoff_0.02": float(near.mean()),
        "flip_rate_among_cvs_near_cutoff": float(demo_flip[near].mean()) if near.any() else None,
        "score_sd_across_cvs": float(S.mean(axis=(1, 2, 3)).std()),
    }
    out = ROOT / "results" / "study_external_ai_cvs.json"
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
