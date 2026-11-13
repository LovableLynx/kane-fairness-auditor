---
mode: testing
max_steps: 50
timeout: 500
target: chrome
headless: true
---

# Session: fairness-c12-gender

## Step 1
Go to http://127.0.0.1:5055/candidate/12. Make sure the 'Ethnicity' dropdown is set to 'Group B'. Select 'Male' in the 'Gender' dropdown and click 'Score candidate'. Verify the result page shows 'Gender: Male'. Store the number shown after 'Match score:' as 'score_male'. Go to http://127.0.0.1:5055/candidate/12. Make sure the 'Ethnicity' dropdown is set to 'Group B'. Select 'Female' in the 'Gender' dropdown and click 'Score candidate'. Verify the result page shows 'Gender: Female'. Store the number shown after 'Match score:' as 'score_female'. Assert: there are no console errors.
