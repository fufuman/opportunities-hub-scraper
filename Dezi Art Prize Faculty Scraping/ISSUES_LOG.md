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

---

## Batch 4 (2026-08-09): VCU, NID Ahmedabad, Jamia Millia Islamia, UIC — Tier 1 complete

**Result: 104 new faculty rows (VCU 78, NID 8, Jamia 7, UIC 11).** `master_faculty.xlsx`
rebuilt with 12 sheets total, 470 faculty rows overall. This completes all 13 Tier 1
schools from the original research brief.

### Virginia Commonwealth University, School of the Arts (VCUarts) — 78 rows have emails
The brief gave no explicit URLs, just "navigate department by department from
arts.vcu.edu." Found each of the 8 in-scope departments' own landing page
(`arts.vcu.edu/department/<slug>/`) links to a shared `/directory/` filtered via
a `department[]` query param — one clean directory, not 8 separate page layouts.
**Real bug caught and fixed**: department directory pages mix teaching faculty
with administrative/support staff under the same card layout (e.g. "Administrative
Affairs Coordinator", "Equipment and Facilities Coordinator") with no separate
field distinguishing them — an early version of the CSV included 6 non-teaching
staff. Fixed with a title-text exclusion filter (Coordinator/Administrative/
Manager/Technician/Advisor). Cross-listed faculty across departments deduped by
email.

### NID Ahmedabad — 8 rows have emails (flagged as possibly incomplete, not a scraper gap)
`/people/faculty` has no pagination and lists only 9 people (1 Director + 8
faculty), covering just Industrial Design, Textile & Apparel Design, and
Communication Design — no Ceramic/Glass or Film/Animation faculty as the brief
expected. Checked NID's own academic program pages
(`/academics/b-des-program/*`): only Industrial Design, Communication Design, and
Textile and Apparel Design exist as current B.Des specializations at this campus.
Ceramic and Glass Design / Animation Film Design are not listed anywhere on the
site (may be offered at a different NID campus — Gandhinagar, Bengaluru, etc. —
or may have been discontinued/restructured since the brief was written). Treated
the 9-person page as likely the genuine complete current roster rather than a
fetch failure, per user decision after being asked.

### Jamia Millia Islamia, Faculty of Fine Arts — 7 rows have emails
The brief's two suggested entry points (`/ffa` hub, university-wide
`Faculty-Dashboard/All-Faculty` search, and the FFA-level `Staff-Member` search)
are all JS-driven search widgets that return **zero results by default** — a
plain fetch shows just an empty search form, and even crawl4ai-rendering those
specific pages doesn't trigger a default search. The fix was to go one level
deeper: each **department's own** "Faculty Members" page
(`/ACADEMICS/Departments/Department-Of-<X>/Faculty-Members`) auto-loads that
department's roster by default when rendered via crawl4ai (plain fetch still
returns nothing — genuinely JS-populated). Scraped Painting, Sculpture, and
Applied Art (all in-scope); Graphic Art department not attempted this pass. Small
counts (1-3 people per department) are real, not a parsing gap — small
departments are typical for Indian public university fine arts programs.

### University of Illinois Chicago, School of Art and Art History — 11 rows have emails
Art History's directory (confirmed to have direct inline emails, matching the
brief) was correctly skipped — Art History is out of scope per the user's medium
list. Used the Studio Art faculty listing instead
(`/content/art-faculty`), split into sections (Studio Arts, Photography, New
Media Arts, Moving Image, Interdisciplinary Degree in the Arts) that map cleanly
to mediums; Art Education section excluded. **Real bug caught and fixed**: the
page uses two different HTML markup patterns for name+title pairs
(`<a>Name</a><br />Title` for most entries vs. `<div><a>Name</a></div><div>Title</div>`
for a few, e.g. Nate Young) — an early version of the person-matching regex only
handled the first pattern and silently dropped anyone using the second, undercounting
by several people across sections. Fixed with a regex that matches either
variant. Confirmed emails are genuinely only on individual profile pages (not the
listing) — required a click-through pass like Ohio State. Emeriti section has no
profile links at all (plain text names only, e.g. "Morris Barazani<br />Professor
Emeritus") and could not be scraped this way — skipped, not attempted via any
fallback.

Also noted: `curl` on this session's machine fails with a schannel TLS error
(`SEC_E_UNSUPPORTED_FUNCTION`) specifically on `artandarthistory.uic.edu` — a
local curl/Windows quirk, not a real site block. Python's `urllib.request` (what
the actual scrapers use) fetched it fine. Worth remembering if `curl` fails
oddly on a future school — try Python directly before assuming the site is down.

