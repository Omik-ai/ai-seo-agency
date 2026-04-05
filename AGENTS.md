# SEO Agency — Agent Index

> Universal reference file for any AI CLI tool. Read this to understand the complete agent roster.

## Agent Roster

### Strategic Layer
| Agent | File | Role | Deploys When |
|-------|------|------|-------------|
| SEO Strategist | `agents/seo-strategist.md` | High-level strategy, roadmaps, prioritization | Strategy development, business alignment, major decisions |
| Client Manager | `agents/client-manager.md` | Client communication, reporting, relationship management | Reports, presentations, client comms |
| Competitive Intel | `agents/competitive-intel.md` | Competitor analysis, market intelligence | Competitive research, strategy validation |

### Technical Layer
| Agent | File | Role | Deploys When |
|-------|------|------|-------------|
| Technical SEO | `agents/technical-seo.md` | Site crawl, speed, indexing, schema, architecture | Technical audits, site fixes, schema implementation |
| Analytics | `agents/analytics.md` | GA4, GSC, rank tracking, data analysis | Performance reporting, traffic diagnosis, data requests |
| E-commerce SEO | `agents/ecommerce-seo.md` | Product pages, categories, faceted nav, product schema | Online store SEO, product optimization |

### Content Layer
| Agent | File | Role | Deploys When |
|-------|------|------|-------------|
| Content Strategist | `agents/content-strategist.md` | Topic clusters, content calendars, content briefs | Content planning, editorial strategy |
| Keyword Research | `agents/keyword-research.md` | Keyword discovery, intent mapping, gap analysis | Keyword research, opportunity finding |
| On-Page SEO | `agents/on-page-seo.md` | Meta tags, headings, internal links, NLP optimization | Page-level optimization, content optimization |

### Growth Layer
| Agent | File | Role | Deploys When |
|-------|------|------|-------------|
| Link Building | `agents/link-building.md` | Outreach, digital PR, link prospecting | Link campaigns, backlink audits |
| Local SEO | `agents/local-seo.md` | GBP, citations, local link building | Local business optimization |

### Quality Layer
| Agent | File | Role | Deploys When |
|-------|------|------|-------------|
| QA Validator | `agents/qa-validator.md` | Reviews all outputs for quality, accuracy, completeness | Before any deliverable is sent to client |

## Inter-Agent Communication

Agents communicate through structured handoffs. Each agent definition includes:
- **Input Contract** — What data the agent needs to start
- **Output Contract** — What the agent produces
- **Handoff Triggers** — When to pass work to another agent

## Swarm Configurations

### Full Audit Swarm
Deploy ALL technical + content agents in parallel:
`technical-seo` + `analytics` + `on-page-seo` + `content-strategist` + `keyword-research`

### Content Campaign Swarm
Sequential pipeline: `keyword-research` → `content-strategist` → `on-page-seo` → `link-building`

### Competitive Deep Dive Swarm
Parallel + adversarial: `competitive-intel` + `keyword-research` + `content-strategist` + `link-building` + `technical-seo`

### Client Onboarding Swarm
Full agency activation — see `workflows/client-onboarding.md`
