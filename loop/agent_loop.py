"""Closed loop: Kane audits -> the coding agent reads the evidence and fixes -> Kane audits again.

    python loop/agent_loop.py --target talentscreen --gate-args "--candidates cand01 --no-placebo"
    python loop/agent_loop.py --target talentscreen --dry      # free rehearsal: gate in --direct mode

Each round:
  1. runs the fairness gate (Kane CLI drives the tool's real UI unless --dry);
  2. if blocked, hands Kane's audit report to Claude Code (`claude -p`, edits only, no shell)
     with instructions to fix the tool but never the audit;
  3. repeats until the gate passes or --max-rounds is reached.
A transcript is written to reports/loop_<target>.md.

Run it on a branch: it edits targets/<target>/ for real.
"""
from __future__ import annotations

import argparse
import json
import os
import datetime as dt
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROMPT = """TASK: edit the code in targets/{target}/ now, using the Edit tool, so the hiring tool stops discriminating.
You have no shell in this step and do not need one: this loop re-runs the Kane gate automatically after you reply.

You are fixing the hiring tool in targets/{target}/ so that it passes an independent fairness audit.
The audit was run by Kane CLI through the tool's real web interface using CV twins (identical CVs that
differ only in name and pronouns, plus same-group placebo names). It returned exit code {code} (blocked).

Kane's audit report:
---
{report}
---

Find the cause in targets/{target}/ (for example, the tool inferring sex or ethnicity from the name and
feeding it to the model, or using a model trained on biased labels; models/fair.pkl drops protected
attributes). Apply the fix now by editing the files yourself with the Edit tool: you have permission to edit,
so do not just describe it. Do NOT run any commands or the gate yourself: you have no shell in this step, and
this loop re-runs the Kane gate for you as soon as you finish. A project hook may also print a quick dry-run
verdict after each edit; use it as a hint. Use the smallest sensible change. Do not edit anything under
audit/, data/ or cvkit/names.py, and never weaken the audit. After editing, reply with one short paragraph:
the cause and the fix you applied."""


def run_gate(target: str, gate_args: list[str], dry: bool) -> tuple[int, str]:
    cmd = [sys.executable, str(ROOT / "audit" / "gate.py"), "--target", target, *gate_args]
    if dry:
        cmd.append("--direct")
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="talentscreen")
    ap.add_argument("--gate-args", default="--candidates cand01,cand02,cand03")
    ap.add_argument("--max-rounds", type=int, default=3)
    ap.add_argument("--dry", action="store_true", help="gate runs in --direct mode (no browser, no credits)")
    ap.add_argument("--agent", default="claude", help="Claude Code CLI executable")
    args = ap.parse_args()

    agent = shutil.which(args.agent)
    if not agent:
        print(f"Claude Code CLI '{args.agent}' not found on PATH", file=sys.stderr)
        return 2
    gate_args = shlex.split(args.gate_args)
    log = [f"# Closed loop · {args.target} · {dt.datetime.now().isoformat(timespec='seconds')}",
           f"Gate: {'dry run (--direct)' if args.dry else 'Kane CLI, real browser'} · args `{args.gate_args}`", ""]

    for rnd in range(1, args.max_rounds + 1):
        print(f"== round {rnd}: running the fairness gate ==", flush=True)
        code, out = run_gate(args.target, gate_args, args.dry)
        verdict = next((l for l in out.splitlines() if l.startswith("VERDICT")), f"exit {code}")
        print(verdict, flush=True)
        log += [f"## Round {rnd}", f"- Gate: **{verdict}** (exit {code})"]
        if code == 0:
            log.append("- Kane passed the tool. Loop closed.")
            print("== DEPLOY ALLOWED: loop closed ==")
            break
        if code != 1:
            log.append("- Gate inconclusive; stopping so a human can look.")
            print("== gate inconclusive; stopping ==")
            break
        report_path = ROOT / "reports" / f"twin_audit_{args.target}.md"
        report = report_path.read_text(encoding="utf-8") if report_path.exists() else out[-4000:]
        print("== handing Kane's report to the agent ==", flush=True)
        # Start the agent as a clean, independent session: drop variables that would make it think it is a
        # child of whatever launched this script (e.g. another Claude Code session), which changes its permissions.
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("CLAUDE", "MCP_")) and k != "CLAUDECODE"}
        env["KANE_FAIRNESS_PYTHON"] = sys.executable  # the hook's quick check uses our interpreter
        a = subprocess.run([agent, "-p", PROMPT.format(target=args.target, code=code, report=report),
                            "--permission-mode", "acceptEdits", "--allowedTools", "Read,Edit,Write,MultiEdit,Grep,Glob",
                            "--disallowedTools", "Bash,PowerShell,WebFetch,WebSearch,Task,Agent",
                            "--output-format", "json"],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            res = json.loads(a.stdout)
            reply = str(res.get("result", "")).strip()
            denied = [d.get("tool_name") for d in (res.get("permission_denials") or [])]
        except json.JSONDecodeError:
            reply, denied = (a.stdout or a.stderr).strip(), []
        changed = subprocess.run(["git", "diff", "--stat", "--", f"targets/{args.target}"], cwd=ROOT,
                                 capture_output=True, text=True).stdout.strip()
        print(reply, flush=True)
        print(f"-- files changed by the agent:\n{changed or '(none)'}", flush=True)
        if denied:
            print(f"-- tools denied to the agent: {', '.join(denied)}", flush=True)
        log += [f"- Agent: {reply[:1500]}", f"- Files changed: {changed or '(none)'}",
                *( [f"- Tools denied: {', '.join(denied)}"] if denied else [] ), ""]
    else:
        log.append(f"Still failing after {args.max_rounds} rounds.")
        print(f"== still failing after {args.max_rounds} rounds ==")

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / f"loop_{args.target}.md").write_text("\n".join(log) + "\n", encoding="utf-8")
    return 0 if code == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