### General pattern for this batch
All 13 Tier 1 schools are now done. Two more "the brief's suggested URL doesn't
actually work as described" cases (NID's page being smaller than expected, Jamia's
top-level search pages returning nothing) reinforce the standing rule: verify
before scraping, and when a page genuinely seems incomplete or non-functional,
dig one level deeper (department-specific pages, program pages) before concluding
data doesn't exist. Next up per the original priority order: Tier 2 schools
(Cleveland Institute of Art, Rutgers Mason Gross, Cornell AAP, Syracuse VPA, Slade
UCL, UdK Berlin) — all require profile click-through, the pattern already proven
out on Ohio State and UIC.

---

## Batch 5 (2026-08-09): Cleveland Institute of Art (skipped), Rutgers, Cornell — Tier 2 begins

**Result: 36 new faculty rows (Rutgers 8, Cornell 28). Cleveland Institute of Art
skipped entirely** — no data added for it. `master_faculty.xlsx` rebuilt with 14
sheets total, 506 faculty rows overall.

### Cleveland Institute of Art — SKIPPED, not actually Tier 2
The brief classified CIA as Tier 2 (emails on individual profile pages). Checked 3
of ~181 profile pages (via crawl4ai — plain fetch 307-redirects to a bot-check
page with no useful content) and **none had a public email** — every profile uses
a "direct contact form" widget instead of publishing an address. This makes CIA
functionally Tier 3 (no public emails), not Tier 2. Per user decision after being
asked, skipped scraping entirely rather than capturing 181 names with no emails;
no general school contact email was found either (not fabricated). If this school
matters enough to revisit, the actual roster + discipline data (visible directly
on the listing cards, no click-through needed for that part) is easy to re-scrape
later if a contact-form-based outreach approach becomes acceptable.

