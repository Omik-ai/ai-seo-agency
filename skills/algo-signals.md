# Algorithmic Signals Alignment

> Maps Google algorithm updates to on-page signals we measure.

## Core Algorithm Updates

### March 2024 Core Update
- **Focus**: Content quality, reducing unoriginal / low-value content.
- **Signals**: `content` (word_count, flesch), `eeat` (author bios, about page), `topical_authority` (cohesion, freshness).
- **Action**: Audit for thin content (< 300 words), missing authorship, stale clusters.

### September 2023 Helpful Content Update
- **Focus**: Site-level helpfulness classifier.
- **Signals**: `content`, `eeat`, `topical_authority`.
- **Action**: Ensure every page has clear purpose, original insight, and expert authorship.

### Page Experience (2021+)
- **Focus**: CWV + mobile usability + HTTPS + no intrusive interstitials.
- **Signals**: `cwv`, `technical` (mobile, https, hsts).
- **Action**: Fix LCP > 2.5s, CLS > 0.1, missing HTTPS.

### Spam Updates (2023–2024)
- **Focus**: SpamBrain detection of link schemes, hidden text, keyword stuffing.
- **Signals**: `content` (keyword stuffing), `linkgraph` (nofollow commercial, reciprocal), `schema` (misleading markup).
- **Action**: Audit anchor text diversity, internal link density, schema accuracy.

### Reviews Update (Product Reviews)
- **Focus**: First-hand evidence in reviews.
- **Signals**: `eeat` (expertise), `schema` (Review schema with pros/cons).
- **Action**: Add original images, quantitative metrics, and clear reviewer credentials.

### AIO / SGE Preparation
- **Focus**: AI Overviews pull from structured data, entity graphs, and authoritative clusters.
- **Signals**: `schema`, `content` (entities), `topical_authority`, `serp` (brand presence).
- **Action**: Implement FAQ, HowTo, and Article schema. Build entity-rich content.

## Signal → Algorithm Mapping

| Signal | Algorithms | Key Thresholds |
|--------|-----------|----------------|
| technical | Core, Page Experience | HTTPS, mobile, HSTS, robots |
| headings | Core, Helpful Content | Single H1, no skips, keyword in H1 |
| schema | Core, Spam, AIO | Valid JSON-LD + microdata + RDFa |
| cwv | Page Experience | LCP < 2.5s, CLS < 0.1, INP < 200ms |
| eeat | Helpful Content, Core | Author pages, About page, bios, org schema |
| content | Core, Helpful Content, Spam | > 300 words, Flesch 60-70, density < 3% |
| linkgraph | Spam, Core | Nofollow UGC/commercial, no orphans |
| accessibility | Page Experience | Alt text, labels, lang attr, skip links |
| topical_authority | Helpful Content, Core | Cohesion > 20%, link density > 30% |
| serp | Brand, AIO | Brand in top 10, Knowledge Panel |
| aio | SGE / AIO | FAQ schema, entity density, PAA coverage |

## QA Gate

Any audit finding must reference the relevant algorithm in its `google_algo_ref` field.
The QA validator checks that all P0/P1 findings have a non-empty `google_algo_ref`.
