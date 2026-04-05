#!/usr/bin/env bash
#
# SEO Agency Orchestrator Runtime
# Lightweight coordinator that spawns Claude Code agent teams
# for multi-agent SEO workflows.
#
# Usage:
#   ./orchestrator.sh audit <url>              Run full site audit
#   ./orchestrator.sh onboard <url> <name>     Onboard new client
#   ./orchestrator.sh content <topic>          Content pipeline
#   ./orchestrator.sh links <url>              Link building campaign
#   ./orchestrator.sh report                   Monthly report
#   ./orchestrator.sh compete <domain>         Competitive analysis
#   ./orchestrator.sh agent <name> <task>      Deploy single agent
#   ./orchestrator.sh status                   Show current state
#   ./orchestrator.sh resume                   Resume from ledger

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_DIR="$SCRIPT_DIR/state"
TASKS_DIR="$STATE_DIR/tasks"
DATA_DIR="$SCRIPT_DIR/data"
LEDGER="$STATE_DIR/ledger.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Helpers ────────────────────────────────────────────────────────

log_info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_agent() { echo -e "${CYAN}[AGENT]${NC} $*"; }

ensure_dirs() {
    mkdir -p "$TASKS_DIR" "$STATE_DIR/handoffs" \
             "$DATA_DIR/clients" "$DATA_DIR/audits" \
             "$DATA_DIR/reports" "$DATA_DIR/research" \
             "$DATA_DIR/content"
}

