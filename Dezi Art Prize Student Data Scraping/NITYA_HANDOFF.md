# Handoff: Dezi Art Prize Student Data Scraper

This doc is written for **your Claude Code chat** to read first, before touching
anything in this repo. Paste this whole file (or point Claude at it) at the start of
your session so it has full context on what this project is, what's relevant, what to
ignore, and how to keep working the same way it's been worked on so far.

Repo: **https://github.com/fufuman/opportunities-hub-scraper.git**

---

## 1. What this project actually is

We're building a contact list of art students (MFA/BFA, mostly graduating cohorts)
from ~26 US art schools, for outreach related to the Dezi Art Prize. For each
student we try to capture: **name, email, major, graduation_year, portfolio_url,
college, notes, sent_to_nitya** (plus two outreach-tracking columns,
`contacted`/`response`, added only in the final Excel output).

The work happens in two phases:

1. **Scraping** — for each school, find a public page listing a graduating cohort
   (an MFA thesis exhibition page, a senior show, a department gallery listing,
   etc.), write a small Python scraper for it, and extract names + whatever else is
   published (major, year, a portfolio/Instagram link). Most source pages do **not**
   publish student emails — that's expected and normal.
2. **Email discovery** — for the students who came out of phase 1 with a name but no
   email, search the web (their own portfolio site, Instagram/LinkedIn, school
   directories) to try to find a real, verifiable email, then write it back into the
   same CSV. This is a slower, more manual phase, done city/school by school, with a
   human (you) verifying anything the AI couldn't fetch directly or wasn't fully
   confident about.

Two people currently contribute emails to this dataset (you and Nitya), which is why
handoff is now done in small **batches** rather than the whole file at once — see
Section 6.

**Two git branches matter:**

- **`main`** — the full working repo: every scraper script, every per-school CSV, all
  logs, both branches' history. This is the "developer" branch.
- **`final-master-list`** — a deliberately trimmed branch containing **only**
  `Dezi Art Prize Student Data Scraping/master_students_with_email.xlsx` (nothing
  else). This is the clean deliverable — the file that only has students we have a
  confirmed email for. **This is the branch to clone if you just want the current
  contact list** and plan to keep adding emails to it over time.

If Nitya's Claude is going to **continue the same scraping/email-discovery workflow**
(finding new students, finding more emails), it should work from `main`, since that's
where all the source code and full data lives. `final-master-list` only makes sense
as a place to periodically push the refreshed with-email workbook.

---

## 2. Directory structure — what's relevant vs. what to ignore

The repo root (`c:\Scraper` on this machine) contains **two unrelated projects**.
This matters a lot — don't let Claude read or touch the wrong one.

