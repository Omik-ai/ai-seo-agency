"""Headings & semantic HTML signal."""
from __future__ import annotations

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


SEMANTIC_TAGS = ["main", "article", "nav", "header", "footer", "section"]


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    per_page: list[dict] = []

    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        soup = BeautifulSoup(p.html, "lxml")
        h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
        headings_by_level: dict[int, list[str]] = {i: [] for i in range(1, 7)}
        order: list[int] = []
        for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            lvl = int(h.name[1])
            txt = h.get_text(strip=True)
            headings_by_level[lvl].append(txt)
            order.append(lvl)

        page_info = {
            "url": p.final_url,
            "h1_count": len(h1s),
            "h1_texts": h1s[:3],
            "total_headings": sum(len(v) for v in headings_by_level.values()),
            "semantic_tags": {t: bool(soup.find(t)) for t in SEMANTIC_TAGS},
            "level_order": order[:30],
        }
        per_page.append(page_info)

        # H1 checks
        if len(h1s) == 0:
            findings.append(Finding(
                id="headings.h1.missing",
                severity=Severity.P0,
                title=f"No H1 on {p.final_url}",
                evidence=Evidence(url=p.final_url),
                recommendation="Add exactly one H1 that describes the page topic using the primary keyword.",
                effort=Effort.S,
                google_algo_ref="On-page signals / Helpful Content",
            ))
        elif len(h1s) > 1:
            findings.append(Finding(
                id="headings.h1.multiple",
                severity=Severity.P1,
                title=f"{len(h1s)} H1s on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=h1s[:3]),
                recommendation="Keep exactly one H1 per page. Demote the rest to H2.",
                effort=Effort.S,
            ))

        # Empty headings
        empty = [l for l in order for _ in [None]]
        empty_count = sum(1 for lvl in headings_by_level for t in headings_by_level[lvl] if not t.strip())
        if empty_count:
            findings.append(Finding(
                id="headings.empty",
                severity=Severity.P2,
                title=f"{empty_count} empty heading(s) on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=empty_count),
                recommendation="Remove empty H1-H6 tags; they confuse accessibility and SEO parsers.",
                effort=Effort.S,
            ))

        # Skipped levels (e.g., H2 → H4)
        skips = 0
        last = 0
        for lvl in order:
            if last and lvl > last + 1:
                skips += 1
            last = lvl
        if skips:
            findings.append(Finding(
                id="headings.skipped_level",
                severity=Severity.P2,
                title=f"{skips} skipped heading level(s) on {p.final_url}",
                evidence=Evidence(url=p.final_url, value=order[:20]),
                recommendation="Don't skip levels (e.g., H2 → H4). Go in order: H1 → H2 → H3 …",
                effort=Effort.S,
                google_algo_ref="Accessibility (WCAG 1.3.1) + content parsing",
            ))

        # Semantic HTML
        missing_semantic = [t for t in ("main", "header", "footer", "nav") if not soup.find(t)]
        if missing_semantic:
            findings.append(Finding(
                id="headings.semantic.missing",
                severity=Severity.P3,
                title=f"Missing semantic tags on {p.final_url}: {', '.join(missing_semantic)}",
                evidence=Evidence(url=p.final_url, value=missing_semantic),
                recommendation=f"Wrap content in <{'>, <'.join(missing_semantic)}> tags. Helps Google's content extraction.",
                effort=Effort.M,
            ))

    score = score_from_findings(100, findings)
    return SignalResult(name="headings", score=score, findings=findings, data={"per_page": per_page})
