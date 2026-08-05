# Next-Tier US Art Schools with Publicly Accessible Student Data (Ranks ~31–70)

## TL;DR
- I identified **28 prominent US art schools** beyond the original 30 that have publicly accessible, scrapable student-name listings — thesis/grad-show pages, senior showcases, or institutional repositories — with the cleanest single-page rosters at **University of Iowa, University of Washington (Henry Art Gallery), UT Knoxville (TRACE repository), and BGSU (ScholarWorks)**.
- **Almost none of these pages publish student email addresses or personal portfolio links**; they list names (and often medium/discipline), so any outreach will require a separate name → contact enrichment step.
- **Independent art colleges** (KCAI, Cleveland Institute of Art, Ringling, PNCA, CCAD, College for Creative Studies, MIAD, MECA&D, PAFA, Moore, LCAD) tend to use dedicated grad-show microsites (some JavaScript-rendered), while **state-university MFA programs** favor plain-HTML news/gallery/repository pages that are easiest to scrape.

## Key Findings
- **Best scraping targets (plain HTML, complete rosters):** University of Iowa MFA virtual exhibitions page; University of Washington/Henry Art Gallery thesis pages; UT Knoxville TRACE and BGSU ScholarWorks institutional repositories; SUNY New Paltz museum pages. All are server-rendered and require no JavaScript.
- **Microsite-driven independent colleges:** Ringling (ringlingthesis.com, Squarespace, JS-rendered), PNCA (Willamette-hosted gallery pages), Hunter MFA (dedicated microsite), KCAI (kcai.edu).
- **Email/portfolio availability:** Consistently absent across all 28 confirmed schools. Ringling pages surface only a generic admissions email; links, where present, point to virtual-tour tools (Matterport at Iowa) or digital catalogs (Issuu at UW and PAFA), not personal sites.
- **Scale:** BFA showcases at large independent colleges list far more names per event than university MFA cohorts. College for Creative Studies shows more than 4,800 pieces (101st exhibition, 2026, with over 3,200 opening-night attendees per Hour Detroit); KCAI's official 2026 BFA Exhibition features 123 graduates (the 2025 show was reported by Make48 as "over 700 student artists"); MIAD names 51 senior-thesis-award recipients in 2026; MECA&D graduates ~85 BFA students annually. University MFA cohorts typically run 5–35.

## Details

### Independent art colleges / institutes

**1. Kansas City Art Institute (KCAI) — Kansas City, MO**
- Programs: BFA across animation, art history, ceramics, creative writing, fiber, filmmaking, graphic design, illustration, interactive arts, painting, photography, printmaking, sculpture.
- Student data: Annual BFA Exhibition pages at kcai.edu/kcai-gallery.
- URLs: https://kcai.edu/kcai-gallery/exhibitions/2025_BFA_Exhibition/ ; https://kcai.edu/kcai-gallery/
- Emails/portfolio: Not on public pages.
- Approx. count: The official 2026 Annual BFA Exhibition page states it features "recent work by 123 graduates"; the 2025 show was described by Make48 as "over 700 student artists."
- JS rendering: Likely partial (WordPress-based); names may appear in HTML.
- Notes: Individual student names not always consolidated on a single page.

**2. Cleveland Institute of Art (CIA) — Cleveland, OH**
- Programs: BFA in animation, life sciences illustration, game design, illustration, photography, ceramics, drawing, painting, printmaking, sculpture, expanded media, industrial design, interior architecture, glass, etc.
- Student data: Student Exhibitions section and BFA thesis pages (solo mini-shows per graduating senior).
- URLs: https://www.cia.edu/exhibition-categories/student-exhibitions/ ; https://www.cia.edu/exhibitions/
- Emails/portfolio: Not published.
- Approx. count: 566 total undergraduate enrollment (fall 2023, per U.S. News; AICAD lists "about 600 students"); one solo show per graduating senior.
- JS rendering: Partial.
- Notes: Names appear per-exhibition rather than as a single roster.

**3. Ringling College of Art and Design — Sarasota, FL**
- Programs: 13 majors including fine arts, computer animation, game art, motion design, illustration, photography & imaging, graphic design, visual studies, film, creative writing, entertainment design.
- Student data: Dedicated senior thesis microsites with per-major galleries and an online Visual Studies exhibit.
- URLs: https://www.ringlingthesis.com/ ; https://www.ringlingcollege.gallery/2025-thesis ; https://www.ringling.edu/news/ (photo galleries)
- Emails/portfolio: Only a generic admissions email (admissions@ringling.edu) appears.
- Approx. count: Full graduating class across 13 majors.
- JS rendering: Yes — Squarespace-based microsite; requires JS for galleries.
- Notes: Some majors have online exhibits with student names; others show installation photos.

