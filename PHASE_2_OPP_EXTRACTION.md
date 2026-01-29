# Phase 2: Opportunity Extraction

This document guides the extraction of specific opportunities from each organization identified in Phase 1. This is the second phase of a two-phase process.


---

## Critical Understanding: Links Expire, Details Don't

**This is the most important concept for Phase 2.**

Opportunity links are inherently temporary:

* Deadlines pass and pages get removed
* URLs change when sites restructure
* Organizations update their opportunity pages annually
* Some opportunities are one-time only

**However, the DETAILS you extract remain valuable:**

* The organization will likely offer similar opportunities again
* Fee structures, eligibility patterns, and themes tend to persist
* Even if a link dies, knowing "Org X offers $10K grants for emerging photographers annually" is useful
* Your extracted data becomes a reference even when URLs break

### Therefore:

* **Extract comprehensive details** — this is the permanent value
* **Capture the URL** — but understand it may expire
* **Always include the org website** — this is the stable fallback
* **Record the extraction date** — so users know the data's freshness

The org info from Phase 1 is your anchor. Individual opportunity links are supplementary.


---

## Goal

For each organization in the Phase 1 master list, extract ALL opportunities with complete details into a final CSV.


---

## Input

The `ORG_MASTER_LIST_[DATE].csv` from Phase 1, containing:

* Organization names
* Organization websites
* Preliminary opportunity types
* Priority rankings
* Access status flags

**Process orgs in priority order: High → Medium → Low**


---

## Output Columns (Final Opportunity CSV)

| Column | Description | Required |
|----|----|----|
| org_name | Name of the organization offering this opportunity | Yes |
| org_website | Main website of the organization (stable URL) | Yes |
| opportunity_name | Specific name of the opportunity/program | Yes |
| opportunity_type | See opportunity types list below | Yes |
| location | Geographic location or "Global" if open to all | Yes |
| application_open_date | When applications open (or "Rolling" or "Not specified") | Yes |
| deadline | Submission deadline (or "Rolling" or "Not specified") | Yes |
| application_url | Direct link to application page | Yes (if available) |
| info_page_url | Link to opportunity info page (backup if no app URL) | Yes |
| what_it_supports | Short theme keywords describing focus | Yes |
| who_qualifies | Eligibility requirements as bullet points | Yes |
| entry_fee | Fee amount or "Free" | Yes |
| award_amount | Grant/prize amount if applicable | If applicable |
| mediums_supported | See medium list below | Yes |
| source_link | Original seed source where org was found | Yes |
| extraction_date | Date this record was extracted | Yes |
| link_status | verified / unverified / requires_login | Yes |
| notes | Any flags, uncertainties, or additional context | Optional |


---

## Opportunity Types List

Use the closest match. If none fit, use the source's exact wording.

* Grants
* Residencies
* Open calls
* Fellowships
* Scholarships
* Competitions
* Awards
* Public arts and proposals
* Exhibitions


---

## Medium List

Map to the closest match. If the opportunity uses different wording, keep explicit wording in parentheses.

* Filmmaking (fiction + non-fiction + experimental)
* Painting / Drawing / Illustration
* Sculpture / Three-dimensional art
* Sound / Music (experimental + industry)
* Performance
* 2D / 3D Animation (fiction + non-fiction + experimental)
* Fiber / Materials / Textiles
* Photography
* Graphic Design / Industrial Design
* UI / UX
* Fashion
* Multidisciplinary (if explicitly open to multiple/all forms)
* Other: \[specify\]


---

## How to Traverse Each Organization (Phase 2 Rules)

### Step-by-Step Process


1. **Start from the org website** (from Phase 1 data)
2. **Find opportunity pages** — Look for navigation links or pages containing:
   * "Opportunities"
   * "Open calls"
   * "Grants"
   * "Funding"
   * "Support"
   * "Residencies"
   * "Fellowships"
   * "Programs"
   * "Apply"
   * "Resources"
   * "For artists"
