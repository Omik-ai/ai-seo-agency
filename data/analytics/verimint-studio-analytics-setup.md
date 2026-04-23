# Analytics & Tracking Setup: verimint.studio

> **Task**: ANL-001 | **Date**: 2026-04-23 | **Agent**: analytics
> **Client**: Verimint Studio — Premium Academic Content & Content Marketing Agency

---

## Current State

- **Existing**: `@vercel/analytics` (basic page views only)
- **Missing**: GA4, Google Search Console, conversion tracking, rank tracking, custom events

---

## 1. Google Analytics 4 Setup

### Step 1: Create GA4 Property
1. Go to [analytics.google.com](https://analytics.google.com)
2. Create new account: "Verimint Studio"
3. Create property: "verimint.studio"
4. Note the Measurement ID (format: `G-XXXXXXXXXX`)

### Step 2: Install GA4 in Next.js

Create `src/components/analytics.tsx`:

```tsx
import Script from "next/script";

export function Analytics() {
  const measurementId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID;

  if (!measurementId) return null;

  return (
    <>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${measurementId}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${measurementId}', {
            page_path: window.location.pathname,
          });
        `}
      </Script>
    </>
  );
}
```

Add to `src/app/layout.tsx` inside the `<body>`:

```tsx
import { Analytics } from "@/components/analytics";
import { Analytics as VercelAnalytics } from "@vercel/analytics/react";

// Inside body, after ThemeProvider:
<Analytics />
<VercelAnalytics />
```

Add to `.env.local`:
```
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### Step 3: Configure Custom Events

```tsx
// src/lib/analytics.ts
export function trackEvent(eventName: string, params?: Record<string, unknown>) {
  if (typeof window !== "undefined" && (window as any).gtag) {
    (window as any).gtag("event", eventName, params);
  }
}

// Trackable events:
// - form_submit (service inquiry)
// - cta_click (Start Your Project, See Our Results)
// - page_scroll (25%, 50%, 75%, 100%)
// - file_download (if offering downloadable content)
// - external_link_click (social links, etc.)
```

---

## 2. Google Search Console Setup

### Step 1: Verify Ownership
1. Go to [search.google.com/search-console](https://search.google.com/search-console)
2. Add property: `https://verimint.studio`
3. Verify via DNS TXT record (recommended) or HTML file
4. DNS verification is already supported via the `GOOGLE_SITE_VERIFICATION` env var in layout.tsx

### Step 2: Submit Sitemap
1. Go to Sitemaps in GSC
2. Submit: `https://verimint.studio/sitemap.xml`
3. Verify all 9 URLs are discovered

### Step 3: Monitor
- Index Coverage — check for indexing errors
- Performance — track clicks, impressions, CTR, position
- Core Web Vitals — monitor LCP, INP, CLS
- Mobile Usability — check for mobile issues

---

## 3. Conversion Tracking Plan

### Primary Conversions

| Event | Trigger | GA4 Event Name | Parameters |
|-------|---------|----------------|------------|
| Contact Form Submit | Form submission | `form_submit` | { form_name, service_interest } |
| CTA Click — Start Project | Button click | `cta_click` | { cta_name, page_path } |
| CTA Click — See Results | Button click | `cta_click` | { cta_name: "See Our Results", page_path } |
| Pricing Page View | Page load | `view_pricing` | { page_path } |
| Services Page View | Page load | `view_services` | { page_path } |
| Blog Article Read | Scroll 50%+ | `article_read` | { article_title, category } |
| Social Link Click | Link click | `social_click` | { platform, page_path } |

### Implementation

Add to CTA buttons and forms:

```tsx
import { trackEvent } from "@/lib/analytics";

<Button onClick={() => {
  trackEvent("cta_click", { cta_name: "Start Your Project", page_path: window.location.pathname });
  // existing scroll logic
}}>
  Start Your Project
</Button>
```

---

## 4. Rank Tracking Keyword List

Based on STR-003 keyword research, track these priority keywords:

### Tier 1 — Track Immediately (Low Difficulty)
| Keyword | Target Page | Current Position |
|---------|------------|-----------------|
| academic writing agency | / | TBD |
| best academic writing service | / | TBD |
| academic writing USA | /services | TBD |
| academic writing UK | /services | TBD |
| academic writing Australia | /services | TBD |
| academic writing vs content writing | Blog | TBD |
| how much does content marketing cost | /pricing | TBD |

### Tier 2 — Track Within 30 Days
| Keyword | Target Page |
|---------|------------|
| academic writing services | /services |
| content marketing agency | /services |
| professional copywriter | /about |
| content marketing services | /services |
| SEO content writing services | /services |

### Tier 3 — Track Within 60 Days
| Keyword | Target Page |
|---------|------------|
| dissertation writing service | /services |
| research paper writing service | /services |
| content marketing strategy | Blog |
| academic writing help | Blog |
| how to write a research paper | Blog |

---

## 5. Custom Dashboard Specification

### Looker Studio Dashboard Layout

**Page 1: Executive Overview**
- Total organic sessions (vs previous period)
- Organic keywords ranking (top 10, top 20, top 100)
- Top landing pages by organic sessions
- Conversion rate from organic traffic
- Goal completions from organic

**Page 2: Content Performance**
- Blog posts by sessions, engagement time, conversions
- Top performing content categories
- Content decay analysis (posts losing traffic)
- Featured snippet wins/losses

**Page 3: Technical Health**
- Core Web Vitals trends (LCP, INP, CLS)
- Indexed pages count
- Crawl errors
- Page speed scores

**Page 4: Link Building**
- Referring domains (trend)
- Top backlinks by DA
- New vs lost links
- Link acquisition rate

---

## 6. KPI Tracking Framework

### Monthly Reporting Template

```markdown
# SEO Monthly Report — [Month Year]

## Executive Summary
- [1-2 sentence overview of performance]

## Key Metrics
| Metric | This Month | Previous Month | Change |
|--------|-----------|---------------|--------|
| Organic Sessions | | | |
| Organic Keywords | | | |
| Top 10 Rankings | | | |
| Referring Domains | | | |
| Conversion Rate | | | |

## Top Performing Pages
| Page | Sessions | Keywords | Conversions |
|------|----------|----------|-------------|

## Content Published
- [List of new content published]

## Technical Issues
- [Any crawl errors, indexing issues]

## Next Month Priorities
- [Top 3 priorities]
```

---

## 7. Goal/Conversion Setup

### GA4 Goals (Conversions)

| Goal Name | Event | Condition | Value |
|-----------|-------|-----------|-------|
| Lead Generated | `form_submit` | Any form submission | $500 |
| CTA Engagement | `cta_click` | CTA clicked | $50 |
| Content Engaged | `article_read` | 50%+ scroll on blog | $5 |
| Pricing Viewed | `view_pricing` | Pricing page viewed | $10 |

---

## Implementation Checklist

- [ ] Create GA4 property and get Measurement ID
- [ ] Add GA4 script to Next.js layout
- [ ] Set up Google Search Console and verify ownership
- [ ] Submit sitemap.xml to GSC
- [ ] Implement custom event tracking (CTA clicks, form submits)
- [ ] Set up GA4 conversions
- [ ] Create Looker Studio dashboard
- [ ] Configure rank tracking for Tier 1 keywords
- [ ] Set up monthly reporting template
- [ ] Test all tracking with GA4 DebugView

---

*Document generated by Analytics Agent | Task: ANL-001 | 2026-04-23*