```
c:\Scraper\                              <- repo root
│
├── Dezi Art Prize Student Data Scraping/    ✅ THE RELEVANT PROJECT — everything below
│   ├── ISSUES_LOG.md                        ✅ read this first, every session
│   ├── *_scraper.py                         ✅ one Python script per school (25+ files)
│   ├── *_students.csv                       ✅ one CSV per school — the actual data,
│   │                                            source of truth (NOT the xlsx files)
│   ├── build_master_workbook.py             ✅ builds master_students.xlsx from all CSVs
│   ├── split_master_workbook.py             ✅ splits into with-email / no-email xlsx
│   ├── master_students.xlsx                 ✅ generated output (all schools, all students)
│   ├── master_students_with_email.xlsx      ✅ generated output (only students with email)
│   ├── master_students_no_email.xlsx        ✅ generated output (only students without)
│   ├── requirements.txt                     ✅ NEW — added for this handoff, pip installs
│   ├── art_school_scraping_urls.md          ✅ original research doc (28 schools, batches 1-5)
│   ├── next_urls_art_prize_31-50.md         ✅ second research doc (28 more schools, batch 6+)
│   └── art_school_artists_batch1.xlsx       (an early/intermediate file, mostly superseded
│                                              by master_students.xlsx — safe to ignore)
│
├── cache/                                 ⚠️  scraper HTML cache — gitignored, won't be
│                                              on GitHub, regenerates automatically, safe
│                                              to ignore/delete
├── .venv_crawl4ai/                        ⚠️  Python virtual environment — gitignored,
│                                              won't be on GitHub, must be recreated
│                                              (see Section 4)
│
├── CLAUDE.md                              ❌ UNRELATED — rules for a different project
│                                              ("Opportunities Hub Scraper" — grants/
│                                              residencies/open-calls scraper, not this one)
├── EXTRACTION_ISSUES_LOG.md               ❌ UNRELATED — belongs to that other project
├── EXTRACTION_PROGRESS.md                 ❌ UNRELATED
├── ORG_MASTER_LIST_PHASE_2.xlsx           ❌ UNRELATED
├── ORG_MASTER_LIST_Phase_1.xlsx           ❌ UNRELATED
├── PHASE_1_ORG_DISCOVERY.md               ❌ UNRELATED
├── PHASE_2_OPP_EXTRACTION.md              ❌ UNRELATED
├── opportunity_sources_seedlist.xlsx      ❌ UNRELATED
├── phase1_seed_link_test_crawl4ai.py      ❌ UNRELATED
├── phase 1 extraction/                    ❌ UNRELATED
└── phase 2 extraction/                    ❌ UNRELATED
```

**Tell Claude explicitly: only work inside `Dezi Art Prize Student Data Scraping/`.**
Everything at the repo root outside that folder (the `CLAUDE.md`, the `EXTRACTION_*`
and `PHASE_*` files, `ORG_MASTER_LIST*.xlsx`) is a completely different, unrelated
scraper project (grants/residencies/opportunities, not student data) that happens to
share this same git repo. Don't read it for context, don't edit it, don't let its
`CLAUDE.md` rules bleed into how this project's work gets done — this document
supersedes it for anything under `Dezi Art Prize Student Data Scraping/`.

---

## 3. Data model — how the files fit together

- **The CSVs are the source of truth.** Never hand-edit the `.xlsx` files directly —
  always edit the relevant `<school>_students.csv`, then regenerate the Excel outputs
  (see Section 5). Every CSV has exactly these 8 columns:
  `name, email, major, graduation_year, portfolio_url, college, notes, sent_to_nitya`
- **Missing email is written as an empty string**, not "N/A" or similar (a couple of
  older rows — all of Cranbrook — use the literal string `"Not found"`, checked
  case-insensitively and also treated as "no email" everywhere, but new rows should
  just use `""`).
- **`sent_to_nitya`** — blank until a row has been included in a batch sent to Nitya
  (see Section 6), then stamped with the date it was sent (e.g. `2026-08-11`). This is
  handoff-tracking, distinct from `contacted`/`response` (which track whether *Nitya*
  has reached out to *the student* — a separate concern, only present in the Excel
  outputs). Never hand-edit this column — it's only ever written by
  `mark_batch_sent.py`.
- **`notes` should always say what happened**, honestly. Conventions used throughout:
  - `"Email confirmed by user"` — when the human found/verified it manually.
  - `"Email found via web search (own site X.com)"` — when Claude found it directly
    from a source it could fetch and verify.
  - `"UNVERIFIED possible email: x@y.com — ..."` — when a candidate email surfaced
    but couldn't be confirmed as belonging to that specific person (ambiguous
    common name, unconfirmed source). **Never silently upgrade an UNVERIFIED note
    into a real value in the `email` column without independent confirmation.**
  - Plain factual notes when nothing was found — e.g. "No email found via web search
    — no personal site surfaced." Don't skip writing a note; every no-email row should
    say *why* there's no email, for future reference.
