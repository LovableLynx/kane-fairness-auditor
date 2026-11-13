# Demo video script (3:00 max)

## 0:00–0:20 · The problem
On screen: TalentScreen home page.
> "Companies buy AI that screens CVs. The law says they must prove it isn't biased. But they can't see the model. All they get is this screen. Fairness toolkits need the model weights. We built an auditor that needs only the screen."

## 0:20–1:05 · Kane audits through the UI
Terminal: `python audit/gate.py --target talentscreen --candidates cand01`
Split screen: the Kane browser run (or its evidence replay), with the CV pasted and the score stored.
> "Kane gets one line: a URL and a task. It pastes identical CVs that differ only in the name: Greg, Emily, Jamal, Lakisha. It also pastes a second name from the same group as a placebo. It reads each score and decision, and seals the evidence."

Show `DEPLOY BLOCKED: fairness audit failed` and `FAIL: BIASED`.

## 1:05–1:35 · Same audit, different interfaces
Quick cuts: HireLens (PASS) and QuickMatch wizard (FAIL: NAME-UNSTABLE).
> "Same one-line instruction, three completely different interfaces, no selectors. The fair tool passes. The open-source matcher fails differently: its decision changes when only the name changes, even within the same group. One in four realistic CVs."

Dashboard: twin table with flips highlighted; impact ratio card showing sex ratio 1.0 on the biased tool.
> "And the legally required ratio looked perfectly fair here. Twin testing caught what it missed."

## 1:35–2:35 · Closed loop: the coding agent fixes it
GitHub PR: fairness-gate check red, job summary showing the audit table.
Claude Code prompt:
> "The fairness gate failed on this PR. Read reports/twin_audit_talentscreen.md and fix TalentScreen so it passes. Don't change the audit."

Show the agent:
1. Reading the report: demographic swaps move scores, placebo swaps don't.
2. Finding that `targets/talentscreen/app.py` infers gender and group from the name (`cv.infer_identity`) and feeds them to a model trained on biased labels.
3. Removing the inference and switching to the model trained without protected attributes on blind labels.
4. Re-running `python audit/gate.py --target talentscreen`: `PASS`, then `DEPLOY ALLOWED`.

## 2:35–3:00 · Close
Dashboard with three cards.
> "Interface-agnostic bias audits, with a placebo control, with evidence and a CI gate. Built on Kane CLI."

---

## Fix-loop checklist (before recording)
- [ ] TalentScreen on `main` still uses the biased model, so the gate fails.
- [ ] Credits available for 2 real Kane runs (before and after the fix), about 1 candidate each.
- [ ] Dashboard running on :5100 with real Kane reports, not `--direct` ones.
- [ ] Kane Test Manager links open.
