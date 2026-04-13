# Technical SEO Audit: iamamitkumar.dev

**Agent**: technical-seo
**Date**: 2026-04-05

## Executive Summary

The site iamamitkumar.dev is a well-optimized personal portfolio built on Next.js 16 and Tailwind v4. It demonstrates strong fundamentals in crawlability (proper robots.txt with AI bot access, valid sitemap), security (HTTPS), and mobile responsiveness. However, critical issues remain: no canonical URLs across any pages (posing duplicate content risk) and incomplete schema implementation (Person schema exists on homepage but Article schema missing from blog posts). These issues should be addressed to maximize search visibility and prevent indexing problems.

## Findings

### 1. Crawlability

| Check | Status | Details |
|-------|--------|---------|
| robots.txt | PASS | Comprehensive configuration allowing all major crawlers including GPTBot, ChatGPT-User, Bingbot, Googlebot, ClaudeBot, PerplexityBot |
| Sitemap | PASS | Valid XML sitemap with 9 URLs including homepage, about, projects, now, blog, and 4 blog posts |
| Internal Links | PASS | Good navigation structure with proper internal linking |

**Severity**: None - crawlability is excellent.

---

### 2. Indexing

| Check | Status | Details |
|-------|--------|---------|
| Canonical URLs | FAIL | No `<link rel="canonical">` tags found on any page |
| Noindex Tags | PASS | No unwanted noindex directives detected |
| URL Parameters | PASS | Clean URL structure, no tracking parameters |

**Issue**: All pages lack canonical URL implementation, creating potential duplicate content issues. Each page (homepage, about, projects, blog posts) should self-reference with a canonical tag.

**Severity**: HIGH - Without canonical URLs, search engines may struggle to determine the preferred version of pages, especially if URL parameters or trailing slashes cause variations.

---

### 3. Core Web Vitals

| Metric | Estimated Status | Notes |
|--------|------------------|-------|
| LCP | GOOD | Next.js 16 with optimized loading, preloaded fonts |
| FID/INP | GOOD | Server-side rendering, minimal JavaScript blocking |
| CLS | GOOD | Tailwind v4 with stable layout structure |

**Note**: Actual Core Web Vitals should be verified via Google Search Console and PageSpeed Insights. Based on tech stack analysis (Next.js 16, Tailwind v4, font preloading, image optimization), the site is likely to pass Core Web Vitals thresholds.

**Severity**: LOW - Recommend actual testing via Lighthouse/PageSpeed Insights.

---

### 4. Schema Markup

| Check | Status | Details |
|-------|--------|---------|
| Person Schema | PASS | Implemented on homepage with full profile data |
| Article Schema | FAIL | Not implemented on blog posts |
| WebSite Schema | FAIL | Not implemented for search action |
| Breadcrumb Schema | FAIL | Not implemented |

**Current Implementation (Homepage)**:
```json
{
  "@context": "https://schema.org",
  "@type": "Person",
  "@id": "https://iamamitkumar.dev/#person",
  "name": "Amit Kumar",
  "url": "https://iamamitkumar.dev",
  "jobTitle": "AI Systems Architect",
  "email": "hi@iamamitkumar.dev",
  "image": "https://iamamitkumar.dev/images/og-image.png"
}
```

**Issue**: Blog posts lack Article schema, reducing eligibility for rich snippets in search results.

**Severity**: HIGH - Schema markup improves SERP visibility and click-through rates.

---

### 5. Security

| Check | Status | Details |
|-------|--------|---------|
| HTTPS | PASS | Properly configured SSL |
| Mixed Content | PASS | No mixed content detected |
| Security Headers | PASS | Standard Next.js security headers |

**Severity**: None - Security is properly implemented.

---

### 6. Mobile Optimization

| Check | Status | Details |
|-------|--------|---------|
| Responsive Design | PASS | Full responsive implementation via Tailwind CSS |
| Viewport Meta | PASS | Proper viewport configuration |
| Touch Targets | PASS | Adequate tap target sizes |
| Font Scaling | PASS | No horizontal scroll, proper text scaling |

**Severity**: None - Mobile optimization is excellent.

---

## Action Items

- [ ] [Priority: P0] Add canonical URLs to all pages (homepage, about, projects, now, blog, blog posts)
- [ ] [Priority: P0] Add Article schema to all blog posts
- [ ] [Priority: P1] Add WebSite schema with SearchAction for internal search functionality
- [ ] [Priority: P1] Add BreadcrumbList schema for improved navigation in SERPs
- [ ] [Priority: P2] Verify Core Web Vitals using PageSpeed Insights (actual testing)
- [ ] [Priority: P3] Audit images for missing alt text attributes

## Data Sources

- **Live Site Analysis**: Fetched and analyzed https://iamamitkumar.dev
- **robots.txt**: https://iamamitkumar.dev/robots.txt
- **sitemap.xml**: https://iamamitkumar.dev/sitemap.xml
- **Existing Audit**: Referenced /home/luciousfox/Projects/ai-seo-agency/data/audits/iamamitkumar-dev-audit.md

## Handoff Notes

The site has a strong technical foundation with excellent crawlability, security, and mobile optimization. The primary gaps are canonical URLs (critical for preventing duplicate content) and complete schema implementation (person on homepage is done, but article schema needed for blog posts). The next agent should prioritize implementing canonical tags and Article schema markup for the 4 blog posts to improve search visibility and rich result eligibility.
