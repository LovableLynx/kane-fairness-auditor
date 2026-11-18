# Kane Fairness Auditor

**Live demo:** https://kane-fairness-auditor.onrender.com (free tier; the first visit after idle takes about a minute to wake up)

**Bias audits for AI hiring tools, run through the tool's own interface by Kane CLI.**

> Fairness toolkits need the model. Employers only get a login screen.

Employers increasingly screen CVs with AI tools they buy, and they are accountable when those tools discriminate. NYC Local Law 144 requires an independent bias audit of automated employment decision tools, and the EU AI Act classes recruitment AI as high-risk. But the employer cannot see the vendor's model, training data or code. Existing fairness libraries such as Fairlearn and AIF360 need exactly those things.

**This project audits a hiring tool using only its web interface.** Kane CLI submits *CV twins* through the real UI: CVs with identical qualifications that differ only in the candidate's name and pronouns. It reads each score and decision and keeps a sealed evidence pack of every run. The auditor then reports whether the tool is **biased**, **name-unstable**, or **fair**, and the result gates deployment in CI.

The method is automated *correspondence testing*, the established technique for detecting hiring discrimination (Bertrand & Mullainathan, 2004, "Are Emily and Greg More Employable than Lakisha and Jamal?"). The CV names come from that study. No real candidate data is used.

## How it works

```
audit/targets.json          only a URL + one-line task per tool  (blind-target rule)
        │
data/cvs/<candidate>/       identical CVs: male/female × name group A/C
        │                   + a second same-group name per cell (placebo)
        ▼
kane-cli run "<task>, using exactly this CV text: {{cv_…}} … store the match score as 'score_…'" --agent
        │   Kane drives the real UI in Chrome, stores every score and decision,
        │   and seals an evidence pack with a Test Manager link.
        ▼
twin_audit.py               demographic gap vs placebo gap, directional effects,
        │                   LL144-style impact ratios
        ▼
verdict + exit code         PASS (0) · FAIL: BIASED / NAME-UNSTABLE (1) · INCONCLUSIVE (2)
        │
gate.py + GitHub Actions    a failing audit blocks the deploy · auditor/ site shows the evidence
```

**Why the placebo matters.** If swapping *Greg* for *Emily* changes a decision, that could be gender bias, or the model might react to any name change. So every candidate also gets a second name from the *same* demographic group (Greg → Brad). Comparing the two separates two different failures:

- **BIASED:** demographic swaps move scores more than same-group swaps, or there is a consistent gap by sex or name group.
- **NAME-UNSTABLE:** the decision changes when only the name changes, even within one group. A hiring decision should never depend on the name.

## Three audit targets with different interfaces

| Target | Interface | Model | Purpose |
|---|---|---|---|
| **TalentScreen** `:5101` | Dark recruiter app: drag-and-drop or paste a CV, then a 0–1 match score and SHORTLIST/REJECT | Logistic regression trained on FairCVdb labels with injected bias; infers demographics from the name | Known bias: the audit must catch it |
| **HireLens** `:5102` | Light ATS: sidebar, "Add applicant", résumé box, then "Role fit: 47%" and "Advance to interview" | Fair model (protected attributes dropped, blind labels) | Known fair: the audit must pass it |
| **QuickMatch** `:5103` | 3-step wizard (role → candidate → review) with a similarity score and a verdict | Off-the-shelf **all-MiniLM-L6-v2** embeddings vs. the job description | A real black box we did not train |

The same audit, with the same one-line task format and no selectors, runs unchanged on all three.

## Results

### Twin audit (10 candidates, 8 CVs each, short CVs)

| Tool | Verdict | Why |
|---|---|---|
| TalentScreen | **FAIL: BIASED** | Demographic swaps move scores 0.50 more than placebo swaps; 10/10 candidates flip on sex or name group while placebo names never do |
| HireLens | **PASS** | No demographic or name effect |
| QuickMatch | **FAIL: NAME-UNSTABLE** | 5/10 candidates (4/10 on long CVs) get a different decision from a same-group name swap alone |

### Validation study: open-source model (100 candidates × 16 CVs)

To check that these findings are not artefacts of short CVs, cutoff choice or sample size, `audit/study.py` scores 1,600 CVs. It uses short (~50 words) and long (~340 words) versions, a cutoff calibrated on 200 CVs that are never audited, bootstrap 95% CIs and permutation tests.

