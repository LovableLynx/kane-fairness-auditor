"""QuickMatch -- target C. A three-step wizard (role -> CV -> review) that ranks a CV by
semantic similarity to the job description using an off-the-shelf open-source
embedding model (sentence-transformers/all-MiniLM-L6-v2 via fastembed).

We did not train this model and we do not know how it treats names: it is the
genuine black box in the demo. Because an independent twin audit showed that it
scores the same CV differently when only the name or the pronouns change, the CV
is de-identified before it is embedded (see `deidentify`): the model never sees
the name, the name-bearing contact details, honorifics or gendered pronouns.
Everything that is a qualification reaches the model untouched.

    python targets/quickmatch/app.py     # port 5103
"""
from __future__ import annotations

import itertools
import json
import os
import re
import sys
import threading
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding
from flask import Flask, abort, redirect, render_template, request, url_for

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from shared.hardening import BoundedStore, harden  # noqa: E402
from shared.samples import samples  # noqa: E402
from cvkit.extract import SUPPORTED, UnsupportedFile, to_text  # noqa: E402

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

def _jd(title: str, body: str) -> str:
    return (f"{title}. {body} Strong communication skills and the ability to work across teams are important. "
            "Additional languages are a plus. A recommendation from a previous employer is welcome.")


ROLES = {  # the first role is the default; the fairness audit uses "data-analyst"
    "data-analyst": {"title": "Data Analyst", "emoji": "📊", "team": "Insights",
        "jd": ("Data Analyst. We are hiring a data analyst to turn business data into insight. "
               "You will build reports and dashboards, analyse trends, and present findings to stakeholders. "
               "Requirements: a degree in a quantitative field, several years of professional experience in "
               "analytics or a related role, strong communication skills, and the ability to work across teams. "
               "Additional languages are a plus. A recommendation from a previous employer is welcome.")},
    "software-engineer": {"title": "Software Engineer", "emoji": "💻", "team": "Platform",
        "jd": _jd("Software Engineer", "We are hiring a software engineer to build and maintain reliable web services. "
                  "You will write well-tested Python and SQL, review code and improve our delivery pipeline. "
                  "Requirements: a degree in computer science or a related field and several years of professional engineering experience.")},
    "project-manager": {"title": "Project Manager", "emoji": "🗂️", "team": "Delivery",
        "jd": _jd("Project Manager", "We are hiring a project manager to lead cross-functional delivery of business projects. "
                  "You will plan work, manage risks and budgets, and run stakeholder reviews. "
                  "Requirements: a degree and several years of project management experience.")},
    "accountant": {"title": "Accountant", "emoji": "🧾", "team": "Finance",
        "jd": _jd("Accountant", "We are hiring an accountant to prepare management accounts and support audits. "
                  "You will reconcile ledgers, close the books each month and improve finance processes. "
                  "Requirements: a degree in accounting or finance and several years of professional experience.")},
    "marketing-specialist": {"title": "Marketing Specialist", "emoji": "📣", "team": "Growth",
        "jd": _jd("Marketing Specialist", "We are hiring a marketing specialist to plan and run multi-channel campaigns. "
                  "You will analyse campaign performance, manage content and run experiments. "
                  "Requirements: a degree and several years of marketing experience.")},
    "nurse": {"title": "Registered Nurse", "emoji": "🩺", "team": "Patient care",
        "jd": _jd("Registered Nurse", "We are hiring a nurse to deliver safe, compassionate patient care on a busy ward. "
                  "You will keep accurate clinical records, support audits and mentor students. "
                  "Requirements: a nursing qualification and several years of clinical experience.")},
    "teacher": {"title": "Teacher", "emoji": "📚", "team": "Education",
        "jd": _jd("Teacher", "We are hiring a teacher to plan and deliver engaging lessons and track student progress. "
                  "You will use assessment data, lead curriculum work and communicate with parents. "
                  "Requirements: a degree, a teaching qualification and several years of classroom experience.")},
}

# --- Blind screening -------------------------------------------------------
# The identity signals the embedding model demonstrably reacts to, removed
# before it sees the text. None of them is a qualification.

CONTACT = re.compile(r"""[\w.+-]+@[\w.-]+\.\w+                  # email: usually spells the name out
                       | (?:https?://|www\.)\S+                 # links, incl. profile URLs
                       | \b(?:linkedin|github|twitter)\.com/\S+
                       | \+?\d(?:[ ().\-]{0,2}\d){8,}           # phone numbers (>=10 digits)
                      """, re.IGNORECASE | re.VERBOSE)
HONORIFICS = re.compile(r"\b(?:mr|mrs|ms|miss|mx|sir|madam|ma'am)\b\.?", re.IGNORECASE)
# One token for every gendered pronoun: mapping form by form ("her" -> "their" but
# "him" -> "them") would leave the twin CVs textually different, and so still unequal.
PRONOUNS = re.compile(r"\b(?:he|she|him|her|hers|his|himself|herself|"
                      r"they|them|their|theirs|themselves)\b", re.IGNORECASE)
