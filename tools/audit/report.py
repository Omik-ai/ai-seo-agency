"""Report dataclasses + JSON serializer + markdown renderer.

Every audit boils down to:
- AuditReport (the whole thing)
- SignalResult (one of 8 signal families)
- Finding (one issue with evidence)

Severity is P0/P1/P2/P3 per CLAUDE.md:183-187.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class Effort(str, Enum):
    S = "S"
    M = "M"
    L = "L"


SEVERITY_WEIGHT = {
    Severity.P0: 25,
    Severity.P1: 10,
    Severity.P2: 4,
    Severity.P3: 1,
}

SEVERITY_LABEL = {
    Severity.P0: "Critical (P0)",
    Severity.P1: "High (P1)",
    Severity.P2: "Medium (P2)",
    Severity.P3: "Low (P3)",
}


@dataclass
class Evidence:
    url: str
    snippet: str | None = None
    value: Any = None

    def to_dict(self) -> dict:
        return {"url": self.url, "snippet": self.snippet, "value": self.value}

    @classmethod
    def from_dict(cls, d: dict) -> Evidence:
        return cls(url=d.get("url", ""), snippet=d.get("snippet"), value=d.get("value"))


@dataclass
class Finding:
    id: str
    severity: Severity
    title: str
    evidence: Evidence
    recommendation: str
    effort: Effort = Effort.M
    google_algo_ref: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "title": self.title,
            "evidence": self.evidence.to_dict(),
            "recommendation": self.recommendation,
            "effort": self.effort.value,
            "google_algo_ref": self.google_algo_ref,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Finding:
        return cls(
            id=d["id"],
            severity=Severity(d["severity"]),
            title=d["title"],
            evidence=Evidence.from_dict(d["evidence"]),
            recommendation=d["recommendation"],
            effort=Effort(d.get("effort", "M")),
            google_algo_ref=d.get("google_algo_ref"),
        )


@dataclass
class SignalResult:
    name: str
    score: int  # 0-100
    findings: list[Finding] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "score": self.score,
            "findings": [f.to_dict() for f in self.findings],
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, d: dict) -> SignalResult:
        return cls(
            name=d["name"],
            score=d.get("score", 0),
            findings=[Finding.from_dict(f) for f in d.get("findings", [])],
            data=d.get("data", {}),
        )


@dataclass
class RunMeta:
    id: str
    domain: str
    started_at: str
    finished_at: str
    duration_ms: int
    engine_version: str
    urls_crawled: int
    urls_requested: int
    js_rendered: bool
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> RunMeta:
        return cls(**{k: v for k, v in d.items() if k in {f.name for f in cls.__dataclass_fields__.values()}})


@dataclass
class AuditReport:
    schema_version: str
    run: RunMeta
    health_score: int
    category_scores: dict[str, int]
    signals: list[SignalResult]

    def to_dict(self) -> dict:
        top_by_prio: dict[str, list[dict]] = {"P0": [], "P1": [], "P2": [], "P3": []}
        for sig in self.signals:
            for f in sig.findings:
                top_by_prio[f.severity.value].append({**f.to_dict(), "signal": sig.name})
        return {
            "schema_version": self.schema_version,
            "run": self.run.to_dict(),
            "health_score": self.health_score,
            "category_scores": self.category_scores,
            "signals": [s.to_dict() for s in self.signals],
            "top_findings_by_priority": top_by_prio,
        }

    @classmethod
    def from_dict(cls, d: dict) -> AuditReport:
        return cls(
            schema_version=d.get("schema_version", "1.0"),
            run=RunMeta.from_dict(d["run"]),
            health_score=d["health_score"],
            category_scores=d["category_scores"],
            signals=[SignalResult.from_dict(s) for s in d.get("signals", [])],
        )


def write_json(report: AuditReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, default=str))


# ── Markdown rendering ─────────────────────────────────────────────────
# Follows CLAUDE.md:159-181 deliverable format.


def _render_findings_section(report: AuditReport, sev: Severity) -> str:
    rows: list[str] = []
    for sig in report.signals:
        for f in sig.findings:
            if f.severity != sev:
                continue
            ev_url = f.evidence.url or "—"
            snippet = (f.evidence.snippet or "").replace("\n", " ")[:140]
            rows.append(
                f"- **[{sig.name}] {f.title}**  \n"
                f"  - URL: `{ev_url}`  \n"
                + (f"  - Evidence: `{snippet}`  \n" if snippet else "")
                + f"  - Fix: {f.recommendation}  \n"
                f"  - Effort: {f.effort.value}"
                + (f" · Ref: {f.google_algo_ref}" if f.google_algo_ref else "")
            )
    if not rows:
        return "_None._\n"
    return "\n".join(rows) + "\n"


def render_markdown(report: AuditReport, client: str | None = None) -> str:
    r = report.run
    client_name = client or r.domain
    date = r.started_at[:10]
    cat = report.category_scores
    warnings_block = ""
    if r.warnings:
        warnings_block = "\n### Warnings\n" + "\n".join(f"- {w}" for w in r.warnings) + "\n"

    counts = {s.value: 0 for s in Severity}
    for sig in report.signals:
        for f in sig.findings:
            counts[f.severity.value] += 1

    return f"""# SEO Audit Report: {r.domain}
