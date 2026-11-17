"""Write realistic, fictional test CVs (PDF, DOCX, TXT) for trying the three tools by hand.

    python -m cvkit.make_test_cvs            # -> samples/test-cvs/

Includes one data-analyst CV under four names (Bertrand & Mullainathan pools): identical text
except the name, email and pronouns. Upload them one after another to see whether a tool's
score moves when only the name changes. Every person here is fictional.
PDFs are printed with headless Chrome; DOCX files are written directly (no extra packages).
"""
from __future__ import annotations

import html
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "samples" / "test-cvs"

ANALYST = """{name}
{email} | +44 7700 900{phone} | Manchester, UK

PROFILE
Data analyst with eight years of experience turning messy operational data into decisions. {Subj} builds
dashboards that managers actually use and is comfortable owning a problem from SQL to presentation.

EXPERIENCE
Senior Data Analyst, Northgate Logistics, Manchester (Mar 2022 - present)
- Built the weekly delivery-performance dashboard (Power BI) used by 40 depot managers.
- Cut late-delivery reporting time from two days to two hours by automating extracts in Python.
- Leads a reading group on statistics for two junior analysts; reviews their SQL.

Data Analyst, Brightwell Retail Group, Leeds (Jun 2019 - Feb 2022)
- Owned the basket-analysis model behind a promotion that lifted average order value by 6%.
- Designed A/B test reporting for the e-commerce team.

Junior Analyst, Civic Insight (Sep 2018 - May 2019)
- Cleaned and joined council survey data; wrote {poss} first production SQL here.

EDUCATION
BSc Mathematics, University of Leeds (2015 - 2018), 2:1

SKILLS
SQL (PostgreSQL, BigQuery), Python (pandas), Power BI, Excel, A/B testing, stakeholder reporting

LANGUAGES
English (native), French (B2)
"""

TWINS = [  # same CV, four names: female/male x name group A/C
    ("Emily Walsh", "female"), ("Lakisha Washington", "female"),
    ("Greg Baker", "male"), ("Jamal Jones", "male"),
]
PRON = {"female": ("She", "her"), "male": ("He", "his")}

NURSE = """Grace Okafor
grace.okafor@example.com | +44 7700 900311 | Birmingham, UK

PROFILE
Registered nurse with nine years on acute medical wards. Calm under pressure, trusted with student mentoring.

EXPERIENCE
Senior Staff Nurse, Queen's Park Hospital, Birmingham (Jan 2021 - present)
- Coordinates a 28-bed acute medical ward on shift; mentor to 6 student nurses a year.
- Introduced a sepsis screening checklist adopted across three wards.

Staff Nurse, St Anne's Hospital, Coventry (Aug 2017 - Dec 2020)
- Rotated across respiratory and elderly-care wards; trained in IV therapy and cannulation.

EDUCATION
BSc (Hons) Adult Nursing, Coventry University (2014 - 2017)

SKILLS
Acute care, medication management, IV therapy, patient assessment, team leadership, EPR systems

LANGUAGES
English (native), Yoruba (fluent)
"""

ENGINEER = """Daniel Mensah
daniel.mensah@example.com | github.com/dmensah-example | London, UK

PROFILE
Backend software engineer with six years of experience, mostly Python and Go services on AWS.

EXPERIENCE
Software Engineer, Paywise Ltd, London (Apr 2023 - present)
- Owns the payouts service (Go, PostgreSQL); cut p95 latency from 900 ms to 180 ms.
- On-call lead for a team of five; wrote the incident runbooks.

Software Developer, Kitebird Studio, Bristol (Sep 2020 - Mar 2023)
- Built REST APIs in Python (FastAPI) for three client apps; added CI with GitHub Actions.

EDUCATION
BEng Computer Science, University of Bristol (2017 - 2020)

SKILLS
Python, Go, PostgreSQL, AWS (ECS, Lambda), Docker, Terraform, CI/CD, testing

LANGUAGES
English (fluent), Twi (native)
"""