next_task_id() {
    local prefix="${1:-TASK}"
    local max=0
    for f in "$TASKS_DIR"/${prefix}-*.md; do
        [[ -f "$f" ]] || continue
        local num
        num=$(basename "$f" .md | sed "s/${prefix}-//")
        num=$((10#$num))
        (( num > max )) && max=$num
    done
    printf "%s-%03d" "$prefix" $((max + 1))
}

create_task() {
    local id="$1" title="$2" agent="$3" priority="$4" objective="$5"
    local depends="${6:-none}"
    cat > "$TASKS_DIR/${id}.md" <<EOF
# ${id}: ${title}

## Metadata
- **ID**: ${id}
- **Created**: $(date -Iseconds)
- **Created By**: orchestrator
- **Assigned To**: ${agent}
- **Status**: pending
- **Priority**: ${priority}
- **Depends On**: ${depends}
- **Blocks**: [none]

## Objective
${objective}

## Acceptance Criteria
- [ ] Output follows CLAUDE.md standards
- [ ] All required sections present
- [ ] Action items are prioritized
- [ ] Handoff notes included

## Execution Log

## Output Reference
- Deliverable: [pending]
EOF
    log_ok "Created task ${id} → ${agent}"
}

update_ledger() {
    local client="$1" domain="$2" plan="$3"

    # Build agent table outside heredoc
    local agent_table=""
    for f in "$TASKS_DIR"/*.md; do
        [[ -f "$f" ]] || continue
        local tid
        tid=$(basename "$f" .md)
        local agent
        agent=$(grep "Assigned To" "$f" 2>/dev/null | head -1 | sed 's/.*: //')
        local status
        status=$(grep "Status" "$f" 2>/dev/null | head -1 | sed 's/.*: //')
        agent_table="${agent_table}| ${agent} | ${tid} | ${status} | $(date +%Y-%m-%d) |
"
    done

    cat > "$LEDGER" <<EOF
# Agency Ledger

## Current Client
- Name: ${client}
- Domain: ${domain}
- Goals: ${plan}
- Started: $(date -Iseconds)

## Facts Established
[Pending — agents will populate during execution]

## Current Plan
${plan}

## Active Agents
| Agent | Task | Status | Since |
|-------|------|--------|-------|
${agent_table}
## Last Updated
$(date -Iseconds) by orchestrator
EOF
}

check_claude() {
    if ! command -v claude &>/dev/null; then
        log_error "Claude Code CLI not found. Install from: https://claude.ai/code"
        log_info "You can also use this system manually — read CLAUDE.md with any AI tool."
        exit 1
    fi
}

# ─── Workflow Commands ──────────────────────────────────────────────

cmd_audit() {
    local url="${1:?Usage: orchestrator.sh audit <url>}"
    log_info "Starting full site audit: $url"
    ensure_dirs

    # Create parallel tasks
    local t1=$(next_task_id "AUD")
    create_task "$t1" "Technical SEO Audit" "technical-seo" "P1" \
        "Perform a full technical SEO audit of ${url}. Follow the methodology in skills/technical-audit.md. Check crawlability, indexing, Core Web Vitals, schema, mobile, security. Output to data/audits/"

    local t2=$(next_task_id "AUD")
    create_task "$t2" "Performance Analysis" "analytics" "P1" \
        "Analyze historical organic performance for ${url}. Pull traffic trends, ranking data, conversion data. Output to data/audits/"

    local t3=$(next_task_id "AUD")
    create_task "$t3" "On-Page SEO Sample Audit" "on-page-seo" "P2" \
        "Audit the top 20 pages by traffic on ${url}. Check title tags, meta descriptions, headings, internal links. Output to data/audits/"

    local t4=$(next_task_id "AUD")
    create_task "$t4" "Content Assessment" "content-strategist" "P2" \
        "Audit the content ecosystem on ${url}. Inventory, score quality, identify gaps. Output to data/audits/"

    local t5=$(next_task_id "AUD")
    create_task "$t5" "Audit Synthesis & QA" "seo-strategist" "P1" \
        "Synthesize all audit reports into unified audit with health score and prioritized action plan. Route through qa-validator. Output to data/audits/" \
        "${t1},${t2},${t3},${t4}"

    update_ledger "Audit Client" "$url" "Full site audit — 4 parallel agents → synthesis → QA → delivery"

    log_info "Created 5 tasks for site audit workflow"
    log_info ""
    log_info "To execute with Claude Code agent team:"
    echo -e "${CYAN}  claude \"Read workflows/site-audit.md and execute the audit for ${url}. Tasks are in state/tasks/. Update the ledger as you go.\"${NC}"
    log_info ""
    log_info "Or execute individual tasks:"
    echo -e "${CYAN}  claude \"Read agents/technical-seo.md and execute task state/tasks/${t1}.md\"${NC}"
}

cmd_onboard() {
    local url="${1:?Usage: orchestrator.sh onboard <url> <client-name>}"
    local name="${2:-$url}"
    log_info "Starting client onboarding: $name ($url)"
    ensure_dirs
    mkdir -p "$DATA_DIR/clients/$name"

    local t1=$(next_task_id "ONB")
    create_task "$t1" "Client Intake" "client-manager" "P0" \
        "Gather requirements, goals, access for ${name} (${url}). Create client brief in data/clients/${name}/"

    local t2=$(next_task_id "ONB")
    create_task "$t2" "Strategic Framing" "seo-strategist" "P0" \
        "Review client brief, define KPIs, set expectations for ${name}." "$t1"

    local t3=$(next_task_id "ONB")
    create_task "$t3" "Full Audit Swarm" "orchestrator" "P1" \
        "Deploy all audit agents in parallel for ${url}: technical-seo, analytics, keyword-research, content-strategist, link-building, competitive-intel." "$t2"

    local t4=$(next_task_id "ONB")
    create_task "$t4" "Strategy Development" "seo-strategist" "P1" \
        "Synthesize all audits into 90-day, 6-month, and 12-month strategy. GATE: STRATEGY_APPROVAL required." "$t3"

    local t5=$(next_task_id "ONB")
    create_task "$t5" "Deliverable Packaging" "client-manager" "P1" \
        "Package all deliverables, create executive presentation. GATE: CLIENT_DELIVERY required." "$t4"

    update_ledger "$name" "$url" "Client onboarding — intake → framing → audit swarm → strategy → delivery"

    log_info "Created 5 onboarding tasks"
    log_info ""
    log_info "To execute with Claude Code:"
    echo -e "${CYAN}  claude \"Read workflows/client-onboarding.md and onboard ${name} (${url}). Tasks in state/tasks/. Follow all gates.\"${NC}"
}

cmd_content() {
    local topic="${1:?Usage: orchestrator.sh content <topic>}"
    log_info "Starting content pipeline: $topic"
    ensure_dirs

    local t1=$(next_task_id "CON")
    create_task "$t1" "Keyword Research" "keyword-research" "P1" \
        "Research keyword opportunities for topic: ${topic}. Follow skills/keyword-research.md methodology."

    local t2=$(next_task_id "CON")
    create_task "$t2" "Content Brief" "content-strategist" "P1" \
        "Create content brief using keyword data. Follow skills/content-brief.md template." "$t1"

    local t3=$(next_task_id "CON")
    create_task "$t3" "On-Page Optimization Spec" "on-page-seo" "P2" \
        "Optimize the content for SEO. Title, meta, headings, internal links, schema." "$t2"

    local t4=$(next_task_id "CON")
    create_task "$t4" "Link Building Plan" "link-building" "P2" \
        "Create link building plan for the published content." "$t3"

    update_ledger "Content Campaign" "N/A" "Content pipeline: research → brief → optimize → promote for '${topic}'"

    log_info "Created 4 content pipeline tasks"
    echo -e "${CYAN}  claude \"Read workflows/content-pipeline.md and create content for '${topic}'. Tasks in state/tasks/.\"${NC}"
}

cmd_compete() {
    local domain="${1:?Usage: orchestrator.sh compete <competitor-domain>}"
    log_info "Starting competitive analysis: $domain"
    ensure_dirs

    local t1=$(next_task_id "CMP")
    create_task "$t1" "Competitive Deep Dive" "competitive-intel" "P1" \
        "Full competitive analysis of ${domain}. Follow skills/competitor-analysis.md framework."

    local t2=$(next_task_id "CMP")
    create_task "$t2" "Keyword Gap Analysis" "keyword-research" "P1" \
        "Keyword overlap and gap analysis vs ${domain}."

    local t3=$(next_task_id "CMP")
    create_task "$t3" "Backlink Gap Analysis" "link-building" "P1" \
        "Backlink profile comparison vs ${domain}. Follow skills/backlink-analysis.md."

    local t4=$(next_task_id "CMP")
    create_task "$t4" "Counter-Strategy" "seo-strategist" "P1" \
        "Synthesize competitive findings into counter-strategy recommendations." "$t1,$t2,$t3"

    update_ledger "Competitive Analysis" "$domain" "Competitive analysis: parallel intel → keyword gap → link gap → counter-strategy"

    log_info "Created 4 competitive analysis tasks"
    echo -e "${CYAN}  claude \"Read workflows/competitive-analysis.md and analyze ${domain}. Tasks in state/tasks/.\"${NC}"
}

cmd_links() {
    local url="${1:?Usage: orchestrator.sh links <target-url>}"
    log_info "Starting link building campaign: $url"
    ensure_dirs

    local t1=$(next_task_id "LNK")
    create_task "$t1" "Backlink Audit" "link-building" "P1" \
        "Audit current backlink profile for ${url}. Follow skills/backlink-analysis.md."

    local t2=$(next_task_id "LNK")
    create_task "$t2" "Competitive Link Analysis" "competitive-intel" "P1" \
        "Analyze competitor backlinks for the same keywords as ${url}."

    local t3=$(next_task_id "LNK")
    create_task "$t3" "Campaign Strategy" "link-building" "P1" \
        "Build link acquisition campaign plan. GATE: OUTREACH_SEND before any outreach." "$t1,$t2"

    update_ledger "Link Building" "$url" "Link campaign: audit + competitive analysis → strategy → outreach"

    log_info "Created 3 link building tasks"
    echo -e "${CYAN}  claude \"Read workflows/link-building-campaign.md and build links for ${url}. Tasks in state/tasks/.\"${NC}"
}

cmd_report() {
    log_info "Starting monthly report generation"
    ensure_dirs

    local t1=$(next_task_id "RPT")
    create_task "$t1" "Performance Data Collection" "analytics" "P1" \
        "Pull all performance data for the reporting period. Follow the analytics output contract."

    local t2=$(next_task_id "RPT")
    create_task "$t2" "Report Synthesis" "client-manager" "P1" \
        "Assemble monthly report from all agent data. GATE: CLIENT_DELIVERY before sending." "$t1"

    update_ledger "Reporting" "N/A" "Monthly report: data collection → synthesis → QA → delivery"

    log_info "Created 2 reporting tasks"
    echo -e "${CYAN}  claude \"Read workflows/reporting.md and generate the monthly report. Tasks in state/tasks/.\"${NC}"
}

cmd_agent() {
    local agent="${1:?Usage: orchestrator.sh agent <agent-name> <task-description>}"
    local task="${2:?Usage: orchestrator.sh agent <agent-name> <task-description>}"

    # Validate agent exists
    if [[ ! -f "$SCRIPT_DIR/agents/${agent}.md" ]]; then
        log_error "Agent '${agent}' not found. Available agents:"
        ls "$SCRIPT_DIR/agents/" | sed 's/\.md$//' | while read -r a; do echo "  - $a"; done
        exit 1
    fi

    log_agent "Deploying single agent: $agent"
    ensure_dirs

    local tid=$(next_task_id "TASK")
    create_task "$tid" "$task" "$agent" "P1" "$task"

    echo -e "${CYAN}  claude \"Read agents/${agent}.md and execute: ${task}. Track in state/tasks/${tid}.md\"${NC}"
}

cmd_status() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}  SEO Agency Orchestrator Status${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""

    if [[ -f "$LEDGER" ]]; then
        echo -e "${CYAN}Ledger:${NC}"
        head -20 "$LEDGER"
        echo ""
    fi

    echo -e "${CYAN}Tasks:${NC}"
    local pending=0 progress=0 done=0 total=0
    for f in "$TASKS_DIR"/*.md; do
        [[ -f "$f" ]] || continue
        total=$((total + 1))
        local status
        status=$(grep -F "**Status**" "$f" | head -1 | sed 's/.*: //')
        local tid
        tid=$(basename "$f" .md)
        local agent
        agent=$(grep -F "**Assigned To**" "$f" | head -1 | sed 's/.*: //')

        case "$status" in
            pending)     pending=$((pending+1)); echo -e "  ${YELLOW}○${NC} ${tid} → ${agent} (pending)" ;;
            in_progress) progress=$((progress+1)); echo -e "  ${BLUE}●${NC} ${tid} → ${agent} (in progress)" ;;
            completed)   done=$((done+1)); echo -e "  ${GREEN}✓${NC} ${tid} → ${agent} (completed)" ;;
            *)           echo -e "  ${RED}?${NC} ${tid} → ${agent} ($status)" ;;
        esac
    done

    echo ""
    echo -e "Total: ${total} | ${GREEN}Done: ${done}${NC} | ${BLUE}Active: ${progress}${NC} | ${YELLOW}Pending: ${pending}${NC}"
}

cmd_resume() {
    log_info "Resuming from ledger state..."
    if [[ ! -f "$LEDGER" ]]; then
        log_error "No ledger found. Nothing to resume."
        exit 1
    fi
    echo -e "${CYAN}  claude \"Read state/ledger.md and state/tasks/ to understand current progress. Resume any in_progress or pending tasks.\"${NC}"
}

# ─── Main ───────────────────────────────────────────────────────────

show_help() {
    echo -e "${BLUE}SEO Agency Orchestrator${NC}"
    echo ""
    echo "Usage: orchestrator.sh <command> [args]"
    echo ""
    echo "Workflows:"
    echo "  audit <url>              Full site audit (parallel swarm)"
    echo "  onboard <url> <name>     Client onboarding (full pipeline)"
    echo "  content <topic>          Content production pipeline"
    echo "  links <url>              Link building campaign"
    echo "  compete <domain>         Competitive analysis"
    echo "  report                   Monthly report generation"
    echo ""
    echo "Operations:"
    echo "  agent <name> <task>      Deploy single agent"
    echo "  status                   Show task status"
    echo "  resume                   Resume from last state"
    echo ""
    echo "Available agents:"
    for f in "$SCRIPT_DIR"/agents/*.md ; do
        [[ -f "$f" ]] || continue
        echo "  - $(basename "$f" .md)"
    done
}

case "${1:-help}" in
    audit)    cmd_audit "${@:2}" ;;
    onboard)  cmd_onboard "${@:2}" ;;
    content)  cmd_content "${@:2}" ;;
    links)    cmd_links "${@:2}" ;;
    compete)  cmd_compete "${@:2}" ;;
    report)   cmd_report "${@:2}" ;;
    agent)    cmd_agent "${@:2}" ;;
    status)   cmd_status ;;
    resume)   cmd_resume ;;
    help|*)   show_help ;;
esac
