# Phase 1: Organization Discovery

This document guides the extraction of organizations that offer artist opportunities from seed sources. This is the first phase of a two-phase process.

---

## Why We Start With Organizations First

Individual opportunity links are temporary—they expire when deadlines pass, URLs change, or pages get restructured. However, **organizations are stable**. An arts council, foundation, or residency program may update their opportunities yearly, but the organization itself persists.

By building a master organization list first, we create:
- A durable foundation that won't expire
- A reusable asset for ongoing opportunity tracking
- A checkpoint before investing time in deep extraction
- A deduplicated source of truth (many seed lists reference the same orgs)

**Phase 2 will use this org list to extract specific opportunities.**

---

## Goal

Create a comprehensive list of all organizations that offer artist opportunities (grants, residencies, open calls, fellowships, etc.) from our seed sources.

**Do NOT extract full opportunity details in this phase.** Only identify and catalog the organizations.

---

## Output Columns (Organization List CSV)

| Column | Description |
|--------|-------------|
| org_name | Full official name of the organization |
| org_website | Main website URL (homepage or about page) |
| org_type | Foundation / Arts council / Residency program / Festival / Platform / Government body / University / Other |
| source_link | The seed link where you found this org |
| source_type | A/B/C/D/E/F/G/H (see method key below) |
| access_status | open / login_required / paywall / blocked / partial |
| opportunity_types_offered | Preliminary tags: grants, residencies, open calls, fellowships, scholarships, competitions, awards, public arts, exhibitions (comma-separated, based on what you observe) |
| geographic_focus | Country/region focus, or "global" if no restriction apparent |
| mediums_supported | Preliminary observation of art forms supported (use medium list as guide) |
| estimated_opp_count | Rough estimate: 1 / 2-5 / 5-10 / 10+ / unknown |
| priority | High / Medium / Low (see prioritization rules below) |
| notes | Any flags, access issues, or important context |
| date_extracted | Date you extracted this record |

---

## Method Key (Source Types)

Retain this classification for tracking and prioritization:

- **A**: Public directory/DB with list + detail pages
- **B**: Organization programs (program pages + archives)
- **C**: Resource list/static page (parse list + follow outbound links)
- **D**: Magazine/newsletter/announcements (tagged opportunity posts)
- **E**: Platform/login required
- **F**: Social (Facebook, etc.) – manual review or user export
- **G**: PDF guides
- **H**: Paid or freemium access

---

## Seed List (Organized by Source Type)

### Directories and Databases (Type A)
- Artists Futures Fund – Funding Directory
- FundsforWriters – Grants
- Artist Communities Alliance – Open Calls
- TransArtists
- Res Artis – Open Calls
- AIR-J (Japan)
- China Residencies
- away.co.at – Calls and Programs
- Artists in Residence TV
- IDA – Grants Directory
- NYFA – Opportunities
- Fractured Atlas – Artist Opportunity Database (Notion)
- University of Illinois RAPD – Search All Funding Opportunities
- ArtConnect – Opportunities
- ArtJobs
- ArtRabbit – Artist Opportunities
- Contest Watchers
- ForPhotographersOnly
- Photo Contest Insider
- PHmuseum – Grants
- GraphicCompetitions
- ArtsThread – Competitions
- CallforEntries.com
- Artquest – Opportunities
- CuratorSpace – Opportunities
- VANSA – Arts Opportunities
- Run The Check

### Organization Programs (Type B)
- Goethe-Institut – Cultural exchange / residencies
- CEC ArtsLink
- FICA – Foundation for Indian Contemporary Art
- Khoj Studios – Opportunities
- India Foundation for the Arts (IFA) – Programmes

### Resource Lists / Curated Lists (Type C)
- L'AiR Arts – Funding
- Creative Capital – Artist Opportunities
- Art South Asia Project – Grants Library
- Walden School – Composer competitions resources

### Magazines, Newsletters, Announcements (Type D)
- Artwork Archive – Grant and opportunity guides
- India Art Fair – Noticeboard
- Arts Alliance Illinois
- Hyperallergic
- e-flux
- Colossal – Opportunities Newsletter
- On the Move – News

### PDFs (Type G)
- On the Move – Funding Guides (PDFs)

### Platforms / Login / Paid (Type E/H) – Flag for Review
- Unrestricted Funds – Grant Database (login)
- ArtDeadline (paid)
- FilmFreeway – Festivals (platform)
- FilmDaily – Film Funding (paid)
- Artenda (paid/freemium)
- ReverbNation – Opportunities (login)

### Social Sources (Type F) – Manual Review
- Dancing Opportunities (Facebook)
- Call for Artists UK (Facebook)

---

## How to Traverse Seed Sources (Phase 1 Rules)

### For Directory Sources (Type A)

1. Open the seed directory URL.
2. Scan the list for all organizations mentioned.
3. For each organization:
   - Record the org name exactly as listed
   - Find or note their main website URL
   - Note what opportunity types they appear to offer (from directory listing)
   - Do NOT navigate deep into individual opportunity pages yet
4. If a directory entry links to another directory, treat it as a new seed and repeat.
5. Continue until all orgs from that seed are logged.

### For Organization Program Pages (Type B)

1. Open the organization's main website.
2. Identify if they offer opportunities (look for: "support," "funding," "residencies," "open calls," "grants," "fellowships," "programs").
3. Record the org details and note the types of opportunities they seem to offer.
4. If they list partner organizations, note those as separate entries.

### For Resource Lists (Type C)

1. Open the resource list page.
2. Extract every organization mentioned.
3. For each external link, verify it leads to a real org website (not a dead link).
4. Record org details without deep-diving into specific opportunities.

### For Magazines/Newsletters (Type D)

1. Browse recent posts/articles tagged with opportunities.
2. Extract the organizations mentioned in each post.
3. Verify org websites are real and accessible.
4. Note the source article as the source_link.

### For PDFs (Type G)

1. Download and parse the PDF content.
2. Extract all organization names and websites mentioned.
3. Verify each org website is accessible.
4. Note the PDF as the source_link.

### For Login/Paid/Social Sources (Type E/F/H)

1. Attempt to access what you can without login.
2. Record any visible org information.
3. Flag for manual review with clear notes on what access is needed.
4. Do NOT discard—these may contain valuable orgs.

---

## Prioritization Rules

Assign priority based on these factors:

### High Priority
- Appears to offer 5+ opportunities
- Covers multiple mediums
- Global or broad geographic reach
- Open access (no login/paywall)
- Well-established organization (foundation, government body, major institution)

### Medium Priority
- Offers 2-5 opportunities
- Focused on specific medium or region
- Open access
- Smaller but reputable organization

### Low Priority
- Offers only 1 opportunity
- Very narrow focus
- Requires login or has access issues
- Uncertain legitimacy (flag for verification)

---

## Validation Rules (Phase 1)

1. **Verify org existence**: The organization must have a working website or verifiable presence.
2. **Check for legitimacy**: Only trusted organizations. If suspicious, flag for review with notes.
3. **No duplicates**: If an org appears in multiple seeds, keep ONE entry and note all source_links.
4. **Flag access issues**: If login, paywall, or network blocks access, set access_status accordingly and add notes. Do NOT discard.
5. **When uncertain**: If unsure whether an org offers real opportunities, flag it with priority "Low" and note "needs verification."
6. **Always include source**: Every entry must have the source_link where you found it.

---

## What NOT to Do in Phase 1

- Do NOT extract full opportunity details (deadlines, fees, eligibility, etc.)
- Do NOT spend time finding every opportunity page within an org
- Do NOT discard an org just because one link doesn't work
- Do NOT skip orgs behind logins—flag them instead
- Do NOT deep-dive into opportunity specifics—that's Phase 2

---

## Output Format

Save as CSV with filename: `ORG_MASTER_LIST_[DATE].csv`

This file will be the input for Phase 2: Opportunity Extraction.

---

## Handling Edge Cases

### Org website is down or redirects
- Try finding org via web search
- If found, use new URL and note in "notes" column
- If not found, flag as "needs_verification" and keep in list

### Directory lists opportunities without clear org names
- Try to identify the organizing body
- If truly anonymous, use the directory itself as the org name and flag

### Same org, multiple names
- Use the official name from their website
- Note alternative names in the "notes" column

### Org offers opportunities but isn't primarily an arts org
- Include if they have legitimate artist opportunities
- Note "non-arts org" in notes

---

## Next Step

Once Phase 1 is complete and reviewed, proceed to **Phase 2: Opportunity Extraction** using the master org list as input.
