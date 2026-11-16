# Demo video script (3–5 min allowed; aim for 3:30)

Record before **18 Nov, 02:00 UTC** (Render maintenance). Open the live site a minute early so it is awake.
Screen: 1440 px browser + a terminal. Say every line once; no filler. Everything shown must be real.

## 0:00–0:20 · Hook: the Twin Lab
Live site → **Twin Lab** → click *Greg → Emily → Jamal → Lakisha*, then a dashed placebo name.
> "Same CV. Only the name changes. This tool shortlists Greg and rejects Lakisha. And this placebo name, same group, different name: no change. So it isn't noise. It's the demographics."

## 0:20–0:40 · The gap
Scroll to **"Fairness toolkits need the model. Employers get a login screen."**
> "Fairness libraries need the model weights. Employers who buy hiring AI get a login screen. So we audit through the screen, with Kane CLI."

## 0:40–1:30 · Kane drives the real UI (the real evidence)
Open the **GitHub Actions run** (red) → job summary with the audit table → click the **Kane Test Manager evidence link** → replay: the CV pasted, the score stored.
> "Kane gets one line: a URL and a task. In a real browser it submitted four identical CVs under four names, read each score off the page, and sealed this evidence pack. The gate turned that into exit code 1. Deploy blocked."

Then the site's **results page** → the green **"Kane verified run"** panel.
> "The scores Kane read in the browser match the model exactly. Everything else on this page is labelled a dry run; this panel is Kane."

## 1:30–1:55 · Same audit, three interfaces
**Results** page: three window cards.
> "Same one-line task, three different interfaces. The fair tool passes. The open-source model, which we didn't build, fails differently: it's name-unstable. On realistic CVs, one in four candidates gets a different decision from a name change alone. Validated on 1,600 CVs with a placebo control."

Click **"Run live check"** on QuickMatch; let 3–4 lines stream in.
> "Anyone can re-run the quick check from the site. The authoritative run is Kane's: the command for your own Kane account is right here."

## 1:55–2:50 · Closed loop: Kane's verdict feeds the agent
Terminal, on a branch:
```
python loop/agent_loop.py --target talentscreen --dry --max-rounds 2
```
Show, in order: `VERDICT FAIL: BIASED` → "handing Kane's report to the agent" → the agent's one-paragraph diagnosis → `patch applied to targets/talentscreen/app.py` → round 2 → `VERDICT PASS` → `DEPLOY ALLOWED: loop closed`.
> "The gate fails. The loop hands Kane's report to Claude Code. The agent finds the cause, the tool guesses sex and ethnicity from the name and feeds a model trained on biased labels, and returns a patch. The loop applies it and audits again. Pass. The agent never touched the audit: that's deny-listed."

**If a real Kane re-run is available** (credits), replace `--dry` with `--gate-args "--candidates cand01 --no-placebo"` and show Kane's own PASS.
**If not**, say once, plainly, over the round-2 PASS:
> "This re-run is the quick check. Kane confirms it on the next CI run; the CI gate is wired to the same command."

Show `reports/loop_talentscreen.md` with the recorded diff for two seconds.
> "Every patch is recorded verbatim. Kane is the referee; the agent doesn't grade its own homework."

## 2:50–3:20 · Close
Landing hero → footer *"Hiring AI shouldn't care what your name is."*
> "Black-box bias audits, through the tool's own interface, with a placebo control, sealed evidence, and a loop that blocks a biased release until the agent fixes it. Built on Kane CLI."

---

## Checklist before recording
- [ ] `main` still has the biased TalentScreen (the gate must fail first).
- [ ] Work on a branch: `git checkout -b demo-fix`; afterwards `git checkout main` so judges get the biased version.
- [ ] `kane-cli balance`: if ≥ 100, use real Kane in the loop step; if credits ever reach ~250, run QuickMatch with Kane first.
- [ ] Kane Test Manager link open in a tab (from `results/twin_audit_talentscreen.kane.json`).
- [ ] Live site awake; Twin Lab works; "Run live check" tried once (20 s cooldown).
- [ ] Terminal font ≥ 16 px; window 1440 px wide.
- [ ] Upload to YouTube as **Unlisted**; title: "Kane Fairness Auditor — black-box bias audits for hiring AI (Kane CLI Hackathon)".
