"""HTTP fetchers.

HttpFetcher — v1 lean impl, requests + bs4.
RenderedFetcher — Playwright-backed impl for JS-rendered HTML diff.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import urlparse

import requests

USER_AGENT = "SEOAuditEngine/0.2.0 (+https://github.com/RavenRepo/ai-seo-agency)"
TIMEOUT_S = 20

SPA_MARKERS = [
    'id="__next"',
    'id="root"',
    'id="app"',
    "__NEXT_DATA__",
    "window.__remixContext",
    "window.__NUXT__",
    "window.__INITIAL_STATE__",
    'data-reactroot',
    'data-reactid',
]


@dataclass
class FetchResult:
    url: str
    final_url: str
    status: int
    html: str
    headers: dict
    redirect_chain: list[str] = field(default_factory=list)
    error: str | None = None
    js_rendered: bool = False
    elapsed_ms: int = 0
    _soup = None

    @property
    def soup(self):
        if self._soup is None and self.html:
            from bs4 import BeautifulSoup
            self._soup = BeautifulSoup(self.html, "lxml")
        return self._soup


class Fetcher(Protocol):
    def fetch(self, url: str) -> FetchResult: ...


class HttpFetcher:
    """Raw HTTP fetch. No JS execution."""

    def __init__(self, user_agent: str = USER_AGENT, timeout: int = TIMEOUT_S):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent, "Accept-Language": "en-US,en;q=0.9"})
        self.timeout = timeout

    def fetch(self, url: str) -> FetchResult:
        start = time.time()
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            chain = [h.url for h in resp.history] if resp.history else []
            ctype = resp.headers.get("Content-Type", "").lower()
            keep_body = any(
                t in ctype
                for t in ("text/html", "text/xml", "application/xml", "text/plain", "application/rss")
            )
            return FetchResult(
                url=url,
                final_url=resp.url,
                status=resp.status_code,
                html=resp.text if keep_body else "",
                headers=dict(resp.headers),
                redirect_chain=chain,
                js_rendered=False,
                elapsed_ms=int((time.time() - start) * 1000),
            )
        except requests.RequestException as e:
            return FetchResult(
                url=url,
                final_url=url,
                status=0,
                html="",
                headers={},
                error=str(e),
                elapsed_ms=int((time.time() - start) * 1000),
            )


class RenderedFetcher:
    """Playwright-backed fetcher for JS-rendered HTML."""

    def __init__(self, user_agent: str = USER_AGENT, timeout: int = 30):
        self.user_agent = user_agent
        self.timeout = timeout

    def fetch(self, url: str) -> FetchResult:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return FetchResult(
                url=url,
                final_url=url,
                status=0,
                html="",
                headers={},
                error="playwright not installed. Run: pip install playwright && playwright install chromium",
            )

        start = time.time()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=self.user_agent)
                page = context.new_page()
                resp = page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                html = page.content()
                status = resp.status if resp else 0
                final_url = page.url
                browser.close()
                return FetchResult(
                    url=url,
                    final_url=final_url,
                    status=status,
                    html=html,
                    headers={},
                    js_rendered=True,
                    elapsed_ms=int((time.time() - start) * 1000),
                )
        except Exception as e:
            return FetchResult(
                url=url,
                final_url=url,
                status=0,
                html="",
                headers={},
                error=str(e),
                elapsed_ms=int((time.time() - start) * 1000),
            )


def _detect_spa_framework(html: str) -> str | None:
    html_lower = html.lower()
    for marker in SPA_MARKERS:
        if marker.lower() in html_lower:
            if "next" in marker.lower():
                return "Next.js"
            if "nuxt" in marker.lower():
                return "Nuxt.js"
            if "remix" in marker.lower():
                return "Remix"
            if "react" in marker.lower():
                return "React"
    return None


def compare_rendered_vs_source(domain: str) -> dict:
    """Fetch homepage with both fetchers and compare HTML.

    Returns dict with:
    - has_rendering_diff: bool
    - diff_ratio: float (0.0–1.0, higher = more different)
    - spa_framework: str | None
    - source_len: int
    - rendered_len: int
    - warnings: list[str]
    """
    base, _ = normalize_domain(domain)
    url = base + "/"

    http = HttpFetcher()
    rendered = RenderedFetcher()

    source = http.fetch(url)
    render = rendered.fetch(url)

    warnings: list[str] = []
    if source.error:
        warnings.append(f"source fetch error: {source.error}")
    if render.error:
        warnings.append(f"rendered fetch error: {render.error}")

    source_html = (source.html or "").strip()
    render_html = (render.html or "").strip()

    spa_framework = _detect_spa_framework(source_html)

    if not source_html or not render_html:
        return {
            "has_rendering_diff": False,
            "diff_ratio": 0.0,
            "spa_framework": spa_framework,
            "source_len": len(source_html),
            "rendered_len": len(render_html),
            "warnings": warnings,
        }

    # Crude diff: compare stripped whitespace text content length
    import re
    source_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", source_html)).strip()
    render_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", render_html)).strip()

    max_len = max(len(source_text), len(render_text))
    if max_len == 0:
        diff_ratio = 0.0
    else:
        # Simple LCS-based similarity is too heavy; use word-set Jaccard
        source_words = set(source_text.lower().split())
        render_words = set(render_text.lower().split())
        intersection = len(source_words & render_words)
        union = len(source_words | render_words)
        jaccard = intersection / union if union else 1.0
        diff_ratio = round(1.0 - jaccard, 3)

    has_diff = diff_ratio > 0.3 or (len(render_text) > len(source_text) * 2)

    if has_diff and spa_framework:
        warnings.append(
            f"significant rendering diff detected ({diff_ratio}) with {spa_framework}; audit based on source HTML may miss client-rendered content"
        )

    return {
        "has_rendering_diff": has_diff,
        "diff_ratio": diff_ratio,
        "spa_framework": spa_framework,
        "source_len": len(source_html),
        "rendered_len": len(render_html),
        "warnings": warnings,
    }


def normalize_domain(input_str: str) -> tuple[str, str]:
    """Return (scheme+host, bare_domain)."""
    if "://" not in input_str:
        input_str = "https://" + input_str
    p = urlparse(input_str)
    host = p.netloc or p.path
    host = host.strip("/").lower()
    if host.startswith("www."):
        host = host[4:]
    return f"https://{host}", host
