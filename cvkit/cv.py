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


def identities_for(seed: int, slot: int = 0) -> list[Identity]:
    """Four twins: every (gender, group) combination, names picked deterministically by seed.
    A different `slot` gives a different name from the SAME demographic cell (placebo twins)."""
    out = []
    for gender in ("male", "female"):
        for group in ("A", "C"):
            firsts, lasts = N.FIRST[(gender, group)], N.LAST[group]
            out.append(Identity(gender, group, firsts[(seed + 4 * slot) % len(firsts)],
                                lasts[(seed + 2 * slot) % len(lasts)]))
    return out


# Role-specific content for long CVs. Identical across twins; only identity changes.
ROLE_DETAIL = {
    "Project manager": (["Led cross-functional delivery of a CRM migration on time and 8% under budget",
                         "Ran weekly stakeholder reviews and maintained the programme risk register",
                         "Introduced a lightweight agile cadence across three delivery teams",
                         "Coached two junior coordinators who were later promoted"],
                        "Planning, risk management, budgeting, stakeholder communication, Jira, MS Project",
                        ["Rolled out a shared delivery dashboard used by 40 managers",
                         "Wrote the team's onboarding guide for new project staff"]),
    "Accountant": (["Prepared monthly management accounts and variance commentary",
                    "Reconciled ledgers across four subsidiaries and closed the books in five days",
                    "Supported external audit with schedules and evidence packs",
                    "Automated recurring journals with spreadsheet macros"],
                   "Financial reporting, reconciliations, Excel, SAP, IFRS, forecasting",
                   ["Built a cash-flow forecast model adopted by the finance team",
                    "Cut month-end close time by two days through process changes"]),
    "Marketing specialist": (["Planned and ran multi-channel campaigns for three product lines",
                              "Analysed campaign performance and reported weekly on conversion",
                              "Managed a content calendar and a small freelance budget",
                              "Ran A/B tests on landing pages and email subject lines"],
                             "Campaign analytics, Google Analytics, CRM, copywriting, A/B testing, SQL basics",
                             ["Launched a referral campaign that grew sign-ups by 12%",
                              "Built a reporting template for campaign ROI"]),
    "Chef": (["Ran a busy service section and supervised a team of four", "Designed seasonal menus within cost targets",
              "Maintained food-safety records and passed every inspection", "Tracked stock and reduced waste week on week"],
             "Menu costing, stock control, team leadership, food safety, scheduling",
             ["Created a waste-tracking sheet that cut food waste by 15%", "Trained new starters on kitchen procedures"]),
    "Retail associate": (["Served customers on the shop floor and at the till", "Handled stock deliveries and weekly counts",
                          "Resolved customer complaints and processed returns", "Kept visual displays up to standard"],
                         "Customer service, stock counts, point-of-sale systems, merchandising",
                         ["Tracked best-selling lines in a weekly spreadsheet", "Helped set up a new click-and-collect process"]),
    "Photographer": (["Shot and edited commercial and event photography for clients", "Managed bookings, quotes and invoices",
                      "Delivered edited galleries to tight deadlines", "Built a client base through referrals"],
                     "Photography, Lightroom, Photoshop, client management, scheduling",
                     ["Organised a portfolio exhibition", "Built a simple booking tracker in a spreadsheet"]),
    "Software engineer": (["Built and maintained data-heavy web services in Python and SQL",
                           "Wrote automated tests and improved CI pipeline reliability",
                           "Partnered with analysts to expose reporting data through APIs",
                           "Reviewed code and mentored a junior developer"],
                          "Python, SQL, REST APIs, Git, testing, cloud services, data modelling",
                          ["Rebuilt a reporting pipeline, cutting runtime from hours to minutes",
                           "Open-sourced an internal data-validation library"]),
    "Data analyst": (["Built dashboards tracking sales and retention for senior leadership",
                      "Wrote SQL to clean and join data from five source systems",
                      "Analysed trends and presented findings to stakeholders monthly",
                      "Defined KPI definitions with finance and operations"],
                     "SQL, Python, Excel, Power BI, Tableau, statistics, data visualisation",
                     ["Churn analysis that informed a retention campaign", "Automated a weekly KPI report"]),
    "Teacher": (["Planned and taught lessons to classes of thirty students", "Tracked student progress with assessment data",
                 "Led a subject working group on curriculum changes", "Communicated regularly with parents"],
                "Lesson planning, assessment, data tracking, presentation, mentoring",
                ["Built a spreadsheet to track class attainment over the year", "Ran an after-school study club"]),
    "Nurse": (["Delivered patient care on a busy medical ward", "Kept accurate clinical records and handovers",
               "Supported audits of ward safety indicators", "Mentored student nurses on placement"],
              "Patient care, clinical documentation, audit, teamwork, communication",
              ["Contributed to a ward audit that reduced medication errors", "Created a handover checklist adopted by the ward"]),
}


