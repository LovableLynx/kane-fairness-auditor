# Demo video script (3:00 max)

Record before **18 Nov, 02:00 UTC** (Render maintenance). Open the live site a minute early so it is awake.
Screen: 1440 px wide browser plus a terminal. Speak slowly; every line below fits in the time given.

## 0:00–0:20 · Hook: the Twin Lab
Live site → scroll to **Twin Lab** → click *Greg → Emily → Jamal → Lakisha*.
> "Same CV. Different name. Watch the scores. This tool rejects Lakisha and shortlists Greg, with the same CV. Employers buy tools like this and can't see inside them. But the law says they're responsible."

## 0:20–0:45 · The gap
Scroll to **"Fairness toolkits need the model. Employers get a login screen."**
> "Fairness libraries need the model weights. Employers only get a login screen. So we built an auditor that needs only the screen, with Kane CLI."

## 0:45–1:30 · Kane drives the real UI
Terminal: `python audit/gate.py --target talentscreen --candidates cand01 --no-placebo`
Split screen: the Kane evidence replay (Test Manager link) showing the CV being pasted and the score being stored.
> "Kane gets one line: a URL and a task. It pastes identical CVs under different names into the real interface, reads each score, and seals evidence. Our gate turns that into an exit code."

Show `VERDICT FAIL: BIASED` and `DEPLOY BLOCKED`, then the **GitHub Actions** run in red with the report in the job summary.

## 1:30–1:55 · Same audit, three interfaces
Site → **Results**: three window cards with stamps.
> "Same one-line instruction, three completely different interfaces. The fair tool passes. The open-source model fails in a different way: it's name-unstable. Change only the name, even to one from the same group, and one in four realistic CVs gets a different decision. We validated that on 1,600 CVs with a placebo control."

Open the **decision map** on a result page for a second.

## 1:55–2:40 · Closed loop: the coding agent fixes it
Claude Code, prompt:
> "The fairness gate failed. Read reports/twin_audit_talentscreen.md and fix TalentScreen so it passes. Don't change the audit."

Show the agent:
1. Reading the report: demographic swaps move scores, placebo swaps don't.
2. Finding `cv.infer_identity` in `targets/talentscreen/app.py` feeding sex and group into a model trained on biased labels.
3. Removing the inference and switching to the model without protected attributes.
4. Rerunning the Kane gate: `PASS`, then `DEPLOY ALLOWED`, exit 0.
> "The agent doesn't grade its own homework. Kane does."

## 2:40–3:00 · Close
Landing page hero, then the footer: *"Hiring AI shouldn't care what your name is."*
> "Black-box bias audits, through the tool's own interface, with evidence, on every release. Built on Kane CLI."

---

## Checklist before recording
- [ ] TalentScreen on `main` still uses the biased model, so the gate fails.
- [ ] Credits for 2 Kane runs (before and after the fix): `kane-cli balance`.
- [ ] A Kane Test Manager link from the CI run, opened in a tab.
- [ ] The live site warmed up; Twin Lab works.
- [ ] Do the fix on a branch so `main` stays biased for the judges' own runs.
