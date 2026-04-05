# SEO Agency Orchestrator — Quickstart Guide

## What Is This?

A **file-based AI SEO Agency** that works with ANY AI coding CLI tool. The "intelligence" lives in the files — any AI assistant that reads them instantly understands how to operate as a full-service SEO agency with 10+ specialist agents.

## Compatible CLI Tools

| Tool | Config File | How It Loads |
|------|-------------|-------------|
| **Claude Code** | `CLAUDE.md` + `.claude/agents/` | Auto-loaded on session start |
| **Cursor** | `.cursorrules` | Auto-loaded on session start |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Auto-loaded on session start |
| **Aider** | Read `CLAUDE.md` manually | `/read CLAUDE.md` |
| **OpenCode** | Read `CLAUDE.md` manually | Load as context |
| **Any other tool** | Read `CLAUDE.md` manually | Paste or load as context |

## Quick Start (30 seconds)

### With Claude Code
```bash
cd "bonsai testing"
claude
# Just start talking — CLAUDE.md is auto-loaded
> "Audit example.com for technical SEO issues"
```

### With Cursor
Open the project folder in Cursor. The `.cursorrules` file is auto-loaded.

### With Any Other Tool
Tell it to read CLAUDE.md first:
```
Read CLAUDE.md and follow the Master Orchestrator instructions.
Then audit example.com for technical SEO issues.
```

## Example Prompts

### Single Agent Tasks
```
"Research keywords for a SaaS project management tool"
→ Deploys: keyword-research agent

"Check if example.com has proper schema markup"
→ Deploys: technical-seo agent

"Write a content brief for 'best project management software'"
→ Deploys: content-strategist agent

"Analyze our backlink profile vs competitor.com"
→ Deploys: link-building agent

"Optimize our homepage for 'project management software'"
→ Deploys: on-page-seo agent
```

### Multi-Agent Workflows
```
"Do a full site audit of example.com"
→ Runs: workflows/site-audit.md (parallel swarm)

"Onboard a new client: example.com, they sell shoes online"
→ Runs: workflows/client-onboarding.md (full agency activation)

"Create a content strategy for our blog"
→ Runs: workflows/content-pipeline.md (sequential pipeline)

"We need to build links to our new guide"
→ Runs: workflows/link-building-campaign.md (hierarchical delegation)

"Prepare the monthly SEO report"
→ Runs: workflows/reporting.md (parallel collection → synthesis)

"How do we compare to competitor.com?"
→ Runs: workflows/competitive-analysis.md (parallel + adversarial)
```

### Advanced: Agent Team (Claude Code only)
```
"Create an agent team with 4 agents to audit example.com:
- technical-seo specialist
- content-strategist
- keyword-research analyst
- link-building specialist
Have them work in parallel and report back."
```

## File Structure

```
.
├── CLAUDE.md                      ← Master brain (read first)
├── AGENTS.md                      ← Agent index (universal reference)
├── QUICKSTART.md                  ← You are here
├── .cursorrules                   ← Cursor compatibility
├── .github/
│   └── copilot-instructions.md    ← GitHub Copilot compatibility
├── .claude/
│   └── agents/                    ← Claude Code native agents
│       ├── seo-strategist.md
│       ├── technical-seo.md
│       ├── content-strategist.md
│       ├── keyword-research.md
│       ├── link-building.md
│       └── analytics.md
├── agents/                        ← Full agent definitions
│   ├── seo-strategist.md
│   ├── technical-seo.md
│   ├── content-strategist.md
│   ├── keyword-research.md
│   ├── on-page-seo.md
│   ├── link-building.md
│   ├── analytics.md
│   ├── local-seo.md
│   ├── competitive-intel.md
│   ├── ecommerce-seo.md
│   └── client-manager.md
├── workflows/                     ← Multi-agent pipelines
│   ├── client-onboarding.md
│   ├── site-audit.md
│   ├── content-pipeline.md
│   ├── link-building-campaign.md
│   ├── reporting.md
│   └── competitive-analysis.md
├── skills/                        ← Reusable methodology modules
│   ├── keyword-research.md
│   ├── technical-audit.md
│   ├── content-brief.md
│   ├── backlink-analysis.md
│   ├── schema-markup.md
│   ├── competitor-analysis.md
│   ├── rank-tracking.md
│   └── page-optimization.md
└── data/                          ← Working data (created during use)
    ├── clients/
    ├── audits/
    ├── reports/
    ├── research/
    └── content/
```

## Orchestration Patterns

### 1. Single Agent
One specialist handles the full task.
```
User → Orchestrator → [Agent] → Output
```

### 2. Parallel Swarm
Multiple agents work simultaneously on independent subtasks.
```
User → Orchestrator ──┬── [Agent A] ──┐
                      ├── [Agent B] ──┤── Orchestrator merges → Output
                      └── [Agent C] ──┘
```

### 3. Sequential Pipeline
Each agent's output feeds the next.
```
User → [Agent A] → [Agent B] → [Agent C] → Output
```

### 4. Hierarchical Delegation
A manager agent coordinates sub-agents.
```
User → [Manager Agent]
           ├── [Worker A]
           ├── [Worker B]
           └── [Worker C]
```

### 5. Adversarial/Debate
Agents challenge each other to validate findings.
```
[Agent A proposes] → [Agent B critiques] → [Agent C synthesizes]
```

## Customization

### Add a New Agent
1. Create `agents/your-agent.md` following the existing pattern
2. Add to the Agent Registry in `CLAUDE.md`
3. Optionally create `.claude/agents/your-agent.md` for Claude Code native support

### Add a New Workflow
1. Create `workflows/your-workflow.md` following the existing pattern
2. Add to the Quick Command Reference in `CLAUDE.md`

### Add a New Skill
1. Create `skills/your-skill.md` following the existing pattern
2. Add to the Skills Library in `CLAUDE.md`
