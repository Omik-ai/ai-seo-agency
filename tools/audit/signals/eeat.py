"""E-E-A-T signal — Experience, Expertise, Authoritativeness, Trust.

Checks Google's Helpful Content / E-E-A-T surface:
- Organization schema on homepage
- Per-article author schema with sameAs
- Date freshness (dateModified within 730 days)
- Author byline visible in DOM
- Contact page discoverable
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings
from .schema import _extract_jsonld, _types, _page_kind


STALE_DAYS = 730


def _parse_iso(s: str | None) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    # Trim microseconds / timezones
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.replace("Z", "+0000") if fmt == "%Y-%m-%dT%H:%M:%S%z" else s.rstrip("Z"), fmt.replace("Z", ""))
        except ValueError:
            continue
    # last-ditch
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    # ── Homepage org + contact ────────────────────────────────
    homepage = next((p for p in ctx.pages if p.final_url.rstrip("/") == ctx.base_url.rstrip("/") and p.html), None)
    has_org = False
    if homepage:
        items = _extract_jsonld(homepage.html)
        for it in items:
            if any(t in ("Organization", "LocalBusiness") for t in _types(it)):
                has_org = True
                data["organization"] = {
                    "name": it.get("name"),
                    "has_sameAs": bool(it.get("sameAs")),
                    "has_logo": bool(it.get("logo")),
                }
                if not it.get("sameAs"):
                    findings.append(Finding(
                        id="eeat.org.missing_sameAs",
                        severity=Severity.P2,
                        title="Organization schema missing sameAs (social profiles)",
                        evidence=Evidence(url=homepage.final_url),
                        recommendation="Add `sameAs` array pointing to LinkedIn, X/Twitter, GitHub, etc. Strongest entity signal.",
                        effort=Effort.S,
                        google_algo_ref="Knowledge Graph / E-E-A-T",
                    ))
                break
        if not has_org:
            findings.append(Finding(
                id="eeat.org.missing",
                severity=Severity.P1,
                title="No Organization schema on homepage",
                evidence=Evidence(url=homepage.final_url),
                recommendation="Add Organization JSON-LD with name, url, logo, sameAs.",
                effort=Effort.S,
                google_algo_ref="E-E-A-T / Authoritativeness",
            ))

    # Contact page discovery: look for internal link to /contact, /about, or mailto
    contact_found = False
    about_found = False
    for p in ctx.pages:
        path = urlparse(p.final_url).path.lower()
        if "contact" in path:
            contact_found = True
        if "about" in path:
            about_found = True
        if p.html and ("mailto:" in p.html):
            contact_found = True
    data["contact_page_found"] = contact_found
    data["about_page_found"] = about_found
    if not contact_found:
        findings.append(Finding(
            id="eeat.contact.missing",
            severity=Severity.P2,
            title="No Contact page or mailto: link found",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add a /contact page with business email + physical address. Basic trust signal.",
            effort=Effort.S,
            google_algo_ref="E-E-A-T / Trustworthiness",
        ))
    if not about_found:
        findings.append(Finding(
            id="eeat.about.missing",
            severity=Severity.P2,
            title="No About page found",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Add an /about page covering team, history, credentials. Expertise signal.",
            effort=Effort.M,
            google_algo_ref="E-E-A-T / Expertise",
        ))

    # ── Per-article author + dates ────────────────────────────
    article_pages = [p for p in ctx.pages if p.html and _page_kind(p.final_url, p.html) == "article"]
    data["article_pages_count"] = len(article_pages)
    author_ok = 0
    dates_ok = 0
    stale = 0
    byline_visible = 0
    author_with_sameas = 0

    today = datetime.utcnow()
    for p in article_pages:
        items = _extract_jsonld(p.html)
        soup = BeautifulSoup(p.html, "lxml")
        found_article_schema = False
        for it in items:
            if not any(t in ("Article", "BlogPosting", "NewsArticle") for t in _types(it)):
                continue
            found_article_schema = True
            author = it.get("author")
            name = None
            same_as = None
            if isinstance(author, dict):
                name = author.get("name")
                same_as = author.get("sameAs")
            elif isinstance(author, str):
                name = author
            if name:
                author_ok += 1
                if same_as:
                    author_with_sameas += 1
                else:
                    findings.append(Finding(
                        id="eeat.author.missing_sameAs",
                        severity=Severity.P2,
                        title=f"Author on {p.final_url} has no sameAs link",
                        evidence=Evidence(url=p.final_url, value=name),
                        recommendation="Add author.sameAs linking to the author's LinkedIn / X / personal site. Entity verification.",
                        effort=Effort.S,
                        google_algo_ref="E-E-A-T / Author entity",
                    ))
                # Byline visible in DOM?
                if name in soup.get_text():
                    byline_visible += 1
                else:
                    findings.append(Finding(
                        id="eeat.author.not_visible",
                        severity=Severity.P2,
                        title=f"Author '{name}' not visible on page {p.final_url}",
                        evidence=Evidence(url=p.final_url, value=name),
                        recommendation="Display author byline in the article; schema-only bylines weaken the signal.",
                        effort=Effort.S,
                    ))
            else:
                findings.append(Finding(
                    id="eeat.author.missing",
                    severity=Severity.P1,
                    title=f"Article missing author on {p.final_url}",
                    evidence=Evidence(url=p.final_url),
                    recommendation="Add author.@type=Person with name (and ideally sameAs).",
                    effort=Effort.S,
                    google_algo_ref="Helpful Content / E-E-A-T",
                ))

            published = _parse_iso(it.get("datePublished"))
            modified = _parse_iso(it.get("dateModified") or it.get("datePublished"))
            if published or modified:
                dates_ok += 1
            if modified:
                # Normalize tz
                mod_naive = modified.replace(tzinfo=None)
                age_days = (today - mod_naive).days
                if age_days > STALE_DAYS:
                    stale += 1
                    findings.append(Finding(
                        id="eeat.content.stale",
                        severity=Severity.P2,
                        title=f"Content stale ({age_days // 365} years old) on {p.final_url}",
                        evidence=Evidence(url=p.final_url, value=modified.isoformat()),
                        recommendation="Refresh and update dateModified. Freshness helps Helpful Content classifier.",
                        effort=Effort.M,
                        google_algo_ref="Helpful Content / Freshness",
                    ))
            break
        if not found_article_schema and article_pages:
            # covered by schema signal; skip duplicate finding here
            pass

    data.update({
        "articles_with_author": author_ok,
        "articles_with_author_sameAs": author_with_sameas,
        "articles_with_dates": dates_ok,
        "articles_stale": stale,
        "articles_byline_visible": byline_visible,
    })

    score = score_from_findings(100, findings)
    return SignalResult(name="eeat", score=score, findings=findings, data=data)
