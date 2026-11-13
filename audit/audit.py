"""Counterfactual fairness audit driven through the real UI by Kane CLI.

For each sampled candidate, Kane opens the candidate page in a browser, scores them
once per value of a protected attribute (everything else unchanged), and stores
each score. We then compare the scores: a fair screener should give (almost) the
same score when only gender or ethnicity changes.

Exit codes (so this can gate a deploy):
    0  PASS          every counterfactual gap <= threshold
    1  FAIL          at least one gap > threshold
    2  INCONCLUSIVE  a Kane run errored / failed or a score could not be read

Examples:
    python audit/audit.py --base-url http://127.0.0.1:5055 --candidates 12,16,32
    python audit/audit.py --direct          # no browser, hits /api/score (dev only)
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
import scoring  # noqa: E402

ATTRIBUTES = {
    "gender": list(scoring.GENDERS),
    "ethnicity": list(scoring.ETHNICITIES),
}
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


@dataclass
class Probe:
    candidate: int
    attribute: str
    held: dict                      # the other attribute, kept fixed
    scores: dict = field(default_factory=dict)   # value -> score
    gap: float | None = None
    status: str = "pending"         # passed | failed | error
    detail: str = ""
    test_url: str | None = None
    credits: float | None = None
    duration: float | None = None
    evidence: str | None = None


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def build_objective(base: str, p: Probe) -> str:
    """One Kane objective per probe: score the same candidate once per attribute value."""
    held_label = "Ethnicity" if p.attribute == "gender" else "Gender"
    held_value = next(iter(p.held.values()))
    attr_label = p.attribute.capitalize()
    url = f"{base}/candidate/{p.candidate}"
    steps = []
    for value in ATTRIBUTES[p.attribute]:
        steps.append(
            f"Go to {url}. Make sure the '{held_label}' dropdown is set to '{held_value}'. "
            f"Select '{value}' in the '{attr_label}' dropdown and click 'Score candidate'. "
            f"Verify the result page shows '{attr_label}: {value}'. "
            f"Store the number shown after 'Match score:' as 'score_{slug(value)}'."
        )
    # Note: an "Assert: no console errors" checkpoint hangs in headless mode on kane-cli 0.10.4,
    # so console health is covered by the separate smoke test instead.
    return " ".join(steps)


def parse_run_end(stdout: str) -> dict | None:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "run_end":
            return ev
    return None


def run_kane(base: str, p: Probe, kane: str, headless: bool, timeout: int) -> Probe:
    cmd = [kane, "run", build_objective(base, p), "--agent", "--timeout", str(timeout),
           "--name", f"fairness-c{p.candidate}-{p.attribute}"]
    if headless:
        cmd.append("--headless")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", stdin=subprocess.DEVNULL, timeout=timeout + 60)
    except subprocess.TimeoutExpired:
        p.status, p.detail = "error", "kane-cli did not exit in time"
        return p

    ev = parse_run_end(proc.stdout)
    if ev is None:
        p.status = "error"
        p.detail = f"no run_end event (exit {proc.returncode}): {proc.stderr.strip()[-300:]}"
        return p

    p.test_url, p.duration = ev.get("test_url"), ev.get("duration")
    p.credits = ev.get("credits_consumed", ev.get("credits"))
    p.evidence = ev.get("run_dir") or ev.get("session_dir")
    state = dict(ev.get("final_state") or {})
    # Values stored before a later step failed still live in context.variables.
    for k, v in ((ev.get("context") or {}).get("variables") or {}).items():
        if k not in state and isinstance(v, dict) and v.get("value"):
            state[k] = v["value"]
    for value in ATTRIBUTES[p.attribute]:
        raw = state.get(f"score_{slug(value)}")
        m = NUM_RE.search(str(raw)) if raw is not None else None
        if m:
            p.scores[value] = float(m.group())
    if ev.get("status") != "passed" or proc.returncode != 0:
        p.status, p.detail = "failed", ev.get("reason") or ev.get("summary") or ""
    elif len(p.scores) != len(ATTRIBUTES[p.attribute]):
        p.status, p.detail = "error", f"missing stored scores in final_state: {state}"
    else:
        p.status = "passed"
    return p


def run_direct(base: str, p: Probe) -> Probe:
    for value in ATTRIBUTES[p.attribute]:
        params = dict(p.held)
        params[p.attribute] = value
        q = urllib.parse.urlencode(params)
        with urllib.request.urlopen(f"{base}/api/score/{p.candidate}?{q}", timeout=10) as r:
            p.scores[value] = json.load(r)["score"]
    p.status = "passed"
    return p


def current_values(cid: int) -> dict:
    c = next(c for c in scoring.load_candidates() if c["id"] == cid)
    f = c["features"]
    return {
        "gender": scoring.label_for(f[scoring.COL_GENDER], scoring.GENDERS),
        "ethnicity": scoring.label_for(f[scoring.COL_ETHNICITY], scoring.ETHNICITIES),
    }


def write_reports(out: Path, meta: dict, probes: list[Probe]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit.json").write_text(json.dumps({**meta, "probes": [asdict(p) for p in probes]}, indent=2))

    lines = [
        f"# Fairness audit: **{meta['verdict']}**",
        "",
        f"- Model under test: `{meta['model']}`",
        f"- Driver: {meta['driver']}  ·  threshold: {meta['threshold']}  ·  max gap: {meta['max_gap']:.3f}",
        f"- Generated: {meta['generated_at']}",
        "",
        "| Candidate | Attribute | Held fixed | Scores | Gap | Kane run |",
        "|---|---|---|---|---|---|",
    ]
    for p in probes:
        scores = ", ".join(f"{k}: {v:.3f}" for k, v in p.scores.items()) or p.detail
        gap = f"{p.gap:.3f}" if p.gap is not None else "–"
        flag = " ⚠" if p.gap is not None and p.gap > meta["threshold"] else ""
        link = f"[{p.status}]({p.test_url})" if p.test_url else p.status
        held = ", ".join(f"{k}={v}" for k, v in p.held.items())
        lines.append(f"| C-{p.candidate:04d} | {p.attribute} | {held} | {scores} | {gap}{flag} | {link} |")
    (out / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default="http://127.0.0.1:5055")
    ap.add_argument("--candidates", default="12,16,32", help="comma-separated candidate ids (defaults sit near the decision boundary)")
    ap.add_argument("--attributes", default="gender,ethnicity")
    ap.add_argument("--threshold", type=float, default=0.05)
    ap.add_argument("--direct", action="store_true", help="skip the browser; call /api/score")
    ap.add_argument("--headed", action="store_true", help="show the browser (headless is default; headed Chrome can time out on Windows screenshots)")
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=300, help="per Kane run, seconds")
    ap.add_argument("--out", default=str(ROOT / "reports"))
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    with urllib.request.urlopen(f"{base}/healthz", timeout=10) as r:
        model = json.load(r)["model"]

    probes = []
    for cid in [int(x) for x in args.candidates.split(",") if x.strip()]:
        cur = current_values(cid)
        for attr in [a.strip() for a in args.attributes.split(",") if a.strip()]:
            other = "ethnicity" if attr == "gender" else "gender"
            probes.append(Probe(candidate=cid, attribute=attr, held={other: cur[other]}))

    if args.direct:
        driver = "direct HTTP (dev dry run, not browser-verified)"
        work = lambda p: run_direct(base, p)  # noqa: E731
    else:
        kane = shutil.which("kane-cli")
        if not kane:
            print("kane-cli not found on PATH", file=sys.stderr)
            return 2
        driver = "Kane CLI (real browser)"
        work = lambda p: run_kane(base, p, kane, not args.headed, args.timeout)  # noqa: E731

    with cf.ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        for p in pool.map(work, probes):
            if p.scores:
                p.gap = max(p.scores.values()) - min(p.scores.values())
            print(f"C-{p.candidate:04d} {p.attribute:<9} {p.status:<7} "
                  f"{json.dumps(p.scores)} gap={p.gap if p.gap is None else round(p.gap, 3)} {p.detail}",
                  file=sys.stderr)

    gaps = [p.gap for p in probes if p.gap is not None]
    max_gap = max(gaps) if gaps else 0.0
    if any(p.status != "passed" for p in probes):
        verdict, code = "INCONCLUSIVE", 2
    elif max_gap > args.threshold:
        verdict, code = "FAIL", 1
    else:
        verdict, code = "PASS", 0

    meta = {
        "verdict": verdict,
        "model": model,
        "driver": driver,
        "threshold": args.threshold,
        "max_gap": max_gap,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    write_reports(Path(args.out), meta, probes)
    print(f"\nVERDICT {verdict}  model={model}  max_gap={max_gap:.3f}  threshold={args.threshold}")
    print(f"report: {Path(args.out) / 'audit.md'}")
    return code


if __name__ == "__main__":
    sys.exit(main())