- **`build_master_workbook.py`** reads all the CSVs and writes `master_students.xlsx`
  — one sheet per school, with a 3-line italic source-citation header (name/URL/date
  accessed, from a `SOURCE_CITATIONS` dict in that file) above the data. It also
  exposes a module-level `SOURCES` list — `(sheet title, csv filename, college
  label)` per school — that every other script in this folder imports rather than
  keeping its own copy. (There used to be a second, separately hardcoded copy in
  `split_master_workbook.py` that had drifted out of sync — fixed 2026-08-15 by
  having it import `SOURCES` instead. If you ever add a new school, add it to
  `SOURCES` in `build_master_workbook.py` only — every downstream script picks it up
  automatically.)
- **`split_master_workbook.py`** does the same thing but writes two separate
  workbooks: `master_students_with_email.xlsx` (only rows with a real email) and
  `master_students_no_email.xlsx` (the rest).
- **`build_nitya_batch.py`** / **`mark_batch_sent.py`** — the batch handoff tools,
  see Section 6.

---

## 4. Environment setup (what Nitya's machine needs)

The Python virtual environment (`.venv_crawl4ai/`) is **gitignored** — it will not
come through when she clones the repo. She needs to recreate it:

```bash
# from the repo root, after cloning
python -m venv .venv_crawl4ai

# Windows:
.venv_crawl4ai\Scripts\pip install -r "Dezi Art Prize Student Data Scraping\requirements.txt"
.venv_crawl4ai\Scripts\python -m playwright install chromium

# Mac/Linux:
.venv_crawl4ai/bin/pip install -r "Dezi Art Prize Student Data Scraping/requirements.txt"
.venv_crawl4ai/bin/python -m playwright install chromium
```

`requirements.txt` (in the `Dezi Art Prize Student Data Scraping/` folder — newly
added for this handoff) pins the exact versions used so far:
`beautifulsoup4==4.15.0`, `Crawl4AI==0.9.2`, `openpyxl==3.1.5`, `playwright==1.61.0`,
`playwright-stealth==2.0.3`, `requests==2.34.2`.

To run any per-school scraper or the workbook builder scripts, always use this venv's
Python, e.g. from inside `Dezi Art Prize Student Data Scraping/`:

```bash
../.venv_crawl4ai/Scripts/python.exe bgsu_scraper.py
../.venv_crawl4ai/Scripts/python.exe build_master_workbook.py --out master_students.xlsx
../.venv_crawl4ai/Scripts/python.exe split_master_workbook.py
```

Most scrapers use plain `urllib.request` with a browser User-Agent and don't need
`crawl4ai` at all — `crawl4ai` (via Playwright, headless Chromium) is only invoked as
a fallback when a site is JS-rendered or blocked by Cloudflare/cookie-walls. A few
scrapers (e.g. `umich_scraper.py`, `vcu_scraper.py`) show the pattern for when/how to
use it — reuse that pattern rather than writing something new.

The `cache/` folder (also gitignored, lives at the repo root) holds locally-cached
fetched HTML pages, organized in per-school subfolders. It's safe to delete if it
grows large; scrapers will just re-fetch. It exists purely to avoid re-hitting the
same URLs repeatedly.

---

## 5. The standard workflow (how every session has actually gone)

### A. Scraping a new school
1. Take a school name/URL from `art_school_scraping_urls.md` or
   `next_urls_art_prize_31-50.md` (or wherever the next lead comes from).
2. **Verify the URL is real and matches what the doc claims before writing any
   code** — every research doc used so far has had a meaningful error rate (dead
   links, wrong page, overclaimed content). Fetch it directly first.
3. Write `<school>_scraper.py` following the exact pattern of an existing scraper —
   a `fetch(url, cache_path, force_refresh=False)` function, a `parse_students(html)`
   function returning a list of the 7-column dicts, and a `main()` with argparse
   (`--out`, `--force-refresh`). Look at `ucla_scraper.py` or `bgsu_scraper.py` as
   clean, simple examples.
4. Run it, sanity-check the row count against what the source doc claimed.
5. Add the school to `SOURCE_CITATIONS` **and** to the `SOURCES` list — both in
   `build_master_workbook.py` only; `split_master_workbook.py` and the batch tools
   import `SOURCES` from there automatically, no second place to update anymore.
