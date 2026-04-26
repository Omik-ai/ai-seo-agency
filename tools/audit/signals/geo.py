"""Generative Engine Optimization (GEO) signal.

Checks how well a site is optimized to be cited by LLMs:
- sameAs network density (Organization schema)
- Author entity completeness (Person schema with sameAs)
- Knowledge Graph signals (Organization on homepage)
- Citation-friendly content structure (definitive statements, source density)
- Entity disambiguation strength
"""
from __future__ import annotations

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings
from .schema import _extract_jsonld, _types


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    # ── Homepage org + sameAs audit ────────────────────────────
    homepage = next((p for p in ctx.pages if p.final_url.rstrip("/") == ctx.base_url.rstrip("/") and p.html), None)
    has_org = False
    sameas_count = 0
    org_name = None

    if homepage:
        items = _extract_jsonld(homepage.html)
        for it in items:
            if any(t in ("Organization", "LocalBusiness") for t in _types(it)):
                has_org = True
                org_name = it.get("name")
                sameas = it.get("sameAs")
                if isinstance(sameas, list):
                    sameas_count = len(sameas)
                elif isinstance(sameas, str):
                    sameas_count = 1
                data["organization"] = {
                    "name": org_name,
                    "sameAs_count": sameas_count,
                    "has_logo": bool(it.get("logo")),
                    "has_contactPoint": bool(it.get("contactPoint")),
                }
                break

    if not has_org:
        findings.append(Finding(
            id="geo.org.missing",
            severity=Severity.P1,
            title="No Organization schema on homepage — critical for entity recognition",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add Organization JSON-LD with name, url, logo, and sameAs array. LLMs use this for entity grounding.",
            effort=Effort.S,
            google_algo_ref="Knowledge Graph / LLM entity resolution",
        ))
    elif sameas_count < 3:
        findings.append(Finding(
            id="geo.sameAs.sparse",
            severity=Severity.P2,
            title=f"Organization sameAs only has {sameas_count} profile(s) (target: 5+)",
            evidence=Evidence(url=ctx.base_url, value=sameas_count),
            recommendation="Expand sameAs to include LinkedIn, X/Twitter, Crunchbase, GitHub, and industry directories. More profiles = stronger entity signal.",
            effort=Effort.S,
            google_algo_ref="Entity disambiguation / LLM training data",
        ))

    # ── Per-page author entity audit ───────────────────────────
    article_pages = [p for p in ctx.pages if p.html and _page_kind_geo(p.final_url, p.html) == "article"]
    author_pages_with_sameas = 0
    total_article_authors = 0
    visible_bylines = 0

    for p in article_pages:
        items = _extract_jsonld(p.html)
        soup = BeautifulSoup(p.html, "lxml")
        for it in items:
            if not any(t in ("Article", "BlogPosting", "NewsArticle") for t in _types(it)):
                continue
            author = it.get("author")
            name = None
            author_sameas = None
            if isinstance(author, dict):
                name = author.get("name")
                author_sameas = author.get("sameAs")
            elif isinstance(author, str):
                name = author
            if name:
                total_article_authors += 1
                if author_sameas:
                    author_pages_with_sameas += 1
                if name in soup.get_text():
                    visible_bylines += 1
            break

    data.update({
        "article_pages": len(article_pages),
        "articles_with_author": total_article_authors,
        "articles_with_author_sameAs": author_pages_with_sameas,
        "articles_with_visible_byline": visible_bylines,
    })

    if article_pages and total_article_authors == 0:
        findings.append(Finding(
            id="geo.author.missing_all",
            severity=Severity.P1,
            title="No articles have author schema — author entity is invisible to LLMs",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add author.@type=Person with name and sameAs to all articles. Author entities build topical authority in LLM training data.",
            effort=Effort.S,
            google_algo_ref="E-E-A-T / Author entity",
        ))

    if total_article_authors > 0 and author_pages_with_sameas < total_article_authors // 2:
        findings.append(Finding(
            id="geo.author.sameAs.sparse",
            severity=Severity.P2,
            title=f"Only {author_pages_with_sameas}/{total_article_authors} authors have sameAs links",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add sameAs (LinkedIn, X, personal site) to all author schemas. LLMs cross-reference these for authority.",
            effort=Effort.S,
            google_algo_ref="Author entity / LLM authority signals",
        ))

    # ── Citation-friendly content structure ────────────────────
    definitive_statements = 0
    source_links = 0
    total_articles_checked = 0

    for p in article_pages[:20]:  # sample first 20
        if not p.html:
            continue
        soup = BeautifulSoup(p.html, "lxml")
        text = soup.get_text(" ", strip=True)
        # Definitive statement pattern: "X is ..." or "X means ..." near start of section
        if any(phrase in text for phrase in (" is a ", " is the ", " refers to ", " means ")):
            definitive_statements += 1
        # Source links = external links to .edu, .gov, known authoritative domains
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(auth in href for auth in (".edu", ".gov", "researchgate", "arxiv.org", "doi.org", "pubmed")):
                source_links += 1
        total_articles_checked += 1

    data.update({
        "articles_with_definitive_statements": definitive_statements,
        "authoritative_source_links": source_links,
        "articles_checked_for_structure": total_articles_checked,
    })

    if total_articles_checked > 0 and definitive_statements < total_articles_checked // 2:
        findings.append(Finding(
            id="geo.content.not_definitive",
            severity=Severity.P2,
            title="Most articles lack definitive opening statements",
            evidence=Evidence(url=ctx.base_url, value=f"{definitive_statements}/{total_articles_checked}"),
            recommendation="Start key sections with direct definitions ('X is...'). LLMs extract these as answers.",
            effort=Effort.M,
            google_algo_ref="LLM passage extraction / extractive summarization",
        ))

    if total_articles_checked > 0 and source_links == 0:
        findings.append(Finding(
            id="geo.content.no_sources",
            severity=Severity.P2,
            title="No authoritative external source links found in sampled articles",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Cite .edu, .gov, research papers, and authoritative industry sources. Source density builds LLM trust.",
            effort=Effort.M,
            google_algo_ref="LLM training data / citation authority",
        ))

    # ── WebSite schema (sitelinks searchbox = entity signal) ───
    has_website_schema = False
    if homepage:
        for it in _extract_jsonld(homepage.html):
            if "WebSite" in _types(it):
                has_website_schema = True
                break
    data["has_website_schema"] = has_website_schema
    if not has_website_schema:
        findings.append(Finding(
            id="geo.website_schema.missing",
            severity=Severity.P3,
            title="Homepage missing WebSite schema",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add WebSite JSON-LD with SearchAction. It signals the site's primary entity to search engines and LLMs.",
            effort=Effort.S,
            google_algo_ref="Entity signals / Structured data",
        ))

    score = score_from_findings(100, findings)
    return SignalResult(name="geo", score=score, findings=findings, data=data)


def _page_kind_geo(url: str, html: str) -> str:
    """Reuses schema.py page kind logic for GEO signal."""
    from urllib.parse import urlparse
    path = urlparse(url).path.lower().rstrip("/")
    if path in ("", "/"):
        return "homepage"
    if any(seg in path for seg in ("/blog/", "/post/", "/article/", "/news/", "/insights/")):
        return "article"
    if any(seg in path for seg in ("/product/", "/shop/", "/store/")):
        return "product"
    if "/faq" in path or path.endswith("/faq"):
        return "faq"
    if "/about" in path:
        return "about"
    if "/service" in path:
        return "service"
    # heuristic: if page has Article schema, treat as article
    items = _extract_jsonld(html)
    for it in items:
        if any(t in ("Article", "BlogPosting", "NewsArticle") for t in _types(it)):
            return "article"
    return "other"
