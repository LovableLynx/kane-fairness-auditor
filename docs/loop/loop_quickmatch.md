# Closed loop · quickmatch · 2026-11-18T16:13:25
Gate: Kane CLI, real browser · args `--candidates cand02 --timeout 2400`

## Round 1
- Gate: **VERDICT FAIL: BIASED + NAME-UNSTABLE  target=quickmatch  model=sentence-transformers/all-MiniLM-L6-v2** (exit 1)
- Free dry run of the fixed tool, all 10 candidates: **VERDICT PASS  target=quickmatch  model=sentence-transformers/all-MiniLM-L6-v2**
- Agent: **Cause.** Nothing in the pipeline hides identity from the scorer: `similarity()` embeds the raw CV text, so the black-box MiniLM model sees the candidate's name, the name-bearing email address, honorifics and gendered pronouns, and its cosine score moves with them — hence the consistent female−male / group-A−group-C gaps *and* the same-group placebo flip (the model reacts to the name string itself, not to a protected attribute it "understands"). Since the model can't be retrained, the smallest sensible fix is blind screening at the input: de-identify the CV text before it ever reaches the model — strip the header/`Name:` name tokens wherever they recur, drop contact details that spell the name out, drop honorifics, and collapse every gendered pronoun to one token (collapsing rather than mapping form-by-form, because `her` → `their` vs `him` → `them` would leave the twins textually different). Qualifications pass through untouched, so scores still depend on the CV. The calibration pool is de-identified the same way and cached cutoffs are keyed by a scorer fingerprint, so a stale cutoff from the old scorer is recomputed instead of reused (the refreshed cache is written outside `data
- Patch applied: targets/quickmatch/app.py

```diff
diff --git a/targets/quickmatch/app.py b/targets/quickmatch/app.py
index 1692826..d5c3c09 100644
--- a/targets/quickmatch/app.py
+++ b/targets/quickmatch/app.py
@@ -3,8 +3,11 @@ semantic similarity to the job description using an off-the-shelf open-source
 embedding model (sentence-transformers/all-MiniLM-L6-v2 via fastembed).
 
 We did not train this model and we do not know how it treats names: it is the
-genuine black box in the demo. The CV is embedded as-is, name included, the way
-many "AI match score" features work.
+genuine black box in the demo. Because an independent twin audit showed that it
+scores the same CV differently when only the name or the pronouns change, the CV
+is de-identified before it is embedded (see `deidentify`): the model never sees
+the name, the name-bearing contact details, honorifics or gendered pronouns.
+Everything that is a qualification reaches the model untouched.
 
     python targets/quickmatch/app.py     # port 5103
 """
@@ -13,6 +16,7 @@ from __future__ import annotations
 import itertools
 import json
 import os
+import re
 import sys
 import threading
 from pathlib import Path
@@ -67,13 +71,87 @@ ROLES = {  # the first role is the default; the fairness audit uses "data-analys
                   "Requirements: a degree, a teaching qualification and several years of classroom experience.")},
 }
 
+# --- Blind screening -------------------------------------------------------
+# The identity signals the embedding model demonstrably reacts to, removed
+# before it sees the text. None of them is a qualification.
+
+CONTACT = re.compile(r"""[\w.+-]+@[\w.-]+\.\w+                  # email: usually spells the name out
+                       | (?:https?://|www\.)\S+                 # links, incl. profile URLs
+                       | \b(?:linkedin|github|twitter)\.com/\S+
+                       | \+?\d(?:[ ().\-]{0,2}\d){8,}           # phone numbers (>=10 digits)
+                      """, re.IGNORECASE | re.VERBOSE)
+HONORIFICS = re.compile(r"\b(?:mr|mrs|ms|miss|mx|sir|madam|ma'am)\b\.?", re.IGNORECASE)
+# One token for every gendered pronoun: mapping form by form ("her" -> "their" but
+# "him" -> "them") would leave the twin CVs textually different, and so still unequal.
+PRONOUNS = re.compile(r"\b(?:he|she|him|her|hers|his|himself|herself|"
+                      r"they|them|their|theirs|themselves)\b", re.IGNORECASE)
+GENDERED = {"female": "", "male": "", "husband": "spouse", "wife": "spouse",
+            "father": "parent", "mother": "parent", "son": "child", "daughter": "child",
+            "chairman": "chair", "chairwoman": "chair", "salesman": "salesperson",
+            "saleswoman": "salesperson", "waiter": "server", "waitress": "server",
+            "actress": "actor"}
+GENDERED_RE = re.compile(r"\b(" + "|".join(GENDERED) + r")\b", re.IGNORECASE)
+
+NAME_FIELD = re.compile(r"^[ \t]*name[ \t]*[:\-][ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
+NAME_HEAD = re.compile(r"((?:[A-Z][A-Za-z'’\-]*\.?[ \t]+){0,3}[A-Z][A-Za-z'’\-]*)")
+# Words that open a CV header but are never the candidate's name, so they are kept.
+HEADER_STOP = ({w.lower() for r in ROLES.values() for w in re.findall(r"[A-Za-z]+", r["title"])} |
+               {"curriculum", "vitae", "resume", "cv", "name", "candidate", "pronouns", "profile",
+                "summary", "objective", "about", "experience", "education", "skills", "contact",
+                "senior", "junior", "lead", "principal", "staff", "head", "director", "manager",
+                "specialist", "consultant", "engineer", "developer", "analyst", "scientist",
+                "nurse", "teacher", "accountant", "experienced", "professional", "qualified",
+                "skilled", "dedicated", "motivated", "results", "highly", "the"})
+
+
+def _name_tokens(text: str) -> list[str]:
+    """Best-effort guess at the candidate's own name: an explicit "Name:" field, or the
+    run of capitalised words opening the CV header, minus known role/section words."""
+    heads = NAME_FIELD.findall(text)[:1]
+    for line in [ln.strip() for ln in text.splitlines() if ln.strip()][:3]:
+        line = CONTACT.sub(" ", line).strip(" \t*#|-–—•")
+        if not re.search(r"[A-Za-z]", line):
+            continue  # a contact-only line, keep looking for the header
+        m = NAME_HEAD.match(line)
+        if m:
+            heads.append(m.group(1))
+        if any(w.lower() not in HEADER_STOP for w in re.findall(r"[A-Za-z']+", line)):
+            break  # the first header line with a real word is the only one that can hold a name
+    toks: list[str] = []
+    for head in heads:
+        for w in re.split(r"[^A-Za-z'’\-]+", head):
+            w = w.strip("'’-")
+            if len(w) > 2 and w.lower() not in HEADER_STOP and w.lower() not in [t.lower() for t in toks]:
+                toks.append(w)
+    return toks[:4]
+
+
+def deidentify(cv_text: str) -> str:
+    """Strip identity, keep qualifications: the candidate's name wherever it recurs,
+    contact details that spell the name out, honorifics, gendered pronouns and nouns.
+    Applied to every CV the model scores and to the calibration pool, so two CVs that
+    differ only in name or pronouns become the same text and score identically."""
+    text = CONTACT.sub(" ", cv_text)
+    for tok in _name_tokens(cv_text):
+        text = re.sub(rf"\b{re.escape(tok)}(?:'s|’s)?\b", " ", text, flags=re.IGNORECASE)
+    text = HONORIFICS.sub(" ", text)
+    text = PRONOUNS.sub("they", text)
+    text = GENDERED_RE.sub(lambda m: GENDERED[m.group(1).lower()], text)
+    text = re.sub(r"[ \t]+", " ", text)
+    text = re.sub(r"\n\s*\n+", "\n", text).strip()
+    return text or cv_text.strip()  # a CV that was nothing but identity: score it as-is
+
+
+SCORER = "deidentified-cv-v1"  # what the model sees; bump to invalidate cached cutoffs
+
 app = Flask(__name__)
 harden(app)
 _ids = itertools.count(1)
 DRAFTS: BoundedStore = BoundedStore(300)
 # Model files live inside the project so a host can download them at build time.
 CACHE_DIR = os.environ.get("FASTEMBED_CACHE", str(ROOT / ".fastembed_cache"))
-CUTOFF_FILE = ROOT / "data" / "quickmatch_cutoff.json"
+CUTOFF_FILE = ROOT / "data" / "quickmatch_cutoff.json"   # shipped cache, refreshed by --calibrate
+CUTOFF_CACHE = ROOT / ".quickmatch_cutoff.json"          # local cache when the scorer has changed
 
 _lock = threading.Lock()
 _embedder: TextEmbedding | None = None
@@ -101,28 +179,37 @@ def jd_vec(role: str) -> np.ndarray:
 
 
 def similarity(cv_text: str, role: str) -> float:
-    return float(embed([cv_text])[0] @ jd_vec(role))
+    return float(embed([deidentify(cv_text)])[0] @ jd_vec(role))
 
 
 def calibrate(write: bool = False) -> dict[str, float]:
     """Shortlist cutoff per role = median similarity of an independent calibration pool
-    (data/calibration.json: CVs never used in any audit) against that role's job description,
-    so about half of the pool passes for every role. Cached in data/quickmatch_cutoff.json;
-    `python targets/quickmatch/app.py --calibrate` refreshes it."""
+    (data/calibration.json: CVs never used in any audit), de-identified exactly like a
+    scored CV, against that role's job description, so about half of the pool passes for
+    every role. Cached cutoffs are keyed by SCORER: a cutoff computed for a different
+    scorer is recomputed rather than reused, so the cutoff always matches what the model
+    sees. `python targets/quickmatch/app.py --calibrate` refreshes the shipped cache."""
     if os.environ.get("QUICKMATCH_CUTOFF"):
         return {k: float(os.environ["QUICKMATCH_CUTOFF"]) for k in ROLES}
-    if CUTOFF_FILE.exists() and not write:
-        data = json.loads(CUTOFF_FILE.read_text())
-        cuts = data.get("cutoffs") or {"data-analyst": data["cutoff"]}
-        return {k: float(cuts.get(k, cuts.get("data-analyst", 0.5))) for k in ROLES}
+    if not write:
+        for path in (CUTOFF_CACHE, CUTOFF_FILE):
+            if path.exists():
+                data = json.loads(path.read_text())
+                if data.get("scorer") == SCORER:
+                    cuts = data.get("cutoffs") or {"data-analyst": data["cutoff"]}
+                    return {k: float(cuts.get(k, cuts.get("data-analyst", 0.5))) for k in ROLES}
     pool = ROOT / "data" / "calibration.json"
     if not pool.exists():
         return {k: 0.5 for k in ROLES}
-    vecs = embed(json.loads(pool.read_text()))
+    vecs = embed([deidentify(cv) for cv in json.loads(pool.read_text())])
     cuts = {k: float(np.median(vecs @ jd_vec(k))) for k in ROLES}
-    CUTOFF_FILE.write_text(json.dumps({"cutoff": cuts["data-analyst"], "cutoffs": cuts, "model": MODEL_ID,
-                                       "pool": "data/calibration.json",
-                                       "method": "median similarity of the calibration pool, per role"}, indent=1))
+    try:
+        (CUTOFF_FILE if write else CUTOFF_CACHE).write_text(json.dumps(
+            {"cutoff": cuts["data-analyst"], "cutoffs": cuts, "model": MODEL_ID, "scorer": SCORER,
+             "pool": "data/calibration.json",
+             "method": "median similarity of the de-identified calibration pool, per role"}, indent=1))
+    except OSError:
+        pass  # a read-only checkout just recalibrates in memory at start-up
     return cuts
 
 
@@ -212,7 +299,8 @@ def favicon():
 
 @app.get("/healthz")
 def healthz():
-    return {"ok": True, "target": "quickmatch", "model": MODEL_ID, "cutoff": round(CUTOFF, 4)}
+    return {"ok": True, "target": "quickmatch", "model": MODEL_ID, "scorer": SCORER,
+            "cutoff": round(CUTOFF, 4)}
 
 
 if __name__ == "__main__":
```

## Round 2
- Gate: **VERDICT INCONCLUSIVE  target=quickmatch  model=sentence-transformers/all-MiniLM-L6-v2** (exit 2)
- Gate inconclusive; stopping so a human can look.

## Note added by hand: round 2 was re-run
The loop's round 2 Kane run ended INCONCLUSIVE: Kane pasted the first CV, clicked Continue, then
"AP produced no action for 3 consecutive steps" (6.5 credits, no values stored). The fixed wizard was
then walked in-process and worked (review 200, result shown; Geoffrey and Matthew both 0.186), so the
same gate was re-run unchanged: `python audit/gate.py --target quickmatch --candidates cand02`.

- Gate (re-run): **VERDICT PASS** (exit 0): all 8 names 0.186, Not recommended; Kane changed no settings.
- Free dry run of the fixed tool, all 10 candidates: PASS. Each candidate now gets one identical score
  for every name; scores still range 0.101 to 0.253 across candidates (not degenerate).
- Side effect, reported as is: the cutoff is recalibrated on the de-identified pool and came out
  stricter; 8/80 readings shortlisted after the fix vs 24/80 before (which were partly decided by name).
