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
    ap.add_argument("--n", type=int, default=10)
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
        manifest.append({"candidate": cand, "source_index": int(i), "profile": profile, "twins": twins})
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"wrote {len(manifest)} candidates x 4 twins -> {out_dir}")


if __name__ == "__main__":
    main()
