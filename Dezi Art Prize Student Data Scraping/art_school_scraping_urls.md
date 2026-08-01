# Art School Student Data: Scrapable URLs

28 schools. For each: the exact URLs to scrape, what data is on the page, and whether JS rendering is needed.

---

## TIER 1: JS rendering needed (use crawl4ai with render_js=True)

### 1. RIT (Rochester Institute of Technology)
**Main portal:** https://creativity.cad.rit.edu/
**Per-major pages:** https://creativity.cad.rit.edu/students2020.php?major=SOMETHING
**What's there:** Student name, major, portfolio link, resume link
**JS rendering:** Yes, required. Content loads dynamically.
**Notes:** Iterate through each major filter to get all students. Check the main page for available major codes.

---

## TIER 2: Static HTML, scrapable with plain fetch

### 2. MCAD (Minneapolis College of Art and Design)
**Done.** Already extracted. 51 artists in Excel.
**URLs used:**
- https://www.mcad.edu/events/spring-2022-commencement (names + emails + portfolios)
- https://www.mcad.edu/events/spring-2023-commencement-ceremony (names + hometowns, fewer emails)
- https://www.mcad.edu/events/spring-2025-commencement-exhibition (exhibition page, names may be lighter)
- https://www.mcad.edu/events/spring-2026-commencement-exhibition
**Also check Issuu:** https://issuu.com/mcadedu (commencement catalogs with full grad lists)

### 3. RISD (Rhode Island School of Design)
**Grad show site:** https://risdgrad.show (changes each year, may need current year URL)
**Thesis repository:** https://digitalcommons.risd.edu/campusexhibitions_graduatethesisexhibitions/
**What's there:** Per-student pages with name, work, statement. Thesis PDFs with full attribution.
**JS rendering:** Likely needed for risdgrad.show (modern microsite). DigitalCommons is static HTML.
**Notes:** 200+ grads per year across 19 programs. The DigitalCommons archive has years of data.

### 4. Yale School of Art
**Main exhibitions:** https://art.yale.edu/exhibitions
**MFA thesis page:** https://art.yale.edu/MFAThesis
**Per-department show pages (example pattern):**
- https://art.yale.edu/exhibitions/spring-2025-painting-thesis
- https://art.yale.edu/exhibitions/spring-2025-photography-thesis
- https://art.yale.edu/exhibitions/spring-2025-sculpture-thesis
**Viewing rooms:** https://yalemfathesis.viewingrooms.com
**What's there:** Full names per department thesis show. Small cohorts (10-19 per dept).
**JS rendering:** art.yale.edu is a wiki-style site, likely static. Viewing rooms may need JS.
**Also check:** e-flux mirrors Yale MFA thesis announcements with full name lists.

### 5. Cranbrook Academy of Art
**Partially done.** 7 names from 2026, 4 from 2025 in Excel.
**2026 exhibition:** https://cranbrookartmuseum.org/exhibition/2026-graduate-degree-exhibition-of-cranbrook-academy-of-art/
**2025 exhibition:** https://cranbrookartmuseum.org/exhibition/2025-graduate-degree-exhibition-of-cranbrook-academy-of-art/
**Virtual tour (2020, had contact info):** Check if still live at cranbrookart.edu subdomain
**Degree exhibition hub:** https://cranbrookart.edu/educational-experience/degree-exhibition/
**What's there:** Photo captions with some names + departments. Full list (58 in 2026, 68 in 2023) is in the exhibition catalog, not fully on the HTML page.
**JS rendering:** Probably not needed for museum pages. Virtual tour likely needs JS.
**Also check e-flux:**
- https://www.e-flux.com/announcements/6787136/2026-graduate-degree-exhibition (may have full list in body)
- https://www.e-flux.com/announcements/517967/2023-graduate-degree-exhibition-of-cranbrook-academy-of-art

### 6. Parsons School of Design (The New School)
**MFA Fine Arts thesis catalogs:**
- https://amt.parsons.edu/finearts/ (hub page, links to yearly catalogs)
- https://amt.parsons.edu/finearts/2020mfathesis/ (2020 catalog)
- https://amt.parsons.edu/finearts/2023mfathesis/ (try this pattern for 2023)
- https://amt.parsons.edu/finearts/2024mfathesis/ (try for 2024)
**Event pages:** https://event.newschool.edu/mfafineartsthesis2024
**What's there:** Per-student pages with name, work, statement. 20-22 grads per year.
**JS rendering:** Likely static HTML catalog format.

