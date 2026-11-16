"""Closed loop: Kane audits -> the coding agent reads the evidence and proposes a fix -> the loop applies it -> Kane audits again.

    python loop/agent_loop.py --target talentscreen --gate-args "--candidates cand01 --no-placebo"
    python loop/agent_loop.py --target talentscreen --dry      # free rehearsal: gate in --direct mode

Each round:
  1. runs the fairness gate (Kane CLI drives the tool's real UI unless --dry);
  2. if blocked, hands Kane's audit report plus the tool's source to Claude Code (`claude -p`, read-only)
     and asks for a unified diff that fixes the tool;
  3. applies the diff with `git apply` (only paths under targets/<target>/ are accepted);
  4. repeats until the gate passes or --max-rounds is reached.

The agent never needs write permission: it returns a patch, the loop applies it, and every patch is
recorded verbatim in reports/loop_<target>.md. Run it on a branch: it edits targets/<target>/ for real.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROMPT = """You are the coding agent in an audit loop. An independent fairness audit, run by Kane CLI through the
hiring tool's real web interface, has BLOCKED the tool in targets/{target}/ (exit code {code}). The audit used
CV twins: identical CVs that differ only in name and pronouns, plus same-group placebo names.

Kane's audit report:
---
{report}
---

Source of the tool, targets/{target}/app.py:
---
{source}
---

Context: models/fair.pkl was trained on blind labels with the protected columns dropped; models/biased.pkl was
trained on labels carrying gender and ethnicity penalties. cv.features(parsed, gender, group) puts gender and
group into columns 0-1. The sibling tool targets/hirelens/app.py scores fairly by never inferring demographics
and passing constant placeholders ("male", "B") to the fair model.

Your job: reply with ONE unified diff (git format, paths relative to the repo root, e.g.
`--- a/targets/{target}/app.py` / `+++ b/targets/{target}/app.py`) that fixes the discrimination with the
smallest sensible change. Only files under targets/{target}/ may be touched. Never change anything under
audit/, data/ or cvkit/. Put the diff inside a single ```diff fenced block, preceded by one short paragraph
naming the cause. Do not run tools; everything you need is above."""


def run_gate(target: str, gate_args: list[str], dry: bool) -> tuple[int, str]:
    cmd = [sys.executable, str(ROOT / "audit" / "gate.py"), "--target", target, *gate_args]
    if dry:
        cmd.append("--direct")
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def extract_diff(reply: str) -> str | None:
    m = re.search(r"```diff\s*\n(.*?)```", reply, re.S)
    if not m:
        m = re.search(r"(^--- a/.*)", reply, re.S | re.M)
        if not m:
            return None
    diff = m.group(1).rstrip() + "\n"
    return diff if diff.lstrip().startswith(("---", "diff --git")) else None


def diff_paths(diff: str) -> list[str]:
    return re.findall(r"^\+\+\+ b/(\S+)", diff, re.M)


def apply_patch(target: str, diff: str) -> tuple[bool, str]:
    paths = diff_paths(diff)
    bad = [p for p in paths if not p.replace("\\", "/").startswith(f"targets/{target}/")]
    if not paths:
        return False, "patch names no files"
    if bad:
        return False, f"patch touches files outside targets/{target}/: {bad}"
    patch_file = ROOT / "reports" / f"loop_{target}.patch"
    patch_file.parent.mkdir(exist_ok=True)
    patch_file.write_text(diff, encoding="utf-8", newline="\n")
    for extra in ([], ["--ignore-whitespace"], ["--3way"]):
        p = subprocess.run(["git", "apply", *extra, str(patch_file)], cwd=ROOT, capture_output=True, text=True)
        if p.returncode == 0:
            return True, ", ".join(paths)
    return False, (p.stderr or p.stdout).strip()[-600:]


def ask_agent(agent: str, prompt: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "MCP_")) and k != "CLAUDECODE"}
    a = subprocess.run([agent, "-p", prompt, "--output-format", "json",
                        "--disallowedTools", "Bash,PowerShell,Edit,Write,MultiEdit,NotebookEdit,WebFetch,WebSearch,Task,Agent"],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        return str(json.loads(a.stdout).get("result", "")).strip()
    except json.JSONDecodeError:
        return (a.stdout or a.stderr).strip()


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
    (ROOT / "reports" / f"loop_{args.target}.md").unlink(missing_ok=True)
    log = [f"# Closed loop · {args.target} · {dt.datetime.now().isoformat(timespec='seconds')}",
           f"Gate: {'dry run (--direct)' if args.dry else 'Kane CLI, real browser'} · args `{args.gate_args}`", ""]
    code = 1
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
        source = (ROOT / "targets" / args.target / "app.py").read_text(encoding="utf-8")
        print("== handing Kane's report to the agent ==", flush=True)
        reply = ask_agent(agent, PROMPT.format(target=args.target, code=code, report=report, source=source))
        summary = reply.split("```")[0].strip()
        print(summary[:600], flush=True)
        diff = extract_diff(reply)
        if not diff:
            print("-- agent returned no patch", flush=True)
            log += [f"- Agent: {summary[:1200]}", "- No patch returned.", ""]
            continue
        ok, info = apply_patch(args.target, diff)
        print(f"-- patch {'applied to ' + info if ok else 'rejected: ' + info}", flush=True)
        log += [f"- Agent: {summary[:1200]}", f"- Patch {'applied' if ok else 'REJECTED'}: {info}", "", "```diff", diff.rstrip(), "```", ""]
    else:
        log.append(f"Still failing after {args.max_rounds} rounds.")
        print(f"== still failing after {args.max_rounds} rounds ==")

    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / f"loop_{args.target}.md").write_text("\n".join(log) + "\n", encoding="utf-8")
    return 0 if code == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
