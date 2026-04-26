# SEO Audit Report: example.com
**Agent**: audit-engine@0.1.0
**Date**: 2026-04-26
**Client/Project**: example.com
**Status**: Final
**Run ID**: `aud_79a71ddb8e`

## Executive Summary
Crawled 1 of 1 URLs in 2.1s.
Overall health: **78/100**.
Findings: 0 P0 · 7 P1 · 7 P2 · 9 P3.

## Health Score
| Category | Score |
|---|---:|
| Technical | 75/100 |
| Headings & Semantic HTML | 99/100 |
| Schema / JSON-LD | 89/100 |
| Core Web Vitals | 50/100 |
| E-E-A-T | 82/100 |
| Content Quality | 82/100 |
| Internal Link Graph | 100/100 |
| AI Overviews Readiness | 99/100 |
| **Overall** | **78/100** |

## Critical Issues (P0) — Fix within 24 hours
_None._

## High Priority (P1) — Fix within 1 week
- **[technical] No XML sitemap found**  
  - URL: `https://example.com/sitemap.xml`  
  - Fix: Generate and submit an XML sitemap (one URL per indexable page; <50k URLs per file).  
  - Effort: M · Ref: Indexing
- **[technical] Missing canonical tag on https://example.com/**  
  - URL: `https://example.com/`  
  - Fix: Add <link rel="canonical" href="<absolute-url>"> to the <head>.  
  - Effort: S · Ref: Duplicate content handling
- **[schema] Homepage missing Organization (or LocalBusiness) schema**  
  - URL: `https://example.com/`  
  - Fix: Add Organization JSON-LD with name, url, logo, sameAs (social profiles).  
  - Effort: S · Ref: Entity / Knowledge Graph
- **[eeat] No Organization schema on homepage**  
  - URL: `https://example.com/`  
  - Fix: Add Organization JSON-LD with name, url, logo, sameAs.  
  - Effort: S · Ref: E-E-A-T / Authoritativeness
- **[content] Possible keyword stuffing ('domain' 20.0%) on https://example.com/**  
  - URL: `https://example.com/`  
  - Fix: Reduce keyword density to <3%. Use synonyms and natural language.  
  - Effort: M · Ref: SpamBrain / Keyword Stuffing
- **[serp] Domain not in top 10 for brand query 'example'**  
  - URL: `https://example.com`  
  - Fix: Build brand signals (Organization schema, sameAs, social profiles) and earn branded mentions.  
  - Effort: M · Ref: Entity / Knowledge Graph
- **[geo] No Organization schema on homepage — critical for entity recognition**  
  - URL: `https://example.com`  
  - Fix: Add Organization JSON-LD with name, url, logo, and sameAs array. LLMs use this for entity grounding.  
  - Effort: S · Ref: Knowledge Graph / LLM entity resolution

## Medium Priority (P2) — Fix within 30 days
- **[technical] robots.txt missing Sitemap: directive**  
  - URL: `https://example.com/robots.txt`  
  - Fix: Add a `Sitemap: https://<domain>/sitemap.xml` line so crawlers discover your sitemap.  
  - Effort: S
- **[eeat] No Contact page or mailto: link found**  
  - URL: `https://example.com`  
  - Fix: Add a /contact page with business email + physical address. Basic trust signal.  
  - Effort: S · Ref: E-E-A-T / Trustworthiness
- **[eeat] No About page found**  
  - URL: `https://example.com`  
  - Fix: Add an /about page covering team, history, credentials. Expertise signal.  
  - Effort: M · Ref: E-E-A-T / Expertise
- **[content] Title too short (14 chars) on https://example.com/**  
  - URL: `https://example.com/`  
  - Fix: Expand title to 30–60 chars. Include primary keyword + brand.  
  - Effort: S
- **[content] Missing meta description on https://example.com/**  
  - URL: `https://example.com/`  
  - Fix: Add a 70–160 char meta description. Not a ranking factor, but boosts CTR.  
  - Effort: S
- **[serp] No Knowledge Panel detected for brand query**  
  - URL: `https://example.com`  
  - Fix: Add Organization schema with sameAs links to social profiles. Submit to Wikidata/Wikipedia if notable.  
  - Effort: L · Ref: Knowledge Graph
- **[backlinks] No backlink data provided for off-page audit**  
  - URL: `https://example.com`  
  - Fix: Export backlink data from Ahrefs/Moz/Majestic and pass it in crawl_meta['backlinks'] for automated analysis.  
  - Effort: S · Ref: Off-page signals / Link equity

## Low Priority (P3) — Fix within 90 days
- **[technical] HSTS header missing on most pages**  
  - URL: `https://example.com`  
  - Fix: Add `Strict-Transport-Security: max-age=31536000; includeSubDomains` response header.  
  - Effort: S
