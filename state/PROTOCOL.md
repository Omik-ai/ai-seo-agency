# State Management Protocol

This document defines how agents track tasks, pass context, and maintain state across the agency. All agents and the orchestrator MUST follow this protocol.

## Overview

```
state/
├── PROTOCOL.md          ← You are here (rules)
├── ledger.md            ← Master ledger (orchestrator maintains)
├── tasks/               ← Individual task files
│   ├── TASK-001.md
│   ├── TASK-002.md
│   └── ...
└── handoffs/            ← Agent-to-agent handoff records
    ├── HO-001.md
    └── ...
```

## The Ledger (MagenticOne Pattern)

The orchestrator maintains `state/ledger.md` as a living document. It is updated after EVERY significant action.

```markdown
# Agency Ledger

## Current Client
- Name: [client name]
- Domain: [URL]
- Goals: [business objectives]
- Started: [date]

## Facts Established
[Verified facts from agent outputs — things we KNOW to be true]
- [fact 1 — source: agent-name, task-id]
- [fact 2 — source: agent-name, task-id]

## Current Plan
1. [x] [completed step] — TASK-001 (agent: technical-seo)
2. [ ] [current step] — TASK-002 (agent: content-strategist) ← IN PROGRESS
3. [ ] [next step] — TASK-003 (agent: link-building)

## Active Agents
| Agent | Task | Status | Since |
|-------|------|--------|-------|
| content-strategist | TASK-002 | working | 2026-04-04 |

## Blocked Items
[Tasks that cannot proceed and why]

## Decisions Made
- [date] [decision] — rationale: [why]

## Open Questions
- [question for client/user]

## Quality Gates Pending
- [deliverable awaiting QA review]

## Last Updated
[timestamp] by [agent/orchestrator]
```

## Task Protocol

Every task is a markdown file in `state/tasks/` with a standardized format.

### Task File Format: `TASK-{NNN}.md`

```markdown
# TASK-{NNN}: [Short descriptive title]

## Metadata
- **ID**: TASK-{NNN}
- **Created**: [ISO 8601 timestamp]
- **Created By**: [orchestrator | agent-name]
- **Assigned To**: [agent-name]
- **Status**: pending | in_progress | blocked | review | completed | failed
- **Priority**: P0 | P1 | P2 | P3
- **Depends On**: [TASK-IDs this task waits for]
- **Blocks**: [TASK-IDs that wait for this task]
- **Workflow**: [workflow file if part of a workflow]
- **Phase**: [workflow phase if applicable]

## Objective
[Clear statement of what this task must accomplish]

## Context
[Background information the assigned agent needs]
- Previous findings: [reference to prior task outputs]
- Client requirements: [relevant constraints]
- Data available: [what data/access exists]

## Acceptance Criteria
- [ ] [Specific, measurable criterion 1]
- [ ] [Specific, measurable criterion 2]
- [ ] [Specific, measurable criterion 3]

## Input
[Files, data, or references the agent should read]
- [file path or reference]

## Expected Output
- **Format**: [deliverable format per CLAUDE.md]
- **Location**: data/[path where output should be written]
- **Handoff To**: [next agent in pipeline, if any]

## Execution Log
### [timestamp] — Status: in_progress
[Agent notes on approach]

### [timestamp] — Status: completed
[Summary of what was done, output location]

## Output Reference
- Deliverable: [path to output file]
- QA Review: [path to QA review, if reviewed]
```

### Task Status Lifecycle

```
pending → in_progress → review → completed
                ↓           ↓
             blocked      failed
                ↓
          (unblocked) → in_progress
```

- **pending**: Created, waiting to be picked up
- **in_progress**: Agent is actively working on it
- **blocked**: Cannot proceed (dependency unmet, data missing, question unanswered)
- **review**: Work done, awaiting QA validation
- **completed**: QA approved, deliverable accepted
- **failed**: Could not complete (with reason documented)

### Task ID Convention
- `TASK-001` through `TASK-999` — standard sequential numbering
- Prefix with workflow code for workflow tasks: `ONB-001` (onboarding), `AUD-001` (audit), `CON-001` (content), `LNK-001` (link building), `RPT-001` (reporting), `CMP-001` (competitive)

## Handoff Protocol

When one agent passes work to another, create a handoff record in `state/handoffs/`.

### Handoff File Format: `HO-{NNN}.md`

```markdown
# Handoff HO-{NNN}

## Routing
- **From**: [agent-name]
- **To**: [agent-name]
- **Task**: [TASK-ID]
- **Date**: [timestamp]
- **Type**: result | delegation | escalation | feedback

## Context Transfer
### What Was Done
[Summary of completed work]

### Key Findings
[Critical information the receiving agent needs]
- [finding 1]
- [finding 2]

### Data Produced
[Files/outputs created]
- [path to file]

### What Needs To Happen Next
[Clear instructions for receiving agent]

### Constraints & Warnings
[Anything the receiving agent should watch out for]

### Open Questions
[Unresolved issues that may affect the next agent's work]
```

### Handoff Types

| Type | When | Example |
|------|------|---------|
| **result** | Agent completed task, passing output to next in pipeline | keyword-research → content-strategist |
| **delegation** | Orchestrator assigns work to an agent | orchestrator → technical-seo |
| **escalation** | Agent encounters issue beyond its scope | on-page-seo → seo-strategist |
| **feedback** | QA sends revision instructions back | qa-validator → content-strategist |

## Shared Context Rules

1. **Never overwrite another agent's output** — create new files, reference previous ones
2. **Always cite your sources** — reference task IDs and file paths, not vague "previous analysis"
3. **Update the ledger** — after completing a task, update `state/ledger.md` with new facts and plan progress
4. **Explicit > implicit** — write everything down; assume the next agent has zero context from prior conversation
5. **Files are the message bus** — all inter-agent communication happens through files, never through assumptions

## Recovery Protocol

If a task fails or the session is interrupted:

1. Read `state/ledger.md` to understand current state
2. Check `state/tasks/` for task statuses
3. Resume from the last `in_progress` or `pending` task
4. The ledger's "Facts Established" section preserves all prior findings

This makes the system **resumable** — any new AI session can pick up exactly where the last one left off.
