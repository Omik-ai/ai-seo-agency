"""SERP + competitor intelligence signal.

Lightweight Google SERP scraper (no API key required for basic checks).
Detects brand presence, Knowledge Panel, featured snippets, PAA.
"""
from __future__ import annotations

import re
import time
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings

GOOGLE_SERP_URL = "https://www.google.com/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _fetch_serp(query: str, num: int = 10) -> BeautifulSoup | None:
    params = {"q": query, "num": num, "hl": "en"}
    try:
        r = requests.get(GOOGLE_SERP_URL, headers=HEADERS, params=params, timeout=30)
        if r.status_code != 200:
            return None
        return BeautifulSoup(r.text, "lxml")
    except requests.RequestException:
        return None


def _extract_organic_results(soup: BeautifulSoup) -> list[dict]:
    results: list[dict] = []
    # Modern Google results use various selectors; try multiple
    for g in soup.select("div.g, div[data-hveid], div[data-ved]"):
        link = g.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        if not href.startswith("http"):
            continue
        title_el = g.find("h3")
        title = title_el.get_text(strip=True) if title_el else ""
        results.append({"url": href, "title": title})
    return results


def _has_knowledge_panel(soup: BeautifulSoup) -> bool:
    return bool(
        soup.find("div", class_=re.compile("kp-blk|knowledge_panel|kno-kp"))
        or soup.find("g-section-with-header")
    )


def _has_featured_snippet(soup: BeautifulSoup) -> bool:
    return bool(
        soup.find("div", class_=re.compile("xpdopen|featured-snippet|gILtHc"))
        or soup.find("blockquote", class_=re.compile("gILtHc"))
    )


def _has_people_also_ask(soup: BeautifulSoup) -> bool:
    return bool(soup.find("div", class_=re.compile("related-question-pair|related-question")))


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    brand_query = ctx.host.replace("www.", "").replace("-", " ")
    # If domain looks like example.com, use "example" as brand
    brand = brand_query.split(".")[0]

    # Rate-limit: sleep briefly to be polite
    time.sleep(0.5)
    soup = _fetch_serp(f"{brand}")
    if soup is None:
        findings.append(Finding(
            id="serp.fetch_failed",
            severity=Severity.P3,
            title="SERP fetch failed (rate limit or block)",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Verify brand presence manually or use a SERP API (SerpApi, DataForSEO).",
            effort=Effort.S,
        ))
        return SignalResult(name="serp", score=50, findings=findings, data={"fetch_ok": False})

    organic = _extract_organic_results(soup)
    domain_in_top10 = any(ctx.host in r["url"] for r in organic[:10])
    kp = _has_knowledge_panel(soup)
    snippet = _has_featured_snippet(soup)
    paa = _has_people_also_ask(soup)

    data.update({
        "fetch_ok": True,
        "brand_query": brand,
        "organic_results_count": len(organic),
        "domain_in_top10": domain_in_top10,
        "knowledge_panel": kp,
        "featured_snippet": snippet,
        "people_also_ask": paa,
    })

    if not domain_in_top10:
        findings.append(Finding(
            id="serp.brand.missing",
            severity=Severity.P1,
            title=f"Domain not in top 10 for brand query '{brand}'",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Build brand signals (Organization schema, sameAs, social profiles) and earn branded mentions.",
            effort=Effort.M,
            google_algo_ref="Entity / Knowledge Graph",
        ))

    if not kp:
        findings.append(Finding(
            id="serp.knowledge_panel.missing",
            severity=Severity.P2,
            title="No Knowledge Panel detected for brand query",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add Organization schema with sameAs links to social profiles. Submit to Wikidata/Wikipedia if notable.",
            effort=Effort.L,
            google_algo_ref="Knowledge Graph",
        ))

    if not snippet:
        findings.append(Finding(
            id="serp.featured_snippet.missing",
            severity=Severity.P3,
            title="No featured snippet detected for brand query",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add FAQPage schema and concise definitional paragraphs to capture featured snippets.",
            effort=Effort.M,
            google_algo_ref="Featured Snippets",
        ))

    if not paa:
        findings.append(Finding(
            id="serp.paa.missing",
            severity=Severity.P3,
            title="No People Also Ask block detected",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add question-style H2s and direct answers to trigger PAA expansion.",
            effort=Effort.M,
            google_algo_ref="People Also Ask",
        ))

    score = score_from_findings(100, findings)
    return SignalResult(name="serp", score=score, findings=findings, data=data)
