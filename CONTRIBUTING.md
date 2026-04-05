# Contributing to AI SEO Agency

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## How to Contribute

### Reporting Bugs

1. **Search existing issues** — Avoid duplicates
2. **Use the bug template** — Provide all requested information
3. **Be specific** — Include reproduction steps, expected vs actual behavior
4. **Include context** — OS, browser, AI tool version, etc.

### Suggesting Features

1. **Check the roadmap** — See if it's already planned
2. **Open a discussion** — Gauge interest before writing code
3. **Use the feature template** — Explain the use case clearly
4. **Be open to feedback** — The maintainers may have suggestions

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-new-feature`
3. **Make your changes** — Follow the coding standards
4. **Write tests** — If applicable
5. **Update documentation** — Keep docs in sync with code
6. **Submit a PR** — Fill out the PR template completely

## Development Setup

### Prerequisites

- Git
- An AI CLI tool (Claude Code, Cursor, Aider, etc.)
- Python 3.9+ (for MCP tools)

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-seo-agency.git
cd ai-seo-agency

# Install Python dependencies (if needed)
pip install -r requirements.txt

# Test your setup
claude  # or your preferred AI tool
> "Run a test site audit on example.com"
```

## Adding New Agents

### Step 1: Create the Agent Definition

Create `agents/your-agent-name.md`:

```markdown
# Agent: [Agent Name]

## Role
[One sentence describing the role]

## Capabilities
- [Capability 1]
- [Capability 2]

## Tools
- [Tool/API 1]
- [Tool/API 2]

## Input Contract
[What data the agent needs to start]

## Output Contract
[What the agent produces]

## Handoff Rules
[When to pass work to another agent]
```

### Step 2: Add to Agent Index

Update `AGENTS.md` with the new agent in the appropriate layer.

### Step 3: Update Master Registry

Add to the agent registry in `CLAUDE.md`.

### Step 4 (Optional): Claude Code Native

If supporting Claude Code, also create `.claude/agents/your-agent-name.md`.

## Adding New Workflows

### Step 1: Create the Workflow

Create `workflows/your-workflow.md`:

```markdown
# Workflow: [Workflow Name]

**Type**: [Parallel Swarm | Sequential Pipeline | Hierarchical]
**Duration**: [estimated time]
**Agents**: [list of agents]

## Overview
[What this workflow accomplishes]

## Pipeline
[Visual or text representation of the flow]

## Agent Instructions
### [agent-1]
[Instructions for agent 1]

### [agent-2]
[Instructions for agent 2]

## Merge & Synthesis
[How outputs are combined]
```

### Step 2: Add to Quick Reference

Add to the Quick Command Reference in `CLAUDE.md`.

## Coding Standards

### File Organization

- Use lowercase with dashes for file names: `my-agent.md`
- Group related files in directories: `agents/`, `workflows/`, `skills/`
- Keep files focused: One agent = one file

### Markdown Formatting

- Use ATX-style headers: `## Header` not `Header`
- Use tables for structured data
- Use fenced code blocks with language hints
- Keep lines under 120 characters when possible

### Documentation

- Write clear, concise documentation
- Include examples where helpful
- Keep documentation in sync with code
- Use consistent terminology

## Commit Messages

Follow conventional commits:

```
feat: add new agent for local SEO
fix: resolve agent handoff timing issue
docs: update QUICKSTART.md with new example
refactor: simplify workflow merge logic
test: add unit tests for state management
```

## PR Guidelines

### PR Title

Use conventional commit format:
- `feat: description`
- `fix: description`
- `docs: description`
- `refactor: description`
- `test: description`

### PR Description

- Link to related issues
- Explain what changed and why
- List breaking changes if any
- Provide testing instructions

### Review Criteria

- [ ] Code follows the style guide
- [ ] Tests pass (if applicable)
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)

## Recognition

Contributors will be listed in README.md and CHANGELOG.md.

## Questions?

- Open a discussion for general questions
- Open an issue for bugs or feature requests
- Tag maintainers for urgent matters

---

**Thank you for contributing!**