3. **For each opportunity page found:**
   * If it's a LIST of opportunities → treat as mini-directory, process each one
   * If it's a SINGLE opportunity → extract full details
   * If it links to EXTERNAL opportunities → follow and extract (note external source)
4. **Extract ALL opportunities** — Many orgs have multiple programs:
   * Different grant programs
   * Annual and one-time opportunities
   * Different residency locations
   * Opportunities for different career stages
   * Each gets its own row in the CSV
5. **Go deep** — Don't stop at the main opportunity page:
   * Check "Past opportunities" or "Archive" sections
   * Look for opportunities in "News" or "Announcements"
   * Check footer links for additional programs
   * Review "FAQ" pages for opportunity details
6. **Record everything** — Even if an opportunity seems closed or past:
   * It may recur annually
   * The details inform what the org typically offers
   * Note "recurring: annual" or "status: closed" in notes

### When You've Found an Opportunity Page

Before extracting, confirm you're on the RIGHT page:

* Does it have specific eligibility requirements?
* Does it mention deadlines (even if passed)?
* Does it describe what's offered (funding, space, exhibition)?
* Does it explain how to apply?

If the page is vague or just promotional, keep navigating until you find the detailed program page.


---

## Extraction Rules

### Location

* Extract country/city if specified
* If opportunity says "international" or has no location requirement → "Global"
* If residency, use the residency location
* If multiple locations, list all separated by commas

### Dates

* Use ISO format where possible: YYYY-MM-DD
* If only month/year given: "March 2025" is acceptable
* If rolling applications: "Rolling"
* If not specified anywhere: "Not specified"
* If deadline has passed: Still record it with note "Past deadline - check for next cycle"

### URLs

* **application_url**: Direct link to application form or portal
* **info_page_url**: Link to opportunity description page
* If no separate application URL exists, use info page for both
* If URL requires login to view: note "requires_login" in link_status
* **Always verify URLs work** before recording

### What It Supports

* Short keywords only: "emerging artists," "documentary film," "social practice," "environmental themes"
* Don't write paragraphs — be concise
* If very broad/open: "open theme" or "unrestricted"

### Who Qualifies

* Use bullet points for clarity
* Include: career stage, nationality/residency requirements, age limits, professional requirements
* Example:

  ```
  • Emerging artists (less than 5 years professional practice)
  • Must be US citizen or permanent resident
  • Age 21-35
  • Must not be enrolled in degree program
  ```
* If truly open to all: "Open to all artists"

### Entry Fee

* Exact amount with currency: "$25 USD" or "€30"
* If free: "Free"
* If fee waiver available: "€20 (fee waiver available)"
* If unclear: "Not specified — verify before applying"

### Award Amount

* Exact amount if stated: "$10,000" or "€5,000 stipend + housing"
* For residencies without cash: "Accommodation + studio provided"
* If variable: "Up to $15,000" or "$5,000-$20,000"
* If not stated: "Not specified"

### Mediums Supported

* Use medium list as primary reference
* If org uses different terminology, include both: "Filmmaking (org says: 'moving image')"
* If open to all: "All mediums" or "Multidisciplinary"


---

## Validation Rules (Phase 2)

### Before Recording an Opportunity


1. **Is it real?** — The opportunity must have concrete details, not just vague mentions
2. **Is it art-focused?** — Must be relevant to artists/creatives (if unsure, include but flag)
3. **Is it from a trusted org?** — Should have been vetted in Phase 1
4. **Do you have enough detail?** — At minimum: name, org, type, and either eligibility OR application info

### Link Validation


1. **Verify each URL loads** — Click it, confirm it works
2. **Check for redirects** — If URL redirects, use final destination URL
3. **Note access restrictions** — Login required? Paywall? Geographic block?
4. **If link is broken:**
   * Try to find updated URL via site search
   * Try web archive (archive.org) for reference
   * Keep the entry but note "link broken — verify current URL"
   * **Do NOT discard** — the org and opportunity details are still valuable

### Quality Checks


1. **No duplicates** — Same opportunity should appear only once
2. **Complete records** — All "Required" columns must have values
3. **Consistent formatting** — Dates, currencies, and lists should follow the same format
4. **Source attribution** — Every entry must trace back to its source


