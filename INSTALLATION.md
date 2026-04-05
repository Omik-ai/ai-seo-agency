# Installation Guide

This guide provides detailed setup instructions for AI SEO Agency.

## Prerequisites

### Required

- **Git** — Version 2.30 or higher
- **An AI CLI Tool** — One of the supported tools listed below

### Optional (for MCP tools)

- **Python** — Version 3.9 or higher
- **pip** — Python package manager

## Supported AI Tools

| Tool | Installation | Documentation |
|------|--------------|---------------|
| Claude Code | `npm install -g @anthropic-ai/claude-code` | [claude.ai/cli](https://claude.ai/cli) |
| Cursor | Download from [cursor.sh](https://cursor.sh) | [docs.cursor.sh](https://docs.cursor.sh) |
| GitHub Copilot | `gh extension install github/copilot` | [docs.github.com/copilot](https://docs.github.com/en/copilot) |
| Aider | `pip install aider` | [aider.chat](https://aider.chat) |
| OpenCode | Follow [opencode.ai](https://opencode.ai) | [docs.opencode.ai](https://docs.opencode.ai) |

## Quick Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Omik-ai/ai-seo-agency.git
cd ai-seo-agency
```

### Step 2: Configure Your AI Tool

#### Claude Code (Recommended)

No configuration needed! `CLAUDE.md` is automatically loaded.

```bash
claude
> "Audit example.com for technical SEO"
```

#### Cursor

1. Open the project folder in Cursor
2. `.cursorrules` is automatically loaded

#### GitHub Copilot

```bash
gh copilot
> "Read CLAUDE.md and follow its instructions"
```

#### Aider

```bash
aider --init
# Or read the file manually
/read CLAUDE.md
```

#### OpenCode

```bash
opencode .
# Load CLAUDE.md as context
```

## Manual Setup (Advanced)

### Environment Variables

Create a `.env` file for API integrations:

```bash
# Google Analytics / Search Console
GA4_PROPERTY_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=

# SEO Tools (optional)
AHREFS_API_KEY=
MOZ_API_KEY=
SEMRUSH_API_KEY=

# OpenAI (for certain features)
OPENAI_API_KEY=
```

> **Important**: Never commit `.env` to version control!

### MCP Server Setup (Optional)

The project includes an MCP server for advanced SEO tools:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure MCP in your tool
# See tools/mcp-config.json for configuration
```

## Project Structure Explained

```
ai-seo-agency/
├── CLAUDE.md              # Master orchestrator (required reading)
├── AGENTS.md              # Agent index
├── QUICKSTART.md          # 30-second guide
│
├── .claude/               # Claude Code native agents
│   └── agents/
│
├── agents/                # Full agent definitions
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
│
├── workflows/             # Multi-agent pipelines
│   ├── site-audit.md
│   ├── client-onboarding.md
│   ├── content-pipeline.md
│   ├── link-building-campaign.md
│   ├── reporting.md
│   └── competitive-analysis.md
│
├── skills/                # Reusable methodology modules
│   ├── keyword-research.md
│   ├── technical-audit.md
│   ├── content-brief.md
│   ├── backlink-analysis.md
│   ├── schema-markup.md
│   ├── competitor-analysis.md
│   ├── rank-tracking.md
│   └── page-optimization.md
│
├── state/                 # Task & state management
│   ├── PROTOCOL.md
│   ├── ledger.md
│   ├── tasks/
│   └── handoffs/
│
├── tools/                 # MCP servers & utilities
│   ├── seo_mcp_server.py
│   └── mcp-config.json
│
├── examples/              # Sample outputs
│   ├── sample-technical-audit.md
│   ├── sample-keyword-research.md
│   ├── sample-content-brief.md
│   └── sample-qa-review.md
│
└── data/                  # Working data (created at runtime)
    ├── clients/
    ├── audits/
    ├── reports/
    ├── research/
    └── content/
```

## Verifying Your Setup

### Test 1: Basic Functionality

```bash
# In your AI tool
> "What agents are available?"
```

Expected: The AI should list all available agents from AGENTS.md

### Test 2: Run a Simple Task

```bash
> "Research keywords for: small business accounting software"
```

Expected: The AI should deploy the keyword-research agent and produce keyword suggestions

### Test 3: Run a Workflow

```bash
> "What does the site-audit workflow do?"
```

Expected: The AI should explain the site-audit workflow steps

## Troubleshooting

### AI Tool Not Recognizing Files

If your AI tool doesn't automatically load the configuration files:

1. **Check file location** — Files must be in project root
2. **Check file names** — Must match exactly (CLAUDE.md, not Claude.md)
3. **Try manual load** — Tell the tool to read the files explicitly

### Agents Not Working

If agents aren't behaving correctly:

1. **Verify CLAUDE.md is loaded** — The AI should mention the orchestrator
2. **Check agent files exist** — `agents/` directory should have all agents
3. **Review agent definition** — Each agent file has specific structure

### State Not Persisting

If task state isn't being saved:

1. **Check write permissions** — `data/` directory must be writable
2. **Verify git is initialized** — State files should be tracked
3. **Check file paths** — State files use relative paths from project root

## Next Steps

Once setup is complete:

1. Read [QUICKSTART.md](QUICKSTART.md) for 30-second overview
2. Review [CLAUDE.md](CLAUDE.md) for master orchestrator instructions
3. Explore [AGENTS.md](AGENTS.md) to understand available agents
4. Try a sample task like "Audit example.com"

---

**Need help?** Open an issue on GitHub or start a discussion.
