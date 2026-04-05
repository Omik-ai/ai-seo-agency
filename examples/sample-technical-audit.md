# Technical SEO Audit: acmecorp.com

**Agent**: technical-seo
**Date**: 2026-03-15
**Client/Project**: Acme Corp
**Status**: Final

## Executive Summary

Acme Corp's site has 3 critical indexing issues blocking 40% of product pages, severe Core Web Vitals failures on mobile (LCP 6.2s), and missing schema markup across all product pages. Fixing the critical issues alone could recover an estimated 15-20% of lost organic traffic within 60 days.

## Site Overview

| Metric | Value |
|--------|-------|
| Total Pages Crawled | 4,827 |
| Indexable Pages | 2,903 (60%) |
| Response Code 200 | 4,214 (87%) |
| Response Code 301 | 298 (6%) |
| Response Code 404 | 187 (4%) |
| Response Code 5xx | 128 (3%) |
| Average Page Load (Mobile) | 6.2s |
| Average Page Load (Desktop) | 3.1s |
| HTTPS | Yes |
| CMS | Shopify Plus |

## Critical Issues (P0) — Fix Within 24 Hours

### 1. Robots.txt Blocking Product Category Pages
**Pages Affected**: 1,924 (all `/collections/*` URLs)
**Impact**: 40% of product pages not indexable
**Current**:
```
User-agent: *
Disallow: /collections/
```
**Fix**:
```
User-agent: *
Disallow: /collections/*+*
Disallow: /collections/*?sort_by*
# Allow the main collection pages
Allow: /collections/
```
**Effort**: Small (5 min)

### 2. XML Sitemap Contains Noindexed Pages
**Pages Affected**: 847 pages in sitemap that have `noindex` meta tag
**Impact**: Crawl budget waste, mixed indexing signals
**Fix**: Remove all noindexed URLs from sitemap. Configure Shopify sitemap to auto-exclude pages with `noindex`.
**Effort**: Medium (requires app or custom Liquid template)

### 3. 128 Server Errors (5xx) on Active Product Pages
**Pages Affected**: 128 product pages returning 500 errors intermittently
**Impact**: Lost sales, poor user experience, deindexing risk
**Fix**: Investigate server logs for root cause. Likely Shopify app conflict or rate limiting. Escalate to hosting/dev team.
**Effort**: Medium (requires dev investigation)

## High Priority (P1) — Fix Within 1 Week

### 4. Core Web Vitals Failing on Mobile
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| LCP | 6.2s | <2.5s | FAIL |
| INP | 340ms | <200ms | FAIL |
| CLS | 0.08 | <0.1 | PASS |

**Root Causes**:
- Hero image on PDP template is 2.4MB unoptimized JPEG (LCP killer)
- Third-party review widget loads synchronously (INP killer)
- 14 render-blocking CSS/JS files

**Fixes**:
1. Convert hero images to WebP, serve responsive sizes via `srcset` — **est. LCP improvement: -2.5s**
2. Lazy-load review widget, defer to after DOMContentLoaded — **est. INP improvement: -100ms**
3. Inline critical CSS, defer non-critical — **est. LCP improvement: -0.8s**

### 5. 298 Redirect Chains (3+ hops)
**Pages Affected**: 298 URLs with redirect chains of 3+ hops (max: 7 hops)
**Impact**: Crawl budget waste, link equity dilution, slow load
**Fix**: Update all redirects to point directly to final destination. Consolidate chains.
**Effort**: Medium (bulk update via redirect app)

### 6. Missing Schema Markup on All Product Pages
**Pages Affected**: 1,847 product pages
**Impact**: No rich snippets in search (price, availability, reviews not showing)
**Current**: No Product schema detected
**Fix**: Implement Product + Offer + AggregateRating schema:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{product.title}}",
  "image": "{{product.featured_image | img_url: 'grande'}}",
  "description": "{{product.description | strip_html | truncate: 200}}",
  "sku": "{{variant.sku}}",
  "brand": {
    "@type": "Brand",
    "name": "{{product.vendor}}"
  },
  "offers": {
    "@type": "Offer",
    "url": "{{shop.url}}{{product.url}}",
    "priceCurrency": "{{shop.currency}}",
    "price": "{{variant.price | money_without_currency}}",
    "availability": "{% if variant.available %}https://schema.org/InStock{% else %}https://schema.org/OutOfStock{% endif %}"
  }
}
```
**Effort**: Medium (Liquid template modification)

## Medium Priority (P2) — Fix Within 30 Days

### 7. 187 Broken Internal Links (404s)
**Fix**: Redirect to relevant replacement pages or remove links. Export full 404 list to `data/audits/acme-404s.csv`.

### 8. Duplicate Title Tags on 312 Pages
**Fix**: Generate unique titles using product name + category + brand formula.

### 9. Missing Alt Text on 2,340 Product Images
**Fix**: Auto-generate alt text using: `{{product.title}} - {{variant.title}} | Acme Corp`

### 10. No Breadcrumb Schema
**Fix**: Implement BreadcrumbList JSON-LD on all pages following category hierarchy.

## Low Priority (P3) — Fix Within 90 Days

### 11. HTTP/2 Not Enabled
### 12. Missing HSTS Header
### 13. No Image Sitemap

## Action Items

- [ ] **P0** Fix robots.txt blocking collections (5 min)
- [ ] **P0** Clean XML sitemap of noindexed pages (2 hrs)
- [ ] **P0** Investigate 5xx errors on product pages (requires dev)
- [ ] **P1** Optimize hero images — WebP + srcset (4 hrs)
- [ ] **P1** Defer review widget loading (2 hrs)
- [ ] **P1** Implement Product schema on all PDPs (4 hrs)
- [ ] **P1** Consolidate 298 redirect chains (3 hrs)
- [ ] **P2** Fix 187 broken internal links (2 hrs)
- [ ] **P2** Deduplicate 312 title tags (3 hrs)
- [ ] **P2** Add alt text to 2,340 images (2 hrs with automation)
- [ ] **P2** Add breadcrumb schema (2 hrs)
- [ ] **P3** Enable HTTP/2, HSTS, image sitemap (1 hr each)

## Data Sources

- Full site crawl (Screaming Frog equivalent analysis)
- Google Search Console: Coverage report, Core Web Vitals report
- PageSpeed Insights: Lab data for top 10 page templates
- CrUX: Field data for origin-level CWV

## Handoff Notes

**For `content-strategist`**: 312 pages with duplicate titles need unique meta data. Product description quality is generally thin (avg 45 words). Recommend content improvement sprint.

**For `ecommerce-seo`**: Product schema implementation is ready — JSON-LD template above is production-ready for Shopify Liquid. Faceted navigation on collections needs crawl control review.

**For `analytics`**: Set up monitoring for CWV improvements after fixes deployed. Track index coverage weekly for the next 8 weeks to verify robots.txt fix impact.
