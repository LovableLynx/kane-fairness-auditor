"""One-time export of a small candidate pool from FairCVdb for the demo app.

Usage:
    python tools/export_candidates.py path/to/FairCVdb.npy [--n 40]

Writes app/data/candidates.json. Only the structured profile vector (51 features)
and first name are exported -- bios are skipped because they contain pronouns.
"""
import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# FairCVdb stores occupation as a code 0-9 without published labels.
OCCUPATIONS = [f"Occupation {i}" for i in range(10)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("--n", type=int, default=40)
    args = ap.parse_args()

    d = np.load(args.db, allow_pickle=True).item()
    X = d["Profiles Test"]
    names = d["Names Test"]

    rng = np.random.default_rng(7)
    idx = sorted(rng.choice(len(X), size=args.n, replace=False).tolist())

    out = []
    for k, i in enumerate(idx, start=1):
        row = X[i]
        out.append({
            "id": k,
            "source_index": int(i),
            "first_name": str(names[i]),
            "occupation": OCCUPATIONS[int(row[2])],
            "features": [round(float(v), 6) for v in row],
        })

    dest = ROOT / "app" / "data" / "candidates.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"wrote {len(out)} candidates -> {dest}")


if __name__ == "__main__":
    main()