### 7. SVA (School of Visual Arts), New York
**Per-department MFA thesis sites:**
- https://mfafinearts.sva.edu
- https://mfafineart.sva.edu/exhibitions
- https://artpractice.sva.edu
- https://mfavisualnarrative.sva.edu/thesis/
- https://sva.edu/academics/graduate/mfa-computer-arts/student-work
**What's there:** Full participant names per thesis show. 20-28 per department.
**JS rendering:** Unknown. Try static first, fall back to JS rendering.

### 8. Pratt Institute, New York
**Pratt Shows hub:** https://pratt.edu/pratt-shows/
**Per-event example:** https://pratt.edu/events/pratt-shows-mfa-thesis-exhibition-part-1/
**What's there:** Exhibiting artist names listed on each event page. 16-20 per exhibition part.
**JS rendering:** Likely static HTML on Drupal/WordPress.
**Also check Hyperallergic:** mirrors Pratt Fine Arts lists.

### 9. Otis College of Art and Design
**Annual exhibition microsite:**
- https://annual-exhibition.otis.edu (main hub)
- https://annual-exhibition.otis.edu/2022/annual-exhibition/all-students (all students, 2022)
- Try /2024/, /2025/, /2026/ for other years
**What's there:** Full graduating class across ~9 programs with per-student pages.
**JS rendering:** Likely needed for the annual exhibition microsite (modern web app).

### 10. Alfred University, School of Art and Design
**MFA thesis exhibit archive:**
- https://alfred.edu/academics/colleges-schools/art-design/thesis-exhibits/ (hub)
- Per-student subpages example: https://alfred.edu/academics/colleges-schools/art-design/thesis-exhibits/spring-2023/mfa/ahmad/
- Pattern: /thesis-exhibits/[semester-year]/mfa/[lastname]/
**What's there:** Per-student pages with name, bio, artist statement, work images. 5-15 MFA per year.
**JS rendering:** Likely static HTML. Clean per-student URL structure.

### 11. Temple University, Tyler School of Art and Architecture
**2025 MFA thesis:** https://tyler.temple.edu/2025-mfa-thesis-exhibitions-rewoven-collective-stories
**2024 MFA thesis:** https://tyler.temple.edu/2024-mfa-thesis-exhibitions
**STELLA virtual gallery:** https://www.stellaonline.art/
**What's there:** Full participant lists (25-37 MFA per year). STELLA has browsable student work.
**JS rendering:** Tyler pages likely static. STELLA likely needs JS.
**Also check e-flux:** https://www.e-flux.com/announcements/515462/mfa-thesis-exhibitions

### 12. VCU (Virginia Commonwealth University), School of the Arts
**ICA exhibition pages:**
- https://icavcu.org/exhibitions/2025-mfa-thesis/ (26 named)
- https://icavcu.org/exhibitions/2026-vcuarts-mfa-thesis-exhibition-round-1/
**VCUarts event page:** https://arts.vcu.edu/event/2025-vcuarts-mfa-thesis-exhibition/
**Art History grad students directory:** https://arts.vcu.edu/art-history/current-grad-students/
**What's there:** Full names + mediums per exhibition. 26-28 MFA per year.
**JS rendering:** Likely static HTML.
**Also check Hyperallergic:** mirrors full VCU name lists.

### 13. Carnegie Mellon, School of Art
**MFA students directory:** https://art.cmu.edu/mfa/students/ (current students, persistent)
**2025 MFA thesis exhibition:** https://art.cmu.edu/event/holding-still-holding-on/ (5 named)
**What's there:** The /mfa/students/ page lists first and second year MFA candidates by name. Small cohorts (5-8 MFA per year).
**JS rendering:** Likely static WordPress.

### 14. CCA (California College of the Arts)
**Grad Fine Arts MFA thesis exhibitions:**
- https://portal.cca.edu/events-calendar/2025-graduate-fine-arts-mfa-thesis-exhibition/
- Try same pattern for 2023, 2024, 2026
**What's there:** Full exhibitor names on event pages. 30+ MFA per year (16 per part in 2023).
**JS rendering:** Likely static portal page.

