"""Score math.

Each signal emits its own 0-100 score. Health score is the weighted mean.
Findings contribute to a penalty that caps the signal score.
"""
from __future__ import annotations

from .report import Finding, SEVERITY_WEIGHT, Severity


CATEGORY_WEIGHTS = {
    "technical": 16,
    "headings": 8,
    "schema": 12,
    "cwv": 14,
    "eeat": 12,
    "content": 12,
    "linkgraph": 6,
    "accessibility": 5,
    "topical_authority": 5,
    "serp": 4,
    "aio": 6,
}


def score_from_findings(base: int, findings: list[Finding]) -> int:
    """Subtract severity-weighted penalties from a base score (default 100).

    P0 = -25, P1 = -10, P2 = -4, P3 = -1 per finding. Floor at 0.
    """
    penalty = sum(SEVERITY_WEIGHT[f.severity] for f in findings)
    return max(0, min(100, base - penalty))


def health_score(category_scores: dict[str, int]) -> int:
    total_weight = sum(CATEGORY_WEIGHTS.get(k, 0) for k in category_scores)
    if total_weight == 0:
        return 0
    weighted = sum(category_scores[k] * CATEGORY_WEIGHTS.get(k, 0) for k in category_scores)
    return round(weighted / total_weight)
