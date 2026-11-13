---
test: ../fairness-c12-gender_test.md
status: failed
started: 2026-11-13T16:37:02.826Z
duration_s: 224.5
session_id: 2d629409-7e18-4f22-99be-d38a0dd0a650
---

# Session: fairness-c12-gender — Result

## Step 1 ✗ failed (224.5s)
md5: 81a8b92f5ea4fe3d7abde7bd11b717ea
Reason: Console verification timed out despite reporting zero captured errors.
Go to http://127.0.0.1:5055/candidate/12. Make sure the 'Ethnicity' dropdown is set to 'Group B'. Select 'Male' in the 'Gender' dropdown and click 'Score candidate'. Verify the result page shows 'Gender: Male'. Store the number shown after 'Match score:' as 'score_male'. Go to http://127.0.0.1:5055/candidate/12. Make sure the 'Ethnicity' dropdown is set to 'Group B'. Select 'Female' in the 'Gender' dropdown and click 'Score candidate'. Verify the result page shows 'Gender: Female'. Store the number shown after 'Match score:' as 'score_female'. Assert: there are no console errors.
