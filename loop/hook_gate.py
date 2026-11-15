"""Claude Code PostToolUse hook: after the agent edits a hiring tool, run a quick fairness check
and feed the verdict straight back to the agent.

Wired in .claude/settings.json. Reads the hook payload (JSON) from stdin. If the edited file
belongs to targets/<tool>/, it runs the gate in fast dry-run mode (no browser, no Kane credits)
on three candidates. Exit code 2 sends the report to the agent (Claude Code shows stderr to the
model), so a fix that is still biased is caught immediately. The authoritative check remains the
real Kane run in /fairness-fix.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("talentscreen", "hirelens", "quickmatch")


def project_python() -> str:
    """The hook itself needs only the standard library, but the gate needs the project's packages.
    Prefer $KANE_FAIRNESS_PYTHON, then the repo's .venv, then whatever runs this hook."""
    import os
    if os.environ.get("KANE_FAIRNESS_PYTHON"):
        return os.environ["KANE_FAIRNESS_PYTHON"]
    for cand in (ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"):
        if cand.exists():
            return str(cand)
    return sys.executable


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    path = str((payload.get("tool_input") or {}).get("file_path") or "").replace("\\", "/")
    m = re.search(r"targets/(" + "|".join(TOOLS) + r")/", path)
    if not m:
        return 0  # not a hiring tool: nothing to check
    target = m.group(1)
    proc = subprocess.run(
        [project_python(), str(ROOT / "audit" / "gate.py"), "--target", target, "--direct",
         "--candidates", "cand01,cand02,cand03", "--out", str(ROOT / "reports" / "hook")],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    lines = [l for l in proc.stdout.splitlines() if l.startswith(("VERDICT", "  - ", "=="))]
    summary = "\n".join(lines[-8:]) or proc.stdout[-800:]
    if proc.returncode == 0:
        print(f"[fairness hook] {target}: quick dry run PASSED. Confirm with the real Kane gate: "
              f"python audit/gate.py --target {target}")
        return 0
    sys.stderr.write(
        f"[fairness hook] Your edit to {target} still fails the quick fairness check:\n{summary}\n"
        f"Full report: reports/hook/twin_audit_{target}.md. Fix the cause in targets/{target}/; "
        f"do not change audit/ or data/.\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
