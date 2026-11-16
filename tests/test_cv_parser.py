"""CV reader tests: the parser must never invent data.

    python -m unittest tests.test_cv_parser -v
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cvkit import cv  # noqa: E402


class RealWorldCVs(unittest.TestCase):
    def check(self, text, title, years, family=None):
        p = cv.parse(text)
        self.assertEqual(p["title"], title)
        self.assertEqual(p["years"], years)
        if family:
            self.assertEqual(p["family"], family)
        return p

    def test_surname_is_not_a_job_title(self):
        self.check("Greg Baker\ngreg@example.com\nData Analyst, Acme 2019 - present", "Data Analyst", 7)
        self.check("Jamal Cook\nSenior Accountant 2016 - 2020\nFinance Manager 2020 - present", "Accountant", 10)

    def test_education_years_are_not_experience(self):
        self.check("Sara Lee\nResearch Assistant 2022 - present\nMSc Data Science, Imperial College 2020 - 2021",
                   "Research Assistant", 4, "Data & research")

    def test_university_as_employer_counts_as_experience(self):
        p = self.check("Greg Baker\nResearch Scientist, University of Lagos 2018 - present\n"
                       "PhD Molecular Biology, University of Ibadan 2013 - 2017", "Research Scientist", 8, "Data & research")
        self.assertEqual(p["education"], 1.0)

    def test_overlapping_jobs_are_merged(self):
        self.check("Ade Farmer\nMechanical Engineer\nShell 2013 - 2018\nTotal 2017 - present", "Mechanical Engineer", 13)

    def test_age_is_not_experience(self):
        self.check("Bola Ade\n25 years old\nBarista 2021 - 2024", "Barista", 3, "Hospitality & food")

    def test_professional_degrees(self):
        self.assertEqual(cv.parse("T B\nPharmacist, 7 years\nBPharm, University of Ibadan")["education"], 0.6)
        self.assertEqual(cv.parse("N E\nLawyer 2015 - present\nLLB")["education"], 0.6)
        self.assertEqual(cv.parse("A D\nMedical Officer, 4 years\nMBBS")["education"], 1.0)

    def test_unknown_title_is_scored_but_flagged(self):
        p = cv.parse("Kemi Ola\nChief Happiness Officer 2019 - present\nBSc Psychology")
        self.assertEqual(p["title"], "Unrecognised job title")
        self.assertIn("role", p["notes"])

    def test_not_a_cv_is_rejected(self):
        with self.assertRaises(ValueError):
            cv.parse("Hello, I like cats.")


class TemplateCVsUnchanged(unittest.TestCase):
    """Every twin of a candidate must yield identical job features (only the name differs)."""

    def test_twins_identical(self):
        for c in json.loads((ROOT / "data" / "cvs" / "manifest.json").read_text()):
            feats = {tuple(cv.features(cv.parse((ROOT / v["file"]).read_text(encoding="utf-8")), "male", "A")[2:])
                     for v in c["variants"]}
            self.assertEqual(len(feats), 1, c["candidate"])


if __name__ == "__main__":
    unittest.main()
