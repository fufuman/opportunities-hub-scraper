# Extraction Progress Tracker

Quick reference for resuming work in any session.

---

## Current Source: artists_futures_fund
**Phase 1 file:** `phase 1 extraction/artists_futures_fund.csv`
**Phase 2 output:** `phase 2 extraction/artists_futures_fund_TEST.csv`
**Total orgs in source:** 73

---

## Extraction Status

| # | Org Name | Status | Opps Found | Notes |
|---|----------|--------|------------|-------|
| 1 | Arts Council England | ✅ Done | 5 | JS-heavy; used web search |
| 2 | Creative Scotland | ✅ Done | 6 | Web search; multiple deadlines Feb 2026 |
| 3 | Arts Council of Northern Ireland | ✅ Done | 7 | SIAP + Travel + 5 job listings |
| 4 | Arts Council of Wales | ✅ Done | 17 | Funding + 12 jobs/opps from ACW jobs board |
| 5 | AHRC | ⏸️ Skipped | 0 | Academic/institutional only; not for individual artists |
| 6 | British Council | ✅ Done | 3 | International collab focus; all require partner |
| 7 | ACS Studio Prize | ⏳ Next | - | - |
| 8 | Anna Plowden Trust | ✅ Done | 3 | Simple extraction |
| 9 | Artcry | Pending | - | - |
| 10 | Artsadmin | Pending | - | - |
| ... | ... | ... | ... | ... |

### Test Orgs (completed earlier)
| Org | Opps | Notes |
|-----|------|-------|
| Anna Plowden Trust | 3 | Test org - simple |
| QEST | 3 | Test org - JS-heavy |
| Delfina Foundation | 4 | Test org - residencies |

---

## Summary Stats

| Metric | Count |
|--------|-------|
| Orgs processed | 9 |
| Orgs remaining | 64 |
| Total opportunities extracted | 48 |
| Issues logged | 4 |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Rules, workflow, efficiency guidelines |
| `EXTRACTION_ISSUES_LOG.md` | Blockers, PDFs flagged, patterns |
| `EXTRACTION_PROGRESS.md` | This file - progress tracking |
| `phase 2 extraction/*.csv` | Extracted opportunity data |

---

## Workflow Reminder

1. Read org from Phase 1 CSV
2. Fetch with crawl4ai (handles JS)
3. If incomplete → web search fallback
4. Flag any PDFs found
5. Extract to Phase 2 schema
6. Add to CSV
7. Update this progress file
8. Log any issues

---

## Resume Instructions

To continue extraction:
1. Check "Extraction Status" table above for next org
2. Read `CLAUDE.md` for rules
3. Check `EXTRACTION_ISSUES_LOG.md` for patterns
4. Continue from where status shows "⏳ Next"
