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

### BGSU — 1 of 6 emails found
**Description:** Ran individual searches per student.
- **Syed Fatmi**: confirmed high-confidence — `syedway.digital@gmail.com`, found on his
  own portfolio site `syedway.com` (matches thesis title "OMNISYS" and LinkedIn).
  Updated `portfolio_url` from the bare ScholarWorks record to his real personal site.
- **Kamrun Mim**: personal site found (`kamrunnahermim.com`) but the site returns
  HTTP 403 on fetch (blocks the fetch tool) — couldn't retrieve the email. Noted in CSV
  as a manual-follow-up lead; `portfolio_url` updated to the real site.
- **Precious Gyekye**: confirmed as a current BGSU Graduate Teaching Associate, but no
  email found — BGSU's directory page is JS-rendered (not fetchable statically), and
  the only "contact info" surfaced was a masked ZoomInfo listing (data broker, blocked
  on fetch anyway) — not used as a source.
- **Peter Kiladejo / Rachel Krieger / Nick Felaris**: no confirmed match. Same-name
  people exist online (a Nigerian gallery-represented artist "Adetope Peter Kiladejo,"
  several unrelated "Rachel Krieger"s, a 2020 Toledo graffiti-artist Instagram for
  "Nick Felaris") but none could be confirmed as the same BGSU MFA student, so nothing
  was written.
**Action Needed:** None further this session — remaining 5 need either a different
search angle or direct manual outreach.
**Status:** Resolved (partial — 1/6 found, per confidence-gate rules).

**Also fixed:** the project's Excel-building dependency (`openpyxl`) was missing from
`.venv_crawl4ai` (unclear why — possibly never persisted from an earlier session).
Reinstalled via `.venv_crawl4ai/Scripts/python.exe -m pip install openpyxl`. Workbook
rebuild scripts should be run with `../.venv_crawl4ai/Scripts/python.exe`, not system
`python`, going forward.
