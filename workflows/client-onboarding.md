# Workflow: Client Onboarding

**Type**: Sequential Pipeline + Parallel Swarm (hybrid)
**Duration**: 2-4 weeks
**Agents**: ALL (full agency activation)

## Overview

The client onboarding workflow is the agency's most comprehensive process. It activates every department to build a complete picture of the client's SEO landscape and deliver a strategic roadmap.

## Pipeline

```
Phase 1: Discovery (Sequential)
├── client-manager: Gather requirements, goals, access
└── seo-strategist: Review business context, define KPIs

Phase 2: Audit Swarm (Parallel)
├── technical-seo: Full technical audit
├── analytics: Historical performance analysis
├── keyword-research: Keyword landscape mapping
├── content-strategist: Content inventory audit
├── link-building: Backlink profile audit
├── competitive-intel: Competitive landscape analysis
├── local-seo: Local presence audit (if applicable)
└── ecommerce-seo: E-commerce audit (if applicable)

Phase 3: Strategy (Sequential)
├── seo-strategist: Synthesize all audits → strategy document
├── content-strategist: Content roadmap
├── link-building: Link acquisition plan
└── technical-seo: Technical remediation plan

Phase 4: Delivery (Sequential)
├── client-manager: Package all deliverables
├── client-manager: Create onboarding presentation
└── seo-strategist: Final review and sign-off
```

## Phase 1: Discovery

### Step 1.1 — Client Intake (client-manager)
**Input**: New client information
**Actions**:
- Collect business goals, revenue targets, timeline expectations
- Gather site access (GA4, GSC, CMS, hosting)
- Identify key stakeholders and communication preferences
- Document brand guidelines and constraints
- Identify competitors (client-named + discovered)
**Output**: Client Brief Document → feeds all Phase 2 agents

### Step 1.2 — Strategic Framing (seo-strategist)
**Input**: Client Brief Document
**Actions**:
- Define primary KPIs aligned with business goals
- Set realistic expectations and timeline
- Identify which audit modules to activate (skip local-seo for purely online businesses, skip ecommerce-seo for service businesses, etc.)
- Establish baseline metrics
**Output**: Strategic Framework → guides all Phase 2 work

## Phase 2: Audit Swarm

All agents run in **parallel**. Each reads the Client Brief and Strategic Framework, then produces their audit independently.

### Agent Assignments
| Agent | Reads | Produces | Est. Time |
|-------|-------|----------|-----------|
| technical-seo | Client Brief, Site access | Technical Audit Report | 2-3 days |
| analytics | GA4/GSC data, KPIs | Performance Baseline Report | 1-2 days |
| keyword-research | Business context, competitors | Keyword Landscape Report | 2-3 days |
| content-strategist | Site content, competitors | Content Audit Report | 2-3 days |
| link-building | Domain, competitors | Backlink Profile Report | 1-2 days |
| competitive-intel | Competitor list, target KWs | Competitive Analysis Report | 2-3 days |
| local-seo | NAP, locations | Local SEO Audit (if applicable) | 1-2 days |
| ecommerce-seo | Store URL, platform | E-commerce Audit (if applicable) | 2-3 days |

### Merge Point
All audit reports collected → passed to Phase 3.

## Phase 3: Strategy Synthesis

### Step 3.1 — Master Strategy (seo-strategist)
**Input**: All Phase 2 audit reports
**Actions**:
- Synthesize findings across all audits
- Identify cross-cutting themes and priorities
- Build 90-day, 6-month, and 12-month roadmaps
- Allocate budget across channels
- Define success metrics and milestones
**Output**: SEO Strategy Document

### Step 3.2 — Department Plans (Parallel)
| Agent | Input | Output |
|-------|-------|--------|
| content-strategist | Strategy + KW Report + Content Audit | Content Roadmap (Q1) |
| link-building | Strategy + Backlink Audit + Competitor Links | Link Building Plan (Q1) |
| technical-seo | Strategy + Technical Audit | Technical Remediation Plan |

## Phase 4: Delivery

### Step 4.1 — Package (client-manager)
**Input**: All strategy documents and plans
**Actions**:
- Create executive presentation
- Organize all deliverables
- Prepare client-friendly summaries
- Build reporting dashboard template
**Output**: Onboarding Package

### Step 4.2 — Kickoff Preparation (client-manager)
**Input**: Onboarding Package
**Actions**:
- Create meeting agenda
- Prepare Q&A document
- Set up recurring reporting schedule
**Output**: Kickoff Meeting Materials

## Deliverables Checklist

- [ ] Client Brief Document
- [ ] Strategic Framework
- [ ] Technical SEO Audit
- [ ] Performance Baseline Report
- [ ] Keyword Landscape Report
- [ ] Content Audit Report
- [ ] Backlink Profile Report
- [ ] Competitive Analysis Report
- [ ] Local SEO Audit (if applicable)
- [ ] E-commerce SEO Audit (if applicable)
- [ ] SEO Strategy Document (90-day, 6mo, 12mo)
- [ ] Content Roadmap (Q1)
- [ ] Link Building Plan (Q1)
- [ ] Technical Remediation Plan
- [ ] Executive Presentation
- [ ] Reporting Dashboard Template
