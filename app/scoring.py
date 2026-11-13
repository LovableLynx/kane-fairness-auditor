"""Model loading and scoring for the HireScore demo app."""
import json
import os
from pathlib import Path

import joblib
import numpy as np

HERE = Path(__file__).resolve().parent

MODELS = {
    "fair": "baseline_fair_recruiter.pkl",
    "gender_biased": "baseline_biased_recruiter.pkl",
    "ethnicity_biased": "baseline_biased_recruiter_ethnicity.pkl",
}

GENDERS = {"Male": 0.0, "Female": 1.0}
ETHNICITIES = {"Group A": 0.0, "Group B": 1.0, "Group C": 2.0}

# Columns in the FairCVdb profile vector
COL_ETHNICITY = 0
COL_GENDER = 1

SHORTLIST_THRESHOLD = 0.5


def model_name() -> str:
    name = os.environ.get("HIRESCORE_MODEL", "fair")
    if name not in MODELS:
        raise ValueError(f"HIRESCORE_MODEL must be one of {sorted(MODELS)}, got {name!r}")
    return name


_model_cache: dict = {}


def load_model(name: str):
    if name not in _model_cache:
        _model_cache[name] = joblib.load(HERE / "models" / MODELS[name])
    return _model_cache[name]


def load_candidates() -> list[dict]:
    return json.loads((HERE / "data" / "candidates.json").read_text())


def label_for(value: float, mapping: dict) -> str:
    for k, v in mapping.items():
        if v == value:
            return k
    raise KeyError(value)


def score(features: list[float], gender: str, ethnicity: str, name: str | None = None) -> float:
    x = np.array(features, dtype=float)
    x[COL_GENDER] = GENDERS[gender]
    x[COL_ETHNICITY] = ETHNICITIES[ethnicity]
    model = load_model(name or model_name())
    return float(model.predict_proba(x.reshape(1, -1))[0, 1])
