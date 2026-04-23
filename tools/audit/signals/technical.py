"""Technical signal: robots, sitemap, canonicals, redirects, status, headers."""
from __future__ import annotations

from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    # ── robots.txt ─────────────────────────────────────────────
    disallows = ctx.crawl_meta.get("robots_disallows", [])
    robots_raw = ctx.crawl_meta.get("robots_raw", "")
    data["robots_disallows"] = disallows
    data["has_robots_txt"] = bool(robots_raw)

    if not robots_raw:
        findings.append(Finding(
            id="technical.robots.missing",
            severity=Severity.P2,
            title="No robots.txt found",
            evidence=Evidence(url=f"{ctx.base_url}/robots.txt"),
            recommendation="Create a robots.txt at the site root. At minimum: `User-agent: *` + a `Sitemap:` line.",
            effort=Effort.S,
            google_algo_ref="Google crawler guidance",
        ))
    else:
        if "/" in disallows:
            findings.append(Finding(
                id="technical.robots.disallow_all",
                severity=Severity.P0,
                title="robots.txt disallows entire site",
                evidence=Evidence(url=f"{ctx.base_url}/robots.txt", snippet="Disallow: /"),
                recommendation="Remove `Disallow: /` for user-agent * / Googlebot. This blocks all crawling.",
                effort=Effort.S,
                google_algo_ref="Crawling & indexing",
            ))
        if "sitemap:" not in robots_raw.lower():
            findings.append(Finding(
                id="technical.robots.no_sitemap_ref",
                severity=Severity.P2,
                title="robots.txt missing Sitemap: directive",
                evidence=Evidence(url=f"{ctx.base_url}/robots.txt"),
                recommendation="Add a `Sitemap: https://<domain>/sitemap.xml` line so crawlers discover your sitemap.",
                effort=Effort.S,
            ))

    # ── sitemap ────────────────────────────────────────────────
    sm_count = ctx.crawl_meta.get("sitemap_url_count", 0)
    data["sitemap_url_count"] = sm_count
    if sm_count == 0:
        findings.append(Finding(
            id="technical.sitemap.missing",
            severity=Severity.P1,
            title="No XML sitemap found",
            evidence=Evidence(url=f"{ctx.base_url}/sitemap.xml"),
            recommendation="Generate and submit an XML sitemap (one URL per indexable page; <50k URLs per file).",
            effort=Effort.M,
            google_algo_ref="Indexing",
        ))

    # ── per-page checks ────────────────────────────────────────
    status_bad = 0
    redirect_chains = 0
    missing_canonical = 0
    cross_domain_canonical = 0
    noindex_pages = 0
    http_pages = 0
    missing_hsts = 0
    pages_checked = 0

    canonical_samples: list[tuple[str, str]] = []

    for p in ctx.pages:
        if p.status == 0:
            continue
        pages_checked += 1

        if p.status >= 400:
            status_bad += 1
            findings.append(Finding(
                id=f"technical.status.{p.status}",
                severity=Severity.P1 if p.status != 410 else Severity.P2,
                title=f"HTTP {p.status} on crawled URL",
                evidence=Evidence(url=p.url, value=p.status),
                recommendation="Fix the broken page or 301 redirect it to the nearest live equivalent.",
                effort=Effort.S,
            ))
            continue

        if len(p.redirect_chain) > 1:
            redirect_chains += 1
            findings.append(Finding(
                id="technical.redirect.chain",
                severity=Severity.P1,
                title=f"Redirect chain ({len(p.redirect_chain)} hops) on {p.url}",
                evidence=Evidence(url=p.url, value=p.redirect_chain),
                recommendation="Collapse to a single 301 hop. Chains waste crawl budget and lose link equity.",
                effort=Effort.M,
            ))

        # X-Robots-Tag
        x_robots = p.headers.get("X-Robots-Tag", "") or p.headers.get("x-robots-tag", "")
        if "noindex" in x_robots.lower():
            noindex_pages += 1
            findings.append(Finding(
                id="technical.xrobots.noindex",
                severity=Severity.P0,
                title=f"X-Robots-Tag noindex on {p.url}",
                evidence=Evidence(url=p.url, snippet=f"X-Robots-Tag: {x_robots}"),
                recommendation="Remove the X-Robots-Tag noindex header unless you truly want this page excluded from Google.",
                effort=Effort.S,
                google_algo_ref="Indexing directive",
            ))

        # HTTPS
        if urlparse(p.final_url).scheme != "https":
            http_pages += 1

        # HSTS
        if not p.headers.get("Strict-Transport-Security"):
            missing_hsts += 1

        # Canonical
        if p.html:
            soup = BeautifulSoup(p.html, "lxml")
            link = soup.find("link", rel=lambda v: v and "canonical" in v)
            if not link or not link.get("href"):
                missing_canonical += 1
                findings.append(Finding(
                    id="technical.canonical.missing",
                    severity=Severity.P1,
                    title=f"Missing canonical tag on {p.final_url}",
                    evidence=Evidence(url=p.final_url),
                    recommendation='Add <link rel="canonical" href="<absolute-url>"> to the <head>.',
                    effort=Effort.S,
                    google_algo_ref="Duplicate content handling",
                ))
            else:
                href = link["href"].strip()
                canonical_samples.append((p.final_url, href))
                canon_host = urlparse(href).netloc.lower().replace("www.", "")
                if canon_host and canon_host != ctx.host:
                    cross_domain_canonical += 1
                    findings.append(Finding(
                        id="technical.canonical.cross_domain",
                        severity=Severity.P0,
                        title=f"Canonical points off-domain on {p.final_url}",
                        evidence=Evidence(url=p.final_url, snippet=href),
                        recommendation="Cross-domain canonical de-indexes the page. Point to the on-domain URL.",
                        effort=Effort.S,
                        google_algo_ref="Canonicalization",
                    ))

    data.update({
        "pages_checked": pages_checked,
        "status_bad_count": status_bad,
        "redirect_chain_count": redirect_chains,
        "missing_canonical_count": missing_canonical,
        "cross_domain_canonical_count": cross_domain_canonical,
        "xrobots_noindex_count": noindex_pages,
        "http_pages_count": http_pages,
        "missing_hsts_count": missing_hsts,
        "canonical_samples": canonical_samples[:5],
    })

    if http_pages > 0:
        findings.append(Finding(
            id="technical.https.missing",
            severity=Severity.P0,
            title=f"{http_pages} page(s) served over HTTP, not HTTPS",
            evidence=Evidence(url=ctx.base_url, value=http_pages),
            recommendation="Force HTTPS via 301 redirect + HSTS. HTTP is a direct ranking and security negative.",
            effort=Effort.M,
            google_algo_ref="Page Experience / Security",
        ))

    if pages_checked > 0 and missing_hsts >= pages_checked // 2:
        findings.append(Finding(
            id="technical.hsts.missing",
            severity=Severity.P3,
            title="HSTS header missing on most pages",
            evidence=Evidence(url=ctx.base_url, value=f"{missing_hsts}/{pages_checked}"),
            recommendation="Add `Strict-Transport-Security: max-age=31536000; includeSubDomains` response header.",
            effort=Effort.S,
        ))

    score = score_from_findings(100, findings)
    return SignalResult(name="technical", score=score, findings=findings, data=data)
