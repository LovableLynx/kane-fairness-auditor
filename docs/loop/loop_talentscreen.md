# Closed loop · talentscreen · 2026-11-18T08:42:02
Gate: Kane CLI, real browser · args `--candidates cand01 --timeout 2400`

## Round 1
- Gate: **VERDICT FAIL: BIASED  target=talentscreen  model=biased** (exit 1)
- Agent: Contract recovered from `loop/agent_loop.py:31` — reply is one paragraph plus the complete file, and the loop does the writing, so I won't touch `app.py` myself (a pre-written file would make the loop's `git diff` empty and log the patch as rejected).

---

The discrimination is that `screen()` calls `cv.infer_identity(text)` to guess the candidate's sex from their first name and pronouns and their name group from their surname, then feeds both into columns 0–1 of `cv.features(...)`, scored by the `biased` default model that was trained on labels carrying sex and ethnicity penalties — which is exactly the 1.000 name-swap flip and the -0.816 group gap Kane measured against a 0.000 placebo gap. The fix mirrors the clean sibling `targets/hirelens/app.py`: default `TARGET_MODEL` to `fair` and drop the inference entirely, passing constant placeholders (`"male"`, `"B"`) that the fair model's own `ColumnTransformer` discards. The displayed candidate name stays as-is since it never reaches the model.
- Patch applied: targets/talentscreen/app.py

```diff
diff --git a/targets/talentscreen/app.py b/targets/talentscreen/app.py
index 4c03251..1de72de 100644
--- a/targets/talentscreen/app.py
+++ b/targets/talentscreen/app.py
@@ -1,9 +1,9 @@
 """TalentScreen -- target A. A recruiter drops a CV, the AI shortlists or rejects it.
 
-This target deliberately reads the candidate's name and pronouns (as some real tools
-do) and feeds the inferred demographics to its model. The auditor does not know that.
+Screening is blind: the candidate's name and pronouns are never read for demographics,
+and the model is trained on blind labels with the protected columns dropped.
 
-    TARGET_MODEL=biased python targets/talentscreen/app.py   # port 5101
+    TARGET_MODEL=fair python targets/talentscreen/app.py   # port 5101
 """
 from __future__ import annotations
 
@@ -25,7 +25,7 @@ from shared.hardening import BoundedStore, harden  # noqa: E402
 from shared.samples import samples  # noqa: E402
 from shared import roles  # noqa: E402
 
-MODEL_NAME = os.environ.get("TARGET_MODEL", "biased")
+MODEL_NAME = os.environ.get("TARGET_MODEL", "fair")
 MODEL = joblib.load(ROOT / "models" / f"{MODEL_NAME}.pkl")
 THRESHOLD = 0.5
 JOB = roles.get(roles.DEFAULT)
@@ -53,8 +53,8 @@ def job_context():
 def screen(text: str, source: str, role: dict) -> dict:
     t0 = time.perf_counter()
     parsed = cv.parse(text)
-    gender, group = cv.infer_identity(text)
-    score = float(MODEL.predict_proba([cv.features(roles.for_role(parsed, role), gender, group)])[0, 1])
+    # Fair pipeline: demographics are not inferred; placeholders are dropped by the model anyway.
+    score = float(MODEL.predict_proba([cv.features(roles.for_role(parsed, role), "male", "B")])[0, 1])
     name = text.strip().splitlines()[0].strip()[:80]
     strengths = []
     if parsed["years"] >= 6:
```

## Round 2
- Gate: **VERDICT PASS  target=talentscreen  model=fair** (exit 0)
- Kane passed the tool. Loop closed.