def render(profile: list[float], who: Identity, cv_id: str, long: bool = False) -> str:
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
    extra: list[str] = []
    if long:
        bullets, skills, projects = ROLE_DETAIL[occ_title]
        jobs = max(1, min(3, (years + 3) // 4)) if years else 0
        history = []
        for j in range(jobs):
            span = years // jobs if jobs else 0
            history.append(f"{occ_title}, {['Northbridge Ltd', 'Harbour & Co', 'Clearview Group'][j]} ({span} years)")
            history += [f"- {b}" for b in bullets]
            history.append("- Worked closely with colleagues across departments to agree priorities, "
                           "share progress and hand over work cleanly at the end of each project phase")
        extra = [
            "PROFESSIONAL SUMMARY",
            f"Experienced {occ_title.lower()} who enjoys solving practical problems with careful analysis and "
            "clear communication. Known for reliable delivery, attention to detail and a calm approach under "
            "pressure. Comfortable working independently or as part of a team, and keen to keep learning new "
            "tools and methods. Looking for a role where structured thinking and good judgement help the "
            "organisation make better decisions.", "",
            "WORK HISTORY", *(history or ["- Seeking first professional role"]), "",
            "KEY SKILLS", skills, "",
            "SELECTED PROJECTS", *[f"- {p}" for p in projects], "",
            "TRAINING AND CERTIFICATIONS",
            "- Workplace health and safety (annual refresher)",
            "- Data protection and information security awareness",
            "- Effective presentations and stakeholder communication workshop", "",
            "ADDITIONAL INFORMATION",
            "Full driving licence. Comfortable working remotely or on site. Volunteers with a local community "
            "group, helping organise events and keep simple records. Interests include reading, running and "
            "learning new spreadsheet and reporting techniques.", "",
        ]
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
        *extra,
        "REFERENCES",
        refs,
        "",
    ])


# ---------------------------------------------------------------- parsing

