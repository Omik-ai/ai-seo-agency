"""AI Overviews / SGE readiness signal.

Signals that help pages be pulled as extractive answers by Google's
AI Overviews (and ChatGPT / Perplexity):
- FAQ / HowTo schema presence
- Question-style H2/H3 headings
- Self-contained passages under each heading
- TL;DR / summary block at top
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings
from .schema import _extract_jsonld, _types, _page_kind


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    any_faq = False
    any_howto = False
    article_pages = []
    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        items = _extract_jsonld(p.html)
        for it in items:
            if "FAQPage" in _types(it):
                any_faq = True
            if "HowTo" in _types(it):
                any_howto = True
        if _page_kind(p.final_url, p.html) == "article":
            article_pages.append(p)

    data["has_faq_schema"] = any_faq
    data["has_howto_schema"] = any_howto

    if not any_faq:
        findings.append(Finding(
            id="aio.faq.missing",
            severity=Severity.P3,
            title="No FAQPage schema found anywhere on the site",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add an FAQ section with FAQPage schema to pages answering common questions. High AI-Overview pull rate.",
            effort=Effort.M,
            google_algo_ref="AI Overviews / Rich Results: FAQ",
        ))

    # Per-article: question headings + passage fitness
    q_heading_articles = 0
    tldr_articles = 0
    for p in article_pages:
        soup = BeautifulSoup(p.html, "lxml")
        h_text = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])]
        questions = [h for h in h_text if "?" in h]
        if questions:
            q_heading_articles += 1
        else:
            findings.append(Finding(
                id="aio.questions.missing",
                severity=Severity.P3,
                title=f"No question-style H2/H3 on {p.final_url}",
                evidence=Evidence(url=p.final_url),
                recommendation="Add H2s phrased as questions (e.g., 'What is X?') — AI Overviews prefer extractive Q/A.",
                effort=Effort.M,
                google_algo_ref="AI Overviews / passage ranking",
            ))

        # HowTo on how-to-style URLs
        path_low = p.final_url.lower()
        h1 = soup.find("h1")
        h1_text = h1.get_text(strip=True).lower() if h1 else ""
        is_howto_like = ("how-to" in path_low or "/how-" in path_low or h1_text.startswith("how to"))
        if is_howto_like:
            items = _extract_jsonld(p.html)
            has_howto_here = any("HowTo" in _types(it) for it in items)
            if not has_howto_here:
                findings.append(Finding(
                    id="aio.howto.missing",
                    severity=Severity.P2,
                    title=f"How-to style page missing HowTo schema: {p.final_url}",
                    evidence=Evidence(url=p.final_url),
                    recommendation="Add HowTo JSON-LD with name + step array. Rich Results + AI Overviews eligible.",
                    effort=Effort.M,
                    google_algo_ref="Rich Results: HowTo",
                ))

        # TL;DR / summary block (first blockquote or div.summary within first 1/3)
        bq = soup.find(["blockquote", "div"], class_=lambda c: c and any(k in c.lower() for k in ("summary", "tldr", "tl-dr", "abstract")))
        if bq:
            tldr_articles += 1

    data.update({
        "article_count": len(article_pages),
        "articles_with_question_headings": q_heading_articles,
        "articles_with_tldr": tldr_articles,
    })

    if article_pages and tldr_articles == 0:
        findings.append(Finding(
            id="aio.tldr.missing",
            severity=Severity.P3,
            title="No article has a TL;DR / summary block",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add a 2–3 sentence TL;DR at the top of articles; AI Overviews and readers both scan for it.",
            effort=Effort.S,
        ))

    # ── PAA-style question coverage + passage fitness ────────────────
    PAA_PREFIXES = ("what is", "how to", "why does", "why do", "can you", "how does",
                    "how do", "what are", "when should", "where can", "is it", "does ")
    paa_headings = 0
    snippet_fit = 0
    snippet_unfit = 0
    citation_links = 0

    for p in article_pages:
        soup = BeautifulSoup(p.html, "lxml")
        headings = soup.find_all(["h2", "h3"])
        for h in headings:
            h_text = h.get_text(strip=True).lower()
            if h_text.startswith(PAA_PREFIXES) or h_text.endswith("?"):
                paa_headings += 1
                # Check next sibling for direct answer passage
                nxt = h.find_next_sibling()
                passage = ""
                for _ in range(3):  # look at next 3 siblings
                    if nxt and nxt.name in ("p", "div"):
                        passage += " " + nxt.get_text(strip=True)
                    nxt = nxt.find_next_sibling() if nxt else None
                passage = passage.strip()
                word_count = len(passage.split())
                if 35 <= word_count <= 70:
                    snippet_fit += 1
                elif passage:
                    snippet_unfit += 1
                    findings.append(Finding(
                        id="aio.passage.snippet_unfit",
                        severity=Severity.P3,
                        title=f"Passage after question heading is {word_count} words (target 40-60): {p.final_url}",
                        evidence=Evidence(url=p.final_url, value=h_text[:80]),
                        recommendation="Place a concise 40-60 word direct answer immediately after each question heading.",
                        effort=Effort.S,
                        google_algo_ref="AI Overviews / passage extraction",
                    ))
        # Citation density: external links to authoritative sources
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(auth in href for auth in (".edu", ".gov", "arxiv.org", "doi.org", "pubmed", "researchgate")):
                citation_links += 1

    data.update({
        "paa_style_headings": paa_headings,
        "snippet_fit_passages": snippet_fit,
        "snippet_unfit_passages": snippet_unfit,
        "authoritative_citation_links": citation_links,
    })

    if article_pages and paa_headings == 0:
        findings.append(Finding(
            id="aio.paa.missing",
            severity=Severity.P2,
            title="No PAA-style question headings found on articles",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add H2s phrased as questions (e.g., 'What is X?', 'How does Y work?'). AI Overviews pull from Q/A structures.",
            effort=Effort.M,
            google_algo_ref="AI Overviews / PAA",
        ))

    if article_pages and citation_links == 0:
        findings.append(Finding(
            id="aio.citations.missing",
            severity=Severity.P2,
            title="No authoritative external citations found in articles",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Cite .edu, .gov, research papers, and authoritative industry sources. Citation density builds extractive answer trust.",
            effort=Effort.M,
            google_algo_ref="AI Overviews / source credibility",
        ))

    score = score_from_findings(100, findings)
    return SignalResult(name="aio", score=score, findings=findings, data=data)