GENDERED = {"female": "", "male": "", "husband": "spouse", "wife": "spouse",
            "father": "parent", "mother": "parent", "son": "child", "daughter": "child",
            "chairman": "chair", "chairwoman": "chair", "salesman": "salesperson",
            "saleswoman": "salesperson", "waiter": "server", "waitress": "server",
            "actress": "actor"}
GENDERED_RE = re.compile(r"\b(" + "|".join(GENDERED) + r")\b", re.IGNORECASE)

NAME_FIELD = re.compile(r"^[ \t]*name[ \t]*[:\-][ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
NAME_HEAD = re.compile(r"((?:[A-Z][A-Za-z'’\-]*\.?[ \t]+){0,3}[A-Z][A-Za-z'’\-]*)")
# Words that open a CV header but are never the candidate's name, so they are kept.
HEADER_STOP = ({w.lower() for r in ROLES.values() for w in re.findall(r"[A-Za-z]+", r["title"])} |
               {"curriculum", "vitae", "resume", "cv", "name", "candidate", "pronouns", "profile",
                "summary", "objective", "about", "experience", "education", "skills", "contact",
                "senior", "junior", "lead", "principal", "staff", "head", "director", "manager",
                "specialist", "consultant", "engineer", "developer", "analyst", "scientist",
                "nurse", "teacher", "accountant", "experienced", "professional", "qualified",
                "skilled", "dedicated", "motivated", "results", "highly", "the"})


def _name_tokens(text: str) -> list[str]:
    """Best-effort guess at the candidate's own name: an explicit "Name:" field, or the
    run of capitalised words opening the CV header, minus known role/section words."""
    heads = NAME_FIELD.findall(text)[:1]
    for line in [ln.strip() for ln in text.splitlines() if ln.strip()][:3]:
        line = CONTACT.sub(" ", line).strip(" \t*#|-–—•")
        if not re.search(r"[A-Za-z]", line):
            continue  # a contact-only line, keep looking for the header
        m = NAME_HEAD.match(line)
        if m:
            heads.append(m.group(1))
        if any(w.lower() not in HEADER_STOP for w in re.findall(r"[A-Za-z']+", line)):
            break  # the first header line with a real word is the only one that can hold a name
    toks: list[str] = []
    for head in heads:
        for w in re.split(r"[^A-Za-z'’\-]+", head):
            w = w.strip("'’-")
            if len(w) > 2 and w.lower() not in HEADER_STOP and w.lower() not in [t.lower() for t in toks]:
                toks.append(w)
    return toks[:4]


def deidentify(cv_text: str) -> str:
    """Strip identity, keep qualifications: the candidate's name wherever it recurs,
    contact details that spell the name out, honorifics, gendered pronouns and nouns.
    Applied to every CV the model scores and to the calibration pool, so two CVs that
    differ only in name or pronouns become the same text and score identically."""
    text = CONTACT.sub(" ", cv_text)
    for tok in _name_tokens(cv_text):
        text = re.sub(rf"\b{re.escape(tok)}(?:'s|’s)?\b", " ", text, flags=re.IGNORECASE)
    text = HONORIFICS.sub(" ", text)
    text = PRONOUNS.sub("they", text)
    text = GENDERED_RE.sub(lambda m: GENDERED[m.group(1).lower()], text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return text or cv_text.strip()  # a CV that was nothing but identity: score it as-is


SCORER = "deidentified-cv-v1"  # what the model sees; bump to invalidate cached cutoffs

app = Flask(__name__)
harden(app)
_ids = itertools.count(1)
DRAFTS: BoundedStore = BoundedStore(300)
# Model files live inside the project so a host can download them at build time.
CACHE_DIR = os.environ.get("FASTEMBED_CACHE", str(ROOT / ".fastembed_cache"))
CUTOFF_FILE = ROOT / "data" / "quickmatch_cutoff.json"   # shipped cache, refreshed by --calibrate
CUTOFF_CACHE = ROOT / ".quickmatch_cutoff.json"          # local cache when the scorer has changed

_lock = threading.Lock()
_embedder: TextEmbedding | None = None
_jd_vec: dict[str, np.ndarray] = {}


def embedder() -> TextEmbedding:
    """Load the model on first use, so the web server starts fast on small hosts."""
    global _embedder
    with _lock:
        if _embedder is None:
            _embedder = TextEmbedding(MODEL_ID, cache_dir=CACHE_DIR, threads=1)
    return _embedder


def embed(texts: list[str]) -> np.ndarray:
    v = np.array(list(embedder().embed(texts)))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def jd_vec(role: str) -> np.ndarray:
    if role not in _jd_vec:
        _jd_vec[role] = embed([ROLES[role]["jd"]])[0]
    return _jd_vec[role]


def similarity(cv_text: str, role: str) -> float:
    return float(embed([deidentify(cv_text)])[0] @ jd_vec(role))


def calibrate(write: bool = False) -> dict[str, float]:
    """Shortlist cutoff per role = median similarity of an independent calibration pool
    (data/calibration.json: CVs never used in any audit), de-identified exactly like a
    scored CV, against that role's job description, so about half of the pool passes for
    every role. Cached cutoffs are keyed by SCORER: a cutoff computed for a different
    scorer is recomputed rather than reused, so the cutoff always matches what the model
    sees. `python targets/quickmatch/app.py --calibrate` refreshes the shipped cache."""
    if os.environ.get("QUICKMATCH_CUTOFF"):
        return {k: float(os.environ["QUICKMATCH_CUTOFF"]) for k in ROLES}
    if not write:
        for path in (CUTOFF_CACHE, CUTOFF_FILE):
            if path.exists():
                data = json.loads(path.read_text())
                if data.get("scorer") == SCORER:
                    cuts = data.get("cutoffs") or {"data-analyst": data["cutoff"]}
                    return {k: float(cuts.get(k, cuts.get("data-analyst", 0.5))) for k in ROLES}
    pool = ROOT / "data" / "calibration.json"
    if not pool.exists():
        return {k: 0.5 for k in ROLES}
    vecs = embed([deidentify(cv) for cv in json.loads(pool.read_text())])
    cuts = {k: float(np.median(vecs @ jd_vec(k))) for k in ROLES}
    try:
        (CUTOFF_FILE if write else CUTOFF_CACHE).write_text(json.dumps(
            {"cutoff": cuts["data-analyst"], "cutoffs": cuts, "model": MODEL_ID, "scorer": SCORER,
             "pool": "data/calibration.json",
             "method": "median similarity of the de-identified calibration pool, per role"}, indent=1))
    except OSError:
        pass  # a read-only checkout just recalibrates in memory at start-up
    return cuts


CUTOFFS = calibrate()
CUTOFF = CUTOFFS["data-analyst"]  # used by the audit's dev endpoint


@app.get("/")
def step_role():
    return render_template("step_role.html", roles=ROLES, step=1)


@app.post("/start")
def start():
    role = request.form.get("role")
    if role not in ROLES:
        abort(400)
    d = {"id": next(_ids), "role": role, "cv": ""}
    DRAFTS[d["id"]] = d
    return redirect(url_for("step_cv", did=d["id"]))


@app.route("/match/<int:did>/candidate", methods=["GET", "POST"])
def step_cv(did: int):
    d = DRAFTS.get(did) or abort(404)
    if request.method == "POST":
        text, error = (request.form.get("candidate_cv") or ""), "empty"
        f = request.files.get("cv_file")
        if f and f.filename:
            try:
                text = to_text(f.filename, f.read())
            except UnsupportedFile as e:
                text, error = "", ("filetype" if "upload a" in str(e) else "unreadable")
        d["cv"] = text.strip()[:20000]
        if d["cv"]:
            return redirect(url_for("step_review", did=did))
        return render_template("step_cv.html", d=d, role=ROLES[d["role"]], step=2, samples=samples(),
                               error=error, accept=",".join(SUPPORTED))
    return render_template("step_cv.html", d=d, role=ROLES[d["role"]], step=2, samples=samples(),
                           error=None, accept=",".join(SUPPORTED))


@app.get("/match/<int:did>/review")
def step_review(did: int):
    d = DRAFTS.get(did) or abort(404)
    if "similarity" in d:
        return redirect(url_for("result", did=did))
    if not d["cv"]:
        return redirect(url_for("step_cv", did=did))
    return render_template("step_review.html", d=d, role=ROLES[d["role"]], step=3)


@app.post("/match/<int:did>/run")
def run_match(did: int):
    d = DRAFTS.get(did) or abort(404)
    if "similarity" in d:
        return redirect(url_for("result", did=did))
    if not d["cv"]:
        return redirect(url_for("step_cv", did=did))
    d["similarity"] = similarity(d["cv"], d["role"])
    d["recommended"] = d["similarity"] >= CUTOFFS[d["role"]]
    d["cv"] = ""  # data minimisation: the CV text is not kept once it has been scored
    return redirect(url_for("result", did=did))


@app.get("/match/<int:did>")
def result(did: int):
    d = DRAFTS.get(did) or abort(404)
    if "similarity" not in d:
        return redirect(url_for("step_review", did=did))
    return render_template("result.html", d=d, role=ROLES[d["role"]], cutoff=CUTOFFS[d["role"]], step=4)


@app.post("/api/match")
def api_match():
    """Dev-only shortcut used by the auditor's --direct dry runs."""
    cv_text = request.form.get("candidate_cv", "")
    s = similarity(cv_text, "data-analyst")
    return (f"<p>Similarity score: {s:.3f}</p>"
            f"<p>Verdict: {'Recommended for interview' if s >= CUTOFF else 'Not recommended'}</p>")


@app.get("/favicon.ico")
def favicon():
    return ("", 204)


@app.get("/healthz")
def healthz():
    return {"ok": True, "target": "quickmatch", "model": MODEL_ID, "scorer": SCORER,
            "cutoff": round(CUTOFF, 4)}


if __name__ == "__main__":
    if "--calibrate" in sys.argv:
        print(f"cutoffs = {calibrate(write=True)} -> {CUTOFF_FILE}")
    elif "--download" in sys.argv:
        embedder()
        print(f"model cached in {CACHE_DIR}")
    else:
        app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5103)))
