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

---

## Multi-School Batch 4 (Art Student Rosters) — 2026-08-01 (in progress)

Context: continuing into Batch 4 (SVA, Pratt, MICA, BU, CCA, MassArt, U Michigan) per
`art_school_scraping_urls.md`'s priority order. This entry covers Pratt and BU
(completed); SVA, MICA, CCA, MassArt, and U Michigan are still open/in progress.

### SVA — dead subdomains + one live page with no extractable names
**Issue Type:** Mostly dead ends
**Description:** Two of the doc's SVA subdomains are dead:
`mfafineart.sva.edu` doesn't resolve (DNS failure — note this is a different, similarly
named subdomain from the live `mfafinearts.sva.edu`), and `mfavisualnarrative.sva.edu`
fails TLS handshake. `artpractice.sva.edu` redirects and loads, but the MFA Art Practice
program has been **discontinued** ("no longer accepting applications for future
cohorts") — no current student roster. `mfafinearts.sva.edu` redirects to
`sva.edu/academics/graduate/mfa-fine-arts`, which has a "Student Work" subpage
(`/student-work`) — but that page shows only a "SHOW MORE" button with no actual names
in either a plain fetch or a crawl4ai-rendered fetch (likely an infinite-scroll/API-driven
gallery that a simple render-and-wait doesn't trigger).
**Action Needed:** None found. Not scraped.
**Status:** Deferred/mostly dead end. Revisit only if SVA's Student Work gallery's
underlying data endpoint is identified (e.g. via browser devtools network inspection,
which isn't available in this environment).

### Pratt — large 2026 "Pratt Shows" archive found, much bigger than the doc suggested
**Issue Type:** Doc undersold this source + one format is ambiguous
**Description:** The doc only mentioned "MFA Thesis Exhibition Part 1/2." The real 2026
event hub (`pratt.edu/pratt-shows/`) lists 30+ distinct discipline-specific thesis show
pages. Per user decision, scoped to MFA Thesis (Parts 1-2) plus BFA fine-art disciplines:
Painting (6 weeks), Drawing (3 weeks), Sculpture and Integrated Practices, Printmaking,
and BFA/MFA Photography (12 pages total for Photography). Painting/Drawing/Sculpture/
Printmaking/MFA-Thesis all use a clean "Exhibiting Artists: Name1, Name2, ..." format.
Photography pages use a different, structurally ambiguous format instead:
"Students featured:<br>Name<br>Name<br>Name" where `<br>` tags don't reliably align with
name boundaries (e.g. "Alejandro<br>Yullo Eli Meyer<br>Tesia Han" — genuinely unclear
where one name ends and the next begins, likely a data-entry mistake on Pratt's own site).
**Action Needed:** Built `pratt_scraper.py` with two parsers: a "clean" comma-split parser
(also required an initial terminator-string fix, same class of bug as Yale/Ohio State —
the naive "Schafler Gallery" stop-string didn't match on the MFA Thesis pages, which
instead say "Dock 72" / repeat the show title, causing the first run to grab 53 "students"
for MFA Part 1 including curatorial bio text — fixed with a multi-phrase terminator
regex), and a "brk" parser for Photography that treats each `<br>`-separated chunk as one
row verbatim, every row flagged UNVERIFIED per user decision. Also found genuine content
gaps unrelated to parsing: MFA Thesis Part 2's page describes only the curator's bio with
no student list at all, and several Photography show pages (4, 6, 8, 9, MFA-1, MFA-2)
have no "Students featured" text at all — confirmed these are real gaps on Pratt's side,
not parser misses. Result: 107 students (17 MFA + 41 clean BFA disciplines + 49
unverified Photography).
**Status:** Resolved.

### BU — excellent clean source, better structured than most schools found so far
**Issue Type:** Confirmed working, high data quality
**Description:** `bu.edu/cfa/featured-work/mfa-thesis-2024/` has an "Exhibiting Students
by Program" section broken cleanly into 5 MFA programs (Painting, Sculpture, Visual
Narrative, Print Media & Photography, Graphic Design), each a `•`-bullet-separated name
list with a reliable terminator ("Faculty Advisors, Chairs, and Collaborators").
**Action Needed:** Built `bu_scraper.py`. Result: 60 students across 5 programs (page's
own summary text says "61 Artists" — a one-off discrepancy in their own marketing
copy, not a parsing gap; all 60 rows are real names cleanly split by program).
**Status:** Resolved.

### SVA — user found a much better source than the doc's dead subdomains
**Issue Type:** Doc scope correction (major upgrade) + several parsing bugs
**Description:** User pointed to `sva.edu/events/search/type/Exhibition`, a paginated
archive of ~1,050 exhibition event pages (22 list pages × ~50 events each), each
event page potentially containing an "Exhibiting artists include ..." or "Artists
include ..." sentence naming the show's participants. This is a completely different
(and far richer) source than the dead/broken subdomains checked earlier in Batch 4.
Scoped per user decision to 2026-dated exhibitions only: fetched all 22 list pages to
collect event slug + date + department per card (from `calendar-card-*` HTML classes),
filtered to the 53 events dated 2026, then fetched those individual pages.
**Action Needed:** Three parsing bugs found and fixed via user-supplied examples:
(1) the name list is often prefixed with a department/cohort description before the
actual names start, e.g. "Exhibiting artists include **BFA Visual and Critical Studies
students** Elsa Chen, ..." — fixed by stripping everything up through the last
"student(s)" occurrence; (2) some pages use "Artists include:" with a leading colon,
which leaked into the first captured name — fixed by stripping leading `": "`;
(3) parenthetical program/degree annotations contain their own commas (e.g. "Paul Simon
(MFA 2019 Photography, Video and Related Media)"), which broke a naive comma-split —
fixed by masking commas inside parentheses before splitting, then stripping the whole
parenthetical afterward; (4) the sentence-terminator pattern didn't account for curly
quote characters immediately following a period (e.g. "Stephanie Moon.” “Circuit
Tension,”...", where "”" doesn't match a plain `[A-Z]` terminator check), which let one
page's captured text run on for many extra "names" that were actually a repeated image
caption — fixed by adding curly-quote characters to the terminator character class.
Also added a safety filter: if a captured "name" has more than 5 words (a symptom of a
page listing names space-separated with no delimiters at all, confirmed on the
"SVA + NASA at the Intrepid Museum" page — 20+ names run together with no commas), skip
it rather than emit an unreliable merged blob. Result: 85 students from 7 of the 53
2026-dated pages (the rest had no extractable "artists include" sentence — image-only
event pages). Every row is flagged that the exhibition may mix current students with
alumni/faculty/guest artists, since these are curated shows, not clean class rosters.
**Status:** Resolved for 2026-dated exhibitions. ~1,000 more (2016-2025) events exist in
this same archive if a future batch wants to go further back — same scraper/pattern
should work, just change the year filter.

### Pratt (from user) — beyond-digital and pratt-shows-2026 hub checked
**Issue Type:** Confirmed not worth adding
**Description:** User asked to check `pratt.edu/pratt-shows/pratt-shows-2026/` (same
page as the hub already scraped — 395,396 bytes, identical to what
`pratt_scraper.py`'s hub fetch already covers) and `pratt.edu/events/beyond-digital/`
(has a "Participating Artists:" list, but names are space-separated with no delimiters
at all — "Tess Adams Nicolás Cuestas Nate King..." — same ambiguity as the Photography
`<br>`-chunk problem, and the page describes them as Pratt's "Digital Arts **alumni**
community," not current students).
**Action Needed:** None — hub page already covered; beyond-digital skipped due to both
name ambiguity and being alumni rather than current-student data.
**Status:** Resolved (no changes needed).

### MICA — found the real per-program Grad Show pages, plus 2 nested-list parsing bugs
**Issue Type:** Doc's hub page was thin, found the real source + fixed bugs
**Description:** `mica.edu/gradshow` hub page describes the show but lists no names
directly. Found the real source: `mica.edu/.../commencement/grad-show-2026/` links to 14
per-program pages (Community Arts, Curatorial Studies, Filmmaking, Graphic Design MA/MFA,
Illustration MA + Practice, Painting, Mount Royal, Photography, Sculpture, Social Design,
Studio Art, Teaching), each with a "Participating students" (or just "Participating")
`<ul>` of `<li><strong>Name</strong> (website | Instagram)</li>` entries.
**Action Needed:** Two real bugs found and fixed: (1) heading text varies ("Participating
students" vs. bare "Participating&nbsp;") — broadened the regex to accept both; (2) the
Curatorial Studies page nests a sub-`<ul>` of exhibition-detail `<li>`s *inside* a
student's own `<li>` (e.g. exhibition dates/location), which broke a naive "match up to
the first `</ul>`" approach and silently dropped all but the first student on that page —
fixed by writing a small tag-depth tracker (`find_top_level_items`) that correctly skips
over nested `<ul>...</ul>` blocks rather than using a single regex. Also handled: names
split across two adjacent `<strong>` tags (e.g. "Taro" / "Cantú" as two tags for one
person) by joining all `<strong>` fragments per `<li>`; HTML entity unescaping (`&uacute;`
etc.) via Python's `html.unescape`. Result: 132 students across all 14 programs, 109 with
a real website/Instagram link.
**Status:** Resolved.

### CCA — portal is login-walled, found a public newsroom article instead
**Issue Type:** Login wall correctly identified and worked around with a legitimate public source
**Description:** The doc's/redirected event URLs live on `portal.cca.edu`, confirmed to be
a login-walled internal student/staff portal ("CCA Portal Dashboard", "Log in" present) —
per CLAUDE.md, did not attempt to bypass this. Found a genuinely public alternative: CCA's
own newsroom article announcing the 2026 MFA Fine Arts Thesis Exhibition, with a clean
"The international group of artists include Name1, Name2, ..., and NameN." sentence.
**Action Needed:** Built `cca_scraper.py` targeting the newsroom article. Result: 19
students, matching the article's own name count exactly. Note: this only covers MFA Fine
Arts — the Design Division's graduation exhibition (also mentioned in search results) is
on the login-walled portal with no public equivalent found, so it's not included.
**Status:** Resolved (MFA Fine Arts only; Design Division not accessible).

### MassArt — doc's URL pattern outdated, found current year via search
**Issue Type:** Doc's guessed pattern didn't exist for current year, found real URLs
**Description:** The doc's `2023_massart_mfa_thesis`-style guess 404s for all years
2023-2026. The 2022 page (`calendar.massart.edu/event/2022_mfa_thesis_exhibition`) does
work and has a clean "FEATURED ARTISTS: Name (Program)" format, confirming the site's
general pattern — but the URL *scheme* changed for later years. Found the real 2026 URLs
via web search: Part I is `.../event/2026-mfa-thesis-exhibition-PARTI` (hyphenated,
different casing/format entirely) and Part II is
`.../event/2026-spring-mfa-thesis-exhibition-part-ii` (yet another distinct slug pattern
— not a simple "PARTII" swap). Both use "FEATURED ARTISTS: Name | Program" (pipe-
delimited, different from 2022's parenthetical format).
**Action Needed:** Built `massart_scraper.py` targeting both 2026 URLs directly (2022 not
scraped, since the user's scope has consistently been current/2025-2026 cohorts across
other schools). Result: 5 (Part I) + 6 (Part II) = 11 students, exactly matching the
site's own "all eleven 2026 MFA thesis candidates" summary text.
**Status:** Resolved.

### U Michigan Stamps — Cloudflare challenge actually passed by crawl4ai; gallery data is genuinely messy
**Issue Type:** Blocker resolved better than expected + significant data-quality nuance
**Description:** Contrary to the Batch 4 checkpoint note (assumed this would resist
crawl4ai like Otis's old subdomain), crawl4ai's headless browser DID get past the
Cloudflare interactive JS challenge here (confirmed: no "Just a moment..."/`cf_chl_opt`
markers in the rendered output). Found two source types: (1) the 2025 MFA Thesis
Exhibition page — clean, dated, "features the work of MFA students Name1, Name2, ...".
(2) Per user's explicit request, also scraped the Graduate and Undergraduate Research &
Creative Work gallery pages — these turned out to be two different carousels bundled on
one page: a clean one ("Stamps MFA 2026: Name" / "Name: 2024 MFA Profile" / "Name:
Profile") with reliable name+year (year present or explicitly absent), and a second,
structurally different one ("Name: Artwork Title", e.g. "Ruth Burke: Gopi") with no year
information at all and — confirmed on a real entry — inconsistent name/title order
("The Stop Motion Animator's Cat: Kate Bonello" has the artwork title *first* and the
real name *second*, unlike every other entry on the page).
**Action Needed:** Built `umich_scraper.py` (uses crawl4ai, same `.venv_crawl4ai`
requirement as `vcu_scraper.py`) with three parse paths: clean-with-year, clean-no-year,
and a best-effort ambiguous path (splits on the first colon, assumes name-first) — every
ambiguous-path row is flagged UNVERIFIED with an explicit note about the confirmed
reversed-order failure mode, so "The Stop Motion Animator's Cat" is never mistaken for a
real name without a warning attached. Deduplicates by name within the clean-path results
only (so a student doesn't appear twice from the same clean carousel) but intentionally
does NOT dedupe across the thesis page vs. gallery vs. ambiguous-carousel results, since
those are genuinely different sources with different confidence levels — a student like
"Hannah Buchanan" legitimately appears twice (once with year 2025 from the thesis page,
once with no year from the gallery "Profile" entry) and merging them risked hiding which
claim came from which source. Result: 7 (thesis, clean) + 44 (grad gallery, mixed
clean/ambiguous) + 18 (undergrad gallery, entirely ambiguous) = 69 total entries, 41 of
which are UNVERIFIED.
**Status:** Resolved, with the caveat that ~59% of U Michigan's rows are explicitly
flagged low-confidence per the user's own choice to include the ambiguous gallery data.

---

## Batch 4 Complete — Summary

All 7 schools in Batch 4 (SVA, Pratt, MICA, CCA, MassArt, BU, U Michigan Stamps)
investigated; master workbook now has 19 tabs / 1,749 students total. Batch 4 required
more real-time debugging than any prior batch — 3 schools (SVA, Pratt, U Michigan) had
genuinely ambiguous source-page text formats requiring explicit UNVERIFIED flagging
rather than confident extraction, reflecting that art-school exhibition pages get less
editorial care than school directories/rosters (typos, inconsistent delimiters, and at
least one confirmed reversed name/title order in the wild).

Next: Batch 5 (Cranbrook already done, CalArts, Cooper Union, UCLA, SCAD, Columbia
College — the last marked "unconfirmed source" in the original doc).

---

## Multi-School Batch 5 (Art Student Rosters) — 2026-08-02 — FINAL BATCH

Context: the last batch per `art_school_scraping_urls.md`'s priority order — CalArts,
Cooper Union, UCLA, SCAD, Columbia College Chicago (the last flagged "unconfirmed" in
the original doc). All 28 schools from the original doc have now been investigated.

### CalArts — real source found via search, required crawl4ai for cookie-consent/Turnstile
**Issue Type:** Doc's library/news leads were dead ends; found the real page via search
**Description:** The doc's suggested `library.calarts.edu/digitalcollections/masterstheses`
only links to a login-walled OCLC proxy (`calarts.idm.oclc.org/login?url=...`) — not
publicly accessible, not attempted. `calarts.edu/news` has no thesis-specific posts.
Found the real 2026 source via web search: `calarts.edu/high-pass` — "High Pass" is the
BFA Class of 2026 group exhibition (29 artists, Art + Photo Media). Plain fetch returns
mostly cookie-consent-banner boilerplate with no visible name list; crawl4ai renders the
full page (confirmed the "Exhibiting Artists include:" sentence exists near the very end
of the text, after ~27KB of consent-manager/cookie-provider text) — this site uses
Cloudflare Turnstile bot-detection alongside the cookie consent dialog.
**Action Needed:** Built `calarts_scraper.py` (requires `.venv_crawl4ai`, same as
`vcu_scraper.py`/`umich_scraper.py`). Result: 29/29 students, matching the page's own
count exactly.
**Status:** Resolved.

### Cooper Union — confirmed dead end
**Issue Type:** No usable data found, matches doc's own caveat
**Description:** Both the 2026 End of Year Show page and the Art galleries page (checked
via plain fetch AND crawl4ai) contain zero student names — only event logistics and
generic institutional history/nav text. This matches the doc's own note that "Cooper's
tradition is to list works by artist name only" — the implication being that attribution
lives on physical gallery wall text or a printed program, not the website.
**Action Needed:** None found. Not scraped.
**Status:** Confirmed dead end.

### UCLA — excellent clean source, portfolio/Instagram links included
**Issue Type:** Confirmed working, high data quality
**Description:** The doc's suggested event-archive URLs (`art.ucla.edu/events`,
`goarts.ucla.edu/events/mfa-exhibition-1`) were not the best source. Found
`art.ucla.edu/graduate-students` (redirects through `www.` + an S3 redirect chain,
needed `-L` to follow fully) — a clean, current directory of graduate students by area
of study (Ceramics, Interdisciplinary Studio, New Genres, Painting and Drawing,
Photography, Sculpture), each name hyperlinked to a personal portfolio or Instagram.
**Action Needed:** Built `ucla_scraper.py`. Result: 38 students across 6 areas, 29 with
a real portfolio/Instagram link, 9 without (genuine gap on UCLA's page, not a parsing
issue). No email or graduation year published on this page.
**Status:** Resolved.

### SCAD — real source found, but confirmed to be non-current data — skipped per user decision
**Issue Type:** Data-currency problem, not a scraping/access problem
**Description:** The doc's `scad.edu/academics/programs/*/student-work` pattern works
(behind a Cloudflare challenge, bypassed via crawl4ai — confirmed working across all 16
verified program slugs: Painting, Illustration, Photography, Sequential Art, Graphic
Design, Industrial Design, User Experience Design, Animation, Motion Media Design,
Visual Effects, Furniture Design, Interior Design, Fashion, Fibers, Jewelry, Accessory
Design). Each page has a clean `"Artwork Title" | Student Name` caption format. However,
inspecting the Painting page's image filenames (e.g.
`painting-student-work-2020-jessie-lefebre.jpg`) revealed this is a **marketing
showcase of past graduates' best work, predominantly dated 2020** — not a current
2025/2026 graduating-class roster like every other source in this project.
**Action Needed:** Per user decision, skipped entirely — this data doesn't serve the
project's goal of reaching current/recent students. Not scraped.
**Status:** Resolved (deliberately not scraped; logged so this isn't re-attempted
without first re-checking whether SCAD has since added a current-year showcase).

### Columbia College Chicago — confirmed real, resolving the doc's "unconfirmed source" flag
**Issue Type:** Doc's guess ("Manifest") was correct; found the specific page + a genuine
source-side data-quality quirk
**Description:** The doc's guess that "Manifest" (Columbia's annual arts festival) was
the right lead is confirmed correct. The 2026 event-schedule hub page
(`students.colum.edu/.../school-of-visual-art-manifest-event-schedule-may-16-2026`)
itself has no individual names (only promotional copy about "our graduating students"
generally), but links to individual exhibition subpages (via `.html` URLs that 302-redirect
to extensionless versions). The "Human Condition: 2026 BA/BFA in Fine Art Exhibition"
subpage has two clean `<br>`-separated "Featuring works by:" lists (Hokin Gallery,
C33 Gallery). Two of the 24 names have unusual internal letter-spacing in the raw HTML
itself (e.g. "Faith H o g a n", "Liz Z e r m e n o Robles") — not a parsing artifact,
confirmed present in the source `<br>`-delimited text — kept verbatim rather than
"corrected" (guessing the intended spelling would be fabricating data), with a specific
note flagging this on each affected row. The MFA Visual Arts and Photography Graduate
Exhibition and Photography Exhibition subpages were also checked but have no name lists
at all (event logistics only).
**Action Needed:** Built `columbia_scraper.py`. Result: 24/24 students (13 Hokin Gallery
+ 11 C33 Gallery), 2 flagged for the letter-spacing quirk.
**Status:** Resolved — Columbia is no longer "unconfirmed," it's a working source
(narrower than hoped: only the BFA/BA Fine Art show has extractable names, not the
MFA/Photography shows).

---

## Batch 5 Complete — ALL 28 SCHOOLS FROM THE ORIGINAL DOC NOW INVESTIGATED

Master workbook: 22 tabs, 1,840 students total. Final tally across all 5 batches:
21 schools yielded usable data (RIT, MCAD, Cranbrook, RISD, Otis, Parsons, Temple/Tyler,
VCU, Yale, CMU, UW-Madison, Ohio State, Pratt, BU, SVA, MICA, CCA, MassArt, U Michigan
Stamps, CalArts, UCLA, Columbia College Chicago — that's 22, all schools scraped
successfully in some form). 3 schools were investigated and confirmed to have no
usable public data or were deliberately excluded: Alfred University (dead
thesis-archive structure, Batch 2), Cooper Union (no names published on the website
at all, Batch 5), SCAD (real data exists but is non-current/2020-era, excluded per
user decision, Batch 5). Cornell (Batch 3) was also a dead end — its specific
exhibition URLs render a generic "upcoming event" shell with no names, even via
crawl4ai — bringing the true "no usable data found" count to 4 schools out of 28.

---

## Batch 6 (New Doc: Ranks ~31-70) — 2026-08-04

Context: the user supplied a new research document,
`next urls art prize 31-50.md`, listing 28 more schools beyond the original project's
scope. Per user decision, this batch covers only the doc's own "Tier 1" pick — the 4
schools it flags as cleanest/no-JS-needed: University of Iowa, University of Washington
(Henry Art Gallery), UT Knoxville, and BGSU. A 5-URL spot-check done during planning
already found 2 of 5 top doc claims needed correction (same reliability pattern as
every previous batch's source doc) — see plan file for details.

### University of Iowa — confirmed excellent, 2 real parsing bugs fixed
**Issue Type:** Confirmed working as claimed + source-side data quirks
**Description:** `art.uiowa.edu/events/mfa-virtual-exhibitions` is exactly as clean as
claimed: static HTML, ~18-21 named MFA students with discipline, each linking to an
individual Matterport 3D exhibition tour. Spans 2024-2026 on one continuous page (not
separate year-URLs) — per user decision, took the whole page rather than an arbitrary
cutoff, tagging each student with their actual exhibition year.
**Action Needed:** Two bugs fixed: (1) one entry's date range has a genuine source typo
("April 8, 20024" instead of "2024"), which broke a naive first-4-digits year regex —
fixed by taking the *last* year match in the date-range string instead of the first,
which correctly resolves to the real year in both the typo case and normal cases;
(2) several `portfolio_url` values were wrapped in Outlook Safelink email-protection
redirects (e.g. `nam12.safelinks.protection.outlook.com/?url=...`) rather than pointing
directly at Matterport — apparently pasted in from a forwarded email into the CMS —
fixed by unwrapping the real destination URL from the `url=` query parameter. Also
unescaped HTML entities in name/discipline fields (`&amp;` → `&`). Result: 18/18
students, all portfolio URLs now clean Matterport links.
**Status:** Resolved.

### University of Washington (Henry Art Gallery) — confirmed working, discipline claim corrected
**Issue Type:** Partially confirmed; doc overclaimed per-student discipline mapping
**Description:** `henryart.org/exhibitions/2026-university-of-washington-mfa-mdes-thesis-exhibition`
does list 10 real names in clean static HTML (`<h4>Artists</h4><div class='indent'>
Name<br>Name<br>...</div>`), confirmed during pre-batch spot-check and again while
building the scraper. However, the doc's claim of "name + discipline" per student does
NOT hold — the page only describes the program's disciplines (New Genres, Painting +
Drawing, 3D4M, MDes) collectively, with no per-student mapping. Per the plan, did not
guess/fabricate which discipline each person belongs to.
**Action Needed:** Built `uw_art_scraper.py`. `major` field set to a generic
"MFA/MDes (UW Art — discipline not specified per student)" label rather than inventing
a mapping. Scoped to the 2026 page only (current year), per the "most recent year"
scope decision. Result: 10/10 students.
**Status:** Resolved.

### UT Knoxville — confirmed dead end, genuine infrastructure-level block
**Issue Type:** Hard blocker — CAPTCHA + connection failures, not attempted to bypass
**Description:** The doc's cited TRACE URL (`trace.tennessee.edu/utk_ewing/20/`) was
already confirmed wrong during pre-batch spot-check (one document record, not a class
roster). Per the plan, investigated the real collection index instead
(`trace.tennessee.edu/utk_ewing/`) — this returns HTTP 405 with an AWS WAF
**"Human Verification" CAPTCHA challenge page** (`x-amzn-waf-action: captcha` header,
`window.gokuProps`/`awswaf.com` challenge script), both via plain fetch and via
crawl4ai's headless browser (crawl4ai reached the same 405/CAPTCHA page, confirming
this isn't a simple JS-rendering gap — it needs an actual human to solve a challenge).
Per CLAUDE.md, did not attempt to solve or bypass this. The doc's two fallback URLs
(`ewing-gallery.utk.edu/upcoming-exhibitions/`, `art.utk.edu/people/graduate-students/`)
were also tried — both fail with a **TCP-level connection timeout** (`net::
ERR_CONNECTION_TIMED_OUT`, confirmed via both curl and crawl4ai/Playwright), even
though DNS resolves correctly for both hostnames — this looks like the entire
`utk.edu` domain is unreachable from this environment/network, not a per-page issue.
**Action Needed:** None — genuine hard blocker across all 3 known URLs for this school.
Not scraped.
**Status:** Confirmed dead end this session. Worth retrying from a different network
environment in the future, since the TCP timeout pattern suggests this may be
environment-specific rather than a permanent block on UTK's end.

### BGSU — confirmed excellent, clean repository as claimed
**Issue Type:** Confirmed working as claimed, no significant issues
**Description:** `scholarworks.bgsu.edu/ms_art/` is exactly as clean as claimed: a
Digital Commons/bepress-style repository with `<h3 id="year_YYYY">Theses from YYYY</h3>`
section headers, each followed by `<p class="article-listing"><a href="record-url">
Title</a>, Author Name</p>` entries. Scoped to 2025 (most recent complete year; 2026 has
no entries yet this early in the year), per the year-scope decision.
**Action Needed:** Built `bgsu_scraper.py`. Result: 6/6 students for 2025, matching the
doc's "~5-8 MFA/year" estimate exactly. `portfolio_url` points to each thesis's
ScholarWorks repository record (not a personal site) — noted in `notes`.
**Status:** Resolved.

### Batch 6 summary
3 of 4 Tier-1 schools scraped successfully (Iowa 18, UW Art 10, BGSU 6 = 34 new
students). UT Knoxville confirmed unreachable (CAPTCHA + connection timeouts across
all 3 known URLs). Master workbook now has 25 tabs, 1,874 students total. Tier 2
(SUNY New Paltz, NMSU, UNM, UGA, UIC, Tulane, Bard, Herron, Syracuse) and Tier 3
(the JS-microsite independent colleges) from the new doc remain for a future batch,
per the user's explicit scope choice for this session.

---

## Email Discovery Pass (Enrichment, not scraping)

New effort starting 2026-08-06: for students already in the master list with a name
but no email, use `WebSearch`/`WebFetch` interactively (no new script/API) to find a
real, verifiable email, one school at a time, smallest school first. Confidence gate:
only write an email directly into the CSV if it's clearly corroborated (own domain,
matching thesis/name, confirmed personal site); otherwise leave `email` blank and note
an "UNVERIFIED possible email" lead for manual review. No pattern-guessing emails
(e.g. assuming `firstname.lastname@college.edu` without a verified source), no
attempts to bypass logins/CAPTCHAs/blocked pages.

### BGSU — 4 of 6 emails found
**Description:** Ran individual searches per student.
- **Syed Fatmi**: confirmed high-confidence — `syedway.digital@gmail.com`, found on his
  own portfolio site `syedway.com` (matches thesis title "OMNISYS" and LinkedIn).
  Updated `portfolio_url` from the bare ScholarWorks record to his real personal site.
- **Kamrun Mim**: initially blocked (`kamrunnahermim.com` 403'd on fetch), but the user
  found the email manually — `kamrunmim.print@gmail.com` via
  `kamrunnahermim.wordpress.com/about` (bio/CV section), a different domain
  (Wordpress, not the .com site) than what search first surfaced. `portfolio_url`
  updated to the Wordpress site.
- **Rachel Krieger**: user manually confirmed `rachelle@rachellekrieger.com` via
  `rachellekrieger.com/contactinfo` — this was one of several same-name candidates
  found in search that couldn't be disambiguated automatically; the user's manual
  check resolved it. `portfolio_url` updated to her site.
- **Nick Felaris**: user manually confirmed `nickfelaris@hotmail.com` (source not
  specified in detail, taken as user-verified).
- **Precious Gyekye**: still not found — confirmed as a current BGSU Graduate Teaching
  Associate, but BGSU's directory page is JS-rendered (not fetchable statically) and
  the only "contact info" surfaced was a masked ZoomInfo listing (data broker, blocked
  on fetch anyway) — not used as a source.
- **Peter Kiladejo**: still not found — a same-name Nigerian gallery-represented artist
  ("Adetope Peter Kiladejo") exists online but couldn't be confirmed as the same BGSU
  MFA student, so nothing was written.
**Action Needed:** Precious Gyekye and Peter Kiladejo remain open — may need manual
lookup (same pattern as Kamrun Mim/Rachel Krieger, where a human catch found what
automated search missed).
**Status:** Resolved (partial — 4/6 found; 2 remain, per confidence-gate rules).

**Pattern noted:** for ambiguous common-name cases, the user's manual verification (a
quick targeted search + visiting the right contact page) succeeded twice where
automated search alone stalled on multiple same-name candidates — worth flagging
ambiguous cases back to the user rather than giving up on them outright.

### UW Art — 0 of 10 emails found automatically; 2 manual-follow-up leads flagged
**Description:** All 10 students searched individually. None had a portfolio_url
already on file (all pointed to the generic Henry Art Gallery exhibition page), so
every student needed a fresh search.
- **Jeff Jiang**: personal site `jeff-jiang.com` found — no email visible in static
  HTML (likely a JS-rendered contact form). No email found.
- **Oscar Pearson**: personal site `oscarpearsonart.wixsite.com/studio` found
  (Wix, Instagram @oscarpearson_) — contact page is a Wix form only, no email shown.
  Note: a same-name but unrelated California muralist/gallery artist also surfaces in
  search — confirmed NOT the same person as this UW MFA student.
- **Victoria Mackender**: personal site `vamack.com` found via search, but this
  session's `WebFetch` tool cannot resolve that domain (`getaddrinfo ENOTFOUND`) —
  environment/tool limitation, not a dead site. **Flagged for manual check.**
- **Ryan Walters**: personal site `ryanwalters.art` found via search, but `WebFetch`
  cannot resolve `.art` TLD domains in this environment (same DNS failure pattern).
  **Flagged for manual check.**
- **Stephanie Alacon / Dahae Cheon / Andrew Roibal**: UW's own
  `art.washington.edu/people/<name>` profile pages exist (confirmed via search
  snippets showing MFA program + bio details) but return HTTP 404 when fetched
  directly — likely JS-routed or search index is ahead of a page rename. No email
  found.
- **Li-Yuan Chiou / Alex Moni-Sauri / Chave Pichardo**: no personal site or usable
  contact page surfaced in search at all. No email found.
- UW's general people directory (`art.washington.edu/people-0`, a static
  name/title/email table) was checked directly — none of the 10 current MFA/MDes
  thesis students appear in it (looks like a faculty/staff-only listing, not current
  students).
**Action Needed:** Two real leads need a human to open directly (this tool's fetcher
can't reach them): `vamack.com` (Victoria Mackender) and `ryanwalters.art` (Ryan
Walters) — both are DNS/tool-side failures, not confirmed dead links.
**Status:** Resolved (partial — 0/10 auto-confirmed; 2 flagged for manual check).

**Tooling note:** `WebFetch` in this environment fails to resolve some domains
(`.art` TLD, and `vamack.com` specifically) with `getaddrinfo ENOTFOUND` even though
they appear as live sites in search results — this is a DNS/tool-side limitation, not
evidence the site doesn't exist. Worth trying a plain browser or `curl` manually for
any site this tool reports as unresolvable before concluding no email exists.

### MassArt — 4 of 11 emails found
**Description:** All 11 students searched individually (Part I + Part II of the 2026
MFA Thesis Exhibition). Most had personal portfolio sites, since photography/studio-art
MFA students commonly maintain one.
- **Olivia Greenberg**: confirmed — `oliviadylan129@gmail.com`, from her own site
  `oliviadylanphotography.com/contact`.
- **Anastasia Sierra**: confirmed — `info@anastasiasierra.com`, from her own site
  `anastasiasierra.com/about` (also confirmed via her MassArt x SoWa artist profile,
  which independently listed the same personal site).
- **Shailee Thakkar**: confirmed — `shailee.v.thakkar@gmail.com`, from her own site
  `shaileethakkar.com/aboutme` footer.
- **Antonio Bailey**: confirmed — `antoniobaileylocal@gmail.com`, from his own site
  `antoniobailey.com/about`.
- **Suzi Grossman**: site found (`suzigrossman.com`) but the email is JS-obfuscated on
  the live page; a `WebSearch` summary claimed `Suzi@suzigrossman.com` but a direct
  `WebFetch` of the contact page could not independently confirm it — flagged as
  **UNVERIFIED**, not written, per the confidence-gate rule (search-model summaries
  aren't a substitute for confirming the actual page content).
- **Lisa Spencer**: Visura profile page found but returned HTTP 403 on fetch — no
  email confirmed.
- **Camryn Connolly**: personal site found (`camrynconnolly.com`) but only a Squarespace
  contact form is shown, no visible email.
- **Michael d'Entremont / Christopher Gage Arotsky / Robin Jamkatel / Dylan Record**:
  no personal site or usable contact info surfaced in search at all (MassArt x SoWa
  gallery profile pages exist for some artists in this batch but did not exist/resolve
  for these four specifically).
**Action Needed:** None further this session. MassArt x SoWa (`sowa.massart.edu/artist/
<name>`) is confirmed a useful secondary source — worth checking directly for any
future MassArt name-only student, in addition to a generic search.
**Status:** Resolved (partial — 4/11 confirmed, 1 flagged unverified, 6 no-finds).

### CMU — 3 of 6 remaining emails found
**Description:** All 6 name-only CMU students already had a `portfolio_url` on file
(from the original scrape) — checked each site directly first, per the "reuse existing
portfolio_url" rule, before falling back to search.
- **Sarah Al-Sarraj**: confirmed — `info.sarahalsarraj@gmail.com`, from her own site.
- **Stefanie Zito**: confirmed — `info@stefaniezito.com` (site displayed it in an
  anti-scrape "info[at]stefaniezito.com" format, converted normally).
- **Amber N. Ford**: confirmed — `studio@ambernford.com`, from her own site's /info
  page (her CMU directory page had no direct email, only the school's general inbox).
- **Yiying Wang**: own site `yiyingwang666.com` found (and linked from her CMU
  directory page) but this tool's fetcher can't resolve the domain (DNS failure,
  same pattern as `vamack.com`/`ryanwalters.art` in the UW Art batch) — flagged for
  manual check.
- **Walter Smits**: own site `waltersmits.com` returned HTTP 503 on two separate
  attempts (site appears to be down, not a tool-side block); CMU directory has no
  direct email. Flagged for manual check/retry later.
- **Morgan Strahorn**: only online presence found is a Behance profile with no listed
  contact info; no personal site found.
**Action Needed:** Yiying Wang and Walter Smits both have real sites that just
couldn't be reached this session — worth a manual check or retry.
**Status:** Resolved (partial — 3/6 found this pass; CMU now 11/14 total with email).

### Temple/Tyler — 5 of 30 emails found
**Description:** Largest batch so far (30 name-only students, none had a
`portfolio_url` already on file — the original scrape only captured names from
exhibition schedule text). Tyler's MFA program is well-documented: nearly every
student has an individual `tyler.temple.edu/<name>-mfa-2025` bio page (never had a
direct email) and many maintain personal portfolio sites, which was the more
productive lead.
- **Charles Jarboe** (MFA Glass): confirmed — `charles.jarboe@gmail.com`, own site.
- **Amanda Crain-Freeland** (MFA Sculpture): confirmed — `amandancrain@gmail.com`,
  own site's CV page (her main homepage had no email, only Instagram).
- **Rae Helms** (MFA Printmaking): confirmed — `Raehelmsprint@gmail.com`, own site.
- **Francesca Lally** (MFA Printmaking): confirmed — `francescalally@gmail.com`,
  own site (listed as "francesca lally at gmail dot com", an anti-scrape format).
- **Lilly Buttitta** (MFA Painting): confirmed — `lbuttittaart@gmail.com`, own site.
- 4 more real personal sites were found but had no visible email (Mika Obayashi,
  Sophia Dell'Arciprete, Ari Zuaro, Diego Juarez) — Squarespace/WordPress sites with
  only an Instagram link or an unfetched `/contact` page.
- 4 sites/leads exist but couldn't be reached this session — **flagged for manual
  follow-up**: Maedeh Mehdipour (`maedehmehdipour.com`, HTTP 403), Ben Solo
  (`bensoloart.com`, DNS failure), Pegah Saebi (`pegahsaebi.com`, DNS failure), Mo
  (Maria-Fernanda) Nunez Alzate (`fernandanunez.com`, HTTP 503). Also noted: Logan
  Crompton has a link-in-bio page (`scoby.page/log3y-logan-crompton`) not yet checked.
- Remaining ~17 students (Natalia Purchiaroni, Macy West, Heather Swenson, Theodora
  Dagkli Andonopoulos, Jess Lauro, Esther Park, Mollie Hansen, Ally Messer, Madeline
  Rodriguez, Ruoxua Fan, Ivy Jewell, Angelique Scott, Boi Boy, Gianna Santucci, Dora
  Moghaddamikhomami, Marissa Raybuck): no personal site surfaced in search at all,
  only Tyler bio pages / LinkedIn / gallery mentions with no email. No email found.
**Action Needed:** 4 real sites need a manual visit (403/DNS/503 failures on this
tool's side, not confirmed dead). Also worth trying Tyler's actual bio pages directly
for the remaining students in a future pass — several 404'd or weren't tried when a
better lead (a personal site) was already found first.
**Status:** Resolved (partial — 6/30 confirmed this pass).

**Pattern noted:** Tyler MFA students very commonly have a personal portfolio site
with a "Bio" or "CV" page containing a plain-text email (not always the homepage) —
worth checking `/bio`, `/cv`, `/about`, or `/information` subpages specifically when
a homepage alone doesn't show contact info, since 3 of 5 successful finds this batch
were on a secondary page, not the homepage.

### Manual follow-up round — user resolved 24 more emails across 5 schools
**Description:** Paused after Temple/Tyler to let the user manually check the leads
this session's tools couldn't reach (DNS failures, 403/503 errors, JS-obfuscated
contact pages) plus a few names that had turned up no lead at all via automated
search. The user visited sites directly and/or knew answers already, resolving:
- **UW Art (+6, now 6/10)**: Li-Yuan Chiou (`lychiou@uw.edu`), Victoria Mackender
  (`victoriaa961@gmail.com`, confirms the vamack.com DNS-blocked lead), Oscar Pearson
  (`o2thescar@hotmail.com`), Chave Pichardo (`chavepichardostudios@gmail.com`),
  Andrew Roibal (`AndrewRoibalArt@gmail.com`, also has a UW address
  `aroibal@uw.edu`), Ryan Walters (`RyanWaltersFilms@gmail.com`, confirms the
  ryanwalters.art DNS-blocked lead).
- **MassArt (+2, now 6/11)**: Lisa Spencer (`lisaspencergallery@gmail.com`), Suzi
  Grossman (`Photo@suzigrossman.com` — notably different from the earlier
  **unverified** search-summary guess of `Suzi@suzigrossman.com`, confirming the
  confidence-gate rule was right to hold that one back rather than write it).
- **CMU (+2, now 13/14)**: Walter Smits (`smits.walt@gmail.com`, confirms the
  waltersmits.com 503 lead), Yiying Wang (`yiyingwang194@gmail.com`, confirms the
  yiyingwang666.com DNS-blocked lead).
- **Temple/Tyler (+18, now 23/30)**: Natalia Purchiaroni, Macy West, Mika Obayashi,
  Heather Swenson, Sophia Dell'Arciprete, Ari Zuaro (`@theclaystudio.org`, her
  employer), Esther Park, Mollie Hansen, Maedeh Mehdipour (confirms the
  maedehmehdipour.com 403 lead), Madeline Rodriguez, Ivy Jewell (`@theclaystudio.org`
  — same employer as Ari Zuaro), Angelique Scott, Ben Solo (real name appears to be
  Ben Weidlich, per the email `benweidlich.bs@gmail.com`; confirms the bensoloart.com
  DNS-blocked lead), Logan Crompton (`@kcai.edu` — Kansas City Art Institute, likely
  a current/subsequent affiliation), Boi Boy, Diego Juarez, Gianna Santucci, Pegah
  Saebi (confirms the pegahsaebi.com DNS-blocked lead).
**Action Needed:** None — all provided emails written directly as user-confirmed
(highest confidence tier, no further verification needed).
**Status:** Resolved. Updated running totals: BGSU 4/6, UW Art 6/10, MassArt 6/11,
CMU 13/14, Temple/Tyler 23/30.

**Validation of tooling notes:** every DNS-failure/403/503 lead flagged in the prior
entries turned out to be a real, reachable site once the user checked manually
(vamack.com, ryanwalters.art, waltersmits.com, yiyingwang666.com,
maedehmehdipour.com, bensoloart.com, pegahsaebi.com) — confirms these were
environment/tool-side limitations, not dead links, and validates flagging rather than
discarding such leads.

### Columbia College Chicago — 0 of 24 emails found
**Description:** All 24 name-only BFA/BA Fine Art students (Human Condition 2026
exhibition, Hokin + C33 Galleries) searched individually. Unlike every MFA cohort
searched so far, undergrad exhibition students essentially never have a personal
portfolio site — search results were dominated by noise: Dean's List PDFs (confirms
enrollment, never contact info), LinkedIn stubs with no email, ShopColumbia product
listings (confirms the person is a real Columbia Fine Arts student and sells work
there, but the shop has no per-artist contact page), and frequent wrong-person
name collisions (a different "Cristian Romero" mixed-media artist, a different
"Fiona Connor" established LA artist, a different "Jupiter Flynn").
- **Jenna Davis**: real personal site found (`creatingbyjenna.art`) but no email
  visible — only social handles and an unfetched `/contact` page.
- **Ana Lara**: confirmed as a real Columbia Fine Arts student via a ShopColumbia
  product listing ("Lobotomy" by Ana Lara) but no contact info available there.
- **Cristian Romero**: genuinely ambiguous — at least 3 different people share this
  name online (Chicago mixed-media artist, a UIC student per LinkedIn, a musician
  endorser) with none confirmably the same Columbia College Chicago student — not
  treated as a match, per the no-guessing rule.
- Remaining 21 students: no personal site, no confirmable contact info at all.
**Action Needed:** None further this session — this school's undergrad cohort
appears to be a structurally weak fit for name→email web search (no MFA-style
personal-site culture). Future attempts here would likely need a different
approach (e.g. Instagram handle discovery, since several of the doc's original
notes mentioned Instagram tags) rather than more generic search queries.
**Status:** Resolved (0/24 — full pass completed, genuine dead end this session).

**Pattern noted:** undergrad/BFA cohorts are meaningfully harder to enrich via
generic web search than MFA cohorts — MFA students consistently maintain personal
portfolio sites (the pattern that worked well for BGSU/MassArt/CMU/Temple), but BFA
students mostly don't yet, so ShopColumbia/Dean's-List/LinkedIn-only results should
be expected and treated as confirmation-of-enrollment rather than a real contact
lead. Worth setting expectations accordingly for other BFA-heavy schools upcoming in
the plan (Cranbrook, UCLA undergrad portions, CalArts, SVA).

**Also fixed:** the project's Excel-building dependency (`openpyxl`) was missing from
`.venv_crawl4ai` (unclear why — possibly never persisted from an earlier session).
Reinstalled via `.venv_crawl4ai/Scripts/python.exe -m pip install openpyxl`. Workbook
rebuild scripts should be run with `../.venv_crawl4ai/Scripts/python.exe`, not system
`python`, going forward.

### CalArts (Animation) — new high-value source, 251/251 emails found
**Issue Type:** New source, confirmed excellent, no significant issues
**Description:** User provided a direct link to CalArts Film/Video's animation
student portfolio pages (`calarts.edu/filmvideo/animation-student-portfolios/2026/`),
distinct from the existing "CalArts" source (High Pass BFA exhibition, names only).
Assessed before scraping per project discipline: confirmed via `curl` that all 14
sub-pages (Character Animation: BFA 1-4, Affiliates, Recent Alumni; Experimental
Animation: BFA 1-4, MFA 1-3, Recent Alumni) are plain static HTML with real
`mailto:` links per student — no JS rendering needed, no crawl4ai required. Verified
a clean 1:1 name-to-email ratio with zero noise (no admissions/office/faculty emails
mixed in) before committing to the full scrape.
**Action Needed:** Built `calarts_animation_scraper.py`. Parses each student block
(name in "Last, First" format, flipped to "First Last"; class year/specialization
subtitle; a list of labeled links — Resume/Email/Portfolio/Instagram/LinkedIn/
Vimeo/Youtube). `portfolio_url` prefers the actual Portfolio link, falling back to
Instagram/Vimeo/LinkedIn/Youtube if no dedicated portfolio site was listed; Resume
and any secondary social links are preserved in `notes`. Result: **251 students,
251 with a confirmed email (100%)** — by far the highest-yield source in the project.
Added as a new "CalArts Animation" sheet, kept separate from the existing "CalArts"
sheet (different source page, different scope — High Pass is BFA-only names-only,
this is BFA+MFA+alumni with real emails).
**Status:** Resolved. Master workbook now includes both CalArts sheets;
`master_students_with_email.xlsx` gained 251 rows in one pass.

### VCU — email discovery pass, 6/13 confirmed
**Issue Type:** Email discovery, resolved
**Description:** Worked all 13 name-only VCU MFA Fine Arts (2025) students — none
had a `portfolio_url` already, so went straight to targeted web searches per
student. **6 of 13 (46%) found**, above the project's overall ~40% average.
**Action Needed / Findings:**
- **Aya Khalife** (khalifehaya7@gmail.com) — own site ayakhalife.com, a JS-rendered
  Readymag site. First-pass automated checks (plain fetch, crawl4ai passive
  render) missed the email entirely because it only appeared on the root `/` page,
  not the specific sub-pages checked first; also initially misidentified the site
  as belonging to a different, same-named Beirut-based designer until the user
  manually confirmed VCU affiliation via her CV/education page and provided the
  address directly (right-click → copy email address on a "Reach out" link).
- **Rebecca Oh** (rebeccaohart@gmail.com), **David Guarnizo** (guarnizode@vcu.edu,
  VCU institutional address from the official arts.vcu.edu directory) — both
  found via plain web search + direct site verification, straightforward.
- **Tyna Ontko** (ontkotyna@gmail.com) and **Molly Garrett** (hi@mollygarrett.com)
  — both emails were text-obfuscated on the student's own contact page (formats
  "name(at)gmail(dot)com" and "hi [at] domain.com") rather than real `mailto:`
  links, so plain-text email regexes missed them; found by reading the actual
  page text.
- **Amy Duval** (amys.duval@gmail.com) — own site duvalceramics.ca (Squarespace,
  JS-rendered); email only appeared after the new `interactive_email_finder.py`
  tool (see below) interacted with the contact page.
- **Suzy Slykin → corrected to Suzy Lykins**: the source ICA exhibition caption
  had a misspelling; confirmed the correct spelling via a matching thesis title
  ("Post Opera") on VCU Scholars Compass. No email found under the corrected
  name either.
- **No email found** (genuine dead ends, confirmed real via VCU/exhibition
  records but no personal site or published email): Debra Dowden-Crockett,
  August Neuscheler, Diego Pablo Málaga, Aleckxi Hristou-Dorhofer, brooklin
  grantz, Alex Bacon (name ambiguity flagged — an unrelated NYC art historian
  shares the name and has a similarly-named site, confirmed NOT the same person).

**New tool built this pass:** `interactive_email_finder.py` — a Playwright-driven
fallback for portfolio sites where a plain fetch or crawl4ai's passive render
finds no email. Loads the page with a real headless browser, hovers/clicks
anything that looks like a contact affordance (text matching "contact", "reach
out", "get in touch", etc.), then diffs `mailto:` hrefs and email-shaped text
before vs. after interaction. Filters out site-builder placeholder/boilerplate
addresses (Readymag's `@readymag.com` footer addresses, Squarespace's literal
`user@domain.com` template placeholder, common `name@example.com`-style
placeholders) so they don't get mistaken for a real lead. Usage:
`../.venv_crawl4ai/Scripts/python.exe interactive_email_finder.py <url>`. Worth
reaching for whenever a student's own portfolio site is found but crawl4ai's
passive render comes up empty — this pass it correctly surfaced Amy Duval's
email where the passive approach had failed.

**Process note:** a WebFetch summary is not always trustworthy for
specific facts like affiliation — Aya Khalife's site was nearly written off as
belonging to the wrong person based on the homepage alone; the correct call came
from checking a deeper page (her CV/education section) rather than trusting the
first page fetched. Worth checking more than one page on an ambiguous-identity
site before concluding it's the wrong person.

**Status:** Resolved. `master_students_with_email.xlsx` gained 6 new VCU rows
(6/13 with email now, up from 0/13).

### Ohio State — email discovery pass, 4/21 confirmed (2025 cohort only)
**Issue Type:** Email discovery, resolved for the 2025 cohort; 2026 cohort
deliberately left untouched
**Description:** All 21 name-only rows share the same `portfolio_url` (the source
exhibition page, not a personal site), so went straight to web search per
student, same as VCU. The 21 rows split into two cohorts with very different
confidence: 13 names from the 2025 "Desire Lines" show (clean comma-separated
list, high confidence) and 8 names from the 2026 "Waiting for the Light to
Change" show that were already flagged `UNVERIFIED name reconstruction` from an
earlier session (source text is a genuinely ambiguous run-on "Lastname, Firstname
Lastname, Firstname..." string with no delimiter between people).
**Action Needed / Findings (2025 cohort, 4/13 found):**
- **Mandy Darrington** (mandylynndarrington@gmail.com) — own site
  mandydarrington.com/about, obfuscated as "mandylynndarrington [at] gmail [dot]
  com".
- **William Evans** (evans_william@live.com) — own site williamevans.studio/about,
  plain text.
- **Andrew Mehall** (mehall.11@osu.edu) — OSU Department of Art directory
  profile, institutional address.
- **Ivan David Ng** (info@ivandavidng.com) — own site ivandavidng.com/about,
  plain text.
- **No email found** (confirmed real via exhibition/press records, no personal
  site or no email on an existing site, checked via interactive Playwright
  probe where a site existed): Annelise Duque, Breana Hendricks, Josiah Jamison,
  Matty Machado, Zaza Naylor, Julian Robbins, Isabella Saraceni, Alex Trippe,
  James Waite.
- Several OSU Department of Art directory URLs surfaced by web search (e.g.
  `art.osu.edu/people/duque.22`, `.../saraceni.4`, `.../trippe.5`,
  `.../naylor.135`, `.../ng.463`) turned out to be **404 — stale/incorrect search
  snippets**, not real profile pages; only `mehall.11` actually resolved.
  Confirms the project's standing lesson (verify before trusting) applies to
  search-engine snippet URLs too, not just doc-sourced URLs.

**2026 cohort — deliberately NOT touched this pass, near-miss caught and
reversed:** Attempted to independently verify the 8 UNVERIFIED reconstructed
names by re-deriving the token-shift parsing logic by hand from the exact source
string ("Banerjee, Shaheen Beardsley, Maria Conlon, Onni Estabrook, Samuel Lo,
Takahiro Okubo, Shruti Shankar, Sam Wrigglesworth, Xuan") — confirmed the
existing 8 reconstructed names in the CSV are mathematically correct as parsed.
**However, a real mistake was caught mid-process:** search results surfaced a
working OSU directory profile for a "Onni Estabrook" (estabrook.17@osu.edu,
bio'd as a Lecturer with a BFA from a different school) and this was briefly,
incorrectly treated as confirmation for our reconstructed "Samuel Estabrook" —
a **surname-only match, not a full-name match**; the Lecturer bio doesn't fit a
current 2026 MFA candidate at all and is almost certainly an unrelated person.
Caught before writing anything to the CSV. Per user decision after being told
about the near-miss, **stopped entirely rather than continuing** — all 8 2026
rows are unchanged from before this session (still name-only, still flagged
UNVERIFIED). **Lesson for future sessions**: for reconstructed/ambiguous names,
a search hit matching only the surname (not the exact full name) is not
sufficient corroboration, even when the reconstruction logic itself checks out —
person-identity confirmation and name-parsing confirmation are two separate
things and neither substitutes for the other.

**Status:** Resolved for the 2025 cohort (4/13 found). 2026 cohort intentionally
left as-is — do not attempt email discovery on those 8 names without a stronger
identity-verification method than has been tried so far (e.g. a real OSU MFA
student directory/roster page that could independently confirm the reconstructed
names exist as written, not just plausible surname matches).

---

## Batch 8 (2026-08-15): VCU + Ohio State follow-up review — user-assisted second pass

**Result: 8 more emails found (VCU +4 → 10/13, Ohio State +4 → 8/21).** After
reviewing the no-email lists from the first pass, the user ran a few manual
searches with broader/differently-worded queries than the school-specific phrasing
used originally (e.g. plain `"<Name>" artist email` instead of `"<Name>" <College>
<major> email`) and surfaced several addresses the first pass missed. Re-ran the
same broadened phrasing across the rest of both no-email lists.

### VCU — 4 new (10/13 total)
- **Debra Dowden-Crockett** (ddowdenc@odu.edu) — missed originally because she's
  since moved to a faculty appointment at Old Dominion University; the ODU-specific
  context wasn't in the original VCU-scoped search terms. Corroborated by ODU Art
  Department directory.
- **August Neuscheler** (august@mound.info) — **correction to the original
  pass**: `aneuscheler.info` genuinely is his site after all. The first pass only
  checked the bare homepage (near-blank); a deeper page
  (`neuscheler.shtml`, found via the broadened search) has his full name
  ("alexander august canossa neuscheler, richmond, va") next to this email,
  verified in raw HTML. Lesson: a site with minimal homepage content can still
  have real info one page deeper — don't conclude "unrelated site" from the
  homepage alone.
- **brooklin grantz** (hello@brooklin-studio.com) — user-confirmed. Site
  (brooklin-studio.com) has an expired TLS certificate server-side, blocking
  automated fetch entirely (same class of issue as SCAD earlier); user verified
  the address independently.
- **Alex Bacon** (alex.j.bacon@gmail.com) — user-confirmed, used despite an
  unresolved flag: this exact address independently traces via search to a CV PDF
  for a different, well-documented Alex Bacon (art historian/curator, ex-Princeton
  Curatorial Associate). Written in per explicit user instruction ("use it anyway,
  you've verified it's correct") — noted in the CSV as a caution in case it bounces.

Remaining VCU no-email (2): Diego Pablo Málaga, Aleckxi Hristou-Dorhofer — not
re-searched this pass, no new leads surfaced.

### Ohio State — 4 new, all from the 2025 cohort (8/21 total)
- **Zaza Naylor** (naylor.135@osu.edu), **Julian Robbins** (robbins.391@osu.edu),
  **Isabella Saraceni** (saraceni.4@osu.edu), **Alex Trippe** (trippe.5@osu.edu) —
  all four OSU directory URLs that 404'd in the first pass now surface in search
  results with a specific email, but **still 404 on direct fetch as of today** —
  could not independently verify the email or confirm current-student status
  (title/bio) the way `mehall.11`'s page allowed when it was live. All four used
  per explicit user confirmation ("use these they seem correct"), with a caution
  note in each CSV row about the unverified page status.
- **Matty Machado — explicitly NOT used**, real near-miss caught: `machado.50@osu.edu`
  resolved to a live OSU directory page this pass (previous 404 was transient),
  but its Job Title field reads **"Lecturer"**, not a current MFA student — this
  is almost certainly the same "different Matthew Machado" ambiguity flagged in
  the original pass, now confirmed rather than just suspected. Left unmarked.
- 2026 cohort (8 UNVERIFIED reconstructed names): re-searched all 8 with the
  broadened phrasing anyway (with the user's awareness these are lower-confidence
  names) — genuine dead ends across the board, no personal sites or email trails
  for any of the 8 specific reconstructed full names. No change from the prior
  pass; still flagged UNVERIFIED, still no email.

Remaining Ohio State no-email (13): Annelise Duque, Breana Hendricks (real
personal site + contact page found, but only a contact form — no mailto, checked
via `interactive_email_finder.py`), Josiah Jamison, Matty Machado (see above),
James Waite, plus all 8 of the 2026 cohort.

### Pattern worth carrying forward
Query phrasing matters more than expected: switching from school/major-scoped
searches (`"<Name>" <College> <major> portfolio`) to plain `"<Name>" artist email`
surfaced several real, previously-missed results in this pass. Worth trying both
phrasings before concluding "no email found," not just the school-scoped one this
project has defaulted to so far.

**Status:** Both schools' no-email lists reviewed and re-searched with broadened
phrasing; both now closed out for this round (VCU 2 remaining, Ohio State 13
remaining, all with a documented dead-end reason). Moving to the next
smallest-remaining school next.

---

## Batch 9 (2026-08-15, same day): user manual pass on Ohio State — a real name-reconstruction error found and fixed

**Result: 12 more Ohio State emails (8 → 16/22), plus the 2026 cohort's names
corrected from 8 wrong-pairing guesses to 9 correctly-paired names** (one new
row added — the cohort was always 9 people, not 8, per the source page's own
"nine MFA graduate students" text; the reconstruction logic had been silently
dropping one person). The user did a manual search pass on the remaining Batch 8
no-email list and found results this session's searches had missed, including one
that overturned a "same person? uncertain" ambiguity from earlier in the project.

### 2025 cohort — 3 more found (Duque, Jamison, Waite)
All three found via the plain `"<Name>" artist email` phrasing (same pattern
Batch 8 already validated as more effective than school-scoped searches).
Annelise Duque's confirmed address (annelise.duque@gmail.com) notably isn't
published anywhere on her own site (annelise-duque.com) that this project could
find directly — a reminder that "checked their own site, nothing there" doesn't
mean an email doesn't exist somewhere else indexed.

### 2026 cohort — the reconstruction was wrong, now corrected
The original name-reconstruction (done in an earlier session, re-verified but not
re-derived in Batch 8) assumed the raw source string
(`"Banerjee, Shaheen Beardsley, Maria Conlon, Onni Estabrook, Samuel Lo, Takahiro
Okubo, Shruti Shankar, Sam Wrigglesworth, Xuan"`) was a "Lastname, Firstname
Lastname, Firstname..." shifted pattern, producing pairings like "Shaheen
Banerjee" and "Maria Beardsley". **This was wrong.** The user searched a few of
these names directly and got results contradicting the assumed pairing — e.g.
searching "Maria Beardsley" surfaced "**Shaheen** Beardsley" instead. Re-deriving
the string by hand confirms the correct read is much simpler: it's a plain
"Firstname Lastname, Firstname Lastname, ..." list where each token IS a complete
person, **except** the very first token ("Banerjee") is missing its first name
and the very last token ("Xuan") is missing its last name — i.e. 9 people total
(matching the source page's own "nine MFA graduate students" line, which the
original 8-person reconstruction undercounted by one).

Corrected pairings (5 with emails, user-confirmed via search):
- Shaheen Banerjee → **Shaheen Beardsley** (beardsley.55@osu.edu)
- Maria Beardsley → **Maria Conlon** (conlon.65@osu.edu)
- Onni Conlon → **Onni Estabrook** (estabrook.17@osu.edu) — caution retained: an
  earlier session found an OSU directory profile for an "Onni Estabrook" bio'd as
  a Lecturer, the same faculty-vs-student risk seen with Matthew Machado; user
  confirmed this address anyway, kept as a flag in the notes in case it bounces.
- Samuel Estabrook → **Samuel Lo** (lo.327@buckeyemail.osu.edu)
- Takahiro Lo → **Takahiro Okubo** (okubo.11@osu.edu)
- Shruti Okubo → **Shruti Shankar** (no email found under corrected name yet)
- Sam Shankar → **Sam Wrigglesworth** (no email found under corrected name yet)
- Xuan Wrigglesworth → **[9th person, name split across two rows]**: re-checked
  the source page directly, confirmed "Banerjee" and "Xuan" are two separate,
  separately-incomplete people, not fragments of the 7 paired names.
  "Banerjee" resolved to **Meghadityo Banerjee** via a UAS.osu.edu artist
  interview article linking to his personal site (meghadityobanerjee.com,
  confirmed OSU first-year MFA student via the "Convergence" 2024 show) — no
  email found (contact form only). "Xuan" remains unresolved (no last name found
  after checking "Convergence" and "Here & There" show coverage) — left as
  `Xuan [Lastname unknown]` for a future pass.

### Also fixed this session: a self-inflicted sent_to_nitya bug
While writing in the newly-confirmed VCU/Ohio State emails from the first half of
this session (Batch 8), 8 rows were accidentally stamped with today's date in
`sent_to_nitya` at the same time their email was added — before they'd actually
been included in a batch or sent anywhere. Caught by re-running
`build_nitya_batch.py` and noticing it reported the stale count (10) instead of
the expected new total; traced to the CSV edits, corrected by clearing
`sent_to_nitya` on those 8 rows before generating the real batch. Worth
remembering: when writing a newly-found email into a CSV row, `sent_to_nitya`
should always be left blank — it only ever gets a value from `mark_batch_sent.py`.

### Pattern worth carrying forward
When a user's manual search directly contradicts an assumed name pairing (as
happened with "Maria Beardsley" search returning "Shaheen Beardsley"), that's a
strong signal to re-derive the reconstruction from scratch rather than assume the
user's result is the anomaly. The original token-shift logic was never actually
verified character-by-character against the raw string in Batch 8 — it was
re-confirmed by producing the same (wrong) output twice, which felt like
verification but wasn't.

**Status:** Ohio State now 16/22 with email. Remaining no-email (6): Breana
Hendricks, Matty Machado (Lecturer name-collision, unresolved), Shruti Shankar,
Sam Wrigglesworth (both under corrected names, not yet re-searched), Meghadityo
Banerjee (site found, no email published), Xuan (last name still unknown).
`nitya_batch_2026-08-15.xlsx` regenerated — 26 total new rows (VCU 10 + Ohio
State 16), correctly unmarked and ready to send.

## Batch 10 (2026-08-15): New school — UAL Central Saint Martins, full scrape

**Result: 283/283 students with email — a new source, 100% email yield.**
Built `ual_csm_scraper.py` (Playwright-driven) to scrape the UAL Showcase
graduate showcase for Central Saint Martins, per user's explicit instructions
to start at page 17 (start_rank 193) and continue to the end (page 66,
start_rank 781; 790 total listed projects).

### Why a custom scraper was needed
The listing page is a JS-rendered, scroll-triggered grid — a plain fetch or a
passively-rendered crawl4ai fetch (even with `delay_before_return_html` up to
10s) only ever showed "Loading projects" because the grid's content never
renders without an active scroll gesture. Fixed with raw Playwright:
`wait_until="domcontentloaded"` + explicit `page.mouse.wheel(0, 2000)` fired
5 times with ~1.2-1.5s waits between each, which reliably triggered the
lazy-load. `wait_until="networkidle"` was tried first and does not work on
this site (never reaches idle, times out).

Each project card links out via a search-redirect wrapper URL
(`ual-search.arts.ac.uk/s/redirect?...&url=<real-profile-url>`) rather than a
direct link. The initial regex `[?&]url=([^&"]+)` matched zero people because
the raw HTML HTML-entity-encodes the ampersand (`&amp;url=`, not `&url=`) —
fixed to `[?&](?:amp;)?url=([^&";]+)`, verified against cached test HTML
(0 → 12 people parsed correctly on the same page).

Each qualifying student's individual profile page publishes a real `mailto:`
link directly in the page DOM — no interaction needed for extraction despite
the email icon only being visually revealed on hover in a live browser.

### Scope filtering
Course/major text matched against the project's 9 in-scope mediums via
keyword classification (`classify_medium()` in the scraper). Per user decision
2026-08-15: Industrial Design excluded (too far from Design scope), Curation/
Culture/Criticism excluded (curatorial studies, not a medium), Architecture
never in scope. Courses not matching any keyword were skipped entirely (not
written to the CSV at all — this source only ever contains in-scope,
with-email rows, hence 0 no-email rows).

### Run in 4 checkpoints (~15 pages each) per user's requested cadence
- Pages 17-31: 92 students
- Pages 32-46: 75 students (167 running total) — page 33 legitimately returned
  0 projects (confirmed via cache inspection, not a scraping failure)
- Pages 47-61: 101 students (268 running total)
- Pages 62-66: 15 students (283 final total) — pages 65-66 had lower/zero
  qualifying counts as the listing approached its end (790 total projects ÷
  12/page = 66 pages)

### One data-quality fix during review
One row's profile URL resolved to a project cover page (a collaborative/group
project) rather than an individual profile, so the name-extraction regex
grabbed the project title "Collaborative project" instead of a person's name.
Caught during a post-scrape sanity pass (checked for suspicious name patterns
across all 283 rows). Recovered the real name (**Rose Kessler**) from the
page's `<title>` tag ("The Vegas Paradox - Rose Kessler - UAL Showcase") and
corrected the row, with a note explaining the recovery. No duplicate names and
no other anomalies found in the full 283-row set.

### Workbook integration
Added to `build_master_workbook.py`'s `SOURCES` list and `SOURCE_CITATIONS`
dict; rebuilt all three master workbooks. UAL Central Saint Martins sheet:
283 with email, 0 without, in both `master_students.xlsx` and
`master_students_with_email.xlsx` (absent, as expected, from
`master_students_no_email.xlsx`).

**Status:** UAL Central Saint Martins complete, 283/283 with email. Not yet
committed to git. Not yet included in a Nitya batch — per the established
one-school-at-a-time handoff flow, this should either be folded into a
regenerated `nitya_batch_2026-08-15.xlsx` alongside the still-pending VCU/Ohio
State rows, or sent as its own separate batch — needs user confirmation on
which.

## Batch 11 (2026-08-15): CMU + UW-Madison follow-up — smallest-remaining pass

Picked the two smallest no-email counts after UAL (CMU: 1 missing, UW-Madison:
2 missing) per the established smallest-school-first convention.

**Result: 1 more email found (UW-Madison), 1 name correction, 2 confirmed
dead ends.**

### UW-Madison — Anna! resolved to Anna Colombia
The directory listed only "Anna!" (no last name). Her linked personal site
(annacolombia.com) and Instagram (@anna.colombia) identify her as **Anna
Colombia**. Found and verified `annacolombia.colombiaanna@gmail.com` directly
in the raw HTML `mailto:` link on annacolombia.com/contact — worth noting a
WebFetch pass on the same page first reported a truncated/wrong version of the
address (`colombiaanna@gmail.com`, missing the `annacolombia.` prefix), caught
by cross-checking against the raw HTML rather than trusting the fetched-page
summary.

### CMU — Morgan Strahorn, exhaustively checked, no email exists publicly
User supplied an Instagram exhibition-announcement caption for "Dream
Sequence" (CMU 1st/2nd-year MFA show, SPACE gallery, Feb-Apr 2026) listing 11
artists including "Morgan Strahorn (MFA '28) @mrgnstrhrn" — this both
confirmed her Instagram handle and let us cross-check the full CMU roster: all
11 names in the caption were already present in `cmu_students.csv` (the other
3 CMU rows — Afrooz Partovi, Naomi Chambers, Bulumko Mbete — are third-years
not in this particular show, not missing people). So CMU's roster is
confirmed complete; Morgan Strahorn was the only gap.

Followed the Instagram handle through every available surface: Behance (no
contact info), Instagram bio (emoji only) → Linktree (linktr.ee/mrgnstrhrn,
no email, only SoundCloud/Are.na/radio-station links) → Are.na author bio
("Morgan Strahorn is a sweet person with an art degree. She lives and works in
Dayton, OH") → none published an email. Confirmed as the same person (bio
matches, she/her) but no email exists in any public, searchable location.
Left as a no-email dead end — would need a direct DM/ask, out of scope for
this project's search-only method.

### Molly Green (UW-Madison) — also checked, also a dead end
Confirmed real via her MFA Qualifier show "Feed the Birds" (UW News,
art.wisc.edu event page) and Instagram (@mollygreen.pdf), she/her. No personal
site, no published email found via web search or her UW directory listing.
Left as-is.

**Status:** CMU now 0/14 no-email (complete). UW-Madison now 1/21 no-email
(Molly Green only). Not yet committed. Not yet added to a Nitya batch.

## Batch 12 (2026-08-15): BGSU follow-up — no new emails found

Next-smallest school after CMU/UW-Madison (2 missing). Checked both names,
including Instagram per user's reminder that a lot of artists have an
Instagram presence worth checking even when a general web search comes up
empty.

**Result: 0/2 found — both remain confirmed-real dead ends.**

- **Precious Gyekye** — confirmed BGSU MFA 2025 ("Unraveling Silence" thesis,
  3-D Studio Art) and a curatorial assistant for BGSU School of Art galleries
  (alongside curator Matthew Kyba and fellow assistant Matthew Bowlus, per a
  2024 Congressional Art Competition mention). Not in BGSU's public
  faculty/staff directory (grad student, not staff). No personal site found.
  Checked Instagram — no matching account found (search surfaced several
  unrelated "Gyekye" and "Precious" accounts, none tied to BGSU or matching
  bio details). BGSU's own directory search requires a BGSU login for student
  lookups, out of reach.
- **Peter Kiladejo** (Adetope Peter Kiladejo) — confirmed BGSU MFA 2025
  ("Bloom III" oil painting listed for sale via ArtCloud/The African Art Hub
  gallery). Only gallery/general-inquiry emails surfaced (not his own
  address). Ruled out a same-name "Peter Kiladejo" profile at Nigeria's Green
  Institute as a different person — that one's MFA is from Obafemi Awolowo
  University in 2012, not BGSU 2025, no BGSU mention at all. No Instagram
  match found either.

**Status:** BGSU stays at 2/6 no-email — no change this pass.

## Batch 13 (2026-08-15): UW Art follow-up — 2 of 4 found

Next-smallest after BGSU (4 missing).

**Result: 2 more emails found (Dahae Cheon, Alex Moni-Sauri), 2 remain
unresolved (Stephanie Alacon, Jeff Jiang).**

- **Dahae Cheon** — dahae35@uw.edu. Industrial designer, Hongik University
  BFA. Search results cite her official UW Art + Art History + Design
  directory page (art.washington.edu/people/dahae-cheon), same URL 404s on a
  direct curl/WebFetch (no login/referrer) — this is the same
  can't-independently-verify-but-plausible pattern already seen and approved
  on several Ohio State rows in Batch 8. Flagged to user, approved for reuse.
- **Alex Moni-Sauri** — monia@uw.edu. Multidisciplinary artist/writer. Same
  404-on-direct-fetch pattern as Cheon above (art.washington.edu/people/
  alex-moni-sauri), plus corroborated by an active Instagram (@a.moni.sauri)
  including a "grad student spotlight" post confirming current UW MFA status.
  User approved reuse of the same confidence pattern for both rows together.
- **Stephanie Alacon** — confirmed real (3D4M ceramics/glass/sculpture MFA,
  BFA Cal State Long Beach 2024) via her own UW directory page, but that page
  also 404s and no search result surfaced an actual email address (only the
  department's general gradart@uw.edu). Left unresolved — no address to even
  flag for approval, unlike Cheon/Moni-Sauri.
- **Jeff Jiang** — personal site jeff-jiang.com found (footwear/product
  design) but no email in static HTML, likely JS contact form. Web search for
  his specific site/name turned up only unrelated same-name people (a CEO, a
  state senate candidate, various LinkedIn profiles) — none matching. Left
  unresolved.

**Status:** UW Art now 2/10 no-email (was 4). Not yet committed.

## Batch 14 (2026-08-15): MassArt follow-up — 1 of 5 found

Next-smallest after UW Art (5 missing). Checked personal sites, Instagram
(per user's standing reminder to always check it), and MassArt's own grad
student events page for all 5.

- **Michael d'Entremont** — RESOLVED: snailpiratebusiness@gmail.com,
  confirmed by user. An automated search first surfaced Instagram handle
  @michaelkdentremont, whose bio ("Dad X2... Gym Owner... East Coaster > YEG")
  is clearly a different, unrelated person and was correctly not used — the
  real email came from the user separately (his "Snailpirate" animator/artist
  persona/business email), a name-to-persona link this project's automated
  search had no way to make on its own.
- **Christopher Gage Arotsky** — confirmed real via his own MassArt x SoWa
  artist page (sowa.massart.edu/artist/christopher-arotsky), which lists his
  real Instagram (@christophergage_, private account) but only a shared
  gallery inbox email (mxs@massart.edu) — not his personal address, not used
  per the confidence-gating rule (a shared gallery inbox isn't a reliable way
  to reach this specific student).
- **Camryn Connolly** — personal site (camrynconnolly.com) only has a mailing
  -list signup form, no visible email. Instagram (@camrynscollections, "a
  collection of my work") exists but no email in bio per search snippet.
- **Robin Jamkatel** — confirmed MassArt Graduate Teaching/Technical
  Assistant + MFA Photography student via ZoomInfo, which confirms a
  `@massart.edu` address exists but masks the username (`r***@massart.edu`)
  — not guessing it. No personal site or portfolio found (search kept
  surfacing an unrelated "Roshan Jamkatel," a Chicago-based photographer).
- **Dylan Record** — confirmed real only via MassArt's own exhibition/event
  listings (2026 MFA Thesis Part II, Fall 2025 MFA Walkthroughs); no
  personal site, no Instagram, no email found anywhere.

**Status:** MassArt now 4/11 no-email (was 5).

## Batch 15 (2026-08-15): New school — Alfred University, thin roster (site restructured)

Resuming the original priority-28 school list — 5 schools were never scraped
(Alfred, Cornell, UT Austin, Cooper Union, SCAD). Started with Alfred per
user's "finish the original 28 first" decision.

**Result: 14 names only, 0 emails — the source described in the original
research plan no longer exists.**

The original plan (`art_school_scraping_urls.md`) pointed to a per-student
thesis subpage system (`thesis-exhibits/{semester-year}/mfa/{lastname}/`)
with individual student pages. Every one of those URLs now 301-redirects to a
generic `/galleries/` hub page — confirmed on 3 different year/student
combinations (spring-2022, spring-2023, spring-2024/mfa/mcmaster). The
`Fosdick-Nelson Gallery > Exhibits` archive itself only goes up to 2023-2024
and doesn't have a 2024-2025 or 2025-2026 entry yet, despite those shows
having already happened. The site was restructured since the original
research pass and no longer exposes a consolidated roster anywhere.

What was actually recoverable, via press releases and search-indexed event
pages (not a single clean source):
- **2026 cohort (10 names):** Amanda Gentry, Max Heaton, Hazel Liu, Yuxuan
  Wang, Justin Donica, Ignacio Luera, Krist Lee, GH Wood, Marita Manson,
  Elizabeth Scott — pieced together from 2 separate press releases covering
  only the season's first and last weeks; the middle 3 weeks (~April 18, 25,
  May 2) have no indexed press release at all, so this is a known-incomplete
  cohort, not a full one.
- **2025 cohort (4 names):** Michelle Seo, Toomas Toomepuu, David Park, Erin
  Berry — from a search-engine summary of the 2025 MFA Thesis Exhibitions
  event page, itself likely incomplete (the page describes a full
  Saturday-by-Saturday season like 2026's).
- **Older years:** Only 1-2 stray names per year surfaced from photo-caption
  text on the 2022-2023 and 2023-2024 gallery archive pages ("Jaclyn Head,
  MFA 2022"; "Gabrielle Egnaters and Kate Herron, MFA 2023") — not usable as
  rosters, not added.

No emails or portfolio links found anywhere for any of the 14 (matches the
original research's own caveat that Tier-1 school pages "consistently"
lack this info). User confirmed proceeding with this thin, known-partial
14-name roster rather than digging further or skipping the school outright.

**Status:** New file `alfred_students.csv`, 14/14 no-email. Not yet added to
`build_master_workbook.py` SOURCES (pending — will be added once all 5
remaining original-28 schools are scraped in this pass). Not yet committed.

## Batch 16 (2026-08-15): New school — Cornell, fragmented across many small shows

Second of the 5 remaining original-28 schools.

**Result: 37 names, 0 emails.** Cornell's Department of Art doesn't publish a
single roster page — its MFA/BFA thesis shows are split into many small
named group exhibitions (5-10 students each) rather than one class list, so
the roster had to be assembled by finding and cross-referencing several
separate event pages:
- **MFA Image Text '26 (10):** SELF/ASSEMBLY thesis show at Foreign &
  Domestic Gallery — the one genuinely complete, clean cohort list found.
- **MFA Creative Visual Arts '26 (7):** pieced together from a search-engine
  summary (no single source page fetched directly) — flagged as
  slightly less independently verified than the Image Text list.
- **BFA '25 (9 + 1 + 6, ~14 unique after overlap):** three different named
  sub-shows — "Thesis Group Exhibition" (9), "Space of Becoming" (5, 4
  overlapping + Alex Park new), and a separate "Senior B.F.A. Thesis
  Exhibition" (6, 5 overlapping + Amy Lee new, which itself overlaps
  Space of Becoming) — confirms the 2025 BFA class is genuinely split
  across multiple mini-shows rather than one exhibition.
- **BFA '26 ("with a trace", 4):** only 4 names resolved even though the
  page describes "five B.F.A. '26 students" — the 5th name wasn't
  recoverable from the fetched page content.

Two more 2026 BFA sub-shows (FLEXION, 4 students; "North, South, East, West",
count unknown) were referenced in search snippets but their exact page URLs
never surfaced, so no names were recoverable for either — acknowledged gap,
not pursued further per user's "take what's found, close it out" call (small
program, diminishing returns on continued digging).

No emails or portfolio links found for anyone — matches the original
research's note that Cornell pages don't publish contact info.

**Status:** New file `cornell_students.csv`, 37/37 no-email. Not yet added to
SOURCES. Not yet committed.

## Batch 17 (2026-08-15): New school — UT Austin, strongest yield of the 5

Third of the 5 remaining original-28 schools.

**Result: 78 names, 0 emails — the cleanest, highest-yield source of this
batch.** Unlike Alfred/Cornell, UT Austin's exhibitions each have one clean,
complete roster page on the Visual Arts Center site (utvac.org):
- **MFA Studio Art 2025 ("Acceleration Without Arrival", 14):** full roster
  fetched directly from its own utvac.org event page — all 14 names
  confirmed against the "14 graduating MFA artists" count mentioned in press
  coverage.
- **MFA Studio Art 2026 ("Half a Second or Less", 7):** full roster, own
  event page, matches announced count exactly.
- **BFA Studio Art 2026 ("Proof of Life", 57):** the standout find — a
  single senior-exhibition page listing the full graduating BFA cohort by
  name (painting/drawing/print/sculpture/video/photography). One name
  ("Genavieve G.") is truncated on the source page itself with no
  recoverable last name; kept as-is with a note. This is by far the largest
  single-page roster found in this batch of 5 schools.

Also found and deliberately excluded: a "Known Otherwise: 2026 Design MFA
Thesis Exhibition" (8 grads) — this is UT's separate School of Design and
Creative Technologies, not the Department of Art and Art History, and Design
isn't a confirmed in-scope medium per the project's existing scope rules; not
scraped.

No emails or portfolio links found for anyone (matches every other school in
this batch).

**Status:** New file `ut_austin_students.csv`, 78/78 no-email. Not yet added
to SOURCES. Not yet committed.

## Batch 18 (2026-08-15): New school — Cooper Union, thin/confirmed only

Fourth of the 5 remaining original-28 schools. Confirms the original plan
doc's own caveat verbatim: "Cooper's tradition is to list works by artist
name only without additional info. Disambiguation may be harder."

**Result: 2 names, 0 emails — deliberately kept small over guessing.**
Cooper Union's 2026 End of Year Show (the annual public exhibition) has no
roster page — the event page itself lists zero names. Photo-caption names
from the opening-night gallery page mix all 3 of Cooper Union's schools
(Architecture, Art, Engineering) together with no reliable way to tell which
school a name belongs to unless a class-suffix happens to be visible (e.g.
"EE'26" = Electrical Engineering, "CE'26" = Civil Engineering, "A'26" =
Art). Of ~23 names surfaced from photo captions, 9 had an explicit
non-Art suffix (excluded) and the remaining ~13 had no suffix at all
(ambiguous — could be Art or Architecture, excluded rather than guessed).

Only 2 names came with an explicit, unambiguous "A'26" (School of Art)
confirmation, both from a separate "Class of 2026: In Their Own Words"
feature article: Skye Jones (installation art) and Regina Cervantes Ellis
(graphic design research via the Rhoda Lubalin Fellowship). User confirmed
taking only these 2 rather than guessing at the ambiguous names or skipping
the school outright.

No emails or portfolio links found for either.

**Status:** New file `cooper_union_students.csv`, 2/2 no-email. Not yet
added to SOURCES. Not yet committed.

## Batch 19 (2026-08-15): New school — SCAD, largest of the 5, needed a scraper

Fifth and final of the 5 remaining original-28 schools.

**Result: 367 names, 0 emails.** SCAD's public "SCAD Thesis Digital
Collection" (library.scad.edu) is a genuinely large, plain-HTML, keyword
-searchable library catalog covering 50+ programs since Fall 2010 MFA /
Spring 2020 undergrad — far too large to browse manually (486 results for
Painting alone, going back 16 years). Per user decision, scoped to
**2025-2026 only**, matching every other school in this project (current/
recent graduating cohorts, not full historical archives).

Wrote `scad_scraper.py`: plain `curl` fetch (no JS needed — this is a static
library catalog), parses each result card's title/author/year via regex,
paginates 50-per-page, and — since results are sorted newest-first — stops
paginating a program as soon as it hits a pre-2025 entry rather than walking
the entire multi-year archive. One bug found and fixed during testing: SCAD's
saved-search URLs contain literal unencoded spaces (`%22 thesis painting%22`)
which silently broke a bare `curl <url>` call (empty response, no error) —
fixed by percent-encoding spaces before the fetch.

Mapped 11 of SCAD's 50+ programs to this project's 9 in-scope mediums:
Painting, Illustration, Printmaking -> Painting/Drawing; Sculpture ->
Sculpture; Fibers -> Fiber and Material Arts; Photography -> Photography;
Animation -> 2D/3D Animation; Film & Television -> Filmmaking; Graphic
Design -> Design; User Experience (UX) Design -> UI/UX Design; Fashion ->
Fashion. All other SCAD programs (Architecture, Advertising, Interior
Design, Themed Entertainment Design, Writing, etc.) are out of scope and
were not scraped.

Per-program yield (2025-2026 only): Illustration 93, Film & Television 66,
Animation 76, Graphic Design 33, Painting 42, Photography 26, Fashion 17,
Sculpture 4, Fibers 4, User Experience (UX) Design 6, Printmaking 0 (all 11
of its results predate 2025). 367 unique students after de-duplication by
(name, thesis title).

No emails or portfolio links published on any thesis catalog entry (matches
every other school in this batch of 5).

**Status:** New file `scad_students.csv`, 367/367 no-email — by far the
largest addition among the 5 remaining original-28 schools. Not yet added to
SOURCES. Not yet committed. All 5 remaining schools now scraped: Alfred (14),
Cornell (37), UT Austin (78), Cooper Union (2), SCAD (367) = 498 new names,
0 new emails, across 5 new CSV files. Next: wire into
`build_master_workbook.py` SOURCES + SOURCE_CITATIONS and rebuild all three
master workbooks.
