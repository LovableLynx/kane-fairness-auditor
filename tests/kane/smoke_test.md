---
mode: testing
tags: [smoke]
---

# HireScore smoke test

## Candidate list loads
Go to http://127.0.0.1:5055/
Assert: the page shows a table of candidates with at least 10 rows
Assert: there are no console errors

## Scoring flow works end to end
Go to http://127.0.0.1:5055/candidate/12
Select 'Female' in the 'Gender' dropdown
Click 'Score candidate'
Assert: the page shows 'Gender: Female'
Assert: a match score between 0 and 1 is shown
Assert: the decision says either 'Shortlisted' or 'Rejected'
Assert: no network request returned a 5xx status