6. Rebuild all three workbooks (Section 4 commands).
7. Log what happened in `ISSUES_LOG.md` (what worked, what was wrong in the doc, any
   dead ends) — this file is long (900+ lines) and is meant to be read, not just
   written to; check it before starting a new school in case it's already been tried.
8. Commit to `main`. If new emails were added, generate/send a batch (Section 6a) and
   mirror `master_students_with_email.xlsx` onto `final-master-list` (Section 6b).

### B. Finding missing emails (the current phase of work)
1. Work through name-only students **one school at a time**, generally smallest
   school first, to keep sessions focused and checkpoint-able.
2. For each student, if they already have a `portfolio_url` from the original scrape,
   check that site first (cheaper, more reliable than a fresh search).
3. Otherwise, run a few targeted web searches (`"<Name>" <College> <major> portfolio`,
   `"<Name>" <College> MFA email contact`, etc.) and look at the first ~5 results.
4. If a personal site / Instagram / LinkedIn surfaces, fetch it and look for a
   contact/about section, footer, or mailto: link.
5. **Confidence gate — this is important and has been followed strictly:**
   - High confidence (email is on the student's own domain/site, clearly matches
     them) → write directly into the CSV `email` column.
   - Ambiguous (common name, multiple candidates, no strong corroboration) → leave
     `email` blank, write an `UNVERIFIED possible email: ...` note instead. Never
     guess.
   - A real site exists but the tool can't reach it (DNS failure, 403, 503 — this
     came up a LOT this session, seemingly a quirk of the sandboxed fetch tool used)
     → note the site URL and the failure, flag it for a human to check manually.
     **This flagging approach worked very well** — every single flagged "unreachable"
     site turned out to be real and resolvable once a human checked it directly.
   - Never fabricate an email from a guessed pattern (e.g. assuming
     `firstname.lastname@college.edu` without verifying) even if a college's naming
     convention seems obvious from other confirmed emails at that school.
6. After a school's pass is done: rebuild the workbooks, log a summary paragraph in
   `ISSUES_LOG.md` (X of Y found, what worked, what didn't), commit to `main`,
   generate/send a batch (Section 6a), mirror the with-email workbook to
   `final-master-list` (Section 6b), push both.

---

## 6. Handoff: batches (day-to-day) + the two-branch mirror (full backup)

Two people add emails to this dataset now (you and Nitya), so as of 2026-08-15 there
are **two handoff mechanisms that run alongside each other**:

- **WhatsApp batches** — the actual day-to-day handoff. A small `.xlsx` containing
  only the rows Nitya hasn't received yet, generated on demand and shared directly.
- **`final-master-list` branch** — kept exactly as before, as a complete backup/audit
  trail of the with-email file. Still updated every session, but is not what you
  actually send Nitya day to day anymore.

### 6a. Generating and sending a batch

Every CSV has a `sent_to_nitya` column (blank = never sent). After a session where
new emails were added:

```bash
cd "Dezi Art Prize Student Data Scraping"
../.venv_crawl4ai/Scripts/python.exe build_nitya_batch.py
```

This scans every school's CSV for rows with a real email and a blank `sent_to_nitya`,
and writes them to `nitya_batch_<today>.xlsx` — one sheet per school that has
something new, same citation-header formatting as the full master workbook. It prints
a per-school count and **does not modify any CSV** — safe to re-run any time to
preview what would go out.

Review the file, then send it to Nitya (WhatsApp, or however). **Only after
confirming it was actually sent**, mark it as delivered:

```bash
../.venv_crawl4ai/Scripts/python.exe mark_batch_sent.py
```

This stamps today's date into `sent_to_nitya` on every row that was just sent
(re-running the same filter `build_nitya_batch.py` used), after showing a
confirmation prompt (`--yes` to skip it). Do **not** run this before actually sending
the batch — if you generate a batch, get interrupted, and don't send it that session,
just leave it unmarked; running `build_nitya_batch.py` again next session will pick
up the same rows plus anything new.

### 6b. The two-branch mirror (unchanged, still done every session)

```bash
# 1. Commit everything to main as normal
git add "Dezi Art Prize Student Data Scraping/<whatever changed>"
git commit -m "..."
git push origin main

# 2. Mirror just the with-email workbook onto final-master-list
git checkout final-master-list
git checkout main -- "Dezi Art Prize Student Data Scraping/master_students_with_email.xlsx"
git commit -m "Update master_students_with_email.xlsx with ..."
git push origin final-master-list
git checkout main
```

`final-master-list` only ever contains that one file — it's not meant to accumulate
scraper code or other CSVs. Keep doing this every session regardless of whether a
batch also went out — it's the full backup, batches are just the incremental
day-to-day handoff.

### 6c. First batch under this system (2026-08-15)

Nitya's last sync was 2026-08-11. Everything with an email as of that point (1,007
rows — every school except the 10 below) was backfilled with
`sent_to_nitya = 2026-08-11`. The first real batch under this system was VCU (6 new
emails) + Ohio State (4 new emails) = 10 rows, generated as
`nitya_batch_2026-08-15.xlsx`.

