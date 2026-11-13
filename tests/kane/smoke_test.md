---
mode: testing
tags: [smoke]
---

# TalentScreen smoke test

## Home page loads
Go to http://127.0.0.1:5101/
Assert: the page shows a 'Screen CV' button and a CV text box

## Screening flow works end to end
Go to http://127.0.0.1:5101/
Type 'Jill Kelly' followed by a blank line, then 'CURRENT ROLE', 'Data analyst', a blank line, 'EXPERIENCE', '6 years' into the CV text box
Click 'Screen CV'
Assert: the page shows 'Match score:' followed by a number between 0 and 1
Assert: the page shows a decision of either SHORTLIST or REJECT
Assert: no network request returned a 5xx status