### Rutgers University, Mason Gross School of the Arts — 8 rows have emails
Better than the brief's Tier 2 classification: **emails ARE visible directly** on
the Art & Design faculty/staff listing page, no profile click-through needed. Only
32 total people on the page; only 8 have a title specific enough to classify a
medium (e.g. "Associate Professor in Photography", "Director of the Rutgers
Printmaking Collaborative") — the rest have generic titles ("Professor") with no
separate discipline field to fall back on, so were left out rather than guessed.
**Real bug caught and fixed**: a few `mailto:` hrefs are formatted as URL-encoded
`"Name <email>"` rather than a bare address (e.g.
`mailto:Miranda%20Lichtenstein%20&lt;mlichtenstein@mgsa.rutgers.edu&gt;`) — an
early version captured the whole encoded string as the "email"; fixed by
extracting just the actual address pattern from whichever format the href uses.

### Cornell University, Department of Art (AAP) — 28 rows have emails
Confirmed Tier 2 as the brief said: the `/art/art-people` listing (41 entries, 5
of them duplicates from dual program listings — deduped to 36 unique profiles)
shows no per-person email, only a department general address. Required a full
profile click-through pass. Medium classified from title/role text first (mostly
generic — "Professor", "Chair"), falling back to each profile's bio paragraph
(e.g. "...examine feminist care networks... archival and authored photographs..."
→ Photography/Sculpture) when the role alone gave no signal — same pattern as
Ohio State's bio-text fallback, and same lesson learned there about isolating the
actual bio container (`person-topper__bio`) rather than the whole page, to avoid
sitewide nav boilerplate swamping the keyword match.

**Real data-quality finding, not a bug**: 5 of the 28 rows resolve to the same
`imagetext@cornell.edu` address — checked several of these individually and
confirmed each profile page genuinely lists that shared program mailbox as their
own contact (likely visiting/affiliated faculty routed through a specific MFA
program's inbox rather than having a personal Cornell address). Flagged these
with `email_type=department_general` instead of `profile`, since they're not
actually that individual's personal email even though the source page presents
them that way.

### General pattern for this batch
First genuine "brief was wrong about which tier a school belongs to" case in
either direction: CIA was optimistically classified as Tier 2 but is really Tier 3
(no emails at all), while Rutgers was pessimistically classified as Tier 2 but is
actually Tier 1-quality (direct emails). Worth treating every school's tier
classification as a hypothesis to verify, not a given, same as URLs and page
counts have been throughout this project.

---

## Batch 6 (2026-08-09): Syracuse, Slade (UCL) — Tier 2 complete; UdK Berlin skipped

**Result: 25 new faculty rows (Syracuse 4, Slade 21). UdK Berlin skipped entirely**
— no data added. `master_faculty.xlsx` rebuilt with 16 sheets total, 531 faculty
rows overall. This completes all attemptable Tier 2 schools from the original
brief (CIA and UdK Berlin both skipped; 4 of 6 Tier 2 schools yielded data).

### UdK Berlin — SKIPPED, no working staff-directory URL found
The brief's claimed path (Fine Art teaching staff pages with space-obfuscated
emails) doesn't match the live site. Checked the English `/people/` hub (nav-only,
no roster), the Institute of Fine Arts overview page (descriptive text only, one
link back to the same dead-end `/people/` hub, no individual profile links at
all), and the parallel Art Didactics institute page (same pattern, confirming
it's not specific to Fine Arts). Per user's "try 2-3 educated German guesses"
allowance, tried `/studium/bildende-kunst/` (no roster, points to StudyGuide
general contact) and `/universitaet/fakultaet-bildende-kunst/` (overview page
only, points to the same `/personen/` German-language hub — presumably the same
nav-only dead end as the English `/people/` version). Stopped after 3 attempts
per the project's standing "don't keep guessing URLs" rule. If this school is
wanted, it likely needs a human browsing the German-language site directly to
find the real per-institute staff roster (if one exists) or confirm none is
public.

### Syracuse University, VPA School of Art — 4 rows have emails
Confirmed the brief's own finding: the master `/faculty-staff/` directory is a JS
search widget with zero default results (a real site limitation, not a fetch
quirk — independently reproduced). The `/academics/art/contact/` page the brief
also flagged has only 2 people with a direct email (School of Art Director +
Administrative Assistant — the latter excluded as non-faculty) plus 4 "Area
Leads" named with a discipline label (e.g. "Printmaking", "Illustration B.F.A.")
but email only on their own profile page — required a click-through pass for
those 4. The Director's profile page has no discipline field at all; classified
from his bio paragraph instead (same bio-fallback pattern as Ohio State/Cornell,
using the page's `biography-content` container to avoid the sitewide nav-menu
keyword-collision bug found on Ohio State). 1 of the 4 area leads (label "Studio
Arts B.F.A., Studio Arts B.S." — no specific medium named) correctly excluded
rather than guessed.

### Slade School of Fine Art, UCL — 21 rows have emails
Brief's suggested `/people/key-staff/` page is administrative/technical staff
only (confirmed) — real academic staff live at `/people/academic/` instead
(found via WebFetch surfacing the actual link text after the `/people/`
landing-hub page didn't show a usable roster directly). Single page, 46 people,
no pagination. Title text gives a direct, reliable medium signal (e.g. "Lecturer,
Painting", "Associate Professor, Sculpture") — email only on individual profile
pages, requiring a click-through pass for the 21 in-scope people (of 46 total;
the rest are Art History, Fine Art Media/general, or admin-adjacent roles with no
matching medium keyword).

### General pattern for this batch
Two more "the brief's named URL isn't the right one, but a nearby page is" cases
(Slade's key-staff vs. academic page; Syracuse's directory vs. contact page) —
consistent with the whole project's pattern of verifying rather than trusting a
brief's exact URL. UdK Berlin is the first school this project has fully given up
on for lack of a findable data source, as opposed to giving up on it having public
emails (CIA) — worth flagging clearly as "needs manual URL discovery," not
"scraped, zero results," when reporting status.