**4. Pacific Northwest College of Art (PNCA) at Willamette University — Portland, OR**
- Programs: BFA; MFA in Visual Studies, Print Media, Collaborative Design; MA in Design Systems/Critical Studies; low-residency MFA.
- Student data: MFA/BFA thesis exhibition pages with individual names (e.g., MFA Print Media and Collaborative Design cohorts listed by name at partner venue Stelo).
- URLs: https://my.willamette.edu/site/pnca-thesis ; https://pnca-gallery.willamette.edu/ ; https://www.steloarts.org/
- Emails/portfolio: Not published.
- Approx. count: ~53 combined BFA/MFA in 2025; ~30 MFA in a recent year.
- JS rendering: Partial.
- Notes: Names split across host (Willamette) and partner gallery pages.

**5. Columbus College of Art & Design (CCAD) — Columbus, OH**
- Programs: 12 undergraduate majors + MFA in Visual Arts and Master of Professional Studies. Fine Arts thesis = solo senior exhibitions.
- Student data: Student gallery pages; individual thesis exhibition event pages (each named per student).
- URLs: https://www.ccad.edu/experience-art/student-galleries ; https://events.ccad.edu/
- Emails/portfolio: Not published.
- Approx. count: One solo show per graduating Fine Arts senior.
- JS rendering: Partial.
- Notes: Event pages named per student (e.g., "Studio thesis portfolio exhibition - Sarah Hetrick").

**6. College for Creative Studies (CCS) — Detroit, MI**
- Programs: BFA + MFA across illustration, product/transportation design, film, fine arts, textiles, color & materials, entertainment arts, etc. (~1,440 undergraduates).
- Student data: Annual Student Exhibition (101st in 2026).
- URLs: https://www.ccsdetroit.edu/student-exhibition/ ; https://www.ccsdetroit.edu/event-category/exhibition/
- Emails/portfolio: Not published.
- Approx. count: More than 4,800 pieces of art and design in 2026, per Hour Detroit, which also reported "over 3,200 attendees" on opening night.
- JS rendering: Partial.
- Notes: Exhibition is also a sale; individual names not consolidated into a single scrapable roster on the main pages.

**7. Milwaukee Institute of Art & Design (MIAD) — Milwaukee, WI**
- Programs: BFA in communication design, illustration, fine art + new studio practice, interior architecture & design, product design, animation.
- Student data: Senior Exhibition pages plus many individual student profile news posts (name, major, hometown, honor roll).
- URLs: https://www.miad.edu/seniorexhibition ; https://www.miad.edu/newsroom
- Emails/portfolio: Not published; Instagram handles sometimes mentioned in prose.
- Approx. count: 200+ seniors; per MIAD, the college awarded "a record $7,150 to an unprecedented 51 seniors" for 2026 senior-exhibition capstone projects, each named in news posts.
- JS rendering: Partial.
- Notes: Rich per-student prose is useful for downstream enrichment.

**8. Maine College of Art & Design (MECA&D) — Portland, ME**
- Programs: BFA (many majors incl. animation & game art, textile & fashion design); MFA in Studio Art (full/low-residency); MAT. Shows at the ICA at MECA&D.
- Student data: MFA thesis exhibition pages; BFA thesis event pages.
- URLs: https://meca.edu/ica/2024-mfa-thesis-exhibition/ ; https://meca.edu/event/4f9f560/
- Emails/portfolio: Not published.
- Approx. count: MFA ~9–17/year; BFA ~85/year.
- JS rendering: No (WordPress plain HTML).
- Notes: Full MFA rosters also appear on Hyperallergic press pages.

