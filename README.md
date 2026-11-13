# Kane Fairness Gate

**Counterfactual bias tests for AI hiring tools, run through the real UI by Kane CLI and used to gate deploys.**

AI screening tools are usually audited offline, on a dataset, by a data scientist. Real users never see that version. They see a web form. This project audits the product itself. Kane CLI opens the screening app in a browser and scores the same candidate several times, changing only the declared gender or ethnicity each time. It stores each score and checks that the UI really applied the change. The harness then compares the scores. If changing a protected attribute changes the outcome, the deploy is blocked.

```
 model change ──► gate.py boots HireScore ──► Kane CLI drives the browser
                                                │  same candidate, Male vs Female,
                                                │  Group A vs B vs C, "store as score_*"
                                                ▼
              audit.json / audit.md ◄── compare run_end.final_state scores
                     │
                     ├── exit 0 PASS → deploy      exit 1 FAIL → blocked
                     └── badge rendered in the app header (the app shows its own audit status)
```

## What's in the box

| Path | What it is |
|---|---|
| `app/` | **HireScore**, a small Flask screening portal. It serves one of three logistic-regression models trained on FairCVdb: `fair`, `gender_biased` or `ethnicity_biased`. |
| `audit/audit.py` | Builds one Kane objective per (candidate, attribute) and runs `kane-cli run … --agent`. It parses the `run_end` NDJSON, compares the stored scores and writes `reports/audit.{json,md}`. |
| `audit/gate.py` | Boots the app with a chosen model, runs the audit and tears down. Its exit code is the deploy decision. |
| `tests/kane/smoke_test.md` | A Kane test-as-markdown smoke suite for the scoring flow. |
| `.github/workflows/fairness-gate.yml` | Runs the gate in CI and adds the report to the job summary. |

## Quick start

```bash
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
npm install -g @testmuai/kane-cli && kane-cli login

# Expected to be blocked: the gender-biased model
python audit/gate.py --model gender_biased

# Expected to pass
python audit/gate.py --model fair

# Kane smoke suite (start the app first: cd app && python app.py)
kane-cli testmd run tests/kane/smoke_test.md
```

`--direct` skips the browser and calls `/api/score` instead. It is a dry run for development only, because nothing is verified through the UI.

## Results (direct dry run, candidates 12/16/32, threshold 0.05)

| Model | Max counterfactual gap | Gate |
|---|---|---|
| fair | 0.039 | PASS |
| gender_biased | 0.845 | FAIL |
| ethnicity_biased | 0.991 | FAIL |

## Why the default candidates are 12, 16 and 32

Most candidates score near 0 or 1, and at those extremes even a biased model shows no gap. The defaults sit near the decision boundary. That is where bias changes a decision, so it is where an audit has to look.

## Data and lineage

Profiles come from [FairCVdb](https://github.com/BiDAlab/FairCVtest) (Peña et al., 2020): synthetic CVs with known injected bias. The models and fairness thresholds come from the earlier research prototype *Bias as a Test Case*. This repo is new work for the Kane CLI Online Hackathon (Nov 12–19, 2026).
