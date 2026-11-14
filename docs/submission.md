# Kane CLI Online Hackathon: submission answers

**Project name:** Kane Fairness Auditor

**Live URL:** https://kane-fairness-auditor.onrender.com
**Repository:** https://github.com/LovableLynx/kane-fairness-auditor
**Runnable command:** `python audit/gate.py --target talentscreen` (setup in the README)
**Lanes:** Browser agents in the wild · Verification baked into your workflow

## One-paragraph description

Employers increasingly screen CVs with AI tools they buy but can't inspect, yet laws such as NYC Local Law 144 and the EU AI Act hold them responsible for those tools' bias, and fairness libraries need model access they don't have. Kane Fairness Auditor tests a hiring tool through the only door an employer has: its web interface. Kane CLI receives just a URL and a one-line task, then submits *CV twins* through the real UI in a browser. These are identical CVs that differ only in name and pronouns, plus same-group "placebo" names. Kane stores every score and decision with "store as" and seals an evidence pack for each run. The auditor compares demographic swaps against placebo swaps to tell **BIASED** tools apart from **NAME-UNSTABLE** ones, and returns the verdict as an exit code that blocks deployment in GitHub Actions. The same instruction runs unchanged on three interfaces: a tool with planted bias (caught), a fair tool (passed), and an off-the-shelf open-source embedding model, which we found changes the decision for about 1 in 4 realistic CVs when only the name changes (validated on 1,600 CVs, with confidence intervals and a placebo control). The coding agent (Claude Code) built the system and closes the loop. It reads Kane's audit report, fixes the biased tool, and reruns the Kane gate until it passes, so the agent never grades its own homework.

## Shorter versions

**Tweet-length (≤280 chars):**
Same CV, different name, different verdict? Kane Fairness Auditor uses Kane CLI to submit CV twins through any hiring tool's own UI, separates bias from name-noise with a placebo control, and blocks biased releases in CI. No model access needed.

**One-liner:**
Black-box bias audits for AI hiring tools: CV twins, run through the tool's own interface by Kane CLI, gating every release.

## What Kane does in the flow

1. Gets a one-line task per tool (`audit/targets.json`): no selectors, no API.
2. Opens the tool in a real browser, pastes each CV twin and submits it.
3. Stores the score and decision shown (`store … as 'score_<twin>'`), returned in `run_end.final_state` (NDJSON, `--agent --headless`).
4. Seals an evidence pack and a Test Manager link per candidate.
5. Its exit status feeds `gate.py`, which returns 0 (deploy), 1 (blocked) or 2 (inconclusive, also blocked).

## Agent used

Claude Code (Anthropic) built the auditor, the three demo tools, the study and the site. In the demo it reads the failing audit report, fixes TalentScreen, and reruns the Kane gate until it passes.