**9. Pennsylvania Academy of the Fine Arts (PAFA) — Philadelphia, PA**
- Programs: BFA, MFA, Post-Bacc, Certificate, and low-residency MFA (painting, sculpture, printmaking, drawing).
- Student data: Annual Student Exhibition (124th in 2025) with online catalog and sale platform.
- URLs: https://www.pafa.org/museum/exhibitions/124th-annual-student-exhibition ; https://www.pafa.org/education/academic-programs/annual-student-exhibition
- Emails/portfolio: Not published.
- Approx. count: The 124th ASE (on view May 9–June 1, 2025) featured work by "third- and fourth-year Undergraduate students, second-year Graduate students, Post-Bacc students, and third-year Low-Residency MFA students"; the prior (123rd) show showcased nearly 1,000 works by 56 students. The full catalog is published on Issuu (issuu.com/pafa/docs/124th_annual_student_exhibitoon_2025).
- JS rendering: Partial (online catalog/sale platform).
- Notes: The Issuu catalog and sale platform list student names.

**10. Moore College of Art & Design — Philadelphia, PA**
- Programs: BFA (animation & game arts, art education, art history, curatorial studies, fashion design, fine arts, graphic design, illustration, interior design, photography & digital arts); MFA/MA in socially engaged art.
- Student data: Senior Show pages; earlier years used a dedicated "Class of" website with a page per graduate.
- URLs: https://moore.edu/events/senior-show-one-friends-amp-family-reception/2026-04-16/ ; https://moore.edu/news/
- Emails/portfolio: The 2020 "Class of" microsite functioned as a digital "calling card" per artist.
- Approx. count: Full BFA class across ~10 majors.
- JS rendering: Partial.
- Notes: Two senior shows per year, split by major group.

**11. Laguna College of Art + Design (LCAD) — Laguna Beach, CA**
- Programs: BFA in 11 majors (drawing & painting, illustration, game art, animation, graphic design, sculpture emphasis); 3 MFA programs; post-bacc.
- Student data: BFA and MFA thesis exhibition pages with full artist name lists.
- URLs: https://www.lcad.edu/events/bfa-fine-arts-exhibition-2025/ ; https://www.lcad.edu/pacific-current-general-thesis-exhibition/
- Emails/portfolio: Not published.
- Approx. count: MFA ~8–14/year; BFA cohort.
- JS rendering: Partial (WordPress).
- Notes: Names explicitly listed in exhibition descriptions (e.g., 14 MFA grads named in Pacific Current).

### University MFA / studio art programs

**12. Rutgers, Mason Gross School of the Arts — New Brunswick, NJ**
- Programs: MFA (established 1960, the first non-disciplinary fine art MFA in the US) — painting, sculpture, photography, media, printmaking, design; BFA. Private year-round studios.
- Student data: Self-curated MFA thesis exhibitions in Mason Gross Galleries; "Featured artists" name lists on calendar pages.
- URLs: https://www.masongross.rutgers.edu/calendar-event/mfa-thesis-ii-exhibition/ ; https://designing.rutgers.edu/
- Emails/portfolio: Not published.
- Approx. count: ~8–9 per thesis show; multiple shows per year.
- JS rendering: Partial.
- Notes: Names appear in "Featured artists" lists.

**13. Hunter College (CUNY) MFA in Studio Art — New York, NY**
- Programs: 3-year MFA in Studio Art at 205 Hudson (Tribeca).
- Student data: Dedicated MFA program microsite with thesis exhibition pages.
- URLs: https://www.huntermfastudio.org/thesis-exhibitions-2026 ; https://www.huntermfastudio.org/mfa-thesis-exhibitions
- Emails/portfolio: Not published.
- Approx. count: ~35 artists across five thesis shows per year.
- JS rendering: Likely (dedicated microsite).
- Notes: Public program; names grouped by exhibition.

**14. Bard College, Milton Avery Graduate School of the Arts (Bard MFA) — Annandale-on-Hudson, NY**
- Programs: Low-residency MFA in Moving Image, Music/Sound, Painting, Photography, Sculpture, Writing.
- Student data: Class thesis exhibitions with full name rosters published in press (e-flux, bard.edu, Hyperallergic).
- URLs: https://www.bard.edu/news/ (thesis exhibition posts) ; e-flux announcement pages list every candidate by name.
- Emails/portfolio: Not published.
- Approx. count: ~22 candidates in the 2026 class.
- JS rendering: No (plain HTML news/press).
- Notes: e-flux posts give a complete alphabetical roster with discipline — very scrapable.