---

## 7. Current state (as of 2026-08-15)

- **26 schools scraped**, ~2,126 total student rows across all CSVs.
- **1,017 students have a confirmed email** so far; the rest are name-only or have
  only an unverified/flagged lead.
- Email-discovery has been completed (at least one pass) for: BGSU, UW Art, MassArt,
  CMU, Temple/Tyler, Columbia College Chicago (0 emails found there — see below),
  VCU (6/13), Ohio State (4/21, 2025 cohort only — see `ISSUES_LOG.md` for why the
  8 UNVERIFIED 2026-cohort names were deliberately left untouched).
- CalArts Animation (a new source, distinct from the existing names-only "CalArts"
  sheet) was added 2026-08-11 — 251 students, 251 with a confirmed email (100%).
- **Not yet attempted**: Cranbrook (genuinely 0 public emails — confirmed via the
  alumni directory not publishing them, not a scraper gap), UCLA, Iowa, U Michigan
  Stamps, Parsons (partially — some already had emails), SVA, Pratt, MICA, MCAD
  (partially), RISD, BU, CalArts (original High Pass sheet), CCA, Yale.
- **Known pattern**: MFA/graduate cohorts are much easier to find emails for (they
  commonly maintain personal portfolio sites with a bio/CV page listing contact info)
  than BFA/undergrad cohorts (who mostly don't have a personal site yet — searches for
  Columbia College Chicago's 24 BFA students found **zero** emails automatically,
  mostly turning up Dean's List PDFs and LinkedIn stubs with no contact info instead).
  Expect the same difficulty on other BFA-heavy schools (Cranbrook, CalArts, SVA).
- Full details of every school's scrape and every email-discovery pass, including
  exact counts and what worked/didn't, are in `ISSUES_LOG.md` — that file is the
  detailed record; this handoff doc is the orientation summary.

---

## 8. A few house rules worth carrying forward

- **Never bypass a CAPTCHA, login wall, or bot-detection challenge.** If a source is
  blocked that way (this happened with UT Knoxville's TRACE repository — AWS WAF
  CAPTCHA), log it as a dead end and move on. Don't attempt workarounds.
- **Always verify a research doc's claims before writing scraper code** — every doc
  used in this project so far has had errors (wrong URLs, overclaimed page content,
  stale links). Spot-check the actual page first.
- **Don't overwrite `email` with a lower-confidence guess** if a cell already has a
  confirmed value — always check current state before writing.
- **Checkpoint often.** This project has consistently worked in small batches (one
  school, or one small group of schools) with a commit+push+log after each, rather
  than long uncommitted stretches. Recommend Nitya's Claude do the same.
