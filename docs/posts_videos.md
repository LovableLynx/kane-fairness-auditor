# Five video posts

Every number below comes from `results/` in this repo. Tag @TestMu AI on LinkedIn, @kane_cli and @testmuai on X.

| # | Video | Suggested day |
|---|---|---|
| 1 | `docs/media/kane-fairness-auditor-demo.mp4` (4:00, YouTube, the submission video) | Fri 20 Nov |
| 2 | `docs/media/kane-short-twin.mp4` (43 s) | Sat 21 Nov |
| 3 | `docs/media/kane-short-loop.mp4` (46 s) | Sun 22 Nov |
| 4 | `docs/media/kane-short-url.mp4` (45 s) | Mon 23 Nov |
| 5 | `docs/media/kane-short-replay.mp4` (47 s) | Tue 24 Nov |

---

## 1 · The full demo (YouTube link + LinkedIn)

> I built a fairness gate for AI hiring tools with Kane CLI from TestMu AI.
>
> It sends the same CV under different names, men and women from two name groups, and Kane drives each hiring tool's real web page in Chrome, like a recruiter would. If a name changes the decision, the deploy is blocked.
>
> 3 hiring tools, 240 real-browser readings, and every one matches Kane's own raw log (240/240).
>
> 4-minute demo: [YouTube link]
> Try it: https://kane-fairness-auditor.onrender.com
> Code: https://github.com/LovableLynx/kane-fairness-auditor
>
> #KaneCLIHackathon #KaneCLI

## 2 · Twin your CV

> Your CV. Eight names. Does the AI notice?
>
> Paste your CV and we rewrite it under 8 test names. Nothing else changes. Three AI recruiters score every version.
>
> On our sample CV, 2 of the 3 changed their decision when only the name changed. Kane CLI read those same 24 scores in a real browser, and they match exactly.
>
> It's free and your CV is never saved or sent to Kane: https://kane-fairness-auditor.onrender.com/your-cv
>
> #KaneCLIHackathon #KaneCLI

## 3 · The closed loop

> Kane blocked it. An agent fixed it. Kane checked again.
>
> TalentScreen (a demo tool we built to be biased) shortlisted Brendan Kelly at 1.000 and rejected Hakim Jones at 0.001: same CV. Kane CLI flagged it: FAIL: BIASED.
>
> Claude Code read Kane's report and the code, found the cause (the tool guessed gender and ethnicity from the name) and returned a fix. A fresh Kane run: all 8 names 0.644. PASS.
>
> Then an open-source model nobody can retrain: name gap 0.130 → 0.000. The first Kane re-run stalled, so we re-ran it. And the side effect, reported: a stricter cutoff, 8/80 shortlisted after the fix against 24/80 before.
>
> https://github.com/LovableLynx/kane-fairness-auditor
>
> #KaneCLIHackathon #KaneCLI

## 4 · Audit any hiring tool by URL

> One URL. One sentence. That's all Kane CLI needs to audit your hiring tool for name bias. Or put it in a GitHub Action and block the merge.
>
> When we tested it on a public URL, Kane went off-script: it changed the "Hiring for" dropdown to Chef, and a fair tool looked biased. So we added a guard. If Kane changes a setting, those readings are void and the verdict is INCONCLUSIVE, never a false FAIL.
>
> Re-run on the public URL: PASS, 4/4 readings equal to the tool's own scores.
>
> https://github.com/LovableLynx/kane-fairness-auditor
>
> #KaneCLIHackathon #KaneCLI

## 5 · The free regression test

> Every Kane CLI run writes a Playwright test. We use it.
>
> We wipe the numbers Kane stored, so every score must be read from the page again, then replay it offline: 0 Kane credits, about 2 minutes.
>
> Same tools: 12/16, 14/16 and 16/16 readings re-read and identical (the rest were read by Kane's vision AI and can't be replayed). CONFIRMED.
> The fixed tool, whose scores really changed: 12 changed. NOT CONFIRMED. It can't fake a pass.
>
> Replay every commit for free, pay for Kane only when something changed.
>
> https://github.com/LovableLynx/kane-fairness-auditor
>
> #KaneCLIHackathon #KaneCLI
