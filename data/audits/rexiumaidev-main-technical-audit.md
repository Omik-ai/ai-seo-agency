# Technical SEO Audit Report: rexiumaidev-main

**Date:** April 8, 2026  
**Target:** https://www.rexiumit.com  
**Framework:** Next.js 15 (App Router)

---

## Crawl & Indexing

### robots.ts (Dynamic)
- **Status:** Well-configured with comprehensive user-agent rules
- **Strengths:**
  - Separate rules for Google, Bing, AI search bots (GPTBot, Claude-Web, PerplexityBot, OAI-SearchBot, Google-Extended)
  - Disallows tracking parameters (?utm_*, ?fbclid, ?gclid)
  - Includes programmatic SEO sitemap references (/g/sitemap.xml, /sitemaps/)
  - Blocks aggressive crawlers (MJ12bot, YandexBot) with 24h delay
  - Allows AI discoverability file (/llms.txt)
- **Issues:**
  - Multiple conflicting rules for same user-agent (Google-Extended should follow main Google rules)
  - crawlDelay on `*` may be ignored by Google (deprecated)
  - Some blocked SEO tools (AhrefsBot, SemrushBot) with 5s delay

### sitemap.ts
- **Status:** Well-structured with priority-based organization
- **Coverage:** 50+ static pages (core, services, industries, resources, tools, legal)
- **Strengths:**
  - Proper changeFrequency values (daily, weekly, monthly)
  - Priority levels 0.3-1.0 correctly assigned
  - Includes pSEO landing pages (/uk, /us, /dubai, /australia, /singapore)
