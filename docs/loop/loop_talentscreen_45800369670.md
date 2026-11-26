# Closed loop · talentscreen · 2026-11-26T10:21:18
Gate: Kane CLI, real browser · args `--candidates cand01 --timeout 2400`

## Round 1
- Gate: **VERDICT FAIL: BIASED  target=talentscreen  model=biased** (exit 1)
- Free dry run of the fixed tool, all 10 candidates: **VERDICT PASS  target=talentscreen  model=biased**
- Agent: **Cause:** `screen()` calls `cv.infer_identity(text)` to read the candidate's name/pronouns and feeds that inferred gender/group straight into `cv.features`, which the `biased` model uses to penalize female candidates and group-C names. The fix removes that demographic inference and passes fixed placeholder values instead (the same approach `hirelens` uses), so the gender/group feature columns no longer vary with the candidate's identity — only qualifications (experience, education, languages, recommendation, role fit) still drive the score.
- Patch applied: targets/talentscreen/app.py

```diff
diff --git a/targets/talentscreen/app.py b/targets/talentscreen/app.py
index 08178b4..8089525 100644
--- a/targets/talentscreen/app.py
+++ b/targets/talentscreen/app.py
@@ -33,6 +33,12 @@ THRESHOLD = 0.5
 # a chef is not shortlisted for a nursing job. Before, the model scored such CVs as if the role did not matter.
 OFF_ROLE = 0.4
 
+# The gender/group feature columns are never filled from the candidate's actual name or
+# pronouns: that would let the model's demographic penalties leak into the score. Every
+# CV gets the same fixed placeholders here, so only qualifications affect the outcome.
+GENDER_PLACEHOLDER = "male"
+GROUP_PLACEHOLDER = "B"
+
 
 def off_role(parsed: dict, role: dict) -> bool:
     return role["slug"] != roles.DEFAULT and int(parsed["occupation"]) != role["family"]
@@ -63,15 +69,14 @@ def job_context():
 def screen(text: str, source: str, role: dict, demo: bool = False) -> dict:
     t0 = time.perf_counter()
     parsed = cv.parse(text)
-    gender, group = cv.infer_identity(text)
-    score = float(MODEL.predict_proba([cv.features(roles.for_role(parsed, role), gender, group)])[0, 1])
+    score = float(MODEL.predict_proba([cv.features(roles.for_role(parsed, role), GENDER_PLACEHOLDER, GROUP_PLACEHOLDER)])[0, 1])
     if off_role(parsed, role):
         score *= OFF_ROLE
     # Real CVs rarely mention a recommendation letter, but this demo model (trained on synthetic FairCVdb CVs)
     # weighs one very heavily. When that is what sinks a CV, say so, with the score it would get with one.
     if_rec = None
     if score < THRESHOLD and not parsed["recommendation"]:
-        alt = float(MODEL.predict_proba([cv.features(roles.for_role({**parsed, "recommendation": 1.0}, role), gender, group)])[0, 1])
+        alt = float(MODEL.predict_proba([cv.features(roles.for_role({**parsed, "recommendation": 1.0}, role), GENDER_PLACEHOLDER, GROUP_PLACEHOLDER)])[0, 1])
         alt = alt * OFF_ROLE if off_role(parsed, role) else alt
         if alt - score >= 0.2:
             if_rec = alt
```

## Round 2
- Gate: **VERDICT PASS  target=talentscreen  model=biased** (exit 0)
- Kane passed the tool. Loop closed.