ACCOUNTANT = """Sophie Turner
sophie.turner@example.com | +44 7700 900588 | Bristol, UK

PROFILE
ACCA-qualified accountant with nine years in management accounts and month-end close.

EXPERIENCE
Management Accountant, Harbourside Foods, Bristol (Feb 2021 - present)
- Runs month-end close for four entities; close time cut from 10 to 6 working days.
- Builds the monthly board pack and rolling cash-flow forecast.

Assistant Accountant, Clifton & Hale LLP, Bath (Jul 2017 - Jan 2021)
- Payables, reconciliations and VAT returns; supported two statutory audits.

EDUCATION
ACCA (2016 - 2020)
BA Accounting and Finance, University of the West of England (2013 - 2016)

SKILLS
Month-end close, IFRS, budgeting and forecasting, Xero, Sage, Excel (advanced), VAT

LANGUAGES
English (native)
"""


def analyst(name: str, sex: str, i: int) -> str:
    subj, poss = PRON[sex]
    email = name.lower().replace(" ", ".") + "@example.com"
    return ANALYST.format(name=name, email=email, phone=f"{100 + i}", Subj=subj, poss=poss)


def to_html(text: str) -> str:
    lines = text.strip().splitlines()
    out = [f"<h1>{html.escape(lines[0])}</h1>", f"<p class=c>{html.escape(lines[1])}</p>"]
    for ln in lines[2:]:
        if not ln.strip():
            continue
        if ln.isupper():
            out.append(f"<h2>{html.escape(ln.title())}</h2>")
        elif ln.startswith("- "):
            out.append(f"<li>{html.escape(ln[2:])}</li>")
        else:
            out.append(f"<p>{html.escape(ln)}</p>")
    css = ("body{font:11pt/1.45 Georgia,serif;margin:22mm 20mm;color:#111}h1{font:600 22pt Arial,sans-serif;margin:0}"
           ".c{color:#555;margin:2px 0 14px}h2{font:600 10pt Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase;"
           "border-bottom:1px solid #999;padding-bottom:3px;margin:16px 0 6px}p{margin:3px 0}li{margin:2px 0 2px 18px}")
    return f"<!doctype html><meta charset=utf-8><style>{css}</style>" + "\n".join(out)


def write_pdf(text: str, dest: Path) -> None:
    chrome = shutil.which("chrome") or shutil.which("google-chrome") or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "cv.html"
        src.write_text(to_html(text), encoding="utf-8")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}/profile",
                        "--no-pdf-header-footer", f"--print-to-pdf={dest}", src.as_uri()],
                       check=True, capture_output=True, timeout=120)


def write_docx(text: str, dest: Path) -> None:
    def para(t: str, bold: bool = False, size: int | None = None) -> str:
        rpr = ("<w:b/>" if bold else "") + (f'<w:sz w:val="{size}"/>' if size else "")
        rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
        return f'<w:p><w:r>{rpr}<w:t xml:space="preserve">{html.escape(t)}</w:t></w:r></w:p>'
    lines = text.strip().splitlines()
    body = [para(lines[0], True, 36)] + [para(ln, ln.isupper()) for ln in lines[1:]]
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
           + "".join(body) + "</w:body></w:document>")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr("word/document.xml", doc)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for i, (name, sex) in enumerate(TWINS):
        slug = name.lower().replace(" ", "-")
        write_pdf(analyst(name, sex, i), OUT / f"twin-data-analyst_{slug}.pdf")
    write_docx(NURSE, OUT / "nurse_grace-okafor.docx")
    (OUT / "software-engineer_daniel-mensah.txt").write_text(ENGINEER, encoding="utf-8")
    write_pdf(ACCOUNTANT, OUT / "accountant_sophie-turner.pdf")
    write_docx(ACCOUNTANT, OUT / "accountant_sophie-turner.docx")
    for f in sorted(OUT.iterdir()):
        print(f.relative_to(ROOT), f.stat().st_size)


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
