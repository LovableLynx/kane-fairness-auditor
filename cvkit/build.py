"""Train the demo screening models on CV-derivable FairCVdb fields and generate CV twins.

    python -m cvkit.build path/to/FairCVdb.npy [--n 10]

Outputs
    models/biased.pkl   all 11 columns, labels carry both gender and ethnicity penalties
    models/fair.pkl     protected columns dropped, trained on blind labels
    data/cvs/<cand>/<gender>_<group>.txt  + data/cvs/manifest.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import cv

ROOT = Path(__file__).resolve().parents[1]
COLS = 11


def train(X: np.ndarray, y: np.ndarray, drop_protected: bool):
    keep = list(range(2, COLS)) if drop_protected else list(range(COLS))
    sel = ColumnTransformer([("keep", "passthrough", keep)])
    return make_pipeline(sel, StandardScaler(), LogisticRegression(max_iter=2000)).fit(X, y)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--n", type=int, default=10, help="candidates in the Kane audit set")
    ap.add_argument("--study", type=int, default=100, help="candidates in the statistical study set")
    ap.add_argument("--calib", type=int, default=200, help="CVs in the independent calibration pool")
    args = ap.parse_args()

    d = np.load(args.db, allow_pickle=True).item()
    Xtr, Xte = d["Profiles Train"][:, :COLS], d["Profiles Test"][:, :COLS]
    blind = d["Blind Labels Train"]
    combined = np.clip(d["Biased Labels Train (Gender)"] + d["Biased Labels Train (Ethnicity)"] - blind, 0, 1)

    biased = train(Xtr, (combined > 0.5).astype(int), drop_protected=False)
    fair = train(Xtr, (blind > 0.5).astype(int), drop_protected=True)
    (ROOT / "models").mkdir(exist_ok=True)
    joblib.dump(biased, ROOT / "models" / "biased.pkl")
    joblib.dump(fair, ROOT / "models" / "fair.pkl")
    yte = (d["Blind Labels Test"] > 0.5).astype(int)
    print(f"accuracy vs blind test labels: biased={biased.score(Xte, yte):.3f} fair={fair.score(Xte, yte):.3f}")

    # Pick borderline candidates: the fair model is unsure, so bias can flip the outcome.
    p_fair = fair.predict_proba(Xte)[:, 1]
    rng = np.random.default_rng(11)
    pool = np.where((p_fair > 0.35) & (p_fair < 0.75))[0]
    chosen = sorted(rng.choice(pool, size=args.n, replace=False).tolist())

    out_dir = ROOT / "data" / "cvs"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for k, i in enumerate(chosen, start=1):
        cand = f"cand{k:02d}"
        profile = [float(v) for v in Xte[i]]
        (out_dir / cand).mkdir(exist_ok=True)
        twins = []
        for who in cv.identities_for(k):
            text = cv.render(profile, who, cv_id=f"{cand.upper()}")
            path = out_dir / cand / f"{who.gender}_{who.group}.txt"
            path.write_text(text, encoding="utf-8")
            # Round-trip check: the parser must recover exactly the job-relevant fields.
            parsed = cv.parse(text)
            feats = cv.features(parsed, who.gender, who.group)
            assert np.allclose(feats[2:], cv.features(cv.parse(text), "male", "A")[2:])
            twins.append({"gender": who.gender, "group": who.group, "name": f"{who.first} {who.last}",
                          "file": str(path.relative_to(ROOT)).replace("\\", "/")})
        # All variants: 2 names per demographic cell (slot 1 = placebo) x short/long.
        variants = []
        for slot in (0, 1):
            for who in cv.identities_for(k, slot):
                for long in (False, True):
                    suffix = ("_p" if slot else "") + ("_long" if long else "")
                    path = out_dir / cand / f"{who.gender}_{who.group}{suffix}.txt"
                    path.write_text(cv.render(profile, who, cv_id=f"{cand.upper()}", long=long), encoding="utf-8")
                    variants.append({"gender": who.gender, "group": who.group, "slot": slot,
                                     "length": "long" if long else "short", "name": f"{who.first} {who.last}",
                                     "file": str(path.relative_to(ROOT)).replace("\\", "/")})
        manifest.append({"candidate": cand, "source_index": int(i), "profile": profile,
                         "twins": twins, "variants": variants})
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"wrote {len(manifest)} candidates x 16 variants -> {out_dir}")

    # ---- Study set: larger sample, short + long CVs, two names per demographic cell (placebo).
    used = set(chosen)
    rest = np.setdiff1d(pool, list(used))
    study_idx = sorted(np.random.default_rng(23).choice(rest, size=min(args.study, len(rest)), replace=False).tolist())
    study = []
    for k, i in enumerate(study_idx, start=1):
        profile = [float(v) for v in Xte[i]]
        cvs = []
        for slot in (0, 1):
            for who in cv.identities_for(k, slot):
                for long in (False, True):
                    text = cv.render(profile, who, cv_id=f"S{k:03d}", long=long)
                    cvs.append({"gender": who.gender, "group": who.group, "slot": slot,
                                "length": "long" if long else "short", "name": f"{who.first} {who.last}",
                                "words": len(text.split()), "text": text})
        study.append({"candidate": f"s{k:03d}", "source_index": int(i), "cvs": cvs})
    (ROOT / "data" / "study.json").write_text(json.dumps(study))
    print(f"wrote study set: {len(study)} candidates x {len(study[0]['cvs'])} CVs -> data/study.json")

    # ---- Calibration pool: profiles never used in any audit, random identities, mixed length.
    rng_c = np.random.default_rng(31)
    taken = used | set(study_idx)
    calib_idx = rng_c.choice(np.setdiff1d(np.arange(len(Xte)), list(taken)), size=args.calib, replace=False)
    calib = []
    for j, i in enumerate(calib_idx):
        who = cv.identities_for(int(rng_c.integers(0, 9)), int(rng_c.integers(0, 2)))[int(rng_c.integers(0, 4))]
        calib.append(cv.render([float(v) for v in Xte[i]], who, cv_id=f"K{j:03d}", long=bool(j % 2)))
    (ROOT / "data" / "calibration.json").write_text(json.dumps(calib))
    print(f"wrote calibration pool: {len(calib)} CVs (never audited) -> data/calibration.json")


if __name__ == "__main__":
    main()
