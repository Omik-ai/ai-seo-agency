#!/usr/bin/env python3
"""
SEO Agency Full Pipeline - AgentFlow Orchestration

Deploys 4 parallel SEO agents to perform a comprehensive site audit:
- technical-seo
- analytics
- on-page-seo
- content-strategist

Then synthesizes results via seo-strategist
"""

from agentflow import Graph, opencode, merge

TARGET_DOMAIN = "iamamitkumar.dev"
TARGET_URL = f"https://{TARGET_DOMAIN}"

with Graph("seo-full-audit-pipeline", concurrency=4) as g:
    # Phase 1: Parallel Swarm - 4 SEO agents running simultaneously

    technical_seo = opencode(
        task_id="technical-seo",
        prompt=f"""You are the Technical SEO Agent for AI SEO Agency.

## MISSION
Perform a comprehensive technical SEO audit for {TARGET_URL}.

## DOMAIN
{TARGET_DOMAIN}

## YOUR EXPERTISE
- Site crawling and indexing analysis
- Core Web Vitals assessment
- Schema markup implementation
- Site architecture review
- Mobile optimization
- Security (HTTPS)
- Technical audits following skills/technical-audit.md

## OUTPUT REQUIREMENTS
Follow CLAUDE.md deliverable format:
- Executive Summary (2-3 sentences)
- Findings with severity ratings (P0/P1/P2/P3)
- Action items prioritized
- Data sources listed
- Handoff notes for next agent

## SPECIFIC CHECKS
1. Crawlability - robots.txt, sitemap, crawl budget
2. Indexing - canonicals, noindex tags, URL parameters
3. Core Web Vitals - LCP, FID, CLS estimates
4. Schema - structured data implementation
5. Security - HTTPS, headers
6. Mobile - responsive, mobile-first

Deliver to: data/audits/{TARGET_DOMAIN}-technical-audit.md

Begin your audit now.""",
    )

    analytics = opencode(
        task_id="analytics",
        prompt=f"""You are the Analytics Agent for AI SEO Agency.

## MISSION
Analyze historical organic performance for {TARGET_URL}.

## DOMAIN
{TARGET_DOMAIN}

## YOUR EXPERTISE
- GA4, GSC data analysis
- Traffic trend analysis
- Keyword ranking distribution
- Conversion tracking
- Performance baseline reporting
- Analytics methodology from skills/rank-tracking.md

## OUTPUT REQUIREMENTS
Follow CLAUDE.md deliverable format:
- Executive Summary (2-3 sentences)
- Performance metrics with trends
- Top performing pages analysis
- Traffic insights
- Action items prioritized
- Data sources listed

## SPECIFIC ANALYSIS
1. Traffic trends - growth/decline patterns
2. Top pages - by organic sessions
3. Keyword positions - distribution by SERP position
4. CTR analysis - by position bracket
5. Conversions - organic conversion tracking

Note: If you cannot access live GSC/GA4 data, base analysis on:
- Available crawl data
- Site structure analysis
- Industry benchmarks

Deliver to: data/audits/{TARGET_DOMAIN}-analytics-report.md

Begin your analysis now.""",
    )

    on_page_seo = opencode(
        task_id="on-page-seo",
        prompt=f"""You are the On-Page SEO Agent for AI SEO Agency.

## MISSION
Perform on-page SEO audit for top pages on {TARGET_URL}.

## DOMAIN
{TARGET_DOMAIN}

## YOUR EXPERTISE
- Meta tag optimization
- Heading structure analysis
- Internal linking patterns
- NLP/content optimization
- E-E-A-T signal assessment
- On-page methodology from skills/page-optimization.md

## OUTPUT REQUIREMENTS
Follow CLAUDE.md deliverable format:
- Executive Summary (2-3 sentences)
- Page-by-page analysis
- Individual element scores
- Optimization recommendations
- Action items prioritized

## AUDIT SCOPE
Analyze top 10-20 pages by estimated traffic:
1. Title tags - length, keyword placement, uniqueness
2. Meta descriptions - length, CTAs, uniqueness
3. H1/H2 headings - hierarchy, keyword usage
4. Content - depth, quality, NLP optimization
5. Internal links - anchor text, distribution
6. E-E-A-T signals - authority indicators

Deliver to: data/audits/{TARGET_DOMAIN}-onpage-audit.md

Begin your audit now.""",
    )

    content_strategist = opencode(
        task_id="content-strategist",
        prompt=f"""You are the Content Strategist Agent for AI SEO Agency.

## MISSION
Audit the content ecosystem for {TARGET_URL}.

## DOMAIN
{TARGET_DOMAIN}

## YOUR EXPERTISE
- Content inventory and mapping
- Topic cluster analysis
- Content quality scoring
- Content gap identification
- Content calendar planning
- Methodology from skills/content-brief.md

## OUTPUT REQUIREMENTS
Follow CLAUDE.md deliverable format:
- Executive Summary (2-3 sentences)
- Content inventory with scores
- Quality analysis by type
- Gap analysis vs competitors
- Content recommendations
- Action items prioritized

## ASSESSMENT
1. Content inventory - all pages, posts, resources
2. Quality scoring - using Content Scoring Framework
3. Topic clusters - content pillar mapping
4. Gaps - vs target keywords/topics
5. Opportunities - quick wins, expansion

Deliver to: data/audits/{TARGET_DOMAIN}-content-audit.md

Begin your content audit now.""",
    )

# Phase 2: Merge & Synthesis
# After all 4 parallel agents complete, synthesize into final audit

with Graph("seo-synthesis", depends_on=g) as synthesis:
    # Merge point - all 4 audits collected
    merge_point = merge(
        opencode(
            task_id="collect-audits",
            prompt="Collect and summarize all 4 SEO audit reports from previous pipeline",
        ),
        source=g,
        size=4,
    )

    # SEO Strategist synthesizes into final unified report
    final_audit = opencode(
        task_id="seo-strategist-synthesis",
        prompt=f"""You are the SEO Strategist Agent for AI SEO Agency.

## MISSION
Synthesize all audit reports into a unified comprehensive SEO audit for {TARGET_DOMAIN}.

## INPUTS
You have outputs from 4 parallel agents:
- Technical SEO audit
- Analytics report
- On-Page SEO audit
- Content audit

## YOUR TASK
Create a unified audit document with:
1. Overall health score (out of 100)
2. Category scores (Technical, On-Page, Content, Performance)
3. Executive summary with top 3 wins and top 3 critical issues
4. Prioritized action items (P0/P1/P2/P3)
5. Detailed findings from each agent
6. 90-day recommended action plan

## SCORING RUBRIC
- 90-100: Excellent
- 75-89: Good, minor improvements
- 60-74: Fair, several issues
- Below 60: Poor, major work needed

## OUTPUT FORMAT
Follow CLAUDE.md deliverable format.

Deliver to: data/audits/{TARGET_DOMAIN}-audit.md

Begin synthesis now.""",
    )

print("SEO Pipeline Defined")
print(f"Target: {TARGET_DOMAIN}")
print("Agents: technical-seo, analytics, on-page-seo, content-strategist")
print("Pattern: Parallel swarm → Synthesis")
