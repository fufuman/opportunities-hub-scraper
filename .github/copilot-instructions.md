# Copilot Instructions: Opportunities Hub Scraper

## Project Overview

A **two-phase web scraper** that systematically catalogs artist funding opportunities (grants, residencies, open calls, etc.) from seed sources worldwide. Phase 1 discovers organizations; Phase 2 extracts detailed opportunities from each organization.

### Why Two Phases?
- **Phase 1**: Build durable organizational index (stable long-term assets)
- **Phase 2**: Extract ephemeral opportunity details while links are fresh
- Org data survives URL changes; detailed links may expire, but the extracted metadata remains valuable

---

## Architecture & Key Concepts

### Input & Output Flow
1. **Seed sources**: Directories, platforms, newsletters → organized in [PHASE_1_ORG_DISCOVERY.md](PHASE_1_ORG_DISCOVERY.md)
2. **Phase 1 script**: `phase1_seed_link_test_crawl4ai.py` → extracts outbound links from seed pages → `ORG_MASTER_LIST_*.csv`
3. **Phase 2**: Extract detailed opportunity fields per [PHASE_2_OPP_EXTRACTION.md](PHASE_2_OPP_EXTRACTION.md) → `ARTJOBS_JOBS_PHASE2.csv`

### Core Technologies
- **Web crawling**: `crawl4ai` (async, JS rendering support)
- **HTML parsing**: Built-in `HTMLParser` for link extraction
- **Data storage**: CSV with specific column schemas (see markdown docs)
- **Dependencies**: Found in `.venv_crawl4ai/`

---

## Critical Code Patterns

### 1. Link Extraction (`LinkParser` class)
```python
class LinkParser(HTMLParser):
    # Key behavior:
    # - Finds external links (outbound from seed domain)
    # - Requires content within <div class="entry-content"> by default
    # - Falls back to full page if no entry-content found
    # - De-duplicates by URL
```
**When to use**: Discovering org URLs from directory/list pages. Set `require_entry_content=False` if page structure differs.

### 2. Async Crawling
```python
async def fetch_html_crawl4ai(url, render_js):
    # render_js=True for JS-heavy sites (Next.js, Nuxt, React apps)
    # JS_HEAVY_MARKERS list identifies frameworks
```
**Convention**: Try plain fetch first; enable JS rendering for detected frameworks.

### 3. Data Deduplication
- Maintain `seen` set per seed; URLs normalized with `urlparse` + `urljoin`
- Output CSVs should deduplicate on `org_website` (Phase 1) or `opportunity_name + org_name` (Phase 2)

---

## CSV Column Requirements

### Phase 1 Output (`ORG_MASTER_LIST_*.csv`)
Must include: `org_name`, `org_website`, `org_type`, `source_link`, `source_type` (A-H), `access_status`, `opportunity_types_offered`, `geographic_focus`, `mediums_supported`, `estimated_opp_count`, `priority`, `notes`, `date_extracted`

**Priority logic**: High = type A/B with 10+ opps; Medium = type B/C; Low = type E/F/G/H or limited content

### Phase 2 Output (`OPPORTUNITIES_*.csv` / `ARTJOBS_*.csv`)
Must include: `org_name`, `opportunity_name`, `opportunity_type`, `deadline`, `application_url`, `who_qualifies`, `mediums_supported`, `extraction_date`, `link_status`

**Critical**: Always capture `org_website` as stable fallback when individual app URLs expire.

---

## Workflows & Debugging

### Adding New Seed Source
1. Update seed list in [PHASE_1_ORG_DISCOVERY.md](PHASE_1_ORG_DISCOVERY.md) with source type (A-H)
2. Test with: `python phase1_seed_link_test_crawl4ai.py --seed-url <URL> --render-js [if JS-heavy]`
3. Review output; adjust `require_entry_content` or `JS_HEAVY_MARKERS` if needed

### Handling Access Issues
- `access_status = login_required`: Flag in Phase 1; may skip in Phase 2
- `access_status = paywall`: Note in Phase 1; document in Phase 2 notes
- `access_status = blocked`: Log error; skip or retry with different user-agent

### Common Parsing Failures
- **No links found**: `LinkParser` likely needs `require_entry_content=False`
- **Wrong domain included**: Check seed URL domain; validate seed list hasn't changed
- **Async timeout**: Increase crawl4ai timeout for slow/JS-heavy sites

---

## Key Directories & Files
- `.venv_crawl4ai/` – Python dependencies (crawl4ai, asyncio stack)
- `phase1_seed_link_test_crawl4ai.py` – Main Phase 1 script
- `ORG_MASTER_LIST_*.csv` – Phase 1 output (deduplicated orgs)
- `ARTJOBS_*.csv` – Phase 2 output (opportunities with full details)
- `PHASE_1_ORG_DISCOVERY.md`, `PHASE_2_OPP_EXTRACTION.md` – Detailed schemas & methodology

---

## Conventions & Gotchas

1. **Source types (A-H)**: Use consistently; drives prioritization logic
2. **Geographic focus**: Use ISO country codes or "Global" if unrestricted
3. **Mediums**: Pre-defined list in schema; don't invent; use "Other" if needed
4. **Deadlines**: Record as written (`2026-03-15` or `Rolling` or `Not specified`)
5. **De-duplication**: Phase 1 de-dupes on `org_website`; Phase 2 on `org_name + opportunity_name`
