<!-- markdownlint-disable MD033 -->
<h1 align="center">
  <img src="https://img.shields.io/badge/🤖-AI%20SEO%20Agency-blue?style=for-the-badge" alt="AI SEO Agency">
</h1>

<p align="center">
  <a href="https://github.com/Omik-ai/ai-seo-agency/stargazers">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/Omik-ai/ai-seo-agency">
  </a>
  <a href="https://github.com/Omik-ai/ai-seo-agency/issues">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues/Omik-ai/ai-seo-agency">
  </a>
  <a href="https://github.com/Omik-ai/ai-seo-agency/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/Omik-ai/ai-seo-agency">
  </a>
  <a href="https://twitter.com/intent/follow?screen_name=omik_ai">
    <img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/omik_ai">
  </a>
</p>

<p align="center">
  <strong>A file-based multi-agent SEO orchestration system</strong><br>
  Works with Claude Code, Cursor, GitHub Copilot, OpenCode, Aider, and any AI CLI tool
</p>

---

## What Is This?

AI SEO Agency is a **file-based multi-agent orchestration system** that transforms any AI coding CLI tool into a full-service SEO agency. The "intelligence" lives in the files — no APIs, no servers, no vendor lock-in.

### Key Features

- **10+ Specialized AI Agents** — Each agent is an expert in a specific SEO domain
- **Multi-Agent Swarms** — Deploy parallel, sequential, or hierarchical agent teams
- **Tool-Agnostic** — Works with Claude Code, Cursor, Copilot, Aider, OpenCode, etc.
- **Stateful Execution** — Resumable tasks with full audit trails
- **Enterprise-Ready** — Quality gates, human-in-the-loop approvals, audit trails

### Use Cases

- Comprehensive site audits
- Keyword research and content strategy
- Technical SEO analysis and fixes
- Link building campaigns
- Competitive intelligence
- Client onboarding workflows
- Monthly reporting

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Omik-ai/ai-seo-agency.git
cd ai-seo-agency
```

### 2. Choose Your AI Tool

| Tool | Command |
|------|---------|
| Claude Code | `claude` in the project directory |
| Cursor | Open project in Cursor |
| GitHub Copilot | `gh copilot` in the project |
| Aider | `aider` in the project |
| OpenCode | `opencode .` in the project |

### 3. Start an SEO Task

```bash
# Example: Run a site audit
> "Audit example.com for technical SEO issues"

# Example: Research keywords
> "Find keywords for a SaaS project management tool"

# Example: Full client onboarding
> "Onboard a new client: example.com, they sell shoes online"
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Get started in 30 seconds |
| [CLAUDE.md](CLAUDE.md) | Master orchestrator instructions |
| [AGENTS.md](AGENTS.md) | Complete agent roster |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [SECURITY.md](SECURITY.md) | Security policy |
| [INSTALLATION.md](INSTALLATION.md) | Detailed setup guide |

---

## Architecture

```
AI SEO Agency
├── Master Orchestrator (YOU)
│   ├── Strategic Layer
│   │   ├── SEO Strategist
│   │   ├── Client Manager
│   │   └── Competitive Intel
│   ├── Technical Layer
│   │   ├── Technical SEO
│   │   ├── Analytics
│   │   └── E-commerce SEO
│   ├── Content Layer
│   │   ├── Content Strategist
│   │   ├── Keyword Research
│   │   └── On-Page SEO
│   ├── Growth Layer
│   │   ├── Link Building
│   │   └── Local SEO
│   └── Quality Layer
│       └── QA Validator
```

---

## Agent Swarm Patterns

### Single Agent
Use for focused, specialist tasks:
```
User → Orchestrator → [Agent] → Output
```

### Parallel Swarm
Use for comprehensive audits:
```
User → Orchestrator ──┬── [Agent A] ──┐
                      ├── [Agent B] ──┤── Merge → Output
                      └── [Agent C] ──┘
```

### Sequential Pipeline
Use for content campaigns:
```
[Keyword Research] → [Content Strategist] → [On-Page SEO] → Output
```

---

## Project Structure

```
.
├── CLAUDE.md                      # Master orchestrator brain
├── AGENTS.md                      # Agent index
├── QUICKSTART.md                  # Quick start guide
├── README.md                      # This file
├── .claude/                       # Claude Code native agents
│   └── agents/
├── agents/                        # Full agent definitions
│   ├── seo-strategist.md
│   ├── technical-seo.md
│   ├── content-strategist.md
│   └── ...
├── workflows/                     # Multi-agent pipelines
│   ├── site-audit.md
│   ├── client-onboarding.md
│   └── ...
├── skills/                        # Reusable methodology
├── state/                        # Task & state management
├── tools/                        # MCP servers & tools
├── examples/                     # Sample outputs
└── data/                        # Working data (created at runtime)
```

---

## Compatible AI Tools

| Tool | Status | Config File |
|------|--------|-------------|
| Claude Code | ✅ Full Support | `CLAUDE.md` |
| Cursor | ✅ Full Support | `.cursorrules` |
| GitHub Copilot | ✅ Full Support | `.github/copilot-instructions.md` |
| Aider | ✅ Full Support | Read `CLAUDE.md` |
| OpenCode | ✅ Full Support | Read `CLAUDE.md` |
| Windsurf | ✅ Full Support | `.windsurfrules` |
| Any other CLI | ✅ Compatible | Read `CLAUDE.md` |

---

## Quality Assurance

Every deliverable passes through the `qa-validator` agent before reaching the client:

1. **No deliverable leaves without QA review** (except P0 emergencies)
2. QA scores on a 1-10 rubric
3. Score < 7 = revisions needed
4. Score >= 7 = approved for delivery

---

## Human-in-the-Loop Gates

Critical decisions require explicit human approval:

| Gate | When |
|------|------|
| STRATEGY_APPROVAL | Before executing any strategy |
| CONTENT_PUBLISH | Before publishing content |
| OUTREACH_SEND | Before sending outreach emails |
| CLIENT_DELIVERY | Before sending reports to client |
| TECHNICAL_DEPLOY | Before implementing site changes |

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## Support

- 📖 [Documentation](https://github.com/Omik-ai/ai-seo-agency/wiki)
- 🐛 [Issue Tracker](https://github.com/Omik-ai/ai-seo-agency/issues)
- 💬 [Discussions](https://github.com/Omik-ai/ai-seo-agency/discussions)
- 🐦 [Twitter](https://twitter.com/omik_ai)

---

<p align="center">
  <strong>Built with 🤖 by <a href="https://omik.ai">Omik.ai</a></strong>
</p>
