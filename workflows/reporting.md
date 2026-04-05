# Workflow: Monthly/Quarterly Reporting

**Type**: Parallel Swarm → Sequential Synthesis
**Duration**: 1-2 days
**Agents**: analytics, all active agents → client-manager

## Overview

The reporting workflow gathers performance data and work summaries from all active agents, then synthesizes them into a client-facing report.

## Pipeline

```
Phase 1: Data Collection (Parallel Swarm)
├── analytics: Pull all performance data
├── technical-seo: Technical work completed + open issues
├── content-strategist: Content published + pipeline status
├── keyword-research: Ranking changes + new opportunities
├── link-building: Links acquired + campaign progress
├── local-seo: Local ranking changes (if active)
└── ecommerce-seo: E-commerce metrics (if active)

Phase 2: Synthesis (Sequential)
├── seo-strategist: Strategic review and forward plan
└── client-manager: Final report assembly and formatting
```

## Phase 1: Data Collection

Each agent provides a reporting section:

### analytics
```markdown
## Performance Data
- Organic sessions: [current vs prior]
- Organic revenue/conversions: [current vs prior]
- Top growing pages: [list]
- Top declining pages: [list]
- Keyword ranking distribution: [chart data]
- Core Web Vitals: [status]
- Notable anomalies: [if any]
```

### technical-seo
```markdown
## Technical SEO Status
- Issues fixed this period: [list]
- Open critical issues: [list]
- Index coverage changes: [stats]
- Core Web Vitals changes: [stats]
- Upcoming technical work: [list]
```

### content-strategist
```markdown
## Content Status
- Content published: [list with URLs]
- Content in pipeline: [list with status]
- Content performance (published pieces): [traffic, rankings]
- Content calendar: next period preview
```

### keyword-research
```markdown
## Keyword Performance
- New rankings gained: [count + notable keywords]
- Rankings lost: [count + notable keywords]
- Average position change: [delta]
- New opportunities identified: [list]
```

### link-building
```markdown
## Link Building Status
- New referring domains: [count]
- Notable links acquired: [list]
- Average DA of new links: [score]
- Campaign progress vs target: [%]
- Outreach pipeline: [stats]
```

## Phase 2: Synthesis

### seo-strategist
Reviews all data and provides:
```markdown
## Strategic Review
- Progress against quarterly goals: [status]
- Strategy adjustments needed: [if any]
- Next period priorities: [ranked list]
- Risk factors: [anything to watch]
```

### client-manager
Assembles final report following the Client Report output format:
- Formats for client's preferred style
- Adds executive summary
- Highlights wins prominently
- Contextualizes challenges
- Includes clear next steps
- Attaches detailed appendix

## Report Types

### Monthly Report
- Focus: Work completed, quick metrics, tactical updates
- Length: 3-5 pages
- Audience: Day-to-day contacts

### Quarterly Business Review (QBR)
- Focus: Strategic progress, ROI, forward planning
- Length: 10-15 pages + presentation deck
- Audience: Executives and decision-makers
- Additional content: competitive landscape update, strategy evolution

### Ad-hoc Alert Report
- Focus: Specific event (algorithm update, traffic drop, major win)
- Length: 1-2 pages
- Audience: Relevant stakeholders
- Trigger: Anomaly detected by `analytics` or external event