| QuickMatch (all-MiniLM-L6-v2) | Short CVs | Long CVs |
|---|---|---|
| Female − male score | −0.013 [−0.018, −0.008], p<0.001 | −0.001 [−0.003, +0.001], n.s. |
| Group C − group A score | +0.026 [+0.018, +0.035], p<0.001 | **+0.016 [+0.011, +0.021], p<0.001** |
| Same-group name swap (placebo) | +0.003, n.s. | +0.001, n.s. |
| Decision changes from a name change at the tool's cutoff | 69% of candidates | **27% of candidates** |

**Reading:** the gender effect only appears on very short CVs and disappears at realistic length. A small but significant name-group effect remains on long CVs. The larger problem is instability: on realistic CVs, about 1 in 4 candidates' outcomes depend on the name alone. The controls behave as expected. TalentScreen shows zero placebo effect and large demographic effects; HireLens shows zero for both.

### What Kane has verified so far (real browser)

| Run | Scope | Result | Evidence |
|---|---|---|---|
| TalentScreen, GitHub Actions | 1 candidate, 4 demographic twins, **no placebo names** | **FAIL: BIASED**, deploy blocked, 80 credits | [CI run](https://github.com/LovableLynx/kane-fairness-auditor/actions/runs/43607099418) · Test Manager link on the [results page](https://kane-fairness-auditor.onrender.com/results/talentscreen) |
| TalentScreen, local, real Chrome | **full audit: 10 candidates × 8 CVs (80 readings), with placebo names** | **FAIL: BIASED**, deploy blocked, 1,476 credits | 10 Test Manager share links in [`results/twin_audit_talentscreen.kane.json`](results/twin_audit_talentscreen.kane.json) · [results page](https://kane-fairness-auditor.onrender.com/results/talentscreen) |
| HireLens, local, real Chrome | **full audit: 10 candidates × 8 CVs (80 readings), with placebo names** | **PASS**, deploy allowed, 1,351 credits | 10 Test Manager share links in [`results/twin_audit_hirelens.kane.json`](results/twin_audit_hirelens.kane.json) · [results page](https://kane-fairness-auditor.onrender.com/results/hirelens) |
| QuickMatch, local, real Chrome | **full audit: 10 candidates × 8 CVs (80 readings), with placebo names** | **FAIL: NAME-UNSTABLE**, deploy blocked, 1,604 credits | 10 Test Manager share links in [`results/twin_audit_quickmatch.kane.json`](results/twin_audit_quickmatch.kane.json) · [results page](https://kane-fairness-auditor.onrender.com/results/quickmatch) |

**240 real-browser readings, 240/240 identical to the dry run.** Every one is checked three ways by [`audit/verify_kane.py`](audit/verify_kane.py) (read-only): the published number against Kane's own raw `run_end` log, against the dry run through the tool's HTTP endpoint, and that Kane changed no setting on the page before submitting. QuickMatch is the open-source language model we did not build: its NAME-UNSTABLE finding holds in a real browser (5/10 candidates get a different decision from a same-group name swap alone). The full runs were made on 17–18 Nov; the GitHub Actions run above is the earlier CI demo.

**What went wrong once, and how we caught it.** The first TalentScreen full run matched the dry run on only 64/80 readings. Kane's logs showed why: on 6 candidates it had chosen the "Hiring for" job matching the CV (Chef, Teacher, Accountant...) instead of leaving Data Analyst, so twins were scored for different jobs. Kane read every number correctly; replaying those CVs with the job it picked reproduces its scores exactly. We pinned the role in Kane's task, added the setting-change check to the verifier, and re-ran all 10 candidates: 80/80. The discarded run is kept locally for the record, not published.

### Twin your own CV (free, on the website)

[`/your-cv`](https://kane-fairness-auditor.onrender.com/your-cv) rewrites a visitor's CV under the audit's eight test names (only the name, email and he/she pronouns change), scores every version on all three tools through their own forms, and replays the results. It runs in Python on the server: no Kane, no credits. The CV is never written to disk or sent to Kane, GitHub or TestMu; each tool's copy is deleted as soon as its score is read. The sample CV reproduces the Kane-verified readings for candidate 2 exactly ([`tests/test_yourcv.py`](tests/test_yourcv.py)). Kane runs from the website use the prepared test CVs only.

### A finding about the legal metric

On TalentScreen, the LL144-style **impact ratio for sex is 1.0**, which looks perfectly fair, while every woman scored far below her identical male twin. Aggregate selection ratios can hide individual-level discrimination that twin testing exposes. We report both.

## Quick start

```bash
python -m venv .venv && .venv\Scripts\activate          # Windows (source .venv/bin/activate elsewhere)
pip install -r requirements.txt
npm install -g @testmuai/kane-cli && kane-cli login

# Gate a tool: boots it, runs the Kane audit through its UI, exits 0/1/2
python audit/gate.py --target talentscreen               # expect FAIL: BIASED  → deploy blocked
python audit/gate.py --target hirelens                   # expect PASS          → deploy allowed

# Audit the public deployment instead of a local copy
python audit/twin_audit.py --target talentscreen --live --candidates cand01

# Auditor site (landing, results, method, legal)
python auditor/app.py                                    # http://127.0.0.1:5100

# Free dry runs (no browser, no credits): direct HTTP, never used for a real verdict
python audit/gate.py --target quickmatch --direct --candidates all --length long
python audit/study.py --target quickmatch                # needs the tool running
```

Regenerating data needs FairCVdb: `python -m cvkit.build path/to/FairCVdb.npy`.

## Closed loop: Kane's verdict feeds the coding agent

**The loop has been closed with Kane, not just rehearsed** (18 Nov, candidate 1, 8 CVs with placebo names, real browser):

| | Kane verdict | Scores across the 8 names | Evidence |
|---|---|---|---|
| Before: TalentScreen as shipped | **FAIL: BIASED** | 0.000 to 1.000, decision flips on the name | [Kane run](https://test-manager.lambdatest.com/projects/01M7NH370AGCJ2XFPS5Z9FNHT7/test-cases/01M7P5RTAZR0ZPGDFMW3EGTVEX/dashboard/share/US_UTY9XFHKLYP08AH2FMCKP9L4XXOHLBHKFTG1ST48DN84MTZACCAO54UGAILJPK2E?type=summary&agentView=true&fqdn=summary-page) |
| Claude Code's fix | removed name/pronoun-based demographic guessing, switched to the fair model | | [diff](https://github.com/LovableLynx/kane-fairness-auditor/compare/main...loop-kane) · [loop log](https://github.com/LovableLynx/kane-fairness-auditor/blob/loop-kane/docs/loop/loop_talentscreen.md) |
| After: fresh Kane run on the fixed code | **PASS** | every name 0.644, SHORTLIST | [Kane run](https://test-manager.lambdatest.com/projects/01M7NH370AGCJ2XFPS5Z9FNHT7/test-cases/01M7PSYFS7GHQMK11V14KQNV6E/dashboard/share/US_CMKVC1L8MNI2B3W0YMWM1PVW1N3B2YFJ0GB5O3A9Y0M96TUN9LNNI6PUSMSVTRG3?type=summary&agentView=true&fqdn=summary-page) |

Checked like the full audits: 8/8 after-fix readings equal Kane's raw log and the fixed tool's own scores, Kane changed no page settings, and the PASS is a new Kane run (154 credits). Kane checkpoints carry a fingerprint of the tool's code, so an after-fix audit can never reuse a run made before the fix. `main` keeps the biased TalentScreen as a demo target; the fixed version lives on the [`loop-kane`](https://github.com/LovableLynx/kane-fairness-auditor/tree/loop-kane) branch.

Kane is the referee; the agent never grades its own work. Three ways to run the loop:

```bash
# 1. Automatic (judges): gate -> Claude Code reads Kane's report and returns a patch -> the loop applies it -> gate again.
#    The agent needs no write permission; every patch is recorded verbatim in reports/loop_<target>.md.
python loop/agent_loop.py --target talentscreen --dry --max-rounds 2      # free rehearsal
python loop/agent_loop.py --target talentscreen --gate-args "--candidates cand01 --no-placebo"   # real Kane

# 2. Interactive: inside Claude Code in this repo
/fairness-fix talentscreen

# 3. Always-on: .claude/settings.json installs a PostToolUse hook. Whenever the agent edits a hiring tool,
#    a quick fairness check runs and its verdict is fed straight back to the agent (exit 2 = shown to the model).
```

Guardrails (`.claude/settings.json`): the agent may edit `targets/**` and run the gate; `audit/`, `data/`, `results/`, `cvkit/names.py` and the loop itself are deny-listed, so a fix can never be "change the audit". Run the loop on a branch: it edits `targets/<target>/` for real.

Kane runs headless by default. On Windows, headed Chrome screenshots time out. Each candidate is one Kane run with 8 CV submissions.

## Live deployment

The auditor site and all three tools run as one web service (`serve.py`): `/` (auditor), `/talentscreen/`, `/hirelens/`, `/quickmatch/`.
`render.yaml` deploys it on Render's free tier straight from this repo. Kane runs are published to `results/<target>.kane.json` with `audit/publish_kane.py`, which the hosted site reads next to the dry runs.

**Run Kane from the website.** Each results page has a *Run with Kane* button: pick a candidate and the site triggers the GitHub Actions gate, where Kane CLI submits that candidate's 8 CVs through the tool's real UI on the project's TestMu credits. One run at a time, capped per day (counted on GitHub, `KANE_DAILY_CAP`, default 8). Needs `GITHUB_TOKEN` on the server: a fine-grained token for this repo with *Actions: read and write*.

**Pick the role.** TalentScreen and HireLens let the recruiter choose one of 10 roles (one per job family). The demo models were trained on FairCVdb labels for one job, Data Analyst, which stays the default and is the role every audit uses, so audit results are unaffected. For another role, a CV from that role's job family is scored as on-target and any other family as off-target; the rest of the CV is scored as before. HireLens shows *Why this score*: how each part of the profile moved the score (the FairCVdb labels reward a recommendation letter and Spanish or French, so many real CVs score low; the breakdown makes that visible instead of hiding it).

**Test CVs.** `samples/test-cvs/` (and the results page) has realistic fictional CVs as PDF, Word and text, including one data-analyst CV under four names, for trying the tools by hand. Regenerate with `python -m cvkit.make_test_cvs`.

```bash
python serve.py        # the same service locally on http://127.0.0.1:8000
```

## Scope and method

- **Method:** automated correspondence testing with synthetic CV twins, the standard approach for detecting hiring discrimination. No real candidate data is used.
- **Measures:** individual fairness (twin flips and gaps, with a placebo control) and group fairness (LL144-style impact ratios). Impact ratios from small samples are illustrative.
- **Authorised use:** built for employers and auditors testing tools they own or license. The demo targets are purpose-built so the audit can be validated against known ground truth.
- **Black-box rule:** Kane receives only a URL and a one-line task; the `direct` adapters in `targets.json` are dev-only shortcuts and never produce a Kane verdict.

## Repository

| Path | Contents |
|---|---|
| `cvkit/` | CV renderer and parser, name pools, model training, twin and study generation |
| `targets/` | The three audited hiring tools |
| `audit/twin_audit.py` | Kane-driven twin audit and verdict |
| `audit/gate.py` | Boot, audit, tear down; exit code = deploy decision |
| `audit/study.py` | 100-candidate validation study |
| `auditor/` | Product site: landing, Twin Lab, results, method, legal; "Blueprint 95" design system in `auditor/static/ds.css`, self-hosted OFL fonts |
| `shared/` | Hardening shared by every app: size limits, bounded stores, security headers, fixed error messages |
| `loop/` | Closed loop: `agent_loop.py` (patch-based, for judges) and `hook_gate.py` (Claude Code hook) |
| `.claude/` | `/fairness-fix` command, hook wiring and permission guardrails |
| `tests/` | CV parser tests (`python -m unittest tests.test_cv_parser`) and a Kane smoke test |
| `.github/workflows/fairness-gate.yml` | CI gate on pull requests |
| `docs/` | Audit report and demo script |
| `.testmuai/` | Kane test and evidence from real runs |

Data: [FairCVdb](https://github.com/BiDAlab/FairCVtest) (Peña et al., 2020), synthetic profiles. Built for the TestMu AI Kane CLI Online Hackathon, November 2026.
