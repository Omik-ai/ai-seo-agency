# Human-in-the-Loop Gate Protocol

## Overview

Gates are explicit approval checkpoints in workflows where work MUST pause for human review before proceeding. This prevents costly mistakes, ensures strategic alignment, and maintains client trust.

## Gate Types

### GATE: STRATEGY_APPROVAL
**When**: Before executing any strategic plan
**Who Approves**: Client / Account Owner
**What's Reviewed**: Strategy document, roadmap, KPIs, budget allocation
**Block If Not Approved**: All execution work downstream

### GATE: CONTENT_PUBLISH
**When**: Before publishing any content to client's site
**Who Approves**: Client / Content Owner
**What's Reviewed**: Final content, meta tags, schema markup, internal links
**Block If Not Approved**: Publishing and promotion

### GATE: OUTREACH_SEND
**When**: Before sending any outreach emails on behalf of client
**Who Approves**: Client / Link Building Manager
**What's Reviewed**: Outreach templates, prospect list, messaging tone
**Block If Not Approved**: All outreach activity

### GATE: CLIENT_DELIVERY
**When**: Before sending any report or deliverable to the client
**Who Approves**: Account Manager / QA Validator
**What's Reviewed**: Report accuracy, formatting, narrative, recommendations
**Block If Not Approved**: Client communication

### GATE: TECHNICAL_DEPLOY
**When**: Before implementing any technical changes on client's site
**Who Approves**: Client / Developer / Tech Lead
**What's Reviewed**: Code changes, redirects, robots.txt changes, schema changes
**Block If Not Approved**: Technical implementation

### GATE: BUDGET_COMMIT
**When**: Before committing spend (tool purchases, paid placements, ad spend)
**Who Approves**: Client / Budget Owner
**What's Reviewed**: Cost breakdown, expected ROI, alternatives considered
**Block If Not Approved**: Any spend

### GATE: QA_REVIEW
**When**: Before any deliverable moves from "review" to "completed" status
**Who Approves**: QA Validator Agent
**What's Reviewed**: Quality score, completeness, accuracy, standard compliance
**Block If Not Approved**: Delivery to client

## Gate Implementation

### In Task Files
When a task reaches a gate, its status changes to `review` and a gate record is added:

```markdown
## Gate: [GATE_TYPE]
- **Status**: PENDING | APPROVED | REJECTED
- **Reviewer**: [who needs to approve]
- **Submitted**: [timestamp]
- **Reviewed**: [timestamp, when decided]
- **Decision**: [approved/rejected]
- **Feedback**: [if rejected, what needs to change]
```

### In the Ledger
Gates pending approval appear in the "Quality Gates Pending" section:

```markdown
## Quality Gates Pending
- GATE: STRATEGY_APPROVAL — TASK-003 strategy document awaiting client review
- GATE: QA_REVIEW — TASK-007 content brief awaiting QA validation
```

### In Workflows
Each workflow specifies which gates apply. The orchestrator MUST NOT skip gates.

## Gate Status Flow

```
Work Complete → Gate PENDING → Human Reviews
                                    ↓
                         ┌── APPROVED → Proceed to next step
                         └── REJECTED → Return to agent with feedback
                                         ↓
                                    Agent revises → Gate PENDING again
```

## Gate Application by Workflow

### Client Onboarding
| Phase | Gate | Required? |
|-------|------|-----------|
| Phase 2 → Phase 3 | QA_REVIEW (all audits) | Yes |
| Phase 3 end | STRATEGY_APPROVAL | Yes — client must approve strategy |
| Phase 4 end | CLIENT_DELIVERY | Yes — final package review |

### Site Audit
| Phase | Gate | Required? |
|-------|------|-----------|
| After merge | QA_REVIEW | Yes |
| Before delivery | CLIENT_DELIVERY | Yes |

### Content Pipeline
| Stage | Gate | Required? |
|-------|------|-----------|
| After brief creation | QA_REVIEW | Recommended |
| After content written | CONTENT_PUBLISH | Yes |
| After optimization | QA_REVIEW | Yes |
| Before outreach | OUTREACH_SEND | Yes |

### Link Building Campaign
| Phase | Gate | Required? |
|-------|------|-----------|
| Prospect list finalized | QA_REVIEW | Recommended |
| Before outreach begins | OUTREACH_SEND | Yes |
| Budget decisions | BUDGET_COMMIT | Yes |

### Reporting
| Phase | Gate | Required? |
|-------|------|-----------|
| After synthesis | QA_REVIEW | Yes |
| Before client delivery | CLIENT_DELIVERY | Yes |

### Competitive Analysis
| Phase | Gate | Required? |
|-------|------|-----------|
| After adversarial review | QA_REVIEW | Recommended |
| Strategy recommendations | STRATEGY_APPROVAL | Yes |

## Emergency Bypass

For P0 critical issues only (site down, deindexed, security breach):
- Gates can be bypassed with explicit user override
- Bypass must be logged in the ledger with reasoning
- Post-incident review is mandatory

## Orchestrator Behavior at Gates

When the orchestrator reaches a gate:
1. **Pause** all downstream work
2. **Notify** the user that approval is needed
3. **Present** the deliverable for review
4. **Wait** for explicit approval or rejection
5. If **approved**: update gate status, proceed
6. If **rejected**: route feedback to originating agent, agent revises, re-submit to gate
