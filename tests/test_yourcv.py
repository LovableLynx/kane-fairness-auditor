"""Twin-your-CV checks: twins differ only by name, email and pronouns; scores are the tools' own; nothing is kept.

    python -m unittest tests.test_yourcv -v
"""
import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "auditor"))
import yourcv as y  # noqa: E402

CV = """CURRICULUM VITAE
Chiamaka Obi | Lagos | chiamaka.obi@gmail.com

Profile
Chiamaka is a data analyst with 5 years of experience. She builds dashboards and her team relies on her.

Experience
Data Analyst, Paystack, 2021 - present
"""


def wait(job):
    while job["status"] == "running":
        time.sleep(0.2)
    return job


class Twins(unittest.TestCase):
    def test_sample_twins_are_the_audit_files_byte_for_byte(self):
        text, ids = y.sample_cv()
        name, lines = y.find_name(text)
        man = {c["candidate"]: c for c in json.loads((ROOT / "data/cvs/manifest.json").read_text())}["cand02"]
        for i in ids:
            v = next(v for v in man["variants"] if v["length"] == "short" and v["slot"] == i["slot"]
                     and v["gender"] == i["gender"] and v["group"] == i["group"])
            self.assertEqual(y.make_twin(name, lines, i["first"], i["last"], i["gender"]).strip(),
                             (ROOT / v["file"]).read_text(encoding="utf-8").strip())

    def test_only_name_email_and_pronouns_change(self):
        name, lines = y.find_name(CV)
        self.assertEqual(name, "Chiamaka Obi")
        twin = y.make_twin(name, lines, "Greg", "Baker", "male")
        self.assertTrue(twin.startswith("Greg Baker | Lagos | greg.baker@example.com"))
        self.assertIn("Greg is a data analyst with 5 years of experience. He builds dashboards and his team relies on his.", twin)
        self.assertNotIn("Chiamaka", twin)
        self.assertIn("Data Analyst, Paystack, 2021 - present", twin)

    def test_name_must_be_on_first_line(self):
        with self.assertRaises(y.CVError):
            y.find_name("Experience\nData analyst 2019 - present")


class Scoring(unittest.TestCase):
    def test_sample_matches_published_dry_run_and_kane(self):
        job = wait(y.start(None, True)[0])
        self.assertEqual(job["status"], "finished", job.get("error"))
        for t in y.TOOL_ORDER:
            for src in (f"twin_audit_{t}.json", f"twin_audit_{t}.kane.json"):
                pub = json.loads((ROOT / "results" / src).read_text(encoding="utf-8"))
                ref = {x["name"]: x["score"] for c in pub["candidates"] if c["candidate"] == "cand02" for x in c["twins"]}
                for x in job["twins"]:
                    self.assertAlmostEqual(x["scores"][t]["score"], ref[x["name"]], places=9, msg=f"{t} {src} {x['name']}")

    def test_tools_keep_nothing(self):
        wait(y.start(CV, False)[0])
        for t, store in y.STORES.items():
            self.assertEqual(len(getattr(y.tool_module(t), store)), 0, t)


if __name__ == "__main__":
    unittest.main()
