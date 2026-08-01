# Dezi Art Prize Student Data Scraping — Issues & Blockers Log

Track issues, missed items, and blockers encountered while scraping student rosters
(name, major, grad year, email, portfolio link) across art schools, feeding into
`master_students.xlsx` (one tab per school). Split out from the main project's
`EXTRACTION_ISSUES_LOG.md` on 2026-08-01 since this is a separate, standalone effort
from the Opportunities Hub scraper.

Source list for target schools/URLs: `art_school_scraping_urls.md`.

---

## Format

```
### [School] — [short description]
**Issue Type:** ...
**Description:** What happened
**Action Needed:** What to do about it
**Status:** Open / Resolved / Deferred
```

---

## Multi-School Batch 1 (Art Student Rosters) — 2026-07-31

Context: scraping student rosters (name, major, grad year, portfolio link) across
schools listed in `art_school_scraping_urls.md`, feeding into `master_students.xlsx`
(one tab per school). RIT, MCAD, Cranbrook were done in a prior session; this entry
covers Batch 1 (RISD, Otis, MCAD expansion).

### RISD — resolved, source doc's URL was wrong
**Issue Type:** Incomplete data source in original doc
**Description:** The doc's suggested URL, RISD's DigitalCommons
(`digitalcommons.risd.edu/campusexhibitions_graduatethesisexhibitions/`), only catalogs
exhibition-level posters/programs, not individual students.
**Action Needed:** Found and used the real current source instead:
`publications.risd.edu/grad-show-2026` (redirected from risdgrad.show), a static Drupal
site with a student-index page linking to ~210 per-student pages (name, program,
Instagram/LinkedIn link, thesis title). Scraped via `risd_scraper.py` → 210/210 students
processed, 2 dead links on RISD's own index (see below), 2 missing program field.
**Status:** Resolved. Do NOT reuse the DigitalCommons URL for future RISD batches
(e.g. prior years) — go straight to `publications.risd.edu/grad-show-YYYY`.

