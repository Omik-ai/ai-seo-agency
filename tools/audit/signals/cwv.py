"""Core Web Vitals signal — PageSpeed Insights API wrapper.

Thresholds (2024 standard, INP replaced FID):
  LCP  ≤ 2.5s  good, ≤ 4.0s needs-improvement, else poor
  INP  ≤ 200ms good, ≤ 500ms needs-improvement, else poor
  CLS  ≤ 0.1   good, ≤ 0.25 needs-improvement, else poor
  TTFB ≤ 800ms good
"""
from __future__ import annotations

import os

import requests

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def _run_psi(url: str, strategy: str = "mobile", api_key: str | None = None) -> dict | None:
    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "seo", "accessibility", "best-practices"],
    }
    if api_key:
        params["key"] = api_key
    try:
        r = requests.get(PSI_ENDPOINT, params=params, timeout=90)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.RequestException:
        return None


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {"pages": [], "enabled": True}

    cfg = ctx.config
    if cfg and cfg.no_psi:
        data["enabled"] = False
        data["reason"] = "--no-psi flag"
        findings.append(Finding(
            id="cwv.psi.disabled",
            severity=Severity.P3,
            title="Core Web Vitals check skipped (PSI disabled)",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Re-run without --no-psi and with a PAGESPEED_API_KEY for CWV data.",
            effort=Effort.S,
        ))
        # Half credit for not measuring.
        return SignalResult(name="cwv", score=50, findings=findings, data=data)

    api_key = (cfg.psi_key if cfg else None) or os.environ.get("PAGESPEED_API_KEY")

    # Pick homepage + up to 4 other pages
    sample = []
    homepage = None
    for p in ctx.pages:
        if p.status != 200 or not p.html:
            continue
        if p.final_url.rstrip("/") == ctx.base_url.rstrip("/"):
            homepage = p.final_url
        else:
            sample.append(p.final_url)
    targets: list[str] = []
    if homepage:
        targets.append(homepage)
    targets.extend(sample[:4])
    if not targets:
        return SignalResult(name="cwv", score=0, findings=findings, data=data)

    lh_scores: list[int] = []
    for url in targets:
        result = _run_psi(url, "mobile", api_key)
        if not result:
            ctx.warnings.append(f"PSI call failed for {url}")
            continue
        lhr = result.get("lighthouseResult", {})
        cats = lhr.get("categories", {})
        audits = lhr.get("audits", {})
        perf = round((cats.get("performance", {}).get("score") or 0) * 100)
        seo = round((cats.get("seo", {}).get("score") or 0) * 100)
        a11y = round((cats.get("accessibility", {}).get("score") or 0) * 100)
        lh_scores.append(perf)

        def _num(key: str) -> float | None:
            v = audits.get(key, {}).get("numericValue")
            return v if isinstance(v, (int, float)) else None

        lcp = _num("largest-contentful-paint")
        inp = _num("interaction-to-next-paint") or _num("experimental-interaction-to-next-paint")
        cls = _num("cumulative-layout-shift")
        ttfb = _num("server-response-time")

        page_data = {
            "url": url,
            "performance": perf,
            "seo": seo,
            "accessibility": a11y,
            "lcp_ms": lcp,
            "inp_ms": inp,
            "cls": cls,
            "ttfb_ms": ttfb,
        }
        data["pages"].append(page_data)

        if perf < 50:
            findings.append(Finding(
                id="cwv.performance.poor",
                severity=Severity.P0,
                title=f"Lighthouse performance {perf}/100 on {url}",
                evidence=Evidence(url=url, value=perf),
                recommendation="Performance <50 is a serious UX and ranking drag. Start with LCP image optimization and JS reduction.",
                effort=Effort.L,
                google_algo_ref="Page Experience / Core Web Vitals",
            ))
        if lcp and lcp > 2500:
            findings.append(Finding(
                id="cwv.lcp.slow",
                severity=Severity.P1 if lcp <= 4000 else Severity.P0,
                title=f"LCP {int(lcp)}ms on {url} (target ≤ 2500ms)",
                evidence=Evidence(url=url, value=lcp),
                recommendation="Optimize the largest image: preload, WebP/AVIF, correct sizing, CDN.",
                effort=Effort.M,
                google_algo_ref="Core Web Vitals: LCP",
            ))
        if inp and inp > 200:
            findings.append(Finding(
                id="cwv.inp.slow",
                severity=Severity.P1 if inp <= 500 else Severity.P0,
                title=f"INP {int(inp)}ms on {url} (target ≤ 200ms, 2024 standard)",
                evidence=Evidence(url=url, value=inp),
                recommendation="Reduce main-thread work, break up long tasks, debounce event handlers.",
                effort=Effort.L,
                google_algo_ref="Core Web Vitals: INP (March 2024)",
            ))
        if cls and cls > 0.1:
            findings.append(Finding(
                id="cwv.cls.high",
                severity=Severity.P1 if cls <= 0.25 else Severity.P0,
                title=f"CLS {cls:.3f} on {url} (target ≤ 0.1)",
                evidence=Evidence(url=url, value=cls),
                recommendation="Reserve space for images/ads with width/height, avoid inserting DOM above the fold.",
                effort=Effort.M,
                google_algo_ref="Core Web Vitals: CLS",
            ))
        if ttfb and ttfb > 800:
            findings.append(Finding(
                id="cwv.ttfb.slow",
                severity=Severity.P2,
                title=f"TTFB {int(ttfb)}ms on {url} (target ≤ 800ms)",
                evidence=Evidence(url=url, value=ttfb),
                recommendation="Improve server response time: caching, closer CDN edge, faster DB queries.",
                effort=Effort.M,
            ))
        if seo < 90:
            findings.append(Finding(
                id="cwv.lh_seo.suboptimal",
                severity=Severity.P3,
                title=f"Lighthouse SEO {seo}/100 on {url}",
                evidence=Evidence(url=url, value=seo),
                recommendation="Fix Lighthouse SEO audit failures (indexable, meta description, robots, crawlable links).",
                effort=Effort.S,
            ))

    base = round(sum(lh_scores) / len(lh_scores)) if lh_scores else 0
    # Subtract finding penalties but keep Lighthouse perf as the floor signal.
    score = score_from_findings(base if base > 0 else 100, findings)
    return SignalResult(name="cwv", score=score, findings=findings, data=data)