**Agent**: audit-engine@{r.engine_version.split('@')[-1]}
**Date**: {date}
**Client/Project**: {client_name}
**Status**: Final
**Run ID**: `{r.id}`

## Executive Summary
Crawled {r.urls_crawled} of {r.urls_requested} URLs in {r.duration_ms/1000:.1f}s.
Overall health: **{report.health_score}/100**.
Findings: {counts['P0']} P0 · {counts['P1']} P1 · {counts['P2']} P2 · {counts['P3']} P3.
{warnings_block}
## Health Score
| Category | Score |
|---|---:|
| Technical | {cat.get('technical', 0)}/100 |
| Headings & Semantic HTML | {cat.get('headings', 0)}/100 |
| Schema / JSON-LD | {cat.get('schema', 0)}/100 |
| Core Web Vitals | {cat.get('cwv', 0)}/100 |
| E-E-A-T | {cat.get('eeat', 0)}/100 |
| Content Quality | {cat.get('content', 0)}/100 |
| Internal Link Graph | {cat.get('linkgraph', 0)}/100 |
| AI Overviews Readiness | {cat.get('aio', 0)}/100 |
| **Overall** | **{report.health_score}/100** |

## Critical Issues (P0) — Fix within 24 hours
{_render_findings_section(report, Severity.P0)}
## High Priority (P1) — Fix within 1 week
{_render_findings_section(report, Severity.P1)}
## Medium Priority (P2) — Fix within 30 days
{_render_findings_section(report, Severity.P2)}
## Low Priority (P3) — Fix within 90 days
{_render_findings_section(report, Severity.P3)}
## Action Items
{_render_action_items(report)}
## Data Sources
- HTTP fetch of {r.urls_crawled} URLs (user-agent: SEOAuditEngine/{r.engine_version.split('@')[-1]})
- robots.txt + XML sitemap parse
- JSON-LD extraction via bs4 + regex
- PageSpeed Insights API {'(disabled)' if any('PSI' in w for w in r.warnings) else ''}
- Engine version: {r.engine_version}

## Handoff Notes
- Structured JSON at the same path with `.json` extension — machine-parseable.
- `top_findings_by_priority` in JSON gives a flat queue for ticket creation.
- Next agent: `on-page-seo` for P1 title/heading fixes, `technical-seo` for P0 indexing.
"""


def _render_action_items(report: AuditReport) -> str:
    items: list[str] = []
    # Top 10 highest-severity findings
    all_findings = [(s, f) for s in report.signals for f in s.findings]
    all_findings.sort(key=lambda pair: (pair[1].severity.value, -len(pair[1].title)))
    for sig, f in all_findings[:15]:
        prio = {"P0": "High", "P1": "High", "P2": "Medium", "P3": "Low"}[f.severity.value]
        items.append(f"- [ ] [Priority: {prio}] [{sig.name}] {f.title} — {f.recommendation}")
    return "\n".join(items) if items else "_No action items — all signals passing._"


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
