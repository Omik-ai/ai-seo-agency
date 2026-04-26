#!/usr/bin/env python3
"""AI SEO Agency — Audit Engine CLI.

Quantified, non-fluffy site audit aligned with current Google algorithm signals.
Every finding has severity (P0-P3), an evidence URL, and a concrete recommendation.

Usage:
    python3 tools/audit_engine.py <domain> [options]

Example:
    python3 tools/audit_engine.py iamamitkumar.dev --max-urls 15 --no-psi -v
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Make the package importable when run as `python3 tools/audit_engine.py ...`
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.audit.engine import AuditEngine, EngineConfig  # noqa: E402
from tools.audit.report import render_markdown, write_json  # noqa: E402


def slugify_domain(domain: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", domain.lower()).strip("-")


def next_task_id(tasks_dir: Path) -> str:
    tasks_dir.mkdir(parents=True, exist_ok=True)
    existing = [p.stem for p in tasks_dir.glob("AUD-*.md")]
    nums = []
    for name in existing:
        m = re.match(r"AUD-(\d+)", name)
        if m:
            nums.append(int(m.group(1)))
    n = (max(nums) if nums else 0) + 1
    return f"AUD-{n:03d}"


def write_task_file(path: Path, task_id: str, domain: str, health: int, json_path: Path, md_path: Path, started_at: str, finished_at: str, counts: dict[str, int]) -> None:
    body = f"""# {task_id}: SEO Audit — {domain}

## Metadata
- **ID**: {task_id}
- **Created**: {started_at}
- **Created By**: audit-engine
- **Assigned To**: audit-engine
- **Status**: completed
- **Priority**: P0
- **Depends On**: []
- **Blocks**: []
- **Workflow**: workflows/site-audit.md
- **Phase**: audit

## Objective
Quantified, evidence-backed SEO audit of {domain} across 8 signal families (technical, headings, schema, CWV, E-E-A-T, content quality, internal link graph, AI Overviews readiness).

## Context
Automated run via `python3 tools/audit_engine.py {domain}`. No LLM involvement in data collection or scoring — findings are extracted from HTTP responses, HTML parsing, and PageSpeed Insights.

## Acceptance Criteria
- [x] JSON deliverable emitted
- [x] Markdown deliverable emitted
- [x] Every finding has evidence.url populated
- [x] Health score computed (0-100)
- [x] Findings categorised by severity

## Input
- {domain}
- robots.txt, sitemap.xml
- HTML of up to N pages (see run.urls_crawled)

## Expected Output
- **Format**: JSON + markdown per CLAUDE.md deliverable format
- **Location**: {json_path}, {md_path}

## Execution Log
### {started_at} — Status: in_progress
Engine started; crawling.

### {finished_at} — Status: completed
Health score: {health}/100. Findings: P0={counts['P0']}, P1={counts['P1']}, P2={counts['P2']}, P3={counts['P3']}.

