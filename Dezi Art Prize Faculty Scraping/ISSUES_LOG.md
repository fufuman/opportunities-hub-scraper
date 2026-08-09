# Faculty Scraping — Issues Log

This log tracks what worked, what didn't, and any dead ends per school, for the
Dezi Art Prize faculty/professor email scraping project. Read this before starting
a new school to avoid repeating failed approaches.

This is a **separate dataset from the student scraper project**
(`../Dezi Art Prize Student Data Scraping/`) — different people (faculty, not
graduating students), different schema, different outreach purpose. Code patterns
(fetch/parse/main, caching, master workbook builder) are reused from that project,
but CSVs, cache folders, and this log are independent.

Schema: `school_name, faculty_name, title, department, medium, email, email_type,
source_url, date_extracted`. `medium` is filtered to the 9 in-scope departments
(Painting/Drawing, Sculpture, Filmmaking, Photography, Design, UI/UX Design,
2D/3D Animation, Fashion, Fiber and Material Arts) — art history, art education,
architecture, music, theater, dance, curatorial/museum studies, and general liberal
arts faculty are excluded unless they also teach in an in-scope medium.

`email_type` is one of `direct` (found on a listing/directory page),
`profile` (found by clicking into an individual profile page), `department_general`
(no individual emails published, using a department/school contact instead), or
`constructed` (pattern-guessed, not verified — avoid; only used if explicitly
requested, per the same "never guess a pattern email" rule the student project
follows).

---

## Batch 1 (2026-08-08 to 2026-08-09): Bezalel, Temple/Tyler, Ohio State

**Result: 161 faculty rows total (Bezalel 58, Temple/Tyler 51, Ohio State 52), all
with `direct` or `profile` emails.** `master_faculty.xlsx` built with one sheet per
school, source citation header (now includes Country/City, added 2026-08-09, above
Source/URL/Accessed), bold header row, frozen panes, autofilter.

**2026-08-09: Bezalel removed from `master_faculty.xlsx` at user request** — the
workbook now has only Temple-Tyler and Ohio State sheets. `bezalel_faculty.csv`,
`bezalel_faculty_scraper.py`, and its cache (`cache/bezalel_faculty/`) are left on
disk and still work standalone; only the `sources` entry in
`build_faculty_master_workbook.py` was removed, so Bezalel can be added back into
the workbook later by re-adding that one tuple + its `SOURCE_CITATIONS` entry
(with country/city) if wanted again.

