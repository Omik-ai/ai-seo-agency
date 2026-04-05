# Skill: Technical SEO Audit

**Invokable by**: technical-seo, ecommerce-seo, seo-strategist
**Trigger**: Site audit, technical health check, pre-launch review

## Audit Checklist

### 1. Crawlability & Indexing
- [ ] Robots.txt — exists, valid, not blocking important pages
- [ ] XML Sitemap — exists, valid, submitted to GSC, <50k URLs per file
- [ ] Sitemap includes only indexable, canonical pages
- [ ] No important pages blocked by robots.txt
- [ ] No important pages with noindex
- [ ] Crawl budget efficient (no infinite crawl traps)
- [ ] Index coverage report clean (GSC)
- [ ] Orphan pages identified

### 2. Site Architecture
- [ ] Click depth — important pages within 3 clicks from home
- [ ] Flat architecture (not excessively deep)
- [ ] Logical URL hierarchy (/category/subcategory/page)
- [ ] Breadcrumb navigation present
- [ ] Internal linking distributes authority effectively
- [ ] No excessive URL parameters
- [ ] Pagination handled correctly (rel=prev/next or load more)

### 3. URL Structure
- [ ] Clean, descriptive URLs
- [ ] No special characters, uppercase, or spaces
- [ ] Consistent trailing slash convention
- [ ] No session IDs in URLs
- [ ] Reasonable URL length (<100 characters)

### 4. Redirects
- [ ] No redirect chains (more than one hop)
- [ ] No redirect loops
- [ ] All 301 redirects (not 302) for permanent changes
- [ ] Old URLs properly redirected after migration
- [ ] No soft 404s

### 5. Page Speed & Core Web Vitals
- [ ] LCP (Largest Contentful Paint) < 2.5s
- [ ] INP (Interaction to Next Paint) < 200ms
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] TTFB (Time to First Byte) < 800ms
- [ ] Images optimized (WebP/AVIF, lazy loaded, sized)
- [ ] CSS/JS minified and compressed
- [ ] Browser caching configured
- [ ] CDN in use
- [ ] No render-blocking resources

### 6. Mobile
- [ ] Mobile-responsive design
- [ ] No mobile usability errors (GSC)
- [ ] Touch targets appropriately sized
- [ ] No horizontal scrolling
- [ ] Font size readable without zoom
- [ ] Mobile viewport configured

### 7. Security
- [ ] HTTPS on all pages
- [ ] Valid SSL certificate
- [ ] HTTP → HTTPS redirects in place
- [ ] No mixed content warnings
- [ ] HSTS header configured
- [ ] Security headers present (CSP, X-Frame-Options, etc.)

### 8. Structured Data
- [ ] Organization/LocalBusiness schema on homepage
- [ ] Breadcrumb schema
- [ ] Article schema on blog posts
- [ ] Product schema on product pages (if e-commerce)
- [ ] FAQ schema where applicable
- [ ] Review/Rating schema where applicable
- [ ] No structured data errors in GSC

### 9. International (if applicable)
- [ ] Hreflang tags correct and reciprocal
- [ ] Language/region targeting configured in GSC
- [ ] Content properly localized (not just translated)
- [ ] URL structure supports internationalization

### 10. Duplicate Content
- [ ] Canonical tags on all pages
- [ ] Self-referencing canonicals
- [ ] No conflicting canonicals
- [ ] WWW/non-WWW consolidated
- [ ] HTTP/HTTPS consolidated
- [ ] Parameter-based duplicates handled

## Severity Scoring

| Severity | Criteria | Response |
|----------|----------|----------|
| P0 Critical | Blocks indexing or causes major ranking loss | Fix within 24 hours |
| P1 High | Significant impact on rankings or UX | Fix within 1 week |
| P2 Medium | Moderate impact, optimization opportunity | Fix within 30 days |
| P3 Low | Minor improvement, best practice | Fix within 90 days |

## Output Format

```markdown
| # | Issue | Severity | Pages Affected | Fix Description | Effort |
|---|-------|----------|---------------|----------------|--------|
| 1 | | P0/P1/P2/P3 | [count] | | S/M/L |
```
