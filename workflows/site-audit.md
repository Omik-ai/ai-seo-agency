# Workflow: Comprehensive Site Audit

**Type**: Parallel Swarm
**Duration**: 3-5 days
**Agents**: technical-seo, analytics, on-page-seo, content-strategist, ecommerce-seo (if applicable)

## Overview

A full site audit deploys multiple specialist agents simultaneously to analyze every aspect of a site's SEO health. Results are merged into a unified audit report with prioritized recommendations.

## Pipeline

```
Orchestrator receives "audit [URL]"
│
├── Deploy Parallel Swarm:
│   ├── technical-seo: Crawl, indexing, speed, mobile, security
│   ├── analytics: Traffic trends, performance data, conversions
│   ├── on-page-seo: Sample page optimization analysis (top 20 pages)
│   ├── content-strategist: Content quality and coverage assessment
│   └── ecommerce-seo: Product/category audit (if e-commerce)
│
├── Merge Point: Collect all agent reports
│
├── seo-strategist: Synthesize into unified audit with priorities
│
└── client-manager: Format final deliverable
```

## Agent Instructions

### technical-seo
Perform a full technical crawl analysis:
- Crawl the site systematically (or analyze provided crawl data)
- Check indexing status, robots.txt, sitemaps
- Measure Core Web Vitals on key pages
- Identify redirect chains, broken links, 404s
- Review site architecture and URL structure
- Check mobile rendering
- Audit structured data
- Review security (HTTPS, headers)
- **Output**: Technical Audit section with issue severity ratings

### analytics
Analyze historical performance:
- Pull 12 months of organic traffic data
- Identify traffic trends (growing, declining, stable segments)
- Top performing pages and declining pages
- Keyword ranking distribution
- Click-through rates by position bracket
- Conversion data from organic traffic
- Core Web Vitals from field data (CrUX)
- **Output**: Performance Analysis section with trend charts

### on-page-seo
Sample-audit top pages:
- Select top 20 pages by traffic
- Audit title tags, meta descriptions, headings
- Check content structure and keyword targeting
- Review internal linking patterns
- Assess E-E-A-T signals
- Identify featured snippet opportunities
- **Output**: On-Page Audit section with page-by-page scores

### content-strategist
Assess content ecosystem:
- Inventory all content (blog, landing pages, resources)
- Score content quality (using Content Scoring Framework)
- Identify thin, duplicate, and cannibalized content
- Map content to topic clusters
- Find content gaps vs. target topics
- **Output**: Content Assessment section with scores and gaps

### ecommerce-seo (conditional)
If the site is e-commerce:
- Audit product page template SEO
- Review category structure and faceted navigation
- Check product schema implementation
- Analyze product feed health
- **Output**: E-commerce Audit section

## Merge & Synthesis

The `seo-strategist` receives all sections and produces:

```markdown
# Comprehensive SEO Audit: [Domain]
**Date**: [date]
**Audited by**: SEO Agency AI Team

## Executive Summary
[Overall health score, top 3 wins, top 3 critical issues]

## Health Score: [X/100]
- Technical: [X/100]
- Content: [X/100]
- On-Page: [X/100]
- Performance: [X/100]
- Links: [X/100]

## Critical Issues (Fix Immediately)
[P0 items from all agents]

## High Priority (Fix Within 30 Days)
[P1 items from all agents]

## Medium Priority (Fix Within 90 Days)
[P2 items from all agents]

## Opportunities
[Quick wins and growth opportunities]

## Detailed Findings
### Technical SEO [from technical-seo]
### Performance Analysis [from analytics]
### On-Page Optimization [from on-page-seo]
### Content Assessment [from content-strategist]
### E-commerce [from ecommerce-seo, if applicable]

## Recommended Action Plan
[Prioritized 90-day plan]
```