## Output Reference
- Deliverable (JSON): `{json_path}`
- Deliverable (Markdown): `{md_path}`
"""
    path.write_text(body)


LEDGER_LAST_UPDATED = re.compile(r"^## Last Updated\n.*$", re.MULTILINE)
LEDGER_FACTS_HEADER = re.compile(r"^## Facts Established\n", re.MULTILINE)


def append_to_ledger(ledger_path: Path, task_id: str, domain: str, health: int, json_path: Path, finished_at: str) -> None:
    if not ledger_path.exists():
        return
    text = ledger_path.read_text()

    # Insert a fact line under Facts Established (at the end of that section)
    fact_line = f"- {task_id} audit of {domain} produced health_score={health}/100 — source: {json_path.relative_to(ledger_path.parent.parent) if ledger_path.parent.parent in json_path.parents else json_path}\n"
    # Find Facts section and insert before the next "## " header.
    m = LEDGER_FACTS_HEADER.search(text)
    if m:
        start = m.end()
        next_hdr = re.search(r"\n## ", text[start:])
        insert_at = start + (next_hdr.start() if next_hdr else 0)
        text = text[:insert_at] + fact_line + text[insert_at:]

    # Bump Last Updated footer
    new_last = f"## Last Updated\n{finished_at} by audit-engine ({task_id} completed for {domain}, health score {health}/100)"
    if LEDGER_LAST_UPDATED.search(text):
        text = LEDGER_LAST_UPDATED.sub(new_last, text, count=1)
    else:
        text = text.rstrip() + "\n\n" + new_last + "\n"

    ledger_path.write_text(text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="audit_engine",
        description="Quantified SEO audit. Produces JSON + markdown with severity-rated findings.",
    )
    ap.add_argument("domain", help="Target domain (e.g. example.com or https://example.com)")
    ap.add_argument("--max-urls", type=int, default=25, help="Max URLs to crawl (default 25, hard cap 100)")
    ap.add_argument("--out", default="data/audits", help="Output directory (default data/audits)")
    ap.add_argument("--no-psi", action="store_true", help="Skip PageSpeed Insights calls")
    ap.add_argument("--psi-key", default=None, help="Override PAGESPEED_API_KEY env")
    ap.add_argument("--task-id", default=None, help="Use this task ID instead of auto-numbering")
    ap.add_argument("--json-only", action="store_true", help="Skip markdown render")
    ap.add_argument("--strict", action="store_true", help="Exit 1 if health_score < 60")
    ap.add_argument("--no-state", action="store_true", help="Do not write state/tasks or update state/ledger")
    ap.add_argument("--js-render", action="store_true", help="Use Playwright for real JS rendering (slower, more accurate for SPAs)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    if args.max_urls > 100:
        print("--max-urls capped at 100 in v1", file=sys.stderr)
        args.max_urls = 100

    cfg = EngineConfig(
        domain_input=args.domain,
        max_urls=args.max_urls,
        out_dir=Path(args.out),
        no_psi=args.no_psi,
        psi_key=args.psi_key,
        verbose=args.verbose,
        js_render=args.js_render,
    )

    try:
        engine = AuditEngine(cfg)
        report = engine.run()
    except Exception as e:
        print(f"ERROR: engine failure: {e}", file=sys.stderr)
        return 3

    if report.run.urls_crawled == 0:
        print("ERROR: 0 URLs crawled. Check domain and network.", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify_domain(report.run.domain)
    json_path = out_dir / f"{slug}-audit.json"
    md_path = out_dir / f"{slug}-audit.md"

    write_json(report, json_path)
    if not args.json_only:
        md_path.write_text(render_markdown(report))

    # State: task file + ledger
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for sig in report.signals:
        for f in sig.findings:
            counts[f.severity.value] += 1

    if not args.no_state:
        repo = Path(__file__).resolve().parent.parent
        tasks_dir = repo / "state" / "tasks"
        task_id = args.task_id or next_task_id(tasks_dir)
        task_path = tasks_dir / f"{task_id}.md"
        write_task_file(
            task_path,
            task_id,
            report.run.domain,
            report.health_score,
            json_path.resolve(),
            md_path.resolve(),
            report.run.started_at,
            report.run.finished_at,
            counts,
        )
        append_to_ledger(repo / "state" / "ledger.md", task_id, report.run.domain, report.health_score, json_path.resolve(), report.run.finished_at)
        if args.verbose:
            print(f"[audit] state: task {task_id} written, ledger updated")

    # Summary to stdout
    print(f"\n=== Audit complete: {report.run.domain} ===")
    print(f"Health score: {report.health_score}/100")
    print(f"URLs crawled: {report.run.urls_crawled}/{report.run.urls_requested}")
    print(f"Duration: {report.run.duration_ms/1000:.1f}s")
    print("Category scores:")
    for k, v in report.category_scores.items():
        print(f"  {k:<12} {v}/100")
    print(f"Findings: P0={counts['P0']}  P1={counts['P1']}  P2={counts['P2']}  P3={counts['P3']}")
    print(f"JSON: {json_path}")
    if not args.json_only:
        print(f"Markdown: {md_path}")

    if args.strict and report.health_score < 60:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