**15. New Mexico State University (NMSU) — Las Cruces, NM**
- Programs: BFA + MFA (ceramics, photography, metals/jewelry, painting, etc.); University Art Museum hosts thesis shows.
- Student data: Named BFA and MFA thesis rosters on department, museum, and news pages.
- URLs: https://artdepartment.nmsu.edu/pages/calendar/past-thesis-exhibitions.html ; https://uam.nmsu.edu/exhibitions/archive.html
- Emails/portfolio: Not published.
- Approx. count: ~14 combined BFA/MFA in 2025 (4 MFA + 10 BFA).
- JS rendering: No.
- Notes: Names appear on both English and Spanish exhibition pages.

**16. University of New Mexico (UNM) — Albuquerque, NM**
- Programs: 3-year MFA in Art Studio with concentrations in Art & Ecology, Ceramics, Experimental Art & Technology, Painting/Drawing, Photography, Printmaking, Sculpture & Expanded Practice.
- Student data: MFA thesis/graduate exhibition event pages naming artists.
- URLs: https://art.unm.edu/events/ (graduate exhibition posts) ; https://art.unm.edu/become-a-student/graduate
- Emails/portfolio: Not published.
- Approx. count: MFA cohort; the final Confluence low-residency show named nine artists.
- JS rendering: No.
- Notes: Solo-dissertation-exhibition model means names spread across events.

**17. Herron School of Art + Design (Indiana University Indianapolis) — Indianapolis, IN**
- Programs: BFA (painting, sculpture, photography, printmaking, intermedia, design), MFA in Visual Art, art history, art therapy.
- Student data: Senior Showcase / Look-See / graduate thesis exhibition pages; art history theses in IUPUI ScholarWorks.
- URLs: https://herron.indianapolis.iu.edu/galleries/exhibitions/index.html ; https://herron.iupui.edu/look-see/index.html
- Emails/portfolio: Not published.
- Approx. count: Full BFA/MFA graduating cohort.
- JS rendering: No/partial.
- Notes: Look-See covers BA, BAE, BFA, MA, MFA, MS, PhD graduates.

**18. University of Arizona, School of Art — Tucson, AZ**
- Programs: BFA + MFA Studio Art (animation, ceramics, intermedia, metals, painting & drawing, photography, illustration, 2D/3D & extended media, art education).
- Student data: MFA thesis exhibition microsite + plain-HTML news pages listing all names; CCP event pages with bulleted name lists.
- URLs: https://art.arizona.edu/11-artists-showcase-work-in-2025-mfa-exhibition/ ; https://ccp.arizona.edu/events/mfa-thesis-show-2025 ; https://galleries.art.arizona.edu/
- Emails/portfolio: Not published.
- Approx. count: ~6–13 MFA/year (11 in 2025).
- JS rendering: News pages plain HTML; gallery microsite may need JS.
- Notes: This is University of Arizona (Tucson), NOT Arizona State (Tempe); some gallery pages carry content warnings.

**19. University of Georgia, Lamar Dodd School of Art — Athens, GA**
- Programs: BFA + MFA (painting, printmaking, photography, ceramics, sculpture, jewelry/metals, graphic design, interior design, scientific illustration); MA/PhD Art History.
- Student data: MFA thesis news posts listing all artists; BFA "Exit Show."
- URLs: https://art.uga.edu/mfa/ ; MFA thesis news posts under art.uga.edu.
- Emails/portfolio: Not published.
- Approx. count: ~11–20 MFA/year; ~42 BFA/year.
- JS rendering: No (WordPress).
- Notes: Names spread across dated news posts, not a single roster.

**20. Syracuse University, College of Visual and Performing Arts (VPA) — Syracuse, NY**
- Programs: MFA in Studio Arts, Illustration, Art Photography; Transmedia (film/media, computer art & animation).
- Student data: Event and news pages listing exhibiting artists by name.
- URLs: https://events.syracuse.edu/event/2026-mfa-thesis-exhibition-part-1 ; https://vpa.syracuse.edu/news/
- Emails/portfolio: Not published.
- Approx. count: ~8 per group show; ~26–31 total MFA/year.
- JS rendering: Partial (Localist/Concept3D; names in indexed HTML).
- Notes: Names distributed across multiple event pages per year.