def _section(text: str, name: str) -> str:
    m = re.search(rf"^{name}\s*\n(.*?)(?:\n\s*\n|\Z)", text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


ROLE_SYNONYMS = {  # occupation code -> phrases that identify it in a free-form CV
    0: ["project manager", "programme manager", "program manager", "delivery manager", "scrum master"],
    1: ["accountant", "bookkeeper", "finance officer", "accounts officer"],
    2: ["marketing specialist", "marketing manager", "marketing executive", "brand manager", "content strategist"],
    3: ["sous chef", "head chef", "chef", "cook"],
    4: ["retail associate", "sales associate", "shop assistant", "cashier", "store assistant"],
    5: ["photographer", "videographer"],
    6: ["software engineer", "software developer", "web developer", "backend developer", "frontend developer",
        "full stack developer", "full-stack developer", "programmer", "devops engineer"],
    7: ["data analyst", "business analyst", "data scientist", "bi analyst", "analytics analyst"],
    8: ["teacher", "lecturer", "tutor", "instructor"],
    9: ["registered nurse", "nurse", "midwife"],
}
EDU_KEYWORDS = [  # checked from highest level down
    (1.0, r"\b(ph\.?d|doctorate|doctor of)\b"),
    (0.8, r"\b(master'?s|msc|m\.sc|mba|ma|meng|mphil)\b"),
    (0.6, r"\b(bachelor'?s|bsc|b\.sc|ba|beng|b\.eng|undergraduate degree|honours degree)\b"),
    (0.4, r"\b(associate degree|diploma|hnd|ond|foundation degree)\b"),
    (0.2, r"\b(high school|secondary school|waec|gcse|a-levels?)\b"),
]
LANG_LEVEL_WORDS = [
    (1.0, r"native|mother tongue|fluent|bilingual|c2|c1"),
    (0.8, r"professional|advanced|proficient|b2"),
    (0.6, r"intermediate|conversational|b1"),
    (0.4, r"basic|elementary|a2"),
    (0.2, r"beginner|a1"),
]


def _find_role(text: str) -> int | None:
    low = text.lower()
    hits = [(low.find(p), code) for code, phrases in ROLE_SYNONYMS.items() for p in phrases if p in low]
    return min(hits)[1] if hits else None


def _years_freeform(text: str) -> int | None:
    stated = [int(n) for n in re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)\b", text, re.I) if int(n) <= 45]
    if stated:
        return max(stated)
    total = 0
    for a, b in re.findall(r"((?:19|20)\d{2})\s*(?:-|–|—|to)\s*((?:19|20)\d{2}|present|current|now)", text, re.I):
        end = 2026 if not b[:2].isdigit() else int(b)
        total += max(0, end - int(a))
    return min(total, 45) if total else None


def parse(text: str) -> dict:
    """Extract job-relevant fields from a CV.

    Uses the section layout of our generated CVs when present and falls back to keyword
    heuristics for free-form CVs. Anything estimated is listed in `notes`.
    Raises ValueError (with a recruiter-friendly message) if no supported role is found."""
    notes: list[str] = []
    title = _section(text, "CURRENT ROLE").splitlines()[0].strip() if _section(text, "CURRENT ROLE") else ""
    occ = next((c for c, (t, _) in OCCUPATIONS.items() if t.lower() == title.lower()), None)
    if occ is None:
        occ = _find_role(title) if title else None
    if occ is None:
        occ = _find_role(text)
        if occ is not None:
            notes.append("role")
    if occ is None:
        raise ValueError("we couldn't find a supported job title. Supported roles: "
                         + ", ".join(t for t, _ in OCCUPATIONS.values()))

    m = re.search(r"(\d+)\s+years?", _section(text, "EXPERIENCE"))
    if m:
        years = int(m.group(1))
    else:
        years = _years_freeform(text)
        notes.append("experience")
        years = years or 0

    edu_txt = _section(text, "EDUCATION").lower()
    edu = next((v for v, t in EDUCATION.items() if t.lower() in edu_txt), None)
    if edu is None:
        edu = next((v for v, pat in EDU_KEYWORDS if re.search(pat, text, re.I)), 0.2)
        notes.append("education")

    avail_m = re.search(r"available to start ([^.]+)\.", text, re.I)
    avail = next((v for v, t in AVAILABILITY.items() if avail_m and t == avail_m.group(1).strip().lower()), None)
    if avail is None:
        if re.search(r"\bimmediate(ly)?\b", text, re.I):
            avail = 1.0
        elif m2 := re.search(r"(\d+)\s*(week|month)s?'?\s*notice", text, re.I):
            n, unit = int(m2.group(1)), m2.group(2).lower()
            avail = 0.8 if unit == "week" and n <= 2 else 0.6 if (unit == "week" or n <= 1) else 0.4 if n <= 2 else 0.2
        else:
            avail = 0.6
        notes.append("availability")

    langs = []
    lang_txt = _section(text, "LANGUAGES")
    for name in LANGUAGES:
        lm = re.search(rf"{name}\s*:\s*(A1|A2|B1|B2|C1|C2)", lang_txt, re.I)
        if lm:
            lvl = "C2" if lm.group(1).upper() == "C1" else lm.group(1).upper()
            langs.append(next((v for v, t in LEVELS.items() if t == lvl), 0.0))
            continue
        if lang_txt and not re.search(name, text, re.I):
            langs.append(0.0)
            continue
        near = re.search(rf"{name}[^\n]{{0,30}}", text, re.I)
        if near:
            langs.append(next((v for v, pat in LANG_LEVEL_WORDS if re.search(pat, near.group(0), re.I)), 0.6))
        else:
            langs.append(0.8 if name == "English" else 0.0)  # a CV written in English implies working English
        if not lang_txt:
            notes.append(f"language:{name}")

    refs = _section(text, "REFERENCES").lower()
    rec = 1.0 if ("recommendation" in refs if refs else
                  re.search(r"letter of recommendation|recommendation letter", text, re.I)) else 0.0
    if not refs:
        notes.append("recommendation")
    return {
        "occupation": float(occ), "suitability": OCCUPATIONS[occ][1], "education": edu,
        "experience": min(years, 10) / 10, "recommendation": rec, "availability": avail,
        "languages": langs, "title": OCCUPATIONS[occ][0], "years": years,
        "notes": sorted({n.split(":")[0] for n in notes}),
    }


def infer_identity(text: str) -> tuple[str, str]:
    """What a careless vendor does: guess gender and group from name and pronouns."""
    first_line = (text.strip().splitlines() or ["?"])[0].split() or ["?"]
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
