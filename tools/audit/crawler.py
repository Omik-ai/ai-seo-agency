"""Bounded site crawler.

Strategy:
1. Fetch robots.txt (parse sitemap refs + disallow list)
2. Parse sitemap(s) — sitemap-first seeding
3. If no sitemap, BFS from homepage
4. Stop at max_urls, skip obviously non-HTML extensions
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .fetcher import FetchResult, HttpFetcher


SKIP_EXT = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
    ".css", ".js", ".xml", ".zip", ".mp4", ".mp3", ".woff", ".woff2", ".ttf",
}


def _is_html_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    for ext in SKIP_EXT:
        if path.endswith(ext):
            return False
    return True


def discover_sitemaps(base: str, fetcher: HttpFetcher) -> tuple[list[str], list[str], str]:
    """Return (sitemap_urls, robots_disallows, raw_robots)."""
    robots_url = f"{base.rstrip('/')}/robots.txt"
    r = fetcher.fetch(robots_url)
    sitemaps: list[str] = []
    disallows: list[str] = []
    raw = r.html or ""
    if r.status == 200 and raw:
        current_ua = "*"
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lower = line.lower()
            if lower.startswith("sitemap:"):
                sitemaps.append(line.split(":", 1)[1].strip())
            elif lower.startswith("user-agent:"):
                current_ua = line.split(":", 1)[1].strip().lower()
            elif lower.startswith("disallow:") and current_ua in ("*", "googlebot"):
                path = line.split(":", 1)[1].strip()
                if path:
                    disallows.append(path)
    if not sitemaps:
        # Fallback: try /sitemap.xml
        sitemaps.append(f"{base.rstrip('/')}/sitemap.xml")
    return sitemaps, disallows, raw


def parse_sitemap(url: str, fetcher: HttpFetcher, depth: int = 0) -> list[str]:
    if depth > 3:
        return []
    r = fetcher.fetch(url)
    if r.status != 200 or not (r.html or "").strip():
        return []
    urls: list[str] = []
    try:
        root = ET.fromstring(r.html)
    except ET.ParseError:
        return []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    # Index?
    for sm in root.findall("sm:sitemap", ns):
        loc = sm.find("sm:loc", ns)
        if loc is not None and loc.text:
            urls.extend(parse_sitemap(loc.text.strip(), fetcher, depth + 1))
    # URLs
    for u in root.findall("sm:url", ns):
        loc = u.find("sm:loc", ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls


def extract_internal_links(html: str, page_url: str, base_host: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    out: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(page_url, href)
        host = urlparse(full).netloc.lower().replace("www.", "")
        if host != base_host:
            continue
        if not _is_html_url(full):
            continue
        # Strip fragment
        full = full.split("#", 1)[0]
        out.append(full)
    return out


def crawl(base: str, host: str, max_urls: int, fetcher: HttpFetcher) -> tuple[list[FetchResult], dict]:
    """Crawl up to max_urls HTML pages. Returns (pages, meta)."""
    sitemap_urls, disallows, robots_raw = discover_sitemaps(base, fetcher)
    seeded: list[str] = []
    sitemap_set: set[str] = set()
    for sm in sitemap_urls:
        sm_urls = parse_sitemap(sm, fetcher)
        for u in sm_urls:
            if urlparse(u).netloc.lower().replace("www.", "") == host and _is_html_url(u):
                sitemap_set.add(u)
    if sitemap_set:
        seeded = sorted(sitemap_set)[:max_urls]
    else:
        seeded = [base]

    queue = deque(seeded)
    if base not in queue:
        queue.appendleft(base)
    seen: set[str] = set()
    pages: list[FetchResult] = []

    while queue and len(pages) < max_urls:
        url = queue.popleft()
        url = url.split("#", 1)[0].rstrip("/")
        if not url:
            continue
        # Normalize scheme
        if urlparse(url).scheme == "":
            url = base + ("" if url.startswith("/") else "/") + url.lstrip("/")
        key = url.lower()
        if key in seen:
            continue
        seen.add(key)

        r = fetcher.fetch(url)
        pages.append(r)

        if not r.html or r.status >= 400:
            continue
        # BFS expand only if we didn't seed from sitemap, or to reach linkgraph
        for link in extract_internal_links(r.html, r.final_url, host):
            link_key = link.rstrip("/").lower()
            if link_key not in seen and len(pages) + len(queue) < max_urls * 2:
                queue.append(link)

    meta = {
        "sitemap_urls": sitemap_urls,
        "sitemap_url_count": len(sitemap_set),
        "robots_disallows": disallows,
        "robots_raw": robots_raw[:3000],
        "seeded_from": "sitemap" if sitemap_set else "homepage_bfs",
    }
    return pages, meta
