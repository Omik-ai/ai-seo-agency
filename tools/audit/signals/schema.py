"""JSON-LD schema signal — type-aware validation with Rich Results eligibility."""
from __future__ import annotations

import json
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


# Per-@type required + recommended properties for Google Rich Results.
# Source: developers.google.com/search/docs/appearance/structured-data/* (2024-2026)
TYPE_RULES: dict[str, dict] = {
    "Article": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "dateModified", "publisher"],
    },
    "BlogPosting": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "dateModified", "publisher"],
    },
    "NewsArticle": {
        "required": ["headline", "author", "datePublished", "image"],
        "recommended": ["dateModified", "publisher"],
    },
    "Product": {
        "required": ["name"],
        "recommended": ["image", "description", "brand", "offers", "aggregateRating", "review", "sku"],
    },
    "Offer": {
        "required": ["price", "priceCurrency"],
        "recommended": ["availability", "url", "priceValidUntil"],
    },
    "Organization": {
        "required": ["name", "url"],
        "recommended": ["logo", "sameAs", "contactPoint"],
    },
    "LocalBusiness": {
        "required": ["name", "address"],
        "recommended": ["telephone", "openingHoursSpecification", "geo", "url", "image"],
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "recommended": [],
    },
    "HowTo": {
        "required": ["name", "step"],
        "recommended": ["image", "totalTime", "estimatedCost"],
    },
    "BreadcrumbList": {
        "required": ["itemListElement"],
        "recommended": [],
    },
    "Person": {
        "required": ["name"],
        "recommended": ["url", "sameAs", "jobTitle", "image"],
    },
    "WebSite": {
        "required": ["name", "url"],
        "recommended": ["potentialAction"],  # SearchAction = sitelinks searchbox
    },
    "WebPage": {
        "required": ["name"],
        "recommended": ["description", "url"],
    },
    "Service": {
        "required": ["name", "provider"],
        "recommended": ["areaServed", "description", "serviceType"],
    },
    "Event": {
        "required": ["name", "startDate", "location"],
        "recommended": ["endDate", "performer", "offers", "image"],
    },
    "Recipe": {
        "required": ["name", "recipeIngredient", "recipeInstructions"],
        "recommended": ["image", "nutrition", "cookTime", "prepTime"],
    },
    "VideoObject": {
        "required": ["name", "thumbnailUrl", "uploadDate"],
        "recommended": ["description", "duration", "contentUrl"],
    },
}

JSONLD_PATTERN = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def _extract_jsonld(html: str) -> list[dict]:
    """Returns flattened list of JSON-LD objects (handles @graph)."""
    out: list[dict] = []
    for match in JSONLD_PATTERN.findall(html or ""):
        try:
            data = json.loads(match.strip())
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if "@graph" in item and isinstance(item["@graph"], list):
                for g in item["@graph"]:
                    if isinstance(g, dict):
                        out.append(g)
            else:
                out.append(item)
    return out


def _extract_microdata(soup: BeautifulSoup) -> list[dict]:
    """Extract schema.org microdata (itemscope/itemtype/itemprop)."""
    out: list[dict] = []
    scopes = soup.find_all(attrs={"itemscope": True})
    for scope in scopes:
        itemtype = scope.get("itemtype", "")
        if not itemtype or "schema.org" not in str(itemtype):
            continue
        types = [t.split("/")[-1] for t in str(itemtype).split()]
        props: dict = {}
        for child in scope.find_all(attrs={"itemprop": True}):
            prop_name = child.get("itemprop")
            if not prop_name:
                continue
            if child.get("itemscope"):
                # nested item
                nested_type = child.get("itemtype", "")
                nested = {"@type": nested_type.split("/")[-1] if nested_type else "Thing"}
                for nc in child.find_all(attrs={"itemprop": True}):
                    nc_name = nc.get("itemprop")
                    if nc_name and not nc.get("itemscope"):
                        nested[nc_name] = nc.get_text(strip=True)
                props[prop_name] = nested
            else:
                val = child.get("content") or child.get("href") or child.get("src") or child.get_text(strip=True)
                props[prop_name] = val
        for t in types:
            out.append({"@type": t, **props})
    return out


def _extract_rdfa(soup: BeautifulSoup) -> list[dict]:
    """Extract RDFa (typeof/property/resource)."""
    out: list[dict] = []
    scopes = soup.find_all(attrs={"typeof": True})
    for scope in scopes:
        types = [t.split(":")[-1] for t in str(scope.get("typeof", "")).split()]
        props: dict = {}
        for child in scope.find_all(attrs={"property": True}):
            prop_name = child.get("property")
            if not prop_name:
                continue
            val = child.get("content") or child.get("resource") or child.get("href") or child.get_text(strip=True)
            props[prop_name.split(":")[-1]] = val
        for t in types:
            out.append({"@type": t, **props})
    return out


def _types(item: dict) -> list[str]:
    t = item.get("@type")
    if isinstance(t, str):
        return [t]
    if isinstance(t, list):
        return [str(x) for x in t]
    return []