### 15. MassArt (Massachusetts College of Art and Design)
**MFA thesis exhibitions:**
- https://calendar.massart.edu/event/2022_mfa_thesis_exhibition
- https://calendar.massart.edu/event/2023_massart_mfa_thesis (try this pattern)
**MFA artist talks:** https://maam.massart.edu/event/mfa-artist-talks
**Thesis info page:** https://blogs.massart.edu/gradstudents/mfa-thesis-info/
**What's there:** Named artists per show. Small cohorts (7-12).
**JS rendering:** Likely static calendar/event pages.

### 16. UW-Madison, Art Department
**MFA Exhibitions archive:** https://art.wisc.edu/category/events/mfa-exhibitions/
**What's there:** Individual per-student news posts with name, statement, exhibition info. 6-10 MFA per year. Archived back to ~2019.
**JS rendering:** Likely static WordPress.

### 17. Ohio State University, Department of Art
**MFA thesis exhibition:** https://uas.osu.edu/events/thesis-department-art-mfa-third-year-exhibition (13 named)
**Current grad students:** https://art.osu.edu/grad-studies/current
**MFA alumni directory:** https://art.osu.edu/alumni-friends/mfa-alumni-directory
**What's there:** Names on exhibition pages. Alumni directory has spotlight profiles. 8-13 MFA per year.
**JS rendering:** Likely static HTML.

### 18. University of Michigan, Stamps School of Art and Design
**MFA thesis exhibition:** https://stamps.umich.edu/events/2025-mfa-thesis-exhibition (7 named)
**Graduate work gallery:** https://stamps.umich.edu/research-creative-work/graduate-work-mfa
**Undergraduate IP/senior shows:** https://stamps.umich.edu/research-creative-work/undergraduate-work
**What's there:** MFA ~7 per year. IP/senior shows 70-92 students per year.
**JS rendering:** Likely static HTML.

### 19. Cornell University, Department of Art
**BFA thesis group exhibition:** https://aap.cornell.edu/events/exhibition/thesis-group-exhibition/ (9 BFA 2025)
**MFA exhibitions:**
- https://aap.cornell.edu/news-events/exhibition/mfa-students-deep-end (11 MFA)
- https://aap.cornell.edu/news-events/exhibition/mfa-virtual-exhibition-how-build-ocean (12 MFA 2020/2021)
**What's there:** Names + class year. Small program (9-12 per year).
**JS rendering:** Likely static HTML.

### 20. UT Austin, Department of Art and Art History
**Department event pages:** https://art.utexas.edu/events/all-else-2024-studio-art-mfa-thesis-exhibition (6 named)
**Visual Arts Center microsite:** https://utvac.org/event/half-second-or-less-2026-studio-art-mfa-thesis-exhibition (7 named)
**What's there:** Names in exhibition descriptions. 5-16 MFA per year. Names sometimes embedded in prose rather than a clean list.
**JS rendering:** Likely static HTML.

### 21. BU (Boston University), College of Fine Arts
**MFA thesis exhibition articles:**
- https://bu.edu/cfa/featured-work/mfa-thesis-2024/
- https://bu.edu/cfa/news/articles/2024/mfa-thesis-exhibitions/
- Try same pattern for 2023, 2025, 2026
**What's there:** Names + artwork captions. 40-61 MFA per year. Names sometimes in article prose rather than clean lists.
**JS rendering:** Likely static HTML.
**Notes:** May need to combine school article + BU Today press piece for full roster.

### 22. MICA (Maryland Institute College of Art)
**Grad show:** https://mica.edu/gradshow
**Annual events series:** https://mica.edu/events-exhibitions/annual-events-series/mica-grad-show/
**What's there:** Virtual showcase of MFA/MA work by name. "Hundreds" across 14 programs.
**JS rendering:** The online exhibition likely needs JS. Event pages may be static.
**Notes:** Some undergrad info behind Canvas login. Grad show should be public.

### 23. CalArts (California Institute of the Arts)
**Master's theses digital collection:** https://library.calarts.edu/digitalcollections/masterstheses
**News/blog posts:** https://calarts.edu/news (search for thesis exhibitions, MFA spotlights)
**What's there:** Thesis collection has names + full text. Blog posts name cohort members. 20-30 per year.
**JS rendering:** Library digital collections likely static. News pages static HTML.
**Notes:** No single persistent grad show microsite. Names are scattered across news posts and library.

