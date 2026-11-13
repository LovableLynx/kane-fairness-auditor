"""Deployment gate: boot HireScore with a candidate model, run the Kane fairness audit, tear down.

    python audit/gate.py --model gender_biased            # expect FAIL (exit 1)
    python audit/gate.py --model fair --headless          # expect PASS (exit 0)
    python audit/gate.py --model fair --direct            # dev dry run, no browser

Any extra flags are forwarded to audit.py.
"""
import argparse
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def wait_healthy(url: str, seconds: int = 30) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{url}/healthz", timeout=2):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError(f"app did not become healthy at {url}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["fair", "gender_biased", "ethnicity_biased"])
    ap.add_argument("--port", type=int, default=5055)
    args, rest = ap.parse_known_args()

    url = f"http://127.0.0.1:{args.port}"
    env = {**os.environ, "HIRESCORE_MODEL": args.model, "PORT": str(args.port)}
    server = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT / "app", env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        wait_healthy(url)
        print(f"== HireScore up at {url} with model '{args.model}' ==", flush=True)
        code = subprocess.call([sys.executable, str(ROOT / "audit" / "audit.py"), "--base-url", url, *rest])
    finally:
        server.terminate()
        server.wait(timeout=10)
    status = {0: "DEPLOY ALLOWED", 1: "DEPLOY BLOCKED (bias detected)", 2: "DEPLOY BLOCKED (audit inconclusive)"}
    print(f"== {status.get(code, f'exit {code}')} ==")
    return code


if __name__ == "__main__":
    sys.exit(main())