- **[headings] Missing semantic tags on https://example.com/: main, header, footer, nav**  
  - URL: `https://example.com/`  
  - Fix: Wrap content in <main>, <header>, <footer>, <nav> tags. Helps Google's content extraction.  
  - Effort: M
- **[schema] Homepage missing WebSite schema**  
  - URL: `https://example.com/`  
  - Fix: Add WebSite JSON-LD with SearchAction to enable sitelinks searchbox.  
  - Effort: S
- **[cwv] Core Web Vitals check skipped (PSI disabled)**  
  - URL: `https://example.com`  
  - Fix: Re-run without --no-psi and with a PAGESPEED_API_KEY for CWV data.  
  - Effort: S
- **[accessibility] No skip-to-content link found on any page**  
  - URL: `https://example.com`  
  - Fix: Add a 'Skip to main content' link as the first focusable element for keyboard navigation.  
  - Effort: S · Ref: Accessibility / WCAG 2.4.1
- **[serp] No featured snippet detected for brand query**  
  - URL: `https://example.com`  
  - Fix: Add FAQPage schema and concise definitional paragraphs to capture featured snippets.  
  - Effort: M · Ref: Featured Snippets
- **[serp] No People Also Ask block detected**  
  - URL: `https://example.com`  
  - Fix: Add question-style H2s and direct answers to trigger PAA expansion.  
  - Effort: M · Ref: People Also Ask
- **[aio] No FAQPage schema found anywhere on the site**  
  - URL: `https://example.com`  
  - Fix: Add an FAQ section with FAQPage schema to pages answering common questions. High AI-Overview pull rate.  
  - Effort: M · Ref: AI Overviews / Rich Results: FAQ
- **[geo] Homepage missing WebSite schema**  
  - URL: `https://example.com`  
  - Fix: Add WebSite JSON-LD with SearchAction. It signals the site's primary entity to search engines and LLMs.  
  - Effort: S · Ref: Entity signals / Structured data

## Action Items
- [ ] [Priority: High] [geo] No Organization schema on homepage — critical for entity recognition — Add Organization JSON-LD with name, url, logo, and sameAs array. LLMs use this for entity grounding.
- [ ] [Priority: High] [content] Possible keyword stuffing ('domain' 20.0%) on https://example.com/ — Reduce keyword density to <3%. Use synonyms and natural language.
- [ ] [Priority: High] [schema] Homepage missing Organization (or LocalBusiness) schema — Add Organization JSON-LD with name, url, logo, sameAs (social profiles).
- [ ] [Priority: High] [serp] Domain not in top 10 for brand query 'example' — Build brand signals (Organization schema, sameAs, social profiles) and earn branded mentions.
- [ ] [Priority: High] [technical] Missing canonical tag on https://example.com/ — Add <link rel="canonical" href="<absolute-url>"> to the <head>.
- [ ] [Priority: High] [eeat] No Organization schema on homepage — Add Organization JSON-LD with name, url, logo, sameAs.
- [ ] [Priority: High] [technical] No XML sitemap found — Generate and submit an XML sitemap (one URL per indexable page; <50k URLs per file).
- [ ] [Priority: Medium] [content] Title too short (14 chars) on https://example.com/ — Expand title to 30–60 chars. Include primary keyword + brand.
- [ ] [Priority: Medium] [content] Missing meta description on https://example.com/ — Add a 70–160 char meta description. Not a ranking factor, but boosts CTR.
- [ ] [Priority: Medium] [backlinks] No backlink data provided for off-page audit — Export backlink data from Ahrefs/Moz/Majestic and pass it in crawl_meta['backlinks'] for automated analysis.
- [ ] [Priority: Medium] [serp] No Knowledge Panel detected for brand query — Add Organization schema with sameAs links to social profiles. Submit to Wikidata/Wikipedia if notable.
- [ ] [Priority: Medium] [technical] robots.txt missing Sitemap: directive — Add a `Sitemap: https://<domain>/sitemap.xml` line so crawlers discover your sitemap.
- [ ] [Priority: Medium] [eeat] No Contact page or mailto: link found — Add a /contact page with business email + physical address. Basic trust signal.
- [ ] [Priority: Medium] [eeat] No About page found — Add an /about page covering team, history, credentials. Expertise signal.
- [ ] [Priority: Low] [headings] Missing semantic tags on https://example.com/: main, header, footer, nav — Wrap content in <main>, <header>, <footer>, <nav> tags. Helps Google's content extraction.
## Data Sources
- HTTP fetch of 1 URLs (user-agent: SEOAuditEngine/0.1.0)
- robots.txt + XML sitemap parse
- JSON-LD extraction via bs4 + regex
- PageSpeed Insights API 
- Engine version: audit_engine@0.1.0

## Handoff Notes
- Structured JSON at the same path with `.json` extension — machine-parseable.
- `top_findings_by_priority` in JSON gives a flat queue for ticket creation.
- Next agent: `on-page-seo` for P1 title/heading fixes, `technical-seo` for P0 indexing.