**21. University of Iowa, School of Art, Art History, and Design — Iowa City, IA**
- Programs: BFA/BA + MA/MFA Studio Art (ceramics, 3D design, graphic design, jewelry & metal arts, painting & drawing, photography, printmaking, sculpture & intermedia). Per University of Iowa, "in 1940, the University of Iowa was first in the nation to confer a Master of Fine Arts (MFA) degree" (first recipient Elizabeth Catlett).
- Student data: MFA virtual exhibitions page listing each grad by name + discipline, each linking to a Matterport 3D tour; plus a graduate-students roster.
- URLs: https://art.uiowa.edu/events/mfa-virtual-exhibitions ; https://art.uiowa.edu/people/graduate-students
- Emails/portfolio: No emails; links go to Matterport tours, not personal sites.
- Approx. count: ~25+ named across recent years.
- JS rendering: No (Drupal plain HTML).
- Notes: One of the cleanest, most complete listings found — top scraping target.

**22. California State University, Long Beach (CSULB), School of Art — Long Beach, CA**
- Programs: BFA/MFA — drawing & painting, illustration/animation, ceramics, printmaking, fiber, photography, sculpture, metals. Hosts the student-run GLAMFA (Greater LA MFA) survey.
- Student data: Event listings naming MFA/BFA exhibitors by name + medium; GLAMFA microsite.
- URLs: https://www.csulb.edu/college-of-the-arts/art-design-events-2 ; http://greaterlamfa.com/
- Emails/portfolio: Not published on CSULB pages.
- Approx. count: Handfuls per exhibition; GLAMFA lists 35+ (multi-school).
- JS rendering: Largely plain HTML; GLAMFA is WordPress.
- Notes: GLAMFA is multi-institution, so filter for CSULB affiliation.

**23. University of Illinois Chicago (UIC), School of Art & Art History — Chicago, IL**
- Programs: MFA (Studio Arts, Photography, Moving Image, New Media Arts); Museum & Exhibition Studies. Shows at Gallery 400.
- Student data: Thesis-show pages listing 5–6 artists each with bios.
- URLs: https://cada.uic.edu/schedule/see-saw-seen-2024-uic-mfa-thesis-show/ (and sibling thesis-show pages).
- Emails/portfolio: Not published.
- Approx. count: ~5–6 per show; ~20 MFA/year.
- JS rendering: No (WordPress).
- Notes: Names + bios split across multiple thesis pages.

**24. SUNY New Paltz, Department of Art / Samuel Dorsky Museum — New Paltz, NY**
- Programs: BFA/BA/BS + MFA Studio Art (Ceramics, Metals — internationally renowned, Painting & Drawing, Photography & Related Media, Printmaking, Sculpture). Largest studio grad enrollment in SUNY.
- Student data: BFA/MFA thesis exhibition hub + museum exhibition pages with full rosters by medium.
- URLs: https://www.newpaltz.edu/fpa/art/events/bfa-mfa/ ; https://www.newpaltz.edu/museum/exhibitions/bfamfa-thesis-exhibition-spring-2021/
- Emails/portfolio: Not published.
- Approx. count: ~15–25/year.
- JS rendering: No.
- Notes: Names organized by medium; spread across museum + department pages.

**25. University of Washington, School of Art + Art History + Design — Seattle, WA**
- Programs: MFA (New Genres, Painting + Drawing, 3D4M: ceramics + glass + sculpture); MDes. Thesis show at Henry Art Gallery.
- Student data: Henry Art Gallery thesis pages with full name lists; department exhibition pages.
- URLs: https://henryart.org/exhibitions/2026-university-of-washington-mfa-mdes-thesis-exhibition ; https://art.washington.edu/research/exhibitions/2023-mfa-mdes-thesis-exhibition
- Emails/portfolio: No emails; links to an Issuu catalog.
- Approx. count: ~10–12/year.
- JS rendering: No (names in plain HTML).
- Notes: Clean annual rosters going back years — strong scraping target.

**26. University of Tennessee, Knoxville, School of Art — Knoxville, TN**
- Programs: MFA Studio Art — Sculpture, Time-Based Art, Ceramics, Painting + Drawing, Printmaking (highly ranked among public universities). Shows at Ewing Gallery & Gallery 1010.
- Student data: TRACE institutional repository lists full MFA class by name; Ewing Gallery upcoming-exhibitions page; graduate-students roster.
- URLs: https://trace.tennessee.edu/utk_ewing/20/ ; https://ewing-gallery.utk.edu/upcoming-exhibitions/ ; https://art.utk.edu/people/graduate-students/
- Emails/portfolio: Not published.
- Approx. count: ~10–11 MFA/year.
- JS rendering: No (TRACE and gallery pages plain HTML).
- Notes: Repository archives names across many years.