def _page_kind(url: str, html: str) -> str:
    path = urlparse(url).path.lower().rstrip("/")
    if path in ("", "/"):
        return "homepage"
    if any(seg in path for seg in ("/blog/", "/post/", "/article/", "/news/")):
        return "article"
    if any(seg in path for seg in ("/product/", "/shop/", "/store/")):
        return "product"
    if "/faq" in path or path.endswith("/faq"):
        return "faq"
    if "/about" in path:
        return "about"
    if "/service" in path:
        return "service"
    return "other"


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    type_counts: dict[str, int] = {}
    per_page: list[dict] = []
    pages_with_any_schema = 0

    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        items = _extract_jsonld(p.html)
        soup = BeautifulSoup(p.html, "lxml")
        microdata = _extract_microdata(soup)
        rdfa = _extract_rdfa(soup)
        all_items = items + microdata + rdfa
        if all_items:
            pages_with_any_schema += 1
        types_here: list[str] = []
        for item in all_items:
            types_here.extend(_types(item))
        for t in types_here:
            type_counts[t] = type_counts.get(t, 0) + 1

        kind = _page_kind(p.final_url, p.html)
        per_page.append({
            "url": p.final_url,
            "kind": kind,
            "types": types_here,
            "jsonld_count": len(items),
            "microdata_count": len(microdata),
            "rdfa_count": len(rdfa),
        })

        # ── Per-item validation
        for item in all_items:
            for t in _types(item):
                rule = TYPE_RULES.get(t)
                if not rule:
                    continue
                for req in rule["required"]:
                    if req not in item or item.get(req) in ("", None, []):
                        findings.append(Finding(
                            id=f"schema.{t.lower()}.missing_required.{req}",
                            severity=Severity.P1,
                            title=f"{t} schema missing required property: {req}",
                            evidence=Evidence(
                                url=p.final_url,
                                snippet=json.dumps({k: v for k, v in item.items() if k in ("@type", "name", "headline")})[:140],
                            ),
                            recommendation=f"Add `{req}` to the {t} JSON-LD block. Without it, Rich Results are disabled.",
                            effort=Effort.S,
                            google_algo_ref=f"Rich Results: {t}",
                        ))
                for rec in rule["recommended"]:
                    if rec not in item:
                        findings.append(Finding(
                            id=f"schema.{t.lower()}.missing_recommended.{rec}",
                            severity=Severity.P3,
                            title=f"{t} schema missing recommended property: {rec}",
                            evidence=Evidence(url=p.final_url),
                            recommendation=f"Add `{rec}` to the {t} JSON-LD block for stronger rich-result eligibility.",
                            effort=Effort.S,
                            google_algo_ref=f"Rich Results: {t}",
                        ))

        # ── Misleading-markup: author name in schema should appear in DOM
        for item in all_items:
            if "Article" in _types(item) or "BlogPosting" in _types(item):
                author = item.get("author")
                name = None
                if isinstance(author, dict):
                    name = author.get("name")
                elif isinstance(author, str):
                    name = author
                if name and name not in p.html:
                    findings.append(Finding(
                        id="schema.article.author_not_in_dom",
                        severity=Severity.P1,
                        title=f"Schema author '{name}' not visible in page content",
                        evidence=Evidence(url=p.final_url, value=name),
                        recommendation="Display the author name in the rendered page. Schema-only author = misleading markup.",
                        effort=Effort.S,
                        google_algo_ref="Structured Data policy / E-E-A-T",
                    ))

        # ── BreadcrumbList path alignment
        for item in all_items:
            if "BreadcrumbList" in _types(item):
                elems = item.get("itemListElement") or []
                path_segments = [s for s in urlparse(p.final_url).path.split("/") if s]
                if elems and len(elems) < len(path_segments):
                    findings.append(Finding(
                        id="schema.breadcrumb.path_mismatch",
                        severity=Severity.P2,
                        title=f"BreadcrumbList has fewer items than URL depth ({len(elems)} vs {len(path_segments)})",
                        evidence=Evidence(url=p.final_url),
                        recommendation="Align breadcrumb positions with URL path segments for consistent rich results.",
                        effort=Effort.S,
                    ))

        # ── Expected schema for page kind
        if kind == "homepage":
            has_org = any(_types(i) and ("Organization" in _types(i) or "LocalBusiness" in _types(i)) for i in all_items)
            has_site = any("WebSite" in _types(i) for i in all_items)
            if not has_org:
                findings.append(Finding(
                    id="schema.homepage.no_organization",
                    severity=Severity.P1,
                    title="Homepage missing Organization (or LocalBusiness) schema",
                    evidence=Evidence(url=p.final_url),
                    recommendation="Add Organization JSON-LD with name, url, logo, sameAs (social profiles).",
                    effort=Effort.S,
                    google_algo_ref="Entity / Knowledge Graph",
                ))
            if not has_site:
                findings.append(Finding(
                    id="schema.homepage.no_website",
                    severity=Severity.P3,
                    title="Homepage missing WebSite schema",
                    evidence=Evidence(url=p.final_url),
                    recommendation="Add WebSite JSON-LD with SearchAction to enable sitelinks searchbox.",
                    effort=Effort.S,
                ))
        if kind == "article":
            has_article = any(
                any(t in ("Article", "BlogPosting", "NewsArticle") for t in _types(i))
                for i in all_items
            )
            if not has_article:
                findings.append(Finding(
                    id="schema.article.missing",
                    severity=Severity.P1,
                    title=f"Article page missing Article/BlogPosting schema: {p.final_url}",
                    evidence=Evidence(url=p.final_url),
                    recommendation="Add Article JSON-LD with headline, author.@type=Person, datePublished, image.",
                    effort=Effort.S,
                    google_algo_ref="Rich Results: Article",
                ))

    data = {
        "type_counts": type_counts,
        "pages_with_any_schema": pages_with_any_schema,
        "pages_analyzed": len([p for p in ctx.pages if p.html and p.status < 400]),
        "per_page": per_page[:50],
    }
    score = score_from_findings(100, findings)
    return SignalResult(name="schema", score=score, findings=findings, data=data)
