"""Shared state helpers for engines (audit_engine, backlink_engine, ...).

Handles:
- slug generation
- task-file numbering under state/tasks/
- task-file writing per state/PROTOCOL.md:68-118
- state/ledger.md "Last Updated" bump + Facts insertion
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


def slugify_domain(domain: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def next_task_id(tasks_dir: Path, prefix: str) -> str:
    """Return next available TASK-ID with the given prefix (e.g. 'AUD', 'LNK')."""
    tasks_dir.mkdir(parents=True, exist_ok=True)
    nums: list[int] = []
    for p in tasks_dir.glob(f"{prefix}-*.md"):
        m = re.match(rf"{re.escape(prefix)}-(\d+)", p.stem)
        if m:
            nums.append(int(m.group(1)))
    n = (max(nums) if nums else 0) + 1
    return f"{prefix}-{n:03d}"


def write_task_file(
    path: Path,
    *,
    task_id: str,
    title: str,
    assigned_to: str,
    objective: str,
    context: str,
    acceptance_criteria: list[str],
    inputs: list[str],
    output_format: str,
    output_location: str,
    started_at: str,
    finished_at: str | None = None,
    status: str = "completed",
    priority: str = "P0",
    depends_on: list[str] | None = None,
    blocks: list[str] | None = None,
    workflow: str = "",
    phase: str = "",
    exec_log_extra: str = "",
    deliverables: list[str] | None = None,
) -> None:
    """Write a task file per state/PROTOCOL.md:68-118."""
    depends_on = depends_on or []
    blocks = blocks or []
    deliverables = deliverables or []
    criteria_md = "\n".join(f"- [{'x' if status == 'completed' else ' '}] {c}" for c in acceptance_criteria)
    inputs_md = "\n".join(f"- {i}" for i in inputs)
    log_lines = [f"### {started_at} — Status: in_progress\nStarted."]
    if finished_at:
        log_lines.append(f"### {finished_at} — Status: {status}\n{exec_log_extra or 'Done.'}")
    log_md = "\n\n".join(log_lines)
    deliv_md = "\n".join(f"- {d}" for d in deliverables) if deliverables else "- (see Expected Output)"

    body = f"""# {task_id}: {title}

## Metadata
- **ID**: {task_id}
- **Created**: {started_at}
- **Created By**: {assigned_to}
- **Assigned To**: {assigned_to}
- **Status**: {status}
- **Priority**: {priority}
- **Depends On**: {depends_on}
- **Blocks**: {blocks}
- **Workflow**: {workflow}
- **Phase**: {phase}

## Objective
{objective}

## Context
{context}

## Acceptance Criteria
{criteria_md}

## Input
{inputs_md}

## Expected Output
- **Format**: {output_format}
- **Location**: {output_location}

## Execution Log
{log_md}

## Output Reference
{deliv_md}
"""
    path.write_text(body)


LEDGER_LAST_UPDATED = re.compile(r"^## Last Updated\n.*$", re.MULTILINE)
LEDGER_FACTS_HEADER = re.compile(r"^## Facts Established\n", re.MULTILINE)


def append_to_ledger(
    ledger_path: Path,
    *,
    task_id: str,
    actor: str,
    summary: str,
    fact_line: str | None = None,
    finished_at: str | None = None,
) -> None:
    """Bump 'Last Updated' + optionally insert a fact. No-op if ledger missing."""
    if not ledger_path.exists():
        return
    text = ledger_path.read_text()

    if fact_line:
        line = f"- {fact_line}\n"
        m = LEDGER_FACTS_HEADER.search(text)
        if m:
            start = m.end()
            next_hdr = re.search(r"\n## ", text[start:])
            insert_at = start + (next_hdr.start() if next_hdr else 0)
            text = text[:insert_at] + line + text[insert_at:]

    ts = finished_at or iso_now()
    new_last = f"## Last Updated\n{ts} by {actor} ({task_id} — {summary})"
    if LEDGER_LAST_UPDATED.search(text):
        text = LEDGER_LAST_UPDATED.sub(new_last, text, count=1)
    else:
        text = text.rstrip() + "\n\n" + new_last + "\n"

    ledger_path.write_text(text)
