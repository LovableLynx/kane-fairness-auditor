# Independent audit and redesign report

**Date:** 14 November 2026  **Scope:** the full repository and the live deployment (https://kane-fairness-auditor.onrender.com)

## 1. What the product is

Fairness Auditor tests AI hiring tools for bias **through their own web interface**. Kane CLI submits *CV twins* (identical CVs that differ only in name and pronouns, plus same-group "placebo" names) to a tool's UI. It stores each score and decision, and the auditor returns **PASS**, **FAIL: BIASED**, **FAIL: NAME-UNSTABLE** or **INCONCLUSIVE** as an exit code that gates deployment in CI.

- **Users:** employers and auditors who must evidence that a bought hiring tool is fair (NYC LL144, EU AI Act); hackathon judges; recruiters trying the demo tools.
- **Main flows:**
  1. A recruiter uploads or pastes a CV into a demo tool and gets a decision.
  2. An auditor runs `gate.py` or `twin_audit.py`, and Kane drives a tool's UI to produce a verdict.
  3. A visitor reads the verdicts, twin tables, impact ratios, method and study on the auditor site.
  4. CI runs the gate on a pull request.
- **Stack:** Python 3.12 and Flask; scikit-learn models; fastembed (ONNX) for all-MiniLM-L6-v2; Kane CLI 0.10.4; one gunicorn service on Render (free tier). There are no databases or accounts.

## 2. Audit findings

Severities: **C**ritical, **H**igh, **M**edium, **L**ow. Every High and Medium item is fixed unless noted.

| # | Sev | Area | Where | Finding | Why it matters | Fix |
|---|---|---|---|---|---|---|
| 1 | H | Legal / privacy | public site | CV uploads (personal data) were accepted with **no privacy notice, terms or disclaimer**. TalentScreen infers ethnicity from names, which is special-category processing (GDPR Art. 9, NDPA). | Transparency obligations under GDPR, UK GDPR and NDPA; liability for misuse of a deliberately biased tool. | Added `/legal`: terms, privacy notice and disclaimer. A notice in every tool's footer links to it. The landing page warns users to submit sample CVs only. |
| 2 | H | Security / availability | all tools | No request size limit; in-memory stores grew without bound on a public URL. | Anyone could exhaust the server's memory, a denial of service. | 512 KB limit with a styled 413 page; `BoundedStore` caps every store at 300 entries (`shared/hardening.py`). |
| 3 | H | Accessibility | TalentScreen upload | The file input was `hidden`, so **keyboard users could not upload**. | Fails WCAG 2.1.1 Keyboard. | Visually hidden but focusable input with a visible focus ring on the drop zone. |
| 4 | H | Accessibility | QuickMatch, TalentScreen | Button text contrast too low: white on #ff8a1f was about 2.3:1; white on #7c5cff about 4.2:1. | Fails WCAG 1.4.3 (needs 4.5:1). | Darker accents: #b84e00 (about 5.1:1) and #5b3df5 (about 6:1). |
| 5 | H | Functionality | CV parser | Only our own CV template parsed. **A real CV failed**, which broke the core "drop a CV" promise. | The main recruiter flow didn't work for real input. | The parser falls back to heuristics: role synonyms, date-range experience, education keywords, language levels and notice periods. Estimated fields are flagged in the UI. PDF and DOCX uploads are supported. All 1,760 template CVs still parse identically. |
| 6 | M | Security | all tools | Error text was **reflected from the URL** (`?error=anything`). | Lets someone plant fake messages via a crafted link (content spoofing or phishing). | Errors are fixed codes mapped to fixed messages. Unknown codes show nothing. |
| 7 | M | Security | all apps | No security headers. | Weak defence in depth. | CSP, `nosniff`, `Referrer-Policy`, `Permissions-Policy` and `frame-ancestors 'self'`. |
| 8 | M | Privacy | QuickMatch | Full CV text was kept after scoring. | Data minimisation (GDPR Art. 5(1)(c)). | CV text is deleted once matched; re-running is blocked. |
| 9 | M | UX | all tools | No loading state. QuickMatch's first run (model load) looked frozen. | Users double-submit or abandon. | Busy buttons with spinners or dots, plus a message explaining the first-run delay. |
| 10 | M | UX | all apps | Unstyled default 404 and 500 pages. | Looks broken; dead end. | A styled error page per app, with a way back. |
| 11 | M | Functionality | HireLens | Dead "Reports" link (`href="#"`). | Placeholder UI. | Removed. |
| 12 | M | Structure | `serve.py` | The landing page was hard-coded HTML inside the server file. | Hard to maintain; no design system. | A new `auditor/` app (landing, results, method, legal) replaces `dashboard/` and the inline HTML. Old URLs redirect. |
| 13 | M | Legal | tool names | Fictional tool names could collide with real products. A real recruiting product called "HireScore" exists; our earlier prototype used that name and was removed. | Implying a real vendor is biased is a defamation and trademark risk. | Each tool states it is fictional and unaffiliated; the disclaimer covers it. A web search found no product named TalentScreen, HireLens or QuickMatch, though this is not a full trademark search. |
| 14 | M | Robustness | auditor site | Scroll-reveal content stayed hidden if the script didn't run. | Content invisible without JS. | Reveals are gated on a `motion` class that removes itself after 2.5 s if the script hasn't loaded. |
| 15 | M | Hosting | QuickMatch | The model loaded and 200 calibration CVs were embedded at startup, so the free tier missed its health check. | The first deploy failed. | Lazy model load, cutoff cached in `data/quickmatch_cutoff.json`, model downloaded at build time. |
| 16 | L | Accessibility | all | Missing skip links, landmarks, `aria-current`, `role="alert"` and focus styles. | Screen reader and keyboard comfort. | Added throughout. |
| 17 | L | Privacy | fonts | Google Fonts would send visitor IPs to Google (relevant under GDPR). | Privacy. | Bunny Fonts, a privacy-focused mirror. System fonts are the fallback. |
| 18 | L | Claims | copy | Words like "legal proof" or "LL144 audit" would overstate the tool. | Liability. | Copy uses "LL144-style", "illustrative" and "not legal advice"; the disclaimer covers it. |

**No Critical issues were found.** No secrets are in the repository (the Kane run artefacts were checked; their `secrets` fields are empty). There is no auth surface, and Jinja autoescaping blocks XSS (tested with `<script>` payloads).

## 3. Standards compared

- **Hiring-discrimination measurement:** correspondence testing (Bertrand & Mullainathan, 2004). Twins plus a placebo control, as in audit-study practice.
- **Regulation:** NYC LL144 asks for selection rates and impact ratios by sex and race/ethnicity, which we report as *illustrative*. The EU AI Act puts recruitment AI in Annex III (high-risk). The EEOC four-fifths rule is used as a rule of thumb.
- **Web:** WCAG 2.2 AA (contrast, keyboard, focus, reduced motion) and OWASP secure headers.

## 4. Redesign

**Auditor site (new design system, `auditor/static/ds.css`):**
- Cream paper base (#F6F0E1), ink #1F1B16, cobalt #2338C9 primary and tomato #C8401F emphasis. All neutrals are tinted toward the cream hue (an idea from motionin.design).
- Type: Bricolage Grotesque at 800 for chunky display headings, Silkscreen pixel kickers, JetBrains Mono for numbers. There is a fluid type scale and a 4 px spacing scale.
- 90s character: hard offset shadows that collapse on press, pixel micro-labels, a single dithered band as the only texture (motionin's Cabinet idea), stamped verdicts, and "provenance" chips ("Verified by Kane" or "Dry run"; fontinlogo's verification labels).
- Motion:
  - View-transition page changes and stepped reveals that draw in like an old screen.
  - Verdict stamps that thump in, impact meters that grow, count-up numbers, and a hero "live replay" that types each twin's name while both tools re-score.
  - All of it is disabled under `prefers-reduced-motion`.
- Pages:
  - landing (problem contrast table, inspired by screensdesign; how-it-works; results; study; try-it)
  - results index and per-tool detail (KPIs, reasons, twin matrix with sticky column, impact meters with a 0.8 marker, provenance)
  - method, with the study table
  - legal
- **The three demo tools keep deliberately different looks.** That is the point of the interface-agnostic audit. Each was polished within its own identity: accessibility, loading states, motion, error pages and the legal footer.

**Research:** 21 of 24 reference sites were studied. godly.website redirects to recent.design; appkittie.com and appshots.design returned no usable content; on.design was only partly readable before a login wall. Scarcity and urgency patterns seen on wonderlist and paperanimation were deliberately avoided for a trust-first product.

## 5. Verification

- Every route on every app returns the expected status through `serve.py`.
- Edge cases: empty, garbage, oversize (413), wrong file type, and a malformed DOCX each give a clear message. Unknown IDs return a styled 404. A free-form PDF CV is parsed end to end.
- The audit gives the same verdicts after the changes: TalentScreen FAIL: BIASED, HireLens PASS, QuickMatch FAIL: NAME-UNSTABLE.
- Visual checks were done at 1440 px and 390 px.

## 6. Still open

- **Real Kane browser runs:** the published results are still dry runs, waiting on Kane credits (128 available). They are labelled as dry runs everywhere.
- The legal links in the tools point to `/legal`, which works on the combined deployment but not when a tool runs alone on its own port.
- PDF text extraction depends on the PDF having a text layer. Scanned image PDFs would need OCR.
- A full trademark clearance search for the three fictional names was not done.