### RISD — 2 broken per-student links (source site issue, not ours)
**Issue Type:** Broken link
**Description:** RISD's own student-index page links to `/grad-show-2026/greg-kmieciak/`
and `/grad-show-2026/jul-lynn-tanning/`, both of which 404 on RISD's live site.
**Action Needed:** None — kept both rows in `risd_students.csv` with name only, blank
major/portfolio, and a "Fetch failed: HTTP Error 404" note, per the project's "don't
discard on broken link" rule.
**Status:** Deferred (not fixable on our end; RISD's site has dead links).

### MCAD — 2025/2026 "commencement-ceremony" and "commencement-exhibition" pages have no roster
**Issue Type:** Incomplete data source
**Description:** Confirmed by direct fetch: `spring-2025-commencement-exhibition`,
`spring-2025-commencement-ceremony`, and `spring-2026-commencement-ceremony` all return
HTTP 200 but contain zero student entries (0 "NameCard" matches) — they're event
logistics pages only (date, time, gallery hours, parking), not graduate rosters.
**Action Needed:** None further for these specific years/URLs. If a future session wants
2025/2026 MCAD data, a different URL pattern would need to be found (not yet identified).
**Status:** Deferred — flagged so this isn't re-attempted without a new lead.

### MCAD 2023 — different HTML format than 2022, plus 4 source data quirks
**Issue Type:** Format variation + source data quality
**Description:** The 2023 commencement-ceremony page uses different markup than 2022
(no `NameCard` span class; website/email joined by " | " instead of separate lines).
`mcad_scraper.py` was extended to support both formats via a per-cohort config. Four
2023 entries had additional quirks: one student (Kyle Perrin) has no major at all on
MCAD's own page — "Chaska, Minnesota" appears where major should be; three others had
links embedded inside the name `<span>` rather than after it.
**Action Needed:** Broadened the 2023 parsing regex to handle both link-placement
variants; Kyle Perrin's missing major is a genuine gap in MCAD's source page, left as-is
(major field contains his hometown as scraped, since that's literally what MCAD
published) — worth a manual note if this file is ever cleaned up by hand.
**Status:** Resolved (90/90 raw entries now captured for 2023; 115/115 for 2022).

### Otis College — old subdomain blocked, but user found the real current source
**Issue Type:** Resolved — wrong URL in original doc, corrected by user
**Description:** The doc's URL, `annual-exhibition.otis.edu/2022/annual-exhibition/all-students`,
returns HTTP 403 to both a plain `curl`/urllib fetch AND a real crawl4ai headless
Chromium browser ("Blocked by anti-bot protection: HTTP 403 with HTML content
(198 bytes)") — confirmed genuine WAF/anti-bot block on that old subdomain, not a
client quirk. This was initially logged as a hard blocker.
**Action Needed:** User supplied the actual current URL instead:
`www.otis.edu/about/our-work/annual-exhibition/2026/all-students.html` — this is on
the main `otis.edu` domain (not the old `annual-exhibition.otis.edu` subdomain), static
HTML, no blocking, no JS rendering needed. Built `otis_scraper.py` against it: 222
student index links (`.../2026/{slug}/index.html`), each per-student page cleanly
labeled with `exhibitor-name-year`, `exhibitor-department`, `exhibitor-email` (mailto),
and `exhibitor-portfolio` divs. Result: 222/222 students scraped, 0 fetch errors, 0
missing email, 0 missing major, 35 missing portfolio link (many students simply don't
list one).
**Status:** Resolved. For future years, try swapping `2026` for the target year in the
same URL pattern on `www.otis.edu` (not the old subdomain).

### Cranbrook — filtered down to matching mediums + 2026 only (user request)
**Issue Type:** Data filtering per user request, not a scraping issue
**Description:** User asked to remove Cranbrook entries outside painters, photographers,
designers, filmmakers, sculptors, animators, fashion designers, and fiber/material
artists, and to drop all 2025 rows, keeping only 2026. Mapped Cranbrook's actual
department names to these categories: kept Painting, Photography, Fiber, Sculpture,
Ceramics (treated as sculptural per user decision), Graphic Design, 2D Design, 3D
Design, 4D Design (time-based media, closest to filmmakers/animators). Cut Print
Media, Metalsmithing, Architecture, Industrial Design (no match). No Fashion program
exists at Cranbrook at all, so that category has zero Cranbrook rows.
**Action Needed:** `cranbrook_students.csv` was filtered in place from 100 → 40 rows.
**Important:** if `cranbrook_scraper.py` is ever re-run (e.g. to add more years or
refresh data), it will regenerate the full unfiltered 100-row file (2025+2026, all
departments) and silently undo this filter — re-apply the same keep-list/year filter
after any re-scrape.
**Status:** Resolved.

---

## Multi-School Batch 2 (Art Student Rosters) — 2026-08-01

Context: continuing the same scraping effort into Batch 2 (Parsons, Alfred, Temple/Tyler,
VCU) per `art_school_scraping_urls.md`'s priority order.

### Parsons — doc undersold this source; real archive goes further, but user wants only 2025-2026
**Issue Type:** Doc scope correction (in our favor — more data than expected)
**Description:** The doc only mentioned a 2020 thesis page and guessed at 2023/2024 URLs
(both 404). The real hub page (`amt.parsons.edu/finearts/`) has a flat archive going back
to 2016 AND forward through 2026, with clean per-student pages
(`finearts/{year}-{degree}-thesis/{slug}/`) containing name, personal website, email,
Instagram — comparable quality to RISD/Otis.
**Action Needed:** Per user decision, scraped only 2025 BFA Thesis, 2025 MFA Thesis, and
2026 MFA Thesis (60 students total via `parsons_scraper.py`). Excluded known nav/placeholder
slugs found on the hub page: `acknowledgments/acknowledgements`, `curators-note`,
`directors-note`, `press-release`, `test-artist`, `2026-new-artist-name`, and a stray `h`
slug (likely a broken/truncated entry). BFA students' pages have empty website/email
fields on Parsons' own site (confirmed via raw HTML — not a parser gap); MFA students'
pages are fully populated. Result: 60/60 processed, 0 fetch errors, 34 missing email
(all BFA, expected per source).
**Status:** Resolved. If a later batch wants 2016-2024 or 2027+, the same hub page and
URL pattern (`{year}-{degree}-thesis/`, note the hyphen, unlike older `{year}mfathesis/`
style pre-2022 years) should work.

### Alfred University — thesis archive appears to be gone
**Issue Type:** Dead source, doc's structure no longer exists
**Description:** The doc's `alfred.edu/academics/colleges-schools/art-design/thesis-exhibits/`
redirects (301) to `www.alfred.edu/galleries/#ThesisExhibit`, a generic galleries page with
no per-student roster or archive — just a "Thesis Exhibit" nav link with no content behind
it matching the doc's described per-student subpage pattern.
**Action Needed:** None found this batch. Not scraped.
**Status:** Deferred/unresolved. Revisit only if a different URL/archive location for
Alfred's MFA thesis shows is found (e.g. via web search or Wayback Machine).

### Temple/Tyler — thin but real data, names only
**Issue Type:** Low data richness, scraped anyway per user decision
**Description:** 2025 page (works) has student names embedded in prose, grouped by
exhibition week, no per-student pages/email/portfolio. 2024 URL guess 404s.
**Action Needed:** Built `temple_scraper.py` targeting the `<strong>date range:</strong>
Name1, Name2...<br />` pattern in the schedule block. Result: 30 names (page's own summary
text says "29 second-year students" — one-off discrepancy in the source's own wording, not
a parsing bug; all 30 rows are real names from the schedule). No email/major/portfolio
available — each row notes "Name only... no email/major/portfolio published on source page".
**Status:** Resolved (as complete as this source gets).

### VCU — Cloudflare blocked plain fetch, crawl4ai got through but data is sparse
**Issue Type:** Bot protection (partially bypassed) + thin data
**Description:** All VCU URLs tried (ICA exhibition pages, arts.vcu.edu event page,
art-history grad directory) return 403 to a plain fetch — Cloudflare `__cf_bm` cookie
challenge, same family of protection as Otis's old subdomain. Unlike Otis, crawl4ai's
headless browser DID get through this one (HTTP 200, full page). However, the page itself
only credits ~11-13 individual names via artwork/photo captions (some multi-artist
collaborative pieces), not a full clean roster — doc's claim of "26 named" was not
observed on this page as fetched.
**Action Needed:** Built `vcu_scraper.py` (uses crawl4ai, so must be run via
`.venv_crawl4ai\Scripts\python.exe`, not the system Python that the other scrapers use).
Extracts names from `(artwork © Name; photograph by ...)` caption patterns, splitting
multi-artist credits. Result: 13 students, each flagged "likely incomplete relative to
full graduating cohort" in notes.
**Status:** Resolved (partial/best-effort data, flagged as such).

### Note: VCU scraper requires the crawl4ai venv, unlike other Batch 1/2 scrapers
**Issue Type:** Environment note for future sessions
**Description:** `vcu_scraper.py` imports `crawl4ai`, which only exists in
`.venv_crawl4ai` (set up during Batch 1 for Otis, ultimately not needed there since a
plain-fetch alternative URL was found — but VCU genuinely needs it). Running it with the
system Python (`python`/`C:\Python314\python.exe`) will fail with `ModuleNotFoundError`.
**Action Needed:** Always run via
`c:\Scraper\.venv_crawl4ai\Scripts\python.exe vcu_scraper.py`. Also note: activating
this venv in a PowerShell session changes what plain `python` resolves to for the rest
of that session (it lacks `openpyxl`) — use the fully-qualified system Python path
(`C:\Python314\python.exe`) for `build_master_workbook.py` and other non-crawl4ai
scripts if `python` was recently pointed at the venv.
**Status:** Documented, no further action needed.

---

## Folder Reorganization — 2026-08-01

**Issue Type:** Housekeeping, not a scraping issue
**Description:** All school-scraping work (scrapers, per-school CSVs, master workbook,
source-urls doc) was originally created loose in the `c:\Scraper` root, alongside the
unrelated Opportunities Hub scraper project. Per user request, everything specific to
this effort was moved into `c:\Scraper\Dezi Art Prize Student Data Scraping\`.
**Action Needed:** `cache/` and `.venv_crawl4ai/` were deliberately left at the
`c:\Scraper` root (shared/reusable infra, per user decision) rather than moved alongside
the scripts. Every scraper's cache path default was updated from `"cache"` to
`os.path.join("..", "cache")`-style relative paths so they still resolve correctly when
run from inside this folder. Verified working after the move (RIT scraper + master
workbook rebuild both tested successfully from the new location).
**Status:** Resolved.

---

## Multi-School Batch 3 (Art Student Rosters) — 2026-08-01

Context: continuing into Batch 3 (Yale, CMU, Cornell, UW-Madison, Ohio State) per
`art_school_scraping_urls.md`'s priority order.

### Yale — doc's guessed URL pattern actually works
**Issue Type:** Confirmed working, plus a tricky parsing bug
**Description:** The doc's guessed pattern `art.yale.edu/exhibitions/spring-{year}-
{department}-thesis` is correct and static (wiki-style Yale School of Art site, no JS
rendering needed). Verified working for Painting/Printmaking, Sculpture, Photography,
and Graphic Design across both 2025 and 2026 (8 pages). Each page has a "Featuring
[names]" sentence listing the cohort. A separate numbered-slug URL scheme also exists on
`yalemfathesis.viewingrooms.com` (an Artlogic-powered gallery site, e.g.
`.../exhibitions/26-picture-show-2026-mfa-photography-thesis-exhibition/overview/`,
supplied by the user) — confirmed to return the *same* names as the simpler wiki URLs, so
only the simpler pattern was scraped to avoid redundant duplicate data.
**Action Needed:** Initial parser bug: some student names contain periods (e.g.
"Z.T. Nguyen"), which broke a naive "stop at the first period" sentence-boundary
heuristic and silently truncated the Painting 2025 list from 19 names down to 7. Fixed
by matching known trailing phrases ("Exhibition identity by", "Organized by", "Public
reception", "Editor details", "Learn more") as the real list terminator instead of any
bare period. Result: 110 students across 8 pages, 0 errors. No email/portfolio published
on any of these pages — names only, like Temple's data.
**Status:** Resolved.

### CMU — clean source, required using embedded JSON metadata instead of visible HTML
**Issue Type:** Parsing approach correction
**Description:** `art.cmu.edu/mfa/students/` lists 14 current MFA students
(First/Second/Third-Year), each linking to a per-student profile page. Each profile
page's visible `<h1>` is just a generic "People" breadcrumb, not the student's name —
initial scraper used this and produced garbage ("People" as every name). The real name
lives in an `<h2 class="entry-title">`, and — more importantly — there's a
`dataLayer_content` JSON blob embedded in each page containing structured `email`,
`personal_website`, and `pageCategory` (e.g. `["third-year-mfa","people"]`) fields,
which is far more reliable than scraping loose visible text or guessing class-year from
page position on the index.
**Action Needed:** Rewrote the scraper to pull name from `<h2 class="entry-title">` and
email/website/class-year from the embedded JSON. Result: 14/14 students, real
`@andrew.cmu.edu` or personal emails for 8 of them; the other 6 (all First-Year
candidates) genuinely have `"email":""` in CMU's own page metadata — confirmed not a
parsing gap, they simply haven't listed one yet.
**Status:** Resolved.

### Cornell — dead end after two rounds of research; site appears to no longer render past-show content
**Issue Type:** Site behavior issue, not fixable on our end
**Description:** Every Cornell AAP exhibition URL tried — both the doc's originals
(`thesis-group-exhibition`, `mfa-students-deep-end`) and new ones found via a follow-up
web search (`mfa-virtual-exhibition-*`, `b-f-a-thesis-with-a-trace`,
`senior-bfa-thesis-exhibition`) — render as a generic "upcoming event" shell page with
no actual student names, regardless of which specific exhibition slug is requested.
Confirmed this is not a plain-fetch/JS-rendering issue: crawl4ai with a real headless
browser returns the exact same generic shell content for two different exhibition slugs.
This suggests Cornell's site only fully renders whatever is the *current/next* upcoming
event and these specific past-show pages no longer serve their original content, even
though a general web search's own AI synthesis found real names for "Into the Deep End"
(Hyunjin Park, Andy Nicholas Li, etc.) — that data is evidently no longer being served on
the live page as fetched.
**Action Needed:** None — no usable student data found on any Cornell URL across two
research rounds. Not scraped.
**Status:** Deferred/dead end. Revisit only if Cornell's site structure changes or a
different, still-live URL is found.

### Ohio State — found working sources, but one cohort's names are genuinely ambiguous
**Issue Type:** Mixed — one clean source, one ambiguous source requiring user judgment call
**Description:** The doc's original OSU URLs (`grad-studies/current`, `alumni-friends/
mfa-alumni-directory`) turned out to be empty scaffolding or JS/filter-driven directories
with "0 results found" even via crawl4ai. A follow-up web search found two real
individual exhibition pages instead: `art.osu.edu/events/mfa-thesis-exhibition-
desire-lines` (2025, "Participating Artists:" list, 13 clean comma-separated names) and
`uas.osu.edu/events/waiting-light-change` (2026, "Participating Artists:" text but
genuinely ambiguous — 9 names run together with inconsistent "Lastname, Firstname" vs.
"Firstname Lastname" formatting and no reliable delimiter between people, e.g. "Banerjee,
Shaheen Beardsley, Maria Conlon, ...").
**Action Needed:** 2025 scraped cleanly (13 names, straightforward comma split). For
2026, per user decision, included a best-effort reconstruction (pairing each token's
trailing surname with the next token's leading given name) yielding 8 people (source page
says "nine MFA graduate students" — likely a mononym or off-by-one in their own summary
text) — every 2026 row is explicitly flagged in `notes` as "UNVERIFIED name
reconstruction" so this is never mistaken for confirmed data.
**Status:** Resolved for 2025 (high confidence); 2026 resolved but flagged low-confidence
per user's explicit acceptance of the risk.

### UW-Madison — real graduate directory found (better than the doc's exhibition-archive suggestion), plus an expired SSL cert
**Issue Type:** Better source found + site-side TLS certificate expiry
**Description:** The doc's suggested URL (`art.wisc.edu/category/events/mfa-exhibitions/`)
is a thin, one-post-per-student news archive (names only, no email) with pagination —
same low-richness pattern as Temple/Yale. Found a much better source instead:
`art.wisc.edu/people/graduate-students/` — a single static page listing all 20 current
MFA students with class year (MFA '27-'29) and 19 real `@wisc.edu` emails. However,
`art.wisc.edu`'s TLS certificate is **expired on their server** (confirmed:
`ssl.SSLCertVerificationError: certificate has expired`, though `curl` tolerated it) —
per user decision, disabled certificate verification for this one specific host only
(public, read-only page, no sensitive data exchanged) rather than leaving the source
unscraped.
**Action Needed:** Built `uw_madison_scraper.py` with `ssl.CERT_NONE` for this fetch only.
Two parsing bugs found and fixed: (1) my "Facilities & Contact" terminator string didn't
match because the real text has an HTML entity (`&#038;`, decodes differently than
expected) — fixed by searching for just "Facilities" instead; (2) each student's trailing
pronoun/"Follow" text was leaking into the *next* student's captured name (e.g. "He/They
Follow Anastasiia Bulatova") — fixed by stripping known leading noise patterns after
each match. Result: 21/21 students, 19 with real emails.
**Status:** Resolved.
