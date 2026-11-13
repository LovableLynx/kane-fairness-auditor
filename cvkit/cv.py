"""Render FairCVdb profiles as plain-text CVs, build demographic twins, and parse CVs back.

A profile here is the 11 structured FairCVdb columns:
    0 ethnicity group, 1 gender, 2 occupation code, 3 suitability, 4 education,
    5 experience, 6 recommendation, 7 availability, 8-10 language proficiency.

Occupation titles are a synthetic mapping of FairCVdb's occupation codes (which ship
without labels) chosen to respect the dataset's code -> suitability sectors.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import names as N

OCCUPATIONS = {  # code -> (title, suitability as in FairCVdb)
    0: ("Project manager", 0.75), 1: ("Accountant", 0.75), 2: ("Marketing specialist", 0.75),
    3: ("Chef", 0.25), 4: ("Retail associate", 0.25), 5: ("Photographer", 0.25),
    6: ("Software engineer", 1.0), 7: ("Data analyst", 1.0),
    8: ("Teacher", 0.5), 9: ("Nurse", 0.5),
}
EDUCATION = {0.2: "High school diploma", 0.4: "Associate degree", 0.6: "Bachelor's degree",
             0.8: "Master's degree", 1.0: "Doctorate (PhD)"}
AVAILABILITY = {1.0: "immediately", 0.8: "within 2 weeks", 0.6: "within 1 month",
                0.4: "within 2 months", 0.2: "within 3 months"}
LEVELS = {0.0: None, 0.2: "A1", 0.4: "A2", 0.6: "B1", 0.8: "B2", 1.0: "C2"}
LANGUAGES = ["English", "Spanish", "French"]

GENDER_CODE = {"male": 0.0, "female": 1.0}
GROUP_CODE = {"A": 0.0, "B": 1.0, "C": 2.0}


def _r(x: float) -> float:
    return round(float(x), 1) if x not in (0.25, 0.75) else float(x)


@dataclass(frozen=True)
class Identity:
    gender: str  # male | female
    group: str   # A | C
    first: str
    last: str

    @property
    def label(self) -> str:
        return f"{self.gender}/{self.group}"


def identities_for(seed: int) -> list[Identity]:
    """Four twins: every (gender, group) combination, names picked deterministically by seed."""
    out = []
    for gender in ("male", "female"):
        for group in ("A", "C"):
            firsts, lasts = N.FIRST[(gender, group)], N.LAST[group]
            out.append(Identity(gender, group, firsts[seed % len(firsts)], lasts[seed % len(lasts)]))
    return out


def render(profile: list[float], who: Identity, cv_id: str) -> str:
    occ_title, _ = OCCUPATIONS[int(profile[2])]
    years = int(round(profile[5] * 10))
    p = N.PRONOUNS[who.gender]
    email = f"{who.first}.{who.last}".lower().replace("'", "") + "@example.com"
    langs = []
    for name, v in zip(LANGUAGES, profile[8:11]):
        lvl = LEVELS[_r(v)]
        if lvl:
            langs.append(f"- {name}: {lvl}")
    refs = ("Letter of recommendation from previous employer enclosed."
            if profile[6] >= 0.5 else "References available on request.")
    return "\n".join([
        f"{who.first} {who.last}",
        f"{email} | CV ref {cv_id}",
        "",
        "PROFILE",
        f"{who.first} is a {occ_title.lower()} with {years} years of professional experience. "
        f"{p['subj']} is available to start {AVAILABILITY[_r(profile[7])]}.",
        "",
        "CURRENT ROLE",
        occ_title,
        "",
        "EXPERIENCE",
        f"{years} years",
        "",
        "EDUCATION",
        EDUCATION[_r(profile[4])],
        "",
        "LANGUAGES",
        *(langs or ["- English: A1"]),
        "",
        "REFERENCES",
        refs,
        "",
    ])


# ---------------------------------------------------------------- parsing

def _section(text: str, name: str) -> str:
    m = re.search(rf"^{name}\s*\n(.*?)(?:\n\s*\n|\Z)", text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def parse(text: str) -> dict:
    """Extract job-relevant fields. Raises ValueError if the CV can't be read."""
    title = _section(text, "CURRENT ROLE").splitlines()[0].strip() if _section(text, "CURRENT ROLE") else ""
    occ = next((c for c, (t, _) in OCCUPATIONS.items() if t.lower() == title.lower()), None)
    if occ is None:
        raise ValueError(f"unrecognised role: {title!r}")
    m = re.search(r"(\d+)\s+years?", _section(text, "EXPERIENCE"))
    years = int(m.group(1)) if m else 0
    edu_txt = _section(text, "EDUCATION").lower()
    edu = next((v for v, t in EDUCATION.items() if t.lower() in edu_txt), 0.2)
    avail_m = re.search(r"available to start ([^.]+)\.", text, re.I)
    avail = next((v for v, t in AVAILABILITY.items() if avail_m and t == avail_m.group(1).strip().lower()), 0.2)
    langs = []
    lang_txt = _section(text, "LANGUAGES")
    for name in LANGUAGES:
        lm = re.search(rf"{name}\s*:\s*(A1|A2|B1|B2|C1|C2)", lang_txt, re.I)
        lvl = lm.group(1).upper() if lm else None
        if lvl == "C1":
            lvl = "C2"
        langs.append(next((v for v, t in LEVELS.items() if t == lvl), 0.0))
    rec = 1.0 if "recommendation" in _section(text, "REFERENCES").lower() else 0.0
    return {
        "occupation": float(occ), "suitability": OCCUPATIONS[occ][1], "education": edu,
        "experience": min(years, 10) / 10, "recommendation": rec, "availability": avail,
        "languages": langs, "title": OCCUPATIONS[occ][0], "years": years,
    }


def infer_identity(text: str) -> tuple[str, str]:
    """What a careless vendor does: guess gender and group from name and pronouns."""
    first_line = text.strip().splitlines()[0].split()
    first, last = first_line[0], first_line[-1]
    gender, group = None, None
    if first in N.FIRST_TO:
        gender, group = N.FIRST_TO[first]
    if re.search(r"\bShe\b", text):
        gender = "female"
    elif re.search(r"\bHe\b", text):
        gender = gender or "male"
    group = N.LAST_TO.get(last, group)
    return gender or "male", group or "B"


def features(parsed: dict, gender: str, group: str) -> list[float]:
    return [GROUP_CODE[group], GENDER_CODE[gender], parsed["occupation"], parsed["suitability"],
            parsed["education"], parsed["experience"], parsed["recommendation"],
            parsed["availability"], *parsed["languages"]]