**27. Bowling Green State University (BGSU), School of Art — Bowling Green, OH**
- Programs: BFA (metals, sculpture, ceramics, painting, glass, digital art, graphic design); MFA Studio Art.
- Student data: ScholarWorks repository lists MFA thesis titles + author names; events pages name MFA grads; past-exhibition gallery pages.
- URLs: https://scholarworks.bgsu.edu/ms_art/ ; https://events.bgsu.edu/event/2026-mfa-exhibition
- Emails/portfolio: Repository contact email only (not student emails).
- Approx. count: MFA ~5–8/year; BFA ~53/year.
- JS rendering: No (bepress/plain HTML).
- Notes: Full BFA roster sometimes only on third-party news sites.

**28. Tulane University, Newcomb Art Department — New Orleans, LA**
- Programs: BFA/BA + MFA Studio Art (painting & drawing, printmaking, ceramics, sculpture & material studies, photography, glass). Shows at Carroll Gallery & Newcomb Art Museum.
- Student data: Department events archive and exhibitions pages naming MFA thesis and BFA show artists.
- URLs: https://liberalarts.tulane.edu/departments/art/events-archive ; https://liberalarts.tulane.edu/departments/art/news-events/exhibitions
- Emails/portfolio: Not published.
- Approx. count: Small MFA program (often solo/paired shows).
- JS rendering: No.
- Notes: Names spread across dated archive pages.

## Recommendations
1. **Start with the four cleanest repositories/rosters:** University of Iowa (MFA virtual exhibitions), University of Washington (Henry Art Gallery), UT Knoxville (TRACE), and BGSU (ScholarWorks). These are plain HTML, need no JS, and cover multiple years of complete, named cohorts — highest yield per engineering hour.
2. **Add plain-HTML university pages next:** SUNY New Paltz, NMSU, UNM, UGA, UIC, Tulane, Bard (via e-flux/bard.edu), Herron, Syracuse. These reliably yield names + medium.
3. **For microsite-driven independent colleges (Ringling, Hunter MFA, PNCA), budget for a JS-capable scraper** (headless browser) since names load client-side.
4. **Plan an enrichment pipeline:** because none of these pages expose emails or portfolio links, build a name → contact resolution step (institutional directories, LinkedIn, Instagram handles surfaced in MIAD/PNCA prose, personal sites via search). This is the critical-path dependency for outreach, not the name harvesting itself.
5. **Prioritize by objective:** large BFA showcases (KCAI ~123, College for Creative Studies 4,800+ works, MIAD 200+, MECA&D ~85, PAFA, Moore) maximize the number of names per scrape; small MFA programs (Bard, UIC, UW, Iowa) maximize prestige and targeting precision.
- **Thresholds that change the plan:** If email/portfolio capture proves essential and a school exposes neither even after enrichment, deprioritize it in favor of schools whose students self-publish portfolios. If JS scraping proves costly, drop the microsite tier (Ringling, Hunter, PNCA) and concentrate on the repository/plain-HTML tier.

## Caveats
- **No emails or portfolio links** were found on any confirmed school's public student pages; contact data must be sourced separately, which carries privacy and outreach-compliance implications (CAN-SPAM, GDPR for any international students, and institutional terms of use).
- **Rankings are approximate.** These schools cluster in the ~31–70 prominence band by reputation and NASAD/AICAD membership, but exact rank varies by source (US News, Niche, Princeton Review). Treat the tiering as directional, not precise.
- **Page availability is seasonal:** grad-show and thesis pages are typically published in spring and may be archived, moved, or replaced year to year; the URLs cited reflect 2024–2026 instances and should be re-verified before a scraping run.
- **JS-rendering notes are best-effort:** some pages marked "partial" may render names server-side in indexed HTML even when the visual gallery needs JS; confirm per-page before building scrapers. Several university calendar platforms (Localist/Concept3D at Syracuse, LSU, BGSU) embed names in server-rendered HTML, so no JS is strictly required to read them.
- **One clarification:** University of Arizona (Tucson) is included; Arizona State University (Tempe) was not separately confirmed with a visible public roster in this pass and merits a dedicated follow-up check.
- **Check robots.txt and terms of use per site** before scraping; institutional repositories (TRACE, ScholarWorks, IUPUI ScholarWorks) are designed for open access but still have citation/reuse norms.