### Bezalel Academy of Arts and Design — 58/58 rows have emails (CSV retained, not in workbook)
Every faculty member's email genuinely is public, as the research brief claimed —
strongest exposure of the three. Scraped 3 pages: Fine Arts (BFA) staff, Fine Arts
(MFA) staff, Photography staff. **The other 6 department URL patterns in the brief
(ceramics/glass, design, jewelry, fashion, animation, film) all 404 — Bezalel's real
URL slugs for those departments are unknown; would need manual discovery (e.g.
browsing the site's own nav) before those departments can be added.**

Parsing notes: each staff card's medium had to be inferred from a per-person
"Courses" list (e.g. "Sculpture and construction", "Video & Sound"), not the
role-in-department field, which is blank except for department heads. This works
well but is inherently approximate — e.g. "bodybuilding" and "Meeting Point" are
real (if oddly named) course titles that happened to co-occur with clearer signal
courses on the same person, not evidence of a parsing bug. Deduped 9 people who
appeared on more than one of the 3 pages (kept the row with the fuller title/course
list).

### Temple University, Tyler School of Art and Architecture — 51/51 rows have emails
Directory is **10 pages, not 16** as the brief claimed (confirmed via the page
pager itself) — filtered to `profile-type=staff,faculty,adjunct_faculty` (excludes
students already). `/directory` is JS-rendered — a plain fetch returns an empty
shell; required crawl4ai (`wait_for="css:body", delay_before_return_html=3.0`).
Each directory card has an explicit "Discipline" label (e.g. "Painting", "Metals/
Jewelry/CAD-CAM", "Fibers & Material Studies") which mapped cleanly to the 9
in-scope mediums via keyword match. Did not additionally scrape the 6
department-specific faculty pages listed in the brief (sculpture, glass, ceramics,
painting, photography, printmaking, art-design-foundations) — the master
`/directory` with its Discipline filter already appears to be a superset; worth
spot-checking one of those pages in a future session to confirm no one is missing
from the directory.

### Ohio State University, Department of Art — 52/61 in-scope rows have emails
**Correction to the research brief: the `/people` directory does NOT show a
per-person area/discipline label** — only name, title (e.g. "Professor"), and
email. The brief's claimed areas (Ceramics, Film/Video, Glass, etc.) only appear
as (a) sitewide nav links to `/areas/<medium>` pages, which are pure descriptive
copy with **no faculty roster at all**, or (b) free-text bio paragraphs on each
person's individual profile page.

Ended up doing a full profile click-through pass (61 pages — Chair/Faculty/
Associated Faculty/Emeritus Faculty categories; Staff and Graduate Students
excluded) to classify medium from bio text. First attempt classified everyone as
"Painting/Drawing" because the *entire page* (including that same sitewide areas
nav menu) was being keyword-matched — every medium keyword appears exactly twice on
every page regardless of the person. Fixed by restricting text extraction to the
`<article class="user-profile">` container before classifying. 9 of 61 people had no
in-scope medium detected in their title/bio (likely art history/architecture
faculty, or a bio too generic to classify) and were dropped rather than guessed.
Also hit one markup bug: OSU's own HTML has a literal space in one profile href
(`/people/ brauner.14`) — stripped whitespace from the path before fetching.

Known limitation: bio-text keyword classification is approximate — e.g. Chris
Coleman (Director of ACCAD, Ohio State's digital arts/animation center) was
classified as "Sculpture" from bio keywords, which is probably wrong (ACCAD is
animation/digital-arts-adjacent, not sculpture) but no cleaner signal was available
without deeper per-person research. Treat `medium` on this school's sheet as
best-effort, not authoritative, if precision matters for a specific outreach list.

### General pattern for this batch
Confirmed the same lesson as the student-scraper project: **the source research
brief's page counts/claims should always be spot-checked before writing scraper
code** — Temple's page count (16 vs actual 10) and Ohio State's claimed per-person
area labels (not actually present on the directory page) were both wrong in ways
that would have produced broken or misleading scrapers if taken at face value.

---

## Batch 2 (2026-08-09): UGA, University of Iowa, UT Austin

**Result: 80 new faculty rows (UGA 43, Iowa 12, UT Austin 25), all `direct` emails
straight off each directory listing — no profile click-through needed for any of
the 3.** `master_faculty.xlsx` rebuilt with 5 sheets total (183 faculty rows
overall). Bezalel remains excluded from the workbook per the 2026-08-09 removal
(CSV/scraper still on disk, see above).

### University of Georgia, Lamar Dodd School of Art — 43/43 rows have emails
Directory at `/directory/` 301-redirects to `/directory/` with trailing slash —
plain `curl` without `-L` returned an empty body; fixed by fetching the
slash-terminated URL directly. 10 pages (`/directory/page/2/` through `/page/10/`,
page 1 is the bare `/directory/` URL), confirmed via visible "1 2 3 … 10" pager.
Each card has an explicit "Academic Area" field (e.g. "Drawing & Painting",
"Fabric Design, Studio Art") — direct, reliable medium signal, same quality as
Temple's Discipline field.

### University of Iowa, School of Art, Art History and Design — 12/25 rows have emails
2-page `/people/faculty` directory (`?page=0`/`?page=1`), each card's Title/Position
field(s) (can be multiple, e.g. "Area Head, Printmaking" + "Iowa Print Media
Associate Professor") give a direct, reliable medium signal for people whose title
names a specialization. The other ~13 of 25 people on this page genuinely have
generic titles ("Professor", "Associate Professor of Instruction") or are Art
History faculty — correctly excluded, not a parsing gap. One real bug caught and
fixed: an early version of the position-block regex terminated at the first
`</div>` inside the field's own markup (nested divs), silently truncating every
position string and making the medium classifier see empty text for everyone
except two people whose card happened to close early. Fixed by bounding the block
on the next known field marker (`field--name-field-person-email`) instead of a
generic `</div>` count.

### University of Texas at Austin, Department of Art and Art History — 25/25+ rows have emails
**Correction to research brief: emails are NOT obfuscated with spaces** — they
render as plain `mailto:` addresses, just wrapped with `<wbr>` tags for
line-breaking in long addresses (e.g. `peter.<wbr>abrami@<wbr>austin...`), which
were stripped out. 5-page combined Faculty/Staff/Students directory
(`?page=0`..`?page=4`); the brief's assumption of a separate `finearts.utexas.edu`
people page wasn't needed — the single `art.utexas.edu/about/who-we-are/people`
directory was sufficient. No separate area/discipline field exists, but the
"Designation" field is descriptive enough on its own (e.g. "Studio Art (Painting &
Drawing)", "Studio Art (Sculpture & Extended Media)") — same reliable-signal
pattern as Iowa's Title/Position field. Page 5 (`?page=4`) has only 1 entry (tail
of the roster, not a bug).

### General pattern for this batch
All 3 schools in this batch had a **reliable, page-visible medium/discipline
signal** (Academic Area / Title-Position / Designation), unlike Ohio State which
needed a profile click-through fallback — worth checking for a similar field
before assuming a school needs that heavier approach.

---

## Batch 3 (2026-08-09): RIT, Edinburgh College of Art, Seoul National University

**Result: 183 new faculty rows (RIT 106, Edinburgh 44, SNU 33).** `master_faculty.xlsx`
rebuilt with 8 sheets total, 366 faculty rows overall.

### Rochester Institute of Technology, College of Art and Design — 106 rows have emails
**The brief only gave 2 confirmed program-directory URLs and said "try similar
patterns" without giving IDs.** Guessing sequential numeric IDs directly (e.g.
411487, 411488...) turned out to be unsafe — RIT's server returns HTTP 200 for
essentially any ID in range, including ones with an empty `<title>` (e.g. 411500),
so a wrong guess wouldn't even fail loudly. Instead, fetched each of RIT's 20
official program landing pages (`/artdesign/study/<slug>`, found via
`/artdesign/study/undergraduate` and `/artdesign/study/graduate`) and read each
one's own "All Program Faculty" link to get its real `program-directory/<id>` —
no guessing. 3 programs (Furniture Design AOS, Photographic Arts Exploration,
Studio Arts Exploration) have no such link and were skipped; Art Education MST
excluded as out-of-scope.

Medium was assigned **per-program** (e.g. every Ceramics MFA faculty row gets
"Sculpture"), not from a per-person field — RIT's directory cards only show a
generic department name (e.g. "School of Design") with no finer-grained signal,
so the program itself is the medium signal here. Many faculty are cross-listed on
both a BFA and MFA program page for the same area (e.g. Photography); deduped by
email, keeping the first page's assignment. Large program-to-program variance in
count (Film and Animation BFA: 20, Interior Design BFA: 2) reflects real program
size, not a parsing issue.

### Edinburgh College of Art, University of Edinburgh — 44 rows have emails
Unfiltered `/people` directory is 38 pages (~900 entries) mixing postgrad research
students, professional services staff, and academic staff together with no
reliable role-text way to exclude students after the fact (many students' roles
just say "Postgraduate Research Student", which is filterable, but so is
"Lecturer" for real early-career staff — the two aren't reliably distinguishable
from role text alone if fetched unfiltered). Found the directory's own filter
form uses `field_people_type_target_id[N]` checkboxes with N=17 for "Academic
Staff" and N=16 for "Key Academic Office Holders" — passing those as query params
server-side filters down to 13 pages before any scraping happens, excluding
Honorary/Emeritus, Postgrad Research Students, Professional Services, and Student
Representation entirely. Emails on this page are plain text (not `mailto:` links)
inside a styled `<span>`, not an `<a>` tag — no crawl4ai needed despite that.
Medium classified from the role/title text shown directly on each card (e.g.
"Teaching Fellow - Design (Textiles)", "Programme Director, Performance
Costume").

### Seoul National University, College of Fine Arts — 33 rows have emails
All 5 department category pages from the brief (Design, Painting, Sculpture,
Craft, Oriental Painting) confirmed live and scraped. JS-rendered — required
crawl4ai (plain fetch returns 0 emails; crawl4ai finds them immediately). Medium
classified primarily from each person's research-area text (e.g. "Metalwork and
Jewelry" → Sculpture, "Spatial Design, Parametric Design" → Design), with a
per-department fallback (e.g. anyone on the Painting page with no medium keyword
in their area text, like "Theory of Art", still gets tagged Painting/Drawing from
the department itself) rather than being silently dropped.

### General pattern for this batch
Two different "don't guess" lessons reinforced: RIT's sequential-ID temptation
would have silently produced wrong/duplicate data since invalid IDs don't 404;
Edinburgh's unfiltered directory would have required guessing at role-text
patterns to exclude students where the site's own filter mechanism does it
reliably. Worth checking for a site's own filter/query-param mechanism before
building custom exclusion logic.
