"""Run a real Kane audit on a target and publish it to the site as results/twin_audit_<target>.kane.json.

    python audit/publish_kane.py --target quickmatch --candidates cand01            # ~80 credits
    python audit/publish_kane.py --target talentscreen --candidates cand01 --label after-fix

Credit priority when they are scarce:
  1. quickmatch   : the model we did not build; Kane confirming NAME-UNSTABLE is a finding we did not plant
  2. talentscreen : the after-fix run that closes the loop with Kane's own PASS
Each run ~80 credits for 4 CVs (--no-placebo is implied for a single candidate to keep cost down;
pass --placebo to include same-group names, ~160 credits).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True, choices=["talentscreen", "hirelens", "quickmatch"])
    ap.add_argument("--candidates", default="cand01")
    ap.add_argument("--placebo", action="store_true")
    ap.add_argument("--label", default="", help="free text stored with the run, e.g. after-fix")
    ap.add_argument("--ci-run", default="", help="GitHub Actions URL to link, if the run came from CI")
    ap.add_argument("--parallel", type=int, default=1, help="Kane runs at once; keep 1 locally (Kane Chrome instances share CDP port 9222)")
    ap.add_argument("--timeout", type=int, default=0, help="seconds per Kane run (default: twin_audit's)")
    args = ap.parse_args()

    out = ROOT / "reports" / "kane"
    cmd = [sys.executable, str(ROOT / "audit" / "gate.py"), "--target", args.target,
           "--candidates", args.candidates, "--out", str(out)]
    if not args.placebo:
        cmd.append("--no-placebo")
    if args.parallel > 1:
        cmd += ["--parallel", str(args.parallel)]
    if args.timeout:
        cmd += ["--timeout", str(args.timeout)]
    print("==", " ".join(cmd[1:]), flush=True)
    code = subprocess.call(cmd, cwd=ROOT)

    src = out / f"twin_audit_{args.target}.json"
    if not src.exists():
        print("no report produced; nothing published", file=sys.stderr)
        return 2
    r = json.loads(src.read_text(encoding="utf-8"))
    if not r.get("driver", "").startswith("Kane"):
        print("report is not a Kane run; refusing to publish it as verified", file=sys.stderr)
        return 2
    if args.label:
        r["label"] = args.label
    if args.ci_run:
        r["ci_run"] = args.ci_run
    for c in r["candidates"]:
        c["evidence"] = None  # local path, meaningless on the site; the Test Manager link stays
    dest = ROOT / "results" / f"twin_audit_{args.target}.kane.json"
    dest.write_text(json.dumps(r, indent=2), encoding="utf-8")
    links = [c.get("test_url") for c in r["candidates"] if c.get("test_url")]
    print(f"\npublished {dest.relative_to(ROOT)}  verdict={r['verdict']}  credits={r.get('credits', 0):.0f}")
    for u in links:
        print("evidence:", u)
    print("next: git add results && git commit -m 'Kane-verified run: " + args.target + "' && git push")
    return code


if __name__ == "__main__":
    sys.exit(main())
