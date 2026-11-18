"""Deployment gate: boot a hiring tool, run the Kane twin audit against its UI, tear it down.
The exit code is the deploy decision.

    python audit/gate.py --target talentscreen                       # Kane, real browser
    python audit/gate.py --target talentscreen --model fair          # override the tool's model
    python audit/gate.py --target quickmatch --direct --candidates all   # dev dry run, no credits
    python audit/gate.py --url https://your-tool.example/ --task "Paste the CV and submit it"   # your own tool

Any flags not listed here are forwarded to audit/twin_audit.py.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = {"talentscreen": "targets/talentscreen/app.py",
        "hirelens": "targets/hirelens/app.py",
        "quickmatch": "targets/quickmatch/app.py"}
STATUS = {0: "DEPLOY ALLOWED", 1: "DEPLOY BLOCKED: fairness audit failed", 2: "DEPLOY BLOCKED: audit inconclusive"}


def wait_healthy(url: str, seconds: int) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url.rstrip("/") + "/healthz", timeout=3):
                return
        except OSError:
            time.sleep(1)
    raise RuntimeError(f"{url} did not become healthy within {seconds}s")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=sorted(APPS))
    ap.add_argument("--model", help="set TARGET_MODEL for the tool (default: the tool's own setting)")
    ap.add_argument("--boot-timeout", type=int, default=600)
    args, rest = ap.parse_known_args()
    if not args.target:  # your own tool, already running somewhere: nothing to boot
        if "--url" not in " ".join(rest):
            ap.error("give --target (a demo tool) or --url and --task (your own hiring tool)")
        code = subprocess.call([sys.executable, str(ROOT / "audit" / "twin_audit.py"), *rest])
        print(f"== {STATUS.get(code, f'exit {code}')} ==")
        return code

    url = json.loads((ROOT / "audit" / "targets.json").read_text(encoding="utf-8"))[args.target]["url"]
    env = {**os.environ, "PORT": str(urllib.parse.urlparse(url).port)}
    if args.model:
        env["TARGET_MODEL"] = args.model
    server = subprocess.Popen([sys.executable, str(ROOT / APPS[args.target])], cwd=ROOT, env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_healthy(url, args.boot_timeout)
        print(f"== {args.target} up at {url} ==", flush=True)
        code = subprocess.call([sys.executable, str(ROOT / "audit" / "twin_audit.py"), "--target", args.target, *rest])
    finally:
        server.terminate()
        server.wait(timeout=15)
    print(f"== {STATUS.get(code, f'exit {code}')} ==")
    return code


if __name__ == "__main__":
    sys.exit(main())
