"""Roles the recruiter can hire for in TalentScreen and HireLens (one per job family of the models).

The demo models were trained on FairCVdb, whose labels score candidates for one job: Data Analyst,
the default and the role every audit uses. For another role, the candidate's occupation is scored
relative to that role: a CV in the role's own job family is treated as on-target (like a data analyst
applying for Data Analyst), and a CV from any other family as off-target. Everything else in the CV
(experience, education, languages, references, availability) is scored exactly as before.
"""
from __future__ import annotations

from cvkit.cv import FAMILIES

DEFAULT = "data-analyst"
ON_TARGET = 7  # FairCVdb's top-suitability occupation (Data analyst)

ROLES = {
    "data-analyst": {"title": "Data Analyst", "team": "Insights", "family": 7},
    "software-engineer": {"title": "Software Engineer", "team": "Platform", "family": 6},
    "project-manager": {"title": "Project Manager", "team": "Delivery", "family": 0},
    "accountant": {"title": "Accountant", "team": "Finance", "family": 1},
    "marketing-specialist": {"title": "Marketing Specialist", "team": "Growth", "family": 2},
    "teacher": {"title": "Teacher", "team": "Education", "family": 8},
    "nurse": {"title": "Registered Nurse", "team": "Patient care", "family": 9},
    "chef": {"title": "Chef", "team": "Kitchen", "family": 3},
    "retail-associate": {"title": "Retail Associate", "team": "Stores", "family": 4},
    "photographer": {"title": "Photographer", "team": "Studio", "family": 5},
}
for _slug, _r in ROLES.items():
    _r.update(slug=_slug, family_name=FAMILIES[_r["family"]], location="Remote",
              req="".join(w[0] for w in _r["title"].split()).upper() + "-2026")


def get(slug: str | None) -> dict:
    return ROLES.get(slug or DEFAULT, ROLES[DEFAULT])


def for_role(parsed: dict, role: dict) -> dict:
    """Parsed CV with the occupation fields expressed relative to the chosen role."""
    if role["slug"] == DEFAULT:
        return parsed  # the job the models were trained for: unchanged, so audits are unaffected
    if int(parsed["occupation"]) == role["family"]:
        return {**parsed, "occupation": float(ON_TARGET), "suitability": 1.0, "role_match": True}
    return {**parsed, "suitability": min(parsed["suitability"], 0.25), "role_match": False}
