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

Kane runs headless by default. On Windows, headed Chrome screenshots time out. Each candidate is one Kane run with 8 CV submissions.

## Live deployment

The auditor site and all three tools run as one web service (`serve.py`): `/` (auditor), `/talentscreen/`, `/hirelens/`, `/quickmatch/`.
`render.yaml` deploys it on Render's free tier straight from this repo. Real Kane audits are written to `results/`, which the hosted site reads.

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
| `.github/workflows/fairness-gate.yml` | CI gate on pull requests |
| `docs/` | Audit report and demo script |
| `.testmuai/` | Kane test and evidence from real runs |

Data: [FairCVdb](https://github.com/BiDAlab/FairCVtest) (Peña et al., 2020), synthetic profiles. Built for the TestMu AI Kane CLI Online Hackathon, November 2026.
