"""QA Validator — Python scorer that blocks deliverables with health_score < 7.

Validates audit reports against Plan.md acceptance criteria:
- Minimum health score threshold
- Required signals present
- All signals have scores (or documented exceptions)
- Critical findings capped
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.audit.report import AuditReport, Severity


@dataclass
class QAResult:
    passed: bool
    score: float  # 0-10
    issues: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


MIN_HEALTH_SCORE = 7.0  # Plan.md: block if < 7
REQUIRED_SIGNALS = {
    "technical",
    "headings",
    "schema",
    "cwv",
    "eeat",
    "content",
    "linkgraph",
    "accessibility",
    "topical_authority",
    "serp",
    "aio",
}


def validate_report(report: AuditReport) -> QAResult:
    issues: list[str] = []
    details: dict[str, Any] = {}

    # 1. Health score threshold
    hs = report.health_score
    details["health_score"] = hs
    if hs is not None and hs < MIN_HEALTH_SCORE * 10:
        issues.append(f"Health score {hs}/100 is below threshold {int(MIN_HEALTH_SCORE * 10)}/100")

    # 2. Required signals present
    present = {s.name for s in report.signals}
    missing = REQUIRED_SIGNALS - present
    details["signals_present"] = sorted(present)
    details["signals_missing"] = sorted(missing)
    if missing:
        issues.append(f"Missing required signals: {', '.join(sorted(missing))}")

    # 3. All signals must have scores (or be documented as N/A)
    no_score = [s.name for s in report.signals if s.score is None]
    details["signals_without_score"] = no_score
    if no_score:
        issues.append(f"Signals without scores: {', '.join(no_score)}")

    # 4. Critical findings count
    critical_count = sum(
        1 for s in report.signals for f in s.findings if f.severity == Severity.P0
    )
    details["critical_findings"] = critical_count
    if critical_count > 10:
        issues.append(f"Too many critical findings: {critical_count} (max 10)")

    # 5. Signal score distribution (flag if any signal is 0)
    zero_score = [s.name for s in report.signals if s.score == 0]
    details["zero_score_signals"] = zero_score
    if zero_score:
        issues.append(f"Signals with score 0: {', '.join(zero_score)}")

    # 6. Meta validation
    if report.run.urls_crawled == 0:
        issues.append("No URLs were crawled")

    if report.run.duration_ms and report.run.duration_ms > 300000:
        issues.append(f"Audit took too long: {report.run.duration_ms}ms (max 300s)")

    # Compute QA score (0-10)
    base = 10.0
    base -= len(missing) * 2.0
    base -= len(no_score) * 1.0
    base -= critical_count * 0.5
    base -= len(zero_score) * 1.5
    if hs is not None:
        base = min(base, hs / 10)
    score = max(0.0, round(base, 1))

    passed = score >= MIN_HEALTH_SCORE and not issues

    return QAResult(passed=passed, score=score, issues=issues, details=details)


def validate_file(path: Path) -> QAResult:
    import json
    data = json.loads(path.read_text())
    report = AuditReport.from_dict(data)
    return validate_report(report)
