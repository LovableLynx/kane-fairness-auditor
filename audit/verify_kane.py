"""Independent checks on a published Kane audit (results/twin_audit_<target>.kane.json).

    python audit/verify_kane.py --target quickmatch [--cache reports/kane-cache]

For every reading it compares three sources that are produced separately:
  1. the published result (what the audit code parsed),
  2. Kane's own raw run_end event in its session folder (events.ndjson, final_state),
  3. the dry run through the tool's HTTP endpoint (results/twin_audit_<target>.json).
It also checks every candidate has a share link, that Kane's session belongs to the
expected Test Manager project, and adds up the credits. It never edits any file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUM = re.compile(r"[0-9]+(?:\.[0-9]+)?")


def key(t: dict) -> str:
    return t.get("key") or f"{t['gender']}_{t['group'].lower()}_{t['slot']}"


def run_end(session: Path) -> dict | None:
    ev = session / "events.ndjson"
    if not ev.is_file():
        return None
    for line in ev.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "run_end":
            return e
    return None


def kane_selects(session: Path) -> dict[str, list[str]]:
    """Dropdown choices Kane made on its own before typing each twin's CV (e.g. a 'Hiring for' role).
    Twins must be scored under identical settings, so any such choice is reported."""
    out, pending = {}, []
    ev = session / "events.ndjson"
    if not ev.is_file():
        return out
    for line in ev.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        r = e.get("remark") or ""
        if e.get("status") != "done":
            continue
        if r.startswith("navigate:"):
            pending = []
        elif r.startswith("select:"):
            pending.append(r[len("select:"):].strip())
        m = re.search(r"global\.cv_(\w+)\}\}", r)
        if m and pending:
            out[m.group(1)] = list(pending)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--cache", default=str(ROOT / "reports" / "kane-cache"))
    args = ap.parse_args()

    pub = json.loads((ROOT / "results" / f"twin_audit_{args.target}.kane.json").read_text(encoding="utf-8"))
    dry = json.loads((ROOT / "results" / f"twin_audit_{args.target}.json").read_text(encoding="utf-8"))
    dry_map = {(c["candidate"], key(t)): (t["score"], t["selected"]) for c in dry["candidates"] for t in c["twins"]}

    n = raw_ok = dry_ok = 0
    problems, projects, credits = [], set(), 0.0
    for c in pub["candidates"]:
        cand = c["candidate"]
        if c["status"] != "passed":
            problems.append(f"{cand}: Kane run not complete ({c.get('detail')})")
        if not c.get("test_url"):
            problems.append(f"{cand}: no share link")
        else:
            m = re.search(r"projects/(\w+)", c["test_url"])
            projects.add(m.group(1) if m else "?")
        credits += c.get("credits") or 0
        cache = Path(args.cache) / f"{args.target}_local_{pub.get('length', 'short')}_{'p' if pub.get('placebo') else 'np'}_{cand}.json"
        raw = None
        if cache.is_file():
            evidence = json.loads(cache.read_text(encoding="utf-8")).get("evidence")
            if evidence:
                raw = run_end(Path(evidence).parents[1])
                for k, sel in kane_selects(Path(evidence).parents[1]).items():
                    problems.append(f"{cand}/{k}: Kane changed a setting before submitting: {sel}")
        state = dict((raw or {}).get("final_state") or {})
        for k, v in (((raw or {}).get("context") or {}).get("variables") or {}).items():
            if k.startswith(("score_", "decision_")) and k not in state and isinstance(v, dict):
                state[k] = v.get("value")
        if raw is None:
            problems.append(f"{cand}: Kane session log not found, raw check skipped")
        for t in c["twins"]:
            k = key(t)
            n += 1
            if raw is not None:
                rs = NUM.search(str(state.get(f"score_{k}", "")))
                rv = float(rs.group()) if rs else None
                if rv is not None and rv > 1.0:
                    rv = rv / 100.0  # tools that show a percentage
                if rv is not None and t["score"] is not None and abs(rv - t["score"]) < 1e-6 \
                        and str(state.get(f"decision_{k}")) == str(t["decision"]):
                    raw_ok += 1
                else:
                    problems.append(f"{cand}/{k}: published {t['score']} {t['decision']!r} vs Kane raw "
                                    f"{state.get(f'score_{k}')!r} {state.get(f'decision_{k}')!r}")
            d = dry_map.get((cand, k))
            if d and t["score"] is not None and abs(d[0] - t["score"]) < 1e-6 and d[1] == t["selected"]:
                dry_ok += 1
            else:
                problems.append(f"{cand}/{k} ({t['name']}): Kane {t['score']} {t['selected']} vs dry run {d}")

    print(f"target          {args.target}")
    print(f"verdict         Kane: {pub['verdict']}   dry run: {dry['verdict']}")
    print(f"readings        {n}")
    print(f"published = Kane raw log   {raw_ok}/{n}")
    print(f"Kane = dry run             {dry_ok}/{n}")
    print(f"share links     {sum(1 for c in pub['candidates'] if c.get('test_url'))}/{len(pub['candidates'])}   projects {sorted(projects)}")
    print(f"credits         {credits:.0f}")
    for p in problems:
        print("  PROBLEM", p)
    return 0 if not problems and pub["verdict"] == dry["verdict"] else 1


if __name__ == "__main__":
    sys.exit(main())
