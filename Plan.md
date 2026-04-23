AI SEO Agency — Gap Audit vs. "Beat Outrank" Mandate                                                        
                                                                                                              
  Scored against your three requirements: (1) not fluffy, (2) real backlink + distribution, (3) one powerful  
  audit engine aligned with current Google algos (H1/H2/headings + JSON-LD schema).                           
                                                                                                              
  ---                                                                                                       
  The core problem: why it "felt like fluff"                                                                  
                                                                                                              
  Your repo is 95% prompt scaffolding, 5% execution. 28 markdown files describe what agents should do. Only 2 
  Python files actually do anything — and one of them (seo_full_pipeline.py) depends on agentflow, which isn't
   a real library in this repo.                                                                             
                                                                                                              
  ┌─────────────────┬─────────────────────────────────────┬──────────────────────────────────────────────┐    
  │      Layer      │             What exists             │                What's missing                │
  ├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤    
  │ Agent role      │ 12 × .md (well-written)             │ —                                            │  
  │ cards           │                                     │                                              │
  ├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤    
  │ Skill playbooks │ 8 × .md (checklists)                │ —                                            │    
  ├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤    
  │ Workflow        │ 7 × .md (pipelines on paper)        │ No runner that executes them                 │    
  │ diagrams        │                                     │                                              │  
  ├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤    
  │ Actual tools    │ tools/seo_mcp_server.py (6 MCP      │ See gaps below                               │  
  │                 │ tools)                              │                                              │    
  ├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤  
  │ Pipeline runner │ pipelines/seo_full_pipeline.py      │ Imports agentflow — not installed; file is   │    
  │                 │                                     │ dead code                                    │  
  ├─────────────────┼─────────────────────────────────────┼──────────────────────────────────────────────┤
  │ Output          │ Templated markdown reports          │ No scored, quantified deliverable            │
  │ artifacts       │                                     │                                              │    
  └─────────────────┴─────────────────────────────────────┴──────────────────────────────────────────────┘
                                                                                                              
  When the client got a "fluffy" deliverable, it's because the agents had no data to ground their claims — the
   MCP server exposes 6 tools, but most runs fall back to "base analysis on industry benchmarks" (see
  pipelines/seo_full_pipeline.py:97-99). That's the definition of fluff.                                      
                                                                                                            
  ---
  Gap 1 — The audit engine is undersized for "beat Outrank"
                                                                                                              
  What tools/seo_mcp_server.py has (472 lines, 6 tools):
  1. gsc_search_analytics — GSC queries                                                                       
  2. gsc_index_coverage — sitemap list only (not real coverage)                                             
  3. pagespeed_analyze — Lighthouse via PSI                                                                   
  4. validate_schema — regex-extracts JSON-LD, validates it parses (does NOT validate against schema.org spec 
  or Rich Results requirements)                                                                               
  5. analyze_robots_txt — parser                                                                              
  6. parse_sitemap — parser                                                                                   
  7. analyze_headers — HTTP headers                                                                           
                  
  What's missing to beat Outrank and match 2026 Google algos:                                                 
                  
  A. Heading & semantic HTML audit (you explicitly named this)                                                
                  
  - No H1/H2/H3 hierarchy extractor                                                                           
  - No detection of multiple H1s, skipped heading levels, empty headings
  - No semantic-HTML audit (<article>, <main>, <nav>, <section>)                                              
  - No ARIA/accessibility signals (now a weak ranking signal via Page Experience)                             
                                                                                                              
  B. Schema / JSON-LD deep validation (you explicitly named this)                                             
                                                                                                              
  - Current validator only checks "is this valid JSON?" — it does NOT:                                        
    - Validate against schema.org type definitions (required vs. recommended properties)
    - Check Rich Results eligibility per type (Article needs author.name, datePublished, image; Product needs 
  offers.price, availability)                                                                                 
    - Detect misleading markup (schema claims not visible on page — a manual action trigger)                  
    - Cross-reference visible content to JSON-LD (author in schema must exist in DOM)                         
    - Validate BreadcrumbList matches URL path                                                                
  - No microdata or RDFa extraction (sites still use these)                                                   
  - No @graph composition helper (how to connect Organization + WebPage + Article + BreadcrumbList in one     
  script)                                                                                                     
                                                                                                              
  C. Google 2024–2026 algorithm alignment — completely absent                                                 
                  
  - Helpful Content System signals: first-person experience markers, author bylines with credentials, date    
  freshness, originality — no scorer
  - E-E-A-T scoring: no author schema check, no credential detection, no off-site entity verification         
  - SpamBrain / Link Spam Update: toxic-link scoring exists on paper (skills/backlink-analysis.md) but no     
  implementation                                                                                              
  - SGE / AI Overviews readiness: no extractive-snippet audit, no question-answering structure detection, no  
  passage-ranking fitness score                                                                               
  - Core Web Vitals with INP (March 2024 change): pagespeed_analyze returns INP but doesn't flag that 200ms is
   the new threshold                                                                                          
  - Crawl budget diagnosis from logs: not implemented
  - Rendered-HTML vs source-HTML diff (JS-rendering audit): not implemented — critical for Next.js/React sites
                                                                                                              
  D. Content quality engine                                                                                   
                                                                                                              
  - No readability scoring (Flesch, Gunning Fog)                                                              
  - No keyword density / TF-IDF / BM25 against SERP top-10
  - No NLP entity extraction (Google uses entities, not keywords)                                             
  - No topical authority graph                                                                                
  - No duplicate/cannibalization detector (said to exist in content-strategist.md, no code)                   
  - No thin-content detector (word count + unique-content ratio)                                              
                                                                                                              
  E. SERP + competitor intelligence                                                                           
                                                                                                              
  - Zero SERP scraping (no fallback when GSC absent)                                                          
  - No SERP-feature detection (featured snippets, People Also Ask, Knowledge Panel, Video carousel, Local
  Pack)                                                                                                       
  - No competitor content extraction for gap analysis
  - competitive-intel.md agent has no backing tool                                                            
                                                                                                              
  ---                                                                                                         
  Gap 2 — Backlink strategy is a PDF of a strategy                                                            
                                                                                                              
  skills/backlink-analysis.md and agents/link-building.md are solid templates. But there is zero backlink data
   pipeline:                                                                                                  
                  
  - No Ahrefs / Majestic / Moz / DataForSEO / Serpstat API integration (even free tiers)                      
  - No OpenLinkProfiler / CommonCrawl fallback
  - No GSC Links report fetcher (Google exposes this free)                                                    
  - No link-gap computation (you literally cannot fill the competitor-gap table in backlink-analysis.md:82-84 
  — no code produces those rows)                                                                              
  - No disavow-file generator                                                                                 
  - No broken-link-building automation (crawl competitor → find 404s → prospect)                              
  - No unlinked-brand-mention finder (needs SERP + mention API)                                               
  - No HARO / Qwoted / Featured.com queue                                                                     
  - No outreach-tracking DB (prospects, sent/opened/replied, won)                                             
                                                                                                              
  Outrank's angle is a "backlink exchange network." That's cheap and violates Google's link spam policy       
  (reciprocal link schemes). You can beat it honestly with:                                                   
  1. Data-backed digital PR (novel data studies → journalist outreach)                                        
  2. Broken-link reclamation at scale (crawlers find dead competitor links)                                   
  3. Unlinked mention reclamation (Google alerts + mention.com-style API)  
                                                                                                              
  None of those are wired up.                                                                                 
                                                                                                              
  ---                                                                                                         
  Gap 3 — Distribution is named but not built
                                                                                                              
  state/ledger.md:38 lists "Phase 15: Distribution" as pending. There is:
  - No RSS → LinkedIn/X/Medium syndication worker                                                             
  - No canonical-tag-aware republisher (republish to Medium with rel=canonical back)                          
  - No schema-enhanced social embeds (OpenGraph + Twitter Card + oEmbed)                                      
  - No newsletter fanout (Substack API / Buttondown / Beehiiv / ConvertKit)                                   
  - No IndexNow / Google Indexing API submitter (missed free traffic accelerator)                             
  - No AI-surface distribution: Perplexity Pages, Reddit, Quora, YouTube chapter markup, podcast RSS with     
  schema                                                                                                      
                                                                                                              
  ---                                                                                                         
  Gap 4 — Architecture fragility                                                                              
                                                                                                              
  - Dead pipeline: pipelines/seo_full_pipeline.py imports from agentflow import Graph, opencode, merge — not
  in any requirements file, not installed. The "parallel swarm" literally doesn't run.                        
  - No CI / test suite: no pytest, no fixtures, no way to verify the MCP tools don't regress.
  - No output schema: audit deliverables are markdown-with-severity-emoji. A client dashboard or programmatic 
  consumer can't parse them. Need a JSON contract per deliverable type.                                       
  - State ledger is manual: state/ledger.md is edited by the LLM — no validator, easy to drift.               
  - QA gate is advisory: qa-validator.md describes a 1–10 rubric, but there's no scorer that enforces "score <
   7 = reject."                                                                                               
  - No observability: no run IDs, no cost tracking, no latency budget per agent call.                         
                                                                                                              
  ---             
  Gap 5 — What Outrank offers that you don't (positioning)                                                    
                                                                                                              
  ┌────────────────────────────────────────────────────────┬─────────────────────────┬────────────────────┐
  │                    Outrank feature                     │       Your system       │       Delta        │   
  ├────────────────────────────────────────────────────────┼─────────────────────────┼────────────────────┤
  │ Auto-publishes 30 articles/mo to                       │ Content briefs only, no │ Missing entire     │   
  │ WP/Webflow/Shopify/Ghost/Notion                        │  publishing             │ publishing layer   │
  ├────────────────────────────────────────────────────────┼─────────────────────────┼────────────────────┤   
  │ 150+ languages                                         │ Not handled             │ Missing i18n       │
  ├────────────────────────────────────────────────────────┼─────────────────────────┼────────────────────┤   
  │ On-brand AI images                                     │ No image generation     │ Missing            │
  ├────────────────────────────────────────────────────────┼─────────────────────────┼────────────────────┤   
  │ WordPress/Webflow/Shopify/Ghost/Framer/Wix/Notion      │ None                    │ Missing            │
  │ integrations                                           │                         │                    │   
  ├────────────────────────────────────────────────────────┼─────────────────────────┼────────────────────┤
  │ 30-day content roadmap auto-gen                        │ Manual template in      │ Partial            │   
  │                                                        │ content-brief.md        │                    │   
  ├────────────────────────────────────────────────────────┼─────────────────────────┼────────────────────┤
  │ "$99/mo, one plan"                                     │ N/A (agency model)      │ Positioning choice │   
  └────────────────────────────────────────────────────────┴─────────────────────────┴────────────────────┘   
   
  To beat Outrank, you don't need to copy auto-publish 30 articles/mo — that's commoditized and risks Helpful 
  Content penalties. You beat it by being the "audit + strategy + distribution engine that publishes fewer, 
  higher-ranking assets and earns real links."                                                                
                  
  ---
  Recommended rebuild priorities (ranked by ROI)
                                                                                                              
  P0 — Rip out fluff, make the audit engine real
                                                                                                              
  1. Kill pipelines/seo_full_pipeline.py or rewrite against real runner (asyncio + the existing MCP tools) —  
  it's misleading dead code.                                                                                  
  2. Ship a tools/audit_engine.py that wraps 1 CLI command: audit <domain> → produces a JSON artifact with    
  scored sections. This is your moat.                                                                         
  3. Add to MCP server: heading-hierarchy extractor, semantic-HTML auditor, JSON-LD type-aware validator
  (per-type required-property check), rendered-vs-source HTML diff (Playwright), content quality scorer       
  (readability + word count + entity extraction via spaCy), SERP scraper fallback (SerpApi or headless).
                                                                                                              
  P1 — Google-algo alignment layer                                                                            
   
  4. Add a skills/algo-signals.md mapping each known 2023–2026 Google update (Helpful Content, SpamBrain,     
  Reviews, Product Reviews, Core, SGE/AIO) to concrete on-page signals, with a scorer per signal.
  5. Wire E-E-A-T scorer: author schema presence + bylines + author bio depth + external author verification  
  (sameAs).                                                                                                   
  6. Wire INP/CWV thresholds to real pass/fail gates, not raw numbers.
                                                                                                              
  P1 — Real backlink pipeline                                                                                 
                                                                                                              
  7. Pick one data source (DataForSEO is cheapest API; GSC Links is free) and wire a tools/backlink_fetch.py  
  that actually fills the templates in skills/backlink-analysis.md.
  8. Build link-gap computer: diff (our RDs) vs (competitor RDs) → prospect list with relevance score.        
  9. Build outreach tracker: SQLite DB + CLI (prospect add, prospect outreach-sent, prospect won).            
                                                                                                              
  P2 — Distribution engine                                                                                    
                                                                                                              
  10. IndexNow + Indexing API submitters (free, fast win on indexation speed).                                
  11. Canonical-aware syndication worker to Medium/dev.to/LinkedIn/Substack — publish once, syndicate with
  rel=canonical.                                                                                              
  12. AI-surface submitter: Perplexity Pages, Reddit/Quora answer generator with source attribution.
                                                                                                              
  P2 — Publishing integrations (to match Outrank's stickiness)                                                
                                                                                                              
  13. WordPress REST API, Ghost Admin API, Webflow CMS API, Notion API publish adapters. One each; keep it 100
   LOC per adapter.
                                                                                                              
  P3 — Ops hardening

  14. JSON output contract per deliverable type; emit markdown from JSON (one-way).                           
  15. qa-validator as actual scorer (Python, not prompt) that blocks deliverables <7.
  16. pytest suite on the MCP tools with fixture HTML files.                                                  
  17. Run metadata (run_id, cost, duration) in every output.                                                  
                                                                                                              
  ---                                                                                                         
  Positioning to actually beat Outrank
                                                                                                              
  Outrank = "AI writes and publishes content for you."
  You = "AI audits your site against the current Google algorithm, earns real links, and distributes one great
   asset across 10 surfaces — then proves it with data."                                                      
   
  The three headlines that follow from the gaps above:                                                        
  1. "One Audit Engine, Every Google Update" — version your audit rubric with each algo update; show which
  signals you check that competitors don't.                                                                   
  2. "Real Backlinks, Not Reciprocal Schemes" — position Outrank's exchange network as a Google-policy risk;
  publish your clean-link methodology.                                                                        
  3. "Publish Once, Rank Everywhere" — canonical-aware syndication + IndexNow + AI-surface submission; 10x the
   distribution per asset.
