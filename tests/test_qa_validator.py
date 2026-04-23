"""Tests for QA validator."""
from __future__ import annotations

from tests.conftest import make_page
from tools.audit.engine import AuditContext, EngineConfig
from tools.audit.report import AuditReport, RunMeta
from tools.qa.validator import validate_report


def test_validate_good_report():
    report = AuditReport(
        schema_version="1.0",
        run=RunMeta(
            id="test",
            domain="example.com",
            started_at="",
            finished_at="",
            duration_ms=1000,
            engine_version="test",
            urls_crawled=5,
            urls_requested=5,
            js_rendered=False,
            warnings=[],
        ),
        health_score=85,
        category_scores={
            "technical": 80, "headings": 90, "schema": 85, "cwv": 70,
            "eeat": 80, "content": 90, "linkgraph": 85,
            "accessibility": 80, "topical_authority": 75, "serp": 60, "aio": 70,
        },
        signals=[],
    )
    result = validate_report(report)
    assert result.passed is True
    assert result.score >= 7.0


def test_validate_low_health_score():
    report = AuditReport(
        schema_version="1.0",
        run=RunMeta(
            id="test",
            domain="example.com",
            started_at="",
            finished_at="",
            duration_ms=1000,
            engine_version="test",
            urls_crawled=5,
            urls_requested=5,
            js_rendered=False,
            warnings=[],
        ),
        health_score=50,
        category_scores={},
        signals=[],
    )
    result = validate_report(report)
    assert result.passed is False
    assert result.score < 7.0
    assert any("Health score" in i for i in result.issues)
