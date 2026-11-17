"""Why a score came out as it did, for the fair model's logistic regression (HireLens).

Each factor's contribution is coefficient x standardised value, i.e. how far this CV moves the
log-odds away from an average training profile. Occupation code and suitability are reported
together as one factor (fit with the role's job family).
"""
from __future__ import annotations

from cvkit import cv

FACTORS = [  # (label, feature indexes in cv.features order)
    ("Fit with the role's job family", [2, 3]), ("Education", [4]), ("Experience", [5]),
    ("Recommendation letter", [6]), ("Availability", [7]),
    ("English", [8]), ("Spanish", [9]), ("French", [10]),
]


def explain(model, features: list[float]) -> list[dict]:
    """[{label, effect}] sorted by absolute effect; empty if the model is not scaler + logistic regression."""
    try:
        pre, lr = model[:-1], model.steps[-1][1]
        x = pre.transform([features])[0]
        cols = model.steps[0][1].transformers_[0][2]  # columns kept by the ColumnTransformer
    except (AttributeError, IndexError, TypeError):
        return []
    contrib = {c: float(w * v) for c, w, v in zip(cols, lr.coef_[0], x)}
    out = [{"label": lab, "effect": sum(contrib.get(i, 0.0) for i in idx)} for lab, idx in FACTORS]
    return sorted(out, key=lambda f: -abs(f["effect"]))


__all__ = ["explain", "cv"]
