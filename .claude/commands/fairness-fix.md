---
description: Run the Kane fairness gate on a hiring tool, read Kane's audit, fix the tool, and repeat until Kane passes it.
argument-hint: <talentscreen|hirelens|quickmatch> [extra gate flags, e.g. --candidates cand01 --no-placebo]
---

You are fixing a hiring tool so that it passes an **independent** fairness audit run by Kane CLI.
Kane is the referee: you never decide on your own that the tool is fair.

Target and flags: `$ARGUMENTS` (if empty, use `talentscreen --candidates cand01 --no-placebo`).

Repeat at most 3 times:

1. **Run the Kane gate** (real browser, costs Kane credits):
   `python audit/gate.py --target <target> <flags>`
   - Exit 0: the tool passes. Stop and go to the summary.
   - Exit 2 (inconclusive): read the error, fix setup problems (not the audit), and run again.
   - Exit 1 (blocked): continue.
2. **Read Kane's evidence**: `reports/twin_audit_<target>.md` and `.json`. Note:
   - which CV twins changed decision, and whether placebo (same-group) names also moved;
   - the verdict reasons (BIASED vs NAME-UNSTABLE);
   - the Kane Test Manager links for each candidate.
3. **Find the cause** in `targets/<target>/` only. Typical causes: the tool reads names, pronouns or other
   demographic signals (for example `cv.infer_identity`) and feeds them to the model, or it uses a model
   trained on biased labels (`models/biased.pkl`). `models/fair.pkl` drops protected attributes.
4. **Fix it** without touching `audit/`, `data/` or `cvkit/names.py`. Never change the audit to make it pass.
   The PostToolUse hook runs a quick dry-run check after your edit and tells you if it still fails.
5. Go back to step 1.

**Summary** (always): what Kane found, what you changed and why, the final verdict and exit code, and the
Kane evidence links from `reports/twin_audit_<target>.json`. If it still fails after 3 attempts, say so plainly.