- **Issues:**
  - lastModified dates hardcoded to "2025-01-27" — should be dynamic
  - TODO comments for AEO/GEO pages not implemented (answers/*, faq/*, locations/*)
  - No blog post entries (only featuredBlogPosts placeholder with static list)

### public/robots.txt
- **Status:** Outdated and redundant
- **Issue:** Only 7 lines, allows all, no disallows — conflicts with src/app/robots.ts
- **Recommendation:** Delete this file; Next.js serves dynamic robots.ts at /robots.txt

---

## Critical Issues (P0)

### 1. Duplicate Robots.txt Configuration
- **File:** public/robots.txt vs src/app/robots.ts
- **Impact:** Conflicting rules may cause unexpected crawling behavior
- **Fix:** Delete public/robots.txt

### 2. Hardcoded Sitemap Dates
- **File:** src/app/sitemap.ts:19
- **Code:** `const recentUpdate = new Date("2025-01-27");`
- **Impact:** All pages show stale lastModified date to crawlers
- **Fix:** Use dynamic dates or fetch from content CMS

### 3. Missing AEO/GEO Pages in Sitemap
- **Files:** src/app/sitemap.ts:95-135 (commented out)
- **Impact:** Thousands of potential SEO pages not indexed
- **Fix:** Implement answers/*, faq/*, locations/* modules

### 4. Blog Posts Not Dynamically Included
- **File:** src/app/sitemap.ts:208-251
- **Impact:** New blog posts require manual sitemap updates
- **Fix:** Fetch blog posts from CMS/database dynamically

---

## High Priority (P1)

### 5. Incomplete Structured Data Implementation
- **File:** src/app/layout.tsx:215-295
- **Status:** Basic schemas present (Organization, LocalBusiness, WebSite, FAQPage, BreadcrumbList)
- **Missing:**
  - Service schema for /services pages
  - Article schema for blog posts
  - SoftwareApplication schema for tool pages
  - FAQPage on individual FAQ pages (not implemented)
  - HowTo schema for guides
  - Review/Testimonial schema for case studies

### 6. Middleware Security - Prisma Import in Edge Runtime
- **File:** src/middleware.ts:3
- **Code:** `import { PrismaClient } from '@prisma/client'`
- **Issue:** Prisma Client not Edge-compatible; causes cold starts, potential runtime errors
- **Impact:** /api/agents/* middleware may fail on Vercel Edge
- **Fix:** Use @prisma/client/edge or remove unused import (only used for type hints)

### 7. Missing Hreflang Implementation
- **File:** src/app/layout.tsx:172-173 (commented)
- **Impact:** No language/region targeting for international SEO
- **Fix:** Implement generateHreflangTags() for /uk, /us, /dubai, /australia, /singapore

### 8. Inline Script Security Risks
- **Files:** src/app/layout.tsx:397-562
- **Status:** Multiple inline scripts with dangerouslySetInnerHTML
- **Risk:** XSS vulnerabilities; hard to audit
- **Fix:** Move to external script files or use Next.js Script with strategy="afterInteractive"

### 9. Missing Core Web Vitals Tracking Components
- **Files:** src/app/layout.tsx:381-383 (commented)
- **Status:** No active tracking of LCP, FID, CLS, INP
- **Fix:** Implement CoreWebVitalsTracker component

---

## Medium Priority (P2)

### 10. Image Optimization - dangerouslyAllowSVG: false
- **File:** next.config.js:33
- **Status:** Correctly set
- **Note:** Ensure all SVGs served via next/image or static folder

### 11. Missing Next.js Image Component Usage Audit
- **Issue:** Unknown if all images use <Image /> component
- **Fix:** Audit all <img> tags and convert to next/image

### 12. CSP Configuration - 'unsafe-inline' Required
- **File:** lib/csp-config.js:11-12
- **Status:** Required for Next.js but weakens security
- **Fix:** Use CSP hash nonce for inline scripts in production

### 13. Missing robots.txt HTTP Header
- **File:** next.config.js
- **Issue:** No explicit X-Robots-Tag for /robots.txt
- **Fix:** Add header rule for /robots.txt

### 14. No Canonical URL Per-Page Configuration
- **Status:** Only root canonical in layout.tsx
- **Fix:** Ensure each dynamic page exports canonical in metadata

---

## Low Priority (P3)

### 15. console.log in Sitemap
- **File:** src/app/sitemap.ts:338-349
- **Impact:** Pollutes server logs in production
- **Fix:** Remove or use proper logger with ENV check

### 16. Unused SEO Module Imports
- **File:** src/app/layout.tsx:19-36 (commented)
- **Impact:** Technical debt
- **Fix:** Either implement modules or remove imports

### 17. Missing PWA Manifest Validation
- **File:** src/app/layout.tsx:355
- **Reference:** /manifest.json
- **Fix:** Verify manifest.json exists and is valid

### 18. Font Preload Specific to Single Font
- **File:** src/app/layout.tsx:343-349
- **Issue:** Hardcoded Roboto woff2 URL; may 404 if font changes
- **Fix:** Use Next.js font optimization automatically

---

## Site Architecture

### Routing Structure
```
/ (home)
/about
/pricing
/contact
/services (list)
/services/[slug] (dynamic - pSEO)
/industries/[industry] (dynamic - pSEO)
/g/[slug] (programmatic pages)
/blog /blog/[slug] /blog/create /blog/edit/[slug]
/case-studies /case-studies/[slug]
/resources /resources/[slug]
/tools /roi-calculator
/uk /us /dubai /australia /singapore (geo landing pages)
/ai-ethics /privacy /terms /security
/admin/* (protected)
/api/agents/* (M2M auth)
/auth/signin /auth/signup /auth/error
```

### Assessment
- **Positives:**
  - Clean App Router structure
  - Route groups: (public), (protected) properly separated
  - Dynamic routes for pSEO (/services/[slug], /industries/[industry])
- **Concerns:**
  - Duplicate content risk with /g/[slug] vs /services/[slug]
  - No URL normalization ( trailing slash inconsistency?)
  - No canonical redirect rules in middleware

---

## Core Web Vitals Configuration

### next.config.js Optimizations
| Feature | Status | Notes |
|---------|--------|-------|
| poweredByHeader: false | ✅ Good | Hides X-Powered-By |
| compress: true | ✅ Good | Gzip/Brotli |
| optimizeCss: true | ✅ Good | Critical CSS inlining |
| removeConsole (prod) | ✅ Good | Reduces bundle |
| Image formats: avif, webp | ✅ Good | Best-in-class |
| Image sizes/deviceSizes | ✅ Good | Responsive images |
| static/cache: 1 year | ✅ Good | Immutable assets |
| standalone output | ✅ Good | Reduces cold starts |

### Missing Optimizations
- Missing: experimental.ogImageGeneration (Next.js 15 feature)
- Missing: taint (prevent passing large objects to client)
- Missing: mdxRs (if using MDX for blog)

---

## Security Headers

### Configured (next.config.js)
```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
X-DNS-Prefetch-Control: on
X-Robots-Tag: index, follow, max-image-preview:large, max-snippet:200
```

### CSP (lib/csp-config.js)
- default-src: 'self'
- script-src: 'self' 'unsafe-inline' 'unsafe-eval' + Google domains
- style-src: 'self' 'unsafe-inline' + Google Fonts
- img-src: 'self' data: blob: https:
- connect-src: 'self' + Google Analytics
- frame-src: googletagmanager
- object-src: 'none' ✅ Good

### Gaps
- No Strict-Transport-Security (should be at edge/server level)
- No Content-Security-Policy meta tag (CSP only in lib, not applied)
- CSP 'unsafe-inline' weakens XSS protection

---

## Rendering Analysis

### SSR/CSR Mix
| Page Type | Rendering | Notes |
|-----------|-----------|-------|
| Root layout | SSR | Static metadata, dynamic head scripts |
| /page.tsx (home) | Static (default) | SSG with ISR potential |
| /services/[slug] | Dynamic | ISR with revalidate |
| /blog/[slug] | Dynamic | SSR or ISR |
| /admin/* | SSR | Protected, auth required |
| /api/* | API Routes | Edge/Node runtime |

### Assessment
- **Good:** Next.js App Router defaults to Server Components (optimal for SEO)
- **Concern:** Heavy client-side hydration in layout (analytics, theme provider)
- **Fix:** Move analytics scripts to next/script with strategy="worker" for non-blocking

---

## Structured Data Recommendations

### Immediate Additions
1. **Service Schema** - For /services and /services/[slug]
   ```json
   {
     "@type": "Service",
     "name": "AI Software Development",
     "provider": { "@type": "Organization", "name": "Rexiumit" },
     "areaServed": "Worldwide",
     "description": "..."
   }
   ```

2. **Article Schema** - For /blog/[slug]
   ```json
   {
     "@type": "BlogPosting",
     "headline": "...",
     "author": { "@type": "Organization", "name": "Rexiumit" },
     "datePublished": "...",
     "image": "..."
   }
   ```

3. **SoftwareApplication Schema** - For /tools/*
   ```json
   {
     "@type": "SoftwareApplication",
     "name": "AI ROI Calculator",
     "applicationCategory": "BusinessApplication",
     "operatingSystem": "Web"
   }
   ```

4. **HowTo Schema** - For tutorials/guides

5. **Review Schema** - For case studies

### AEO Enhancements
- Add FAQPage schema to dedicated /faq route
- Implement SpeakableSpecification on Q&A pages
- Add Q&A pages to sitemap (currently commented out)

### GEO Enhancements
- Add LocalBusiness schema to each geo landing page (/uk, /us, etc.)
- Different address/telephone per location
- Add hreflang tags for regional variants

---

## Implementation Specs

### Quick Wins (1 Sprint)
1. Delete public/robots.txt
2. Fix sitemap lastModified to use dynamic dates
3. Remove console.log from sitemap.ts
4. Clean up commented imports in layout.tsx

### Short-term (1-2 Sprints)
5. Add Service, Article, SoftwareApplication schemas per-page
6. Implement blog post fetching in sitemap.ts
7. Remove Prisma import from middleware.ts or use edge-compatible version
8. Add CoreWebVitalsTracker component

### Medium-term (2-3 Sprints)
9. Implement AEO modules (answers/*, faq/*)
10. Implement hreflang for geo pages
11. Refactor inline scripts to external files
12. Implement comprehensive per-page canonical URLs

### Long-term
13. Add ISR/revalidate for dynamic pages
14. Implement full CSP with nonces
15. Audit all images use next/image
16. Add structured data for reviews/testimonials

---

## Summary Score

| Area | Score | Notes |
|------|-------|-------|
| Crawl & Indexing | 85% | Good robots/sitemap, stale dates |
| Core Web Vitals Config | 90% | Well-optimized Next.js config |
| Site Architecture | 80% | Clean structure, duplicate content risk |
| Structured Data | 60% | Basic schemas, missing per-page types |
| Security Headers | 75% | Good defaults, CSP not fully applied |
| Rendering | 85% | Server Components, hydration concerns |
| URL Structure | 70% | No canonical redirects, param handling |
| **Overall** | **78%** | Production-ready with cleanup needed |