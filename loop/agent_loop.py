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

Context: {context}
A fix that makes every CV score the same is not a fix: the loop rejects any change after which scores no longer
depend on the CV's qualifications.

Your job: fix the discrimination with the smallest sensible change to targets/{target}/app.py. Never change
anything under audit/, data/ or cvkit/. Reply with one short paragraph naming the cause, then the COMPLETE new
contents of targets/{target}/app.py in a single ```python fenced block (the loop computes and records the diff).
You have no tools in this session and need none: do not try to run, read or edit anything."""


CONTEXT = {
    "talentscreen": "models/fair.pkl was trained on blind labels with the protected columns dropped; models/biased.pkl "
                    "was trained on labels carrying gender and ethnicity penalties. cv.features(parsed, gender, group) "
                    "puts gender and group into columns 0-1. The sibling tool targets/hirelens/app.py scores fairly by "
                    "never inferring demographics and passing constant placeholders (\"male\", \"B\") to the fair model.",
    "quickmatch": "QuickMatch is an off-the-shelf open-source sentence-embedding model (all-MiniLM-L6-v2) that nobody "
                  "trained for this; you cannot retrain it. It scores the cosine similarity between the whole CV text and "
                  "the role's job description, and shortlists above a cutoff calibrated on an independent pool "
                  "(data/calibration.json) by calibrate(). Keep the calibration consistent with whatever the scorer sees.",
}


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


def extract_file(reply: str) -> str | None:
    """The complete new app.py, when the agent returns the file instead of a diff."""
    blocks = re.findall(r"```python\s*\n(.*?)```", reply, re.S)
    return max(blocks, key=len) if blocks else None


def write_file(target: str, source: str) -> tuple[bool, str, str]:
    """Write the agent's file (only targets/<target>/app.py), refuse anything that does not compile,
    and return the exact diff as git sees it."""
    path = ROOT / "targets" / target / "app.py"
    try:
        compile(source, str(path), "exec")
    except SyntaxError as e:
        return False, f"file does not compile: {e}", ""
    path.write_text(source.rstrip() + "\n", encoding="utf-8", newline="\n")
    d = subprocess.run(["git", "diff", "--", str(path)], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace").stdout
    return bool(d.strip()), (f"targets/{target}/app.py" if d.strip() else "no change"), d


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
    # Drop the parent session's own Claude variables, but keep the credentials the agent is meant to use in CI.
    keep = {"CLAUDE_CODE_OAUTH_TOKEN"}
    env = {k: v for k, v in os.environ.items() if k in keep or (not k.startswith(("CLAUDE", "MCP_")) and k != "CLAUDECODE")}
    # The prompt goes in on stdin: with a tool's full source it is longer than Windows allows on a command line.
    a = subprocess.run([agent, "-p", "--output-format", "json",
                        "--disallowedTools", "Bash,PowerShell,Edit,Write,MultiEdit,NotebookEdit,WebFetch,WebSearch,Task,Agent"],
                       input=prompt, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
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
        reply = ask_agent(agent, PROMPT.format(target=args.target, code=code, report=report, source=source,
                                          context=CONTEXT.get(args.target, "not available")))
        summary = reply.split("```")[0].strip()
        print(summary[:600], flush=True)
        new_file, diff = extract_file(reply), extract_diff(reply)
        if new_file:
            ok, info, diff = write_file(args.target, new_file)
        elif diff:
            ok, info = apply_patch(args.target, diff)
        else:
            print("-- agent returned no fix", flush=True)
            log += [f"- Agent: {summary[:1200]}", "- No fix returned.", ""]
            if re.search(r"(?i)failed to authenticate|invalid (bearer|api) |401|credit balance|not logged in", reply):
                log.append("- The agent could not sign in; stopping without further Kane runs.")
                print("== agent could not sign in; stopping ==", flush=True)
                code = 2
                break
            continue
        if ok:  # free sanity check on all 10 candidates before spending Kane credits on the fix
            sc, sout = run_gate(args.target, ["--candidates", "all", "--out", str(ROOT / "reports" / "sanity")], True)
            sv = next((l for l in sout.splitlines() if l.startswith("VERDICT")), f"exit {sc}")
            log.append(f"- Free dry run of the fixed tool, all 10 candidates: **{sv}**")
            print(f"-- dry run of the fix on all candidates: {sv}", flush=True)
            if "do not depend on the CV" in sout:
                subprocess.run(["git", "checkout", "--", f"targets/{args.target}/"], cwd=ROOT)
                ok, info = False, "scores no longer depend on the CV (degenerate fix); reverted"
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
