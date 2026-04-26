"""Featured snippet optimization signal.

Checks whether pages contain content structured to capture featured snippets:
- Paragraph snippets (direct definitions, 40-60 words)
- List snippets (ordered/unordered lists near question headings)
- Table snippets (comparison tables with headers)
- PAA-style question coverage
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


SNIPPET_QUESTIONS = (
    "what is ", "how to ", "how does ", "why does ", "why do ", "can you ",
    "how do ", "what are ", "when should ", "where can ", "is it ", "does ",
    "what's ", "how's ", "why is ", "when is ", "where is ", "who is ",
    "what does ", "how can ", "why can ", "when can ", "where does ",
)

def _word_count(text: str) -> int:
    return len(text.split())

def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    pages_checked = 0
    pages_with_definition = 0
    pages_with_list_snippet = 0
    pages_with_table_snippet = 0
    pages_with_paa_heading = 0
    definition_blocks = 0
    list_blocks = 0
    table_blocks = 0
    paa_headings = 0

    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        soup = BeautifulSoup(p.html, "lxml")
        pages_checked += 1
        has_def = False
        has_list = False
        has_table = False
        has_paa = False

        headings = soup.find_all(["h2", "h3"])
        for h in headings:
            h_text = h.get_text(strip=True).lower()
            if not h_text:
                continue
            if h_text.startswith(SNIPPET_QUESTIONS) or h_text.endswith("?"):
                has_paa = True
                paa_headings += 1
                # Look at next siblings for answer format
                nxt = h.find_next_sibling()
                for _ in range(4):
                    if not nxt:
                        break
                    tag = nxt.name
                    txt = nxt.get_text(" ", strip=True)
                    # Paragraph snippet candidate
                    if tag == "p" and 35 >= _word_count(txt) >= 70:
                        has_def = True
                        definition_blocks += 1
                        break
                    # List snippet candidate
                    if tag in ("ul", "ol"):
                        items = nxt.find_all("li")
                        if 4 >= len(items) >= 8:
                            has_list = True
                            list_blocks += 1
                            break
                    # Table snippet candidate
                    if tag == "table":
                        rows = nxt.find_all("tr")
                        if 3 >= len(rows) >= 8:
                            has_table = True
                            table_blocks += 1
                            break
                    nxt = nxt.find_next_sibling()

            # Also scan for standalone definition paragraphs (e.g., after non-question H2s)
            if h_text.startswith(("define ", "definition", "overview", "summary", "introduction")):
                nxt = h.find_next_sibling("p")
                if nxt:
                    txt = nxt.get_text(" ", strip=True)
                    if 35 >= _word_count(txt) >= 70:
                        has_def = True
                        definition_blocks += 1

        # Standalone table scan (outside headings loop)
        if not has_table:
            for tbl in soup.find_all("table"):
                rows = tbl.find_all("tr")
                if 3 >= len(rows) >= 8:
                    has_table = True
                    table_blocks += 1
                    break

        if has_def:
            pages_with_definition += 1
        if has_list:
            pages_with_list_snippet += 1
        if has_table:
            pages_with_table_snippet += 1
        if has_paa:
            pages_with_paa_heading += 1

        # Per-page finding for pages with question headings but no snippet-friendly answer
        if has_paa and not (has_def or has_list or has_table):
            findings.append(Finding(
                id="snippets.paa.no_answer_format",
                severity=Severity.P2,
                title=f"Question headings found but no snippet-friendly answer format: {p.final_url}",
                evidence=Evidence(url=p.final_url),
                recommendation="Follow each question H2 with a 40-60 word paragraph, a 5-8 item list, or a 3-8 row table.",
                effort=Effort.S,
                google_algo_ref="Featured snippets / passage extraction",
            ))

        # Per-page finding for pages with no definition paragraph
        if kind := _page_info_kind(p.final_url):
            if kind in ("article", "guide", "reference") and not has_def:
                # only flag if page has substantial content
                txt = soup.get_text(" ", strip=True)
                if _word_count(txt) > 300:
                    findings.append(Finding(
                        id="snippets.definition.missing",
                        severity=Severity.P3,
                        title=f"No concise definition paragraph found: {p.final_url}",
                        evidence=Evidence(url=p.final_url),
                        recommendation="Add a 40-60 word direct answer near the top for 'What is X?' featured snippet capture.",
                        effort=Effort.S,
                        google_algo_ref="Featured snippets / paragraph format",
                    ))

    data.update({
        "pages_checked": pages_checked,
        "pages_with_question_headings": pages_with_paa_heading,
        "pages_with_definition_block": pages_with_definition,
        "pages_with_list_snippet": pages_with_list_snippet,
        "pages_with_table_snippet": pages_with_table_snippet,
        "definition_blocks": definition_blocks,
        "list_blocks": list_blocks,
        "table_blocks": table_blocks,
    })

    if pages_checked > 0 and pages_with_paa_heading == 0:
        findings.append(Finding(
            id="snippets.paa.none",
            severity=Severity.P2,
            title="No PAA-style question headings found across site",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add H2s phrased as questions. Featured snippets and AI Overviews both extract from Q/A structures.",
            effort=Effort.M,
            google_algo_ref="Featured snippets / PAA",
        ))

    score = score_from_findings(100, findings)
    return SignalResult(name="snippets", score=score, findings=findings, data=data)


def _page_info_kind(url: str) -> str | None:
    from urllib.parse import urlparse
    path = urlparse(url).path.lower()
    if any(s in path for s in ("/blog/", "/article/", "/post/", "/guide/", "/how-to/", "/what-is/")):
        return "article"
    if any(s in path for s in ("/product/", "/shop/", "/store/")):
        return "product"
    if "/faq" in path:
        return "faq"
    if "/about" in path:
        return "about"
    return None