### 24. Cooper Union, New York
**End of year show:**
- https://cooper.edu/events-and-exhibitions/exhibitions/2026-end-year-show
- Try same pattern for 2025, 2024
**Archived virtual show (2020):** https://endofyearshow2020.cooper.edu
**School of Art galleries:** https://cooper.edu/art/galleries
**What's there:** 200+ works from 200+ students. Names attributed by tradition (name only, no bio/links usually).
**JS rendering:** Main site likely static. 2020 virtual show may need JS.
**Notes:** Cooper's tradition is to list works by artist name only without additional info. Disambiguation may be harder.

### 25. UCLA School of the Arts and Architecture
**Department of Art events:**
- https://art.ucla.edu/events (browse for MFA exhibition pages)
- https://goarts.ucla.edu/events/mfa-exhibition-1
**Design Media Arts:** https://dma.ucla.edu/events
**What's there:** Names per exhibition. Small cohorts (4-16). DMA separate from studio art.
**JS rendering:** Likely static HTML.
**Notes:** Some 2024 shows were disrupted/withdrawn amid campus protests.

### 26. SCAD (Savannah College of Art and Design)
**Thesis digital collection:** https://scad.libguides.com/gradstudents/thesis
**Library thesis resources:** https://www.scad.edu/life/student-services/libraries-and-learning-resources/library-information/theses
**Student work pages:** https://scad.edu/academics/programs/*/student-work (replace * with program name)
**What's there:** MFA theses since Fall 2010 with names + full visual/written components. Thousands across 100+ programs.
**JS rendering:** Libguides is static. Some SCAD pages may need JS.
**Notes:** Huge volume. Filter for visual art programs specifically. Some deeper resources behind MySCAD login.

### 27. Columbia College Chicago
**NOT CONFIRMED in the research.** The most likely source is "Manifest," their annual graduating student urban arts festival.
**Try:** https://colum.edu and search for "Manifest" or "graduating exhibition" or "senior show"
**Notes:** Needs manual verification before scraping. Flagged as the one gap in the research.

---

## PRIORITY ORDER FOR SCRAPING

If you're giving these to Claude Code in batches, do them in this order (highest data yield first):

**Batch 1 (highest yield, cleanest data):**
1. RIT creativity portal (hundreds of students, portfolio links)
2. RISD DigitalCommons (years of thesis data)
3. Otis annual exhibition (full graduating class)
4. MCAD Spring 2023 + 2025 + 2026 commencement pages (expand existing data)

**Batch 2 (good yield, clean per-student pages):**
5. Parsons MFA catalog pages (20-22 per year, per-student pages)
6. Alfred thesis archive (per-student subpages, multi-year)
7. Temple/Tyler thesis pages + STELLA
8. VCU ICA exhibition pages (26-28 per year)

**Batch 3 (smaller cohorts but clean data):**
9. Yale per-department thesis pages
10. CMU MFA students directory
11. Cornell exhibition pages
12. UW-Madison MFA exhibitions archive
13. Ohio State thesis + alumni directory

**Batch 4 (larger schools, more digging needed):**
14. SVA per-department thesis sites (5 separate department sites)
15. Pratt Shows event pages
16. MICA grad show
17. BU CFA thesis articles
18. CCA portal event pages
19. MassArt calendar events
20. U Michigan Stamps

**Batch 5 (hardest to extract or most scattered):**
21. Cranbrook (virtual tour, exhibition catalog)
22. CalArts (library + scattered news posts)
23. Cooper Union (names only, hard to link to individuals)
24. UCLA (small, scattered across departments)
25. SCAD (huge volume, needs filtering)
26. Columbia College (unconfirmed source)

---

## SCRAPING NOTES FOR CLAUDE CODE

For all schools, tell Claude Code:

1. Try plain fetch first. If the page comes back empty or with "Loading..." content, retry with crawl4ai render_js=True
2. For each school, extract: student_name, program/major, graduation_year, email (if present), portfolio_url (if present), resume_url (if present), school_name, source_url
3. Output each school to its own CSV in the phase extraction folder
4. Log: school name, number of students found, number with emails, number with portfolio links, any errors
5. Cache every fetched page per CLAUDE.md rules
6. If a page has pagination or tabs/filters (like RIT's major filter), iterate through all of them
7. If a page is behind a login wall, flag it and skip, don't try to bypass
