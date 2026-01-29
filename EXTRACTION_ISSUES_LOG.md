# Extraction Issues & Blockers Log

Track issues, missed items, and blockers encountered during Phase 2 extraction.

---

## Format

```
### [Date] - [Org Name]
**Issue Type:** JS-heavy / PDF needed / Login required / Broken link / Incomplete data / Other
**Description:** What happened
**Action Needed:** What to do about it
**Status:** Open / Resolved / Deferred
```

---

## Issues Log

### 2026-01-29 - QEST
**Issue Type:** JS-heavy site
**Description:** Website heavily JS-rendered, WebFetch returned mostly navigation/code. crawl4ai worked better but still limited content on some pages.
**Action Needed:** Used web search fallback successfully. Consider using crawl4ai as primary for this site.
**Status:** Resolved

### 2026-01-29 - QEST
**Issue Type:** PDF available
**Description:** QEST has detailed PDF guidance document at https://www.qest.org.uk/wp-content/uploads/2023/06/QEST-Scholarship-Guidance_updated-0623.pdf
**Action Needed:** Could extract more detailed eligibility/requirements from PDF if needed
**Status:** Deferred (basic info captured via web search)

### 2026-01-29 - Arts Council England
**Issue Type:** JS-heavy site + Complex structure
**Description:** Site very navigation-heavy, main content not rendering well. Multiple funding strands with extensive documentation.
**Action Needed:** Used web search fallback. Extensive PDF guidance library available.
**Status:** Resolved (5 opportunities extracted)

### 2026-01-29 - Arts Council England
**Issue Type:** PDFs available
**Description:** 30+ PDF guidance documents in their library including:
- Guidance for applicants (multiple funding levels)
- Information sheets for specific project types
- Application templates
**Action Needed:** Could download key PDFs for more detailed extraction
**Status:** Deferred (flagged for user)

---

## Patterns Observed

| Pattern | Frequency | Solution |
|---------|-----------|----------|
| JS-heavy sites | Common | Use crawl4ai with render_js, then web search fallback |
| PDF documentation | Common | Flag to user, download if approved |
| Navigation-heavy pages | Common | Search for specific content, use web search |
| Multiple funding strands | Some orgs | Create separate CSV rows per program |

---

## Orgs Requiring Follow-up

| Org | Reason | Priority |
|-----|--------|----------|
| QEST | PDF has more details | Low |
| Arts Council England | Many PDFs available | Low |

---

## Missed Opportunities (to revisit)

_None yet_

---

## Technical Blockers

_None currently_
