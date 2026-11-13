"""Statistical study behind the twin audit (dev-side, uses each target's direct adapter).

Addresses three threats to validity:
  1. CV length   -> every candidate has a short (~50 words) and a long (~340 words) CV.
  2. Cutoff      -> main metrics are cutoff-free (paired score differences); flip rates are
                    reported across a range of cutoffs taken from an independent calibration pool.
  3. Sample size -> 100 candidates, bootstrap 95% CIs, sign-flip permutation p-values.
Plus a placebo control: swapping to a different name from the SAME demographic cell.
If demographic swaps move scores no more than placebo swaps, it's name noise, not bias.

    python audit/study.py --target quickmatch
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))
from twin_audit import normalise, to_selected  # noqa: E402

RNG = np.random.default_rng(2026)


def score_text(target: dict, text: str) -> tuple[float, bool | None]:
    d = target["direct"]
    form = {**d.get("extra", {}), d["field"]: text}
    html = urllib.request.urlopen(target["url"].rstrip("/") + d["post"],
                                  data=urllib.parse.urlencode(form).encode(), timeout=60).read().decode()
    flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    sm, dm = re.search(d["score_re"], flat), re.search(d["decision_re"], flat)
    return normalise(float(sm.group(1))), to_selected(dm.group(1)) if dm else None


def boot_ci(x: np.ndarray, n: int = 4000) -> tuple[float, float]:
    idx = RNG.integers(0, len(x), size=(n, len(x)))
    m = x[idx].mean(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def signflip_p(x: np.ndarray, n: int = 10000) -> float:
    obs = abs(x.mean())
    signs = RNG.choice([-1, 1], size=(n, len(x)))
    return float(((np.abs((signs * x).mean(axis=1)) >= obs).sum() + 1) / (n + 1))


def summarise(x: np.ndarray) -> dict:
    lo, hi = boot_ci(x)
    return {"mean": float(x.mean()), "ci95": [lo, hi], "p": signflip_p(x), "n": int(len(x))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    target = json.loads((ROOT / "audit" / "targets.json").read_text())[args.target]
    study = json.loads((ROOT / "data" / "study.json").read_text())
    calib = json.loads((ROOT / "data" / "calibration.json").read_text())

    jobs = [c["text"] for s in study for c in s["cvs"]] + calib
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(lambda t: score_text(target, t), jobs))
    flat = iter(results[: len(jobs) - len(calib)])
    calib_scores = np.array([r[0] for r in results[len(jobs) - len(calib):]])

    # S[length][cand, gender, group, slot] and decisions D likewise
    G, E = {"male": 0, "female": 1}, {"A": 0, "C": 1}
    S = {L: np.zeros((len(study), 2, 2, 2)) for L in ("short", "long")}
    D = {L: np.zeros((len(study), 2, 2, 2), dtype=bool) for L in ("short", "long")}
    for i, s in enumerate(study):
        for c in s["cvs"]:
            sc, sel = next(flat)
            S[c["length"]][i, G[c["gender"]], E[c["group"]], c["slot"]] = sc
            D[c["length"]][i, G[c["gender"]], E[c["group"]], c["slot"]] = bool(sel)

    report = {"target": args.target, "n_candidates": len(study), "by_length": {}}
    for L, s in S.items():
        gender_eff = (s[:, 1] - s[:, 0]).mean(axis=(1, 2))           # female - male
        group_eff = (s[:, :, 1] - s[:, :, 0]).mean(axis=(1, 2))      # group C - group A
        placebo_eff = (s[..., 1] - s[..., 0]).mean(axis=(1, 2))      # name slot 1 - slot 0
        demo_abs = np.concatenate([np.abs(s[:, 1] - s[:, 0]).ravel(), np.abs(s[:, :, 1] - s[:, :, 0]).ravel()])
        plac_abs = np.abs(s[..., 1] - s[..., 0]).ravel()
        cut_rows = []
        for q in (30, 40, 50, 60, 70):
            cut = float(np.percentile(calib_scores, q))
            sel = s >= cut
            demo_flip = (sel[..., 0].reshape(len(study), -1).any(1) != sel[..., 0].reshape(len(study), -1).all(1))
            plac_flip = (sel[..., 0] != sel[..., 1]).any(axis=(1, 2))
            cut_rows.append({"percentile": q, "cutoff": cut, "demographic_flip_rate": float(demo_flip.mean()),
                             "placebo_flip_rate": float(plac_flip.mean())})
        actual = D[L][..., 0].reshape(len(study), -1)
        report["by_length"][L] = {
            "gender_effect_female_minus_male": summarise(gender_eff),
            "group_effect_C_minus_A": summarise(group_eff),
            "placebo_effect_same_demographic": summarise(placebo_eff),
            "mean_abs_gap_demographic_swap": float(demo_abs.mean()),
            "mean_abs_gap_placebo_swap": float(plac_abs.mean()),
            "score_spread_sd": float(s.std()),
            "flip_rate_at_target_cutoff": float((actual.any(1) != actual.all(1)).mean()),
            "cutoff_sensitivity": cut_rows,
        }

    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / f"study_{args.target}.json").write_text(json.dumps(report, indent=2))

    def fmt(e: dict) -> str:
        return f"{e['mean']:+.4f} [{e['ci95'][0]:+.4f}, {e['ci95'][1]:+.4f}] p={e['p']:.4f}"

    lines = [f"# Study · {args.target} · {len(study)} candidates × 16 CVs", ""]
    for L, r in report["by_length"].items():
        lines += [f"## {L} CVs", "",
                  f"- Gender effect (female − male): {fmt(r['gender_effect_female_minus_male'])}",
                  f"- Group effect (C − A): {fmt(r['group_effect_C_minus_A'])}",
                  f"- Placebo (same-demographic name swap): {fmt(r['placebo_effect_same_demographic'])}",
                  f"- Mean |gap|: demographic swap {r['mean_abs_gap_demographic_swap']:.4f} vs placebo swap "
                  f"{r['mean_abs_gap_placebo_swap']:.4f} (score SD {r['score_spread_sd']:.4f})",
                  f"- Flip rate at the tool's own cutoff: {r['flip_rate_at_target_cutoff']:.2f}", "",
                  "| Cutoff (calibration pct) | Demographic flip rate | Placebo flip rate |", "|---|---|---|"]
        lines += [f"| p{c['percentile']} ({c['cutoff']:.3f}) | {c['demographic_flip_rate']:.2f} | {c['placebo_flip_rate']:.2f} |"
                  for c in r["cutoff_sensitivity"]]
        lines.append("")
    (out / f"study_{args.target}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
