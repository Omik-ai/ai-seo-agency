# Workflow: Content Production Pipeline

**Type**: Sequential Pipeline
**Duration**: Ongoing (cyclical)
**Agents**: keyword-research → content-strategist → on-page-seo → link-building

## Overview

The content pipeline transforms keyword opportunities into published, optimized, and promoted content. It runs as a sequential pipeline where each agent's output feeds the next.

## Pipeline

```
keyword-research → content-strategist → on-page-seo → link-building → ai-surface-distribution
     (discover)      (plan & brief)      (optimize)     (promote)       (llm-feed)
```

## Stage 1: Discovery (keyword-research)

**Trigger**: New content cycle begins or topic request received
**Actions**:
- Research keyword opportunities for the target topic/cluster
- Cluster keywords by topic and intent
- Identify content format opportunities (listicles, guides, tools, etc.)
- Assess keyword difficulty vs. current domain authority
- Map keywords to funnel stages

**Output → passes to content-strategist**:
```markdown
## Content Opportunity Brief
- Primary keyword: [keyword] (vol: X, KD: Y)
- Supporting keywords: [list with data]
- Search intent: [type]
- SERP features present: [snippets, PAA, images, etc.]
- Top competing content: [3-5 URLs with analysis]
- Recommended content format: [type]
- Estimated traffic potential: [range]
```

## Stage 2: Planning & Briefing (content-strategist)

**Trigger**: Receives Content Opportunity Brief from keyword-research
**Actions**:
- Develop full content brief with outline
- Define target audience and angle
- Set E-E-A-T requirements
- Plan internal linking targets
- Specify visual asset needs
- Set success metrics for the piece

**Output → passes to on-page-seo**:
```markdown
## Content Brief
[Full brief per content-strategist output contract]
```

## Stage 3: Optimization (on-page-seo)

**Trigger**: Content is drafted (by human or AI writer)
**Actions**:
- Optimize title tag and meta description
- Refine heading hierarchy
- Insert semantic/NLP keywords naturally
- Add internal links with optimized anchor text
- Optimize images (alt text, file names, compression)
- Add schema markup (Article, FAQ, HowTo, etc.)
- Optimize for featured snippet capture
- Add E-E-A-T signals (author bio, citations, credentials)

**Output → passes to link-building**:
```markdown
## Optimized Page Spec
- Final title tag: [title]
- Final meta description: [meta]
- Schema markup: [JSON-LD code]
- Internal links added: [list]
- Featured snippet targeting: [format + content]
- Optimization score: [X/10]
```

## Stage 4: Promotion (link-building)

**Trigger**: Content is published and indexed
**Actions**:
- Identify link prospects for this specific content
- Craft outreach angles relevant to the content topic
- Identify broken link replacement opportunities
- Find resource page targets
- Draft outreach templates specific to this content
- Plan digital PR angle (if data-driven content)

**Output**:
```markdown
## Link Building Plan for [Content Title]
- Link prospect list: [N prospects with scores]
- Outreach templates: [customized for this content]
- Target links: [N links in first 60 days]
- Promotion channels: [outreach, social, communities]
```

## Stage 5: AI Surface Distribution (aio-optimization + geo-optimization)

**Trigger**: Content is published and link building is underway
**Agents**: `aio-optimization` (lead), `geo-optimization` (support)
**Actions**:
- Generate Reddit post draft for relevant subreddits (via `tools/distribution/ai_surfaces.py`)
- Generate Quora answer draft for related questions
- Generate Perplexity Pages draft structure
- Ensure FAQPage / HowTo schema is live on the content
- Verify question-style H2s and TL;DR blocks are present
- Submit to IndexNow / Indexing API for rapid discovery
- Syndicate to community platforms that feed LLM training data

**Output**:
```markdown
## AI Surface Distribution Plan for [Content Title]
### Reddit
- Subreddit: [r/...]
- Post draft: [title + body]
- Status: draft | posted | rejected

### Quora
- Target question: [question text]
- Answer draft: [body]
- Status: draft | posted

### Perplexity Pages
- Page structure: [markdown outline]
- Sources included: [list]
- Status: draft

### Schema Verification
- FAQPage present: [yes/no]
- HowTo present: [yes/no]
- Question headings: [count]
- TL;DR block: [yes/no]

### Indexing
- IndexNow submitted: [yes/no]
- Google Indexing API: [yes/no]
```

## Cycle Metrics

Track per content piece:
- Time from discovery to publish: [days]
- Time from publish to first rankings: [days]
- Organic traffic at 30/60/90 days
- Keywords ranking at 30/60/90 days
- Links acquired at 30/60/90 days
- Conversion events from the content

## Batch Mode

For high-volume content production, run multiple pipeline instances:
```
Pipeline 1: keyword-research → content-strategist → [Topic A]
Pipeline 2: keyword-research → content-strategist → [Topic B]
Pipeline 3: keyword-research → content-strategist → [Topic C]
```

Each can be at a different stage simultaneously, creating continuous output.