---

## Handling Common Situations

### Opportunity Page Has Multiple Programs

Create separate rows for each program. Example:

* "Foundation X — Emerging Artist Grant" (Row 1)
* "Foundation X — Mid-Career Fellowship" (Row 2)
* "Foundation X — Project Grant" (Row 3)

### Opportunity Recurs Annually

* Record current cycle details
* Note in "notes": "Annual program — new cycle typically opens \[month\]"
* If current cycle is closed, still record with past deadline and note

### Details Are Split Across Multiple Pages

* Navigate all relevant pages
* Compile complete information into single row
* List main info page as info_page_url

### Opportunity Requires Login to See Full Details

* Extract whatever is publicly visible
* Note "requires_login" in link_status
* Add to notes: "Full details require account creation"
* Flag for manual review if critical details are hidden

### Org Website Is Down or Changed

* Refer back to Phase 1 notes
* Try web search for new URL
* Try archive.org for cached version
* If org seems defunct: keep entry, note "org website unavailable — may be defunct"

### Opportunity Is for Partner Org

If Org A's page mentions an opportunity actually run by Org B:

* Create entry under Org B (the actual organizer)
* Note Org A as a source in the source_link column
* If Org B isn't in your Phase 1 list, add them

### Information Is Incomplete on Website

* Extract what's available
* Note which fields are missing
* Add: "Incomplete info on website — contact org for details"
* Do NOT make up information

### Opportunity Is Highly Restrictive

Still include it, but note restrictions clearly:

* "Norwegian citizens only"
* "Must be nominated — not open application"
* "By invitation only"


---

## What NOT to Do in Phase 2

* Do NOT skip opportunities because deadlines have passed — they may recur
* Do NOT discard entries with broken links — the details are still valuable
* Do NOT make up details — leave fields as "Not specified" if unknown
* Do NOT merge different opportunities into one row — each gets its own entry
* Do NOT skip orgs flagged as "login required" — extract what you can
* Do NOT assume — when uncertain, note uncertainty rather than guessing


---

## Link Expiration Strategy

Because links WILL expire over time:


1. **Prioritize org_website** — This is your stable reference. If application_url dies, user can navigate from org homepage.
2. **Record descriptive details thoroughly** — "Annual $15K grant for US photographers, typically March deadline" remains useful even when the 2024 link dies.
3. **Note patterns** — "Opens January, deadline March, annual" helps users anticipate future cycles.
4. **Date everything** — extraction_date tells users how fresh the data is.
5. **Include multiple URLs when available** — info_page_url as backup to application_url.


---

## Output Format

Save as CSV with filename: `OPPORTUNITIES_FINAL_[DATE].csv`

Consider also maintaining:

* `OPPORTUNITIES_BY_TYPE_[DATE].csv` — filtered views by opportunity type
* `OPPORTUNITIES_FLAGGED_[DATE].csv` — entries needing manual review


---

## Quality Assurance Checklist

Before finalizing the dataset:

- [ ] All required columns have values (or explicit "Not specified")
- [ ] No duplicate opportunities
- [ ] URLs have been verified (or flagged if broken)
- [ ] Mediums and opportunity types use standardized terms
- [ ] Fees and amounts include currency
- [ ] Eligibility is clear and specific
- [ ] Every entry has source_link and extraction_date
- [ ] Flagged items are documented in notes
- [ ] High-priority orgs have been fully processed


---

## After Extraction

The final CSV should be:


1. Reviewed for accuracy
2. Deduplicated if any slipped through
3. Sorted by priority or type for usability
4. Documented with a README noting:
   * Total opportunities extracted
   * Date range of extraction
   * Known gaps or access limitations
   * Recommendations for next update cycle


---

## Remember

**The value is in the details, not just the links.**

A comprehensive record of what opportunities exist, who offers them, what they provide, and who qualifies — that's the durable asset you're building. URLs are helpful but temporary. Your extracted data is the permanent reference.