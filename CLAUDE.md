# Opportunities Hub Scraper - Rules & Guidelines

## Context Management

**All progress is saved in files - context compaction won't lose work.**

Key files to read at session start:
1. `EXTRACTION_PROGRESS.md` - where we left off
2. `EXTRACTION_ISSUES_LOG.md` - patterns & blockers
3. `CLAUDE.md` - this file (rules)

## Opportunity Types to Capture

- Grants
- Residencies
- Open calls
- Fellowships
- Scholarships
- Competitions
- Awards
- Public arts and proposals
- Exhibitions
- **Jobs** (check /jobs pages on org sites)

---

## Approval Workflow

**CRITICAL: Nothing gets implemented without user approval first.**

- Always propose changes/scripts before implementing
- Present options, let user choose
- Ask before creating new files (except temp/cache)
- Confirm before running long operations

---

## Token/Credit Efficiency

### Minimize API Calls
- Use crawl4ai (local) before WebFetch/WebSearch
- Cache fetched pages locally to avoid re-fetching
- Batch similar operations when possible

### Content Optimization
- Strip navigation, headers, footers before LLM processing
- Extract only relevant sections from pages
- Summarize long content before detailed extraction

### Model Selection
- Use **haiku** for: simple text extraction, formatting, straightforward tasks
- Use **sonnet/opus** for: complex analysis, multi-step reasoning, ambiguous content

---

## Phase 2 Extraction Workflow

```
1. Read org from Phase 1 CSV
2. Fetch org website with crawl4ai
3. Identify opportunity pages (grants, residencies, apply, etc.)
4. For each opportunity page:
   a. Fetch with crawl4ai
   b. Check for PDF links → flag for user
   c. Extract structured data per Phase 2 schema
5. If content incomplete → web search fallback
6. Output to Phase 2 CSV
```

### Required Fields (Phase 2)
- org_name, org_website, opportunity_name, opportunity_type
- location, deadline, application_url, info_page_url
- what_it_supports, who_qualifies, entry_fee, award_amount
- mediums_supported, extraction_date, link_status, notes

---

## PDF Handling

When PDF links are encountered:
1. **Flag to user** - note the PDF URL and what info it may contain
2. **Download if approved** - save to local cache
3. **Extract text** - use pdfplumber or PyMuPDF
4. **Process content** - extract structured data

Do NOT auto-download PDFs without user awareness.

---

## Caching Strategy

### Local Cache Folder
`./cache/` for temporary fetched content

### What to Cache
- Fetched HTML/markdown (filename: sanitized URL)
- Downloaded PDFs
- Intermediate extraction results

### Cache Expiry
- Default: 7 days for opportunity pages (content changes)
- Longer for org homepages (more stable)

---

## File Organization

```
Oppurtunities Hub scraper/
├── phase 1 extraction/     # Org CSVs by source
├── phase 2 extraction/     # Opportunity CSVs by source
├── cache/                  # Fetched pages, PDFs (temp)
├── PHASE_1_ORG_DISCOVERY.md
├── PHASE_2_OPP_EXTRACTION.md
├── CLAUDE.md               # This file
└── *.xlsx                  # Master data files
```

---

## Flags & Alerts

Alert user when encountering:
- PDF links with detailed opportunity info
- Login-required pages
- JS-heavy sites that need special handling
- Sites with 10+ opportunities (complex extraction)
- Broken links or access issues

---

## Quality Checks

Before finalizing extraction:
- [ ] All required fields populated (or marked "Not specified")
- [ ] URLs verified working
- [ ] No duplicate opportunities
- [ ] Dates in consistent format
- [ ] Currency included with amounts
