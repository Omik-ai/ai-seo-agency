"""Internal link graph signal — orphans, click depth, anchor distribution."""
from __future__ import annotations

from collections import Counter, deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


GENERIC_ANCHORS = {"click here", "read more", "learn more", "here", "this", "link", "more", "continue"}


def _norm(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/").lower()


def check(ctx) -> SignalResult:
    findings: list[Finding] = []

    # Build graph from crawled pages
    inbound: dict[str, set[str]] = {}
    edges: dict[str, list[str]] = {}  # src -> [dests]
    all_anchors: list[str] = []

    nodes: set[str] = {_norm(p.final_url) for p in ctx.pages if p.status == 200}

    for p in ctx.pages:
        if p.status != 200 or not p.html:
            continue
        soup = BeautifulSoup(p.html, "lxml")
        src = _norm(p.final_url)
        edges.setdefault(src, [])
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            full = _norm(urljoin(p.final_url, href))
            host = urlparse(full).netloc.lower().replace("www.", "")
            if host != ctx.host:
                continue
            anchor = a.get_text(strip=True)
            all_anchors.append(anchor.lower())
            edges[src].append(full)
            inbound.setdefault(full, set()).add(src)

    # Orphans: nodes in sitemap (and in crawl) with zero inbound from other nodes
    orphans: list[str] = []
    for node in nodes:
        inset = inbound.get(node, set()) - {node}
        if not inset:
            # Exclude homepage (it's the root; no one links TO home except via nav)
            if node == _norm(ctx.base_url):
                continue
            orphans.append(node)

    for o in orphans[:10]:
        findings.append(Finding(
            id="linkgraph.orphan",
            severity=Severity.P1,
            title=f"Orphan page (no internal links point to it): {o}",
            evidence=Evidence(url=o),
            recommendation="Link to this page from at least 1 relevant hub page so Google can discover it via crawl.",
            effort=Effort.S,
            google_algo_ref="Crawling & link equity",
        ))
    if len(orphans) > 10:
        findings.append(Finding(
            id="linkgraph.orphan.bulk",
            severity=Severity.P1,
            title=f"{len(orphans)} orphan pages total",
            evidence=Evidence(url=ctx.base_url, value=len(orphans)),
            recommendation="Review orphan list; add internal links from hub pages or the sitemap-linked menu.",
            effort=Effort.M,
        ))

    # Click depth from homepage (BFS)
    home = _norm(ctx.base_url)
    depth: dict[str, int] = {home: 0}
    q = deque([home])
    while q:
        n = q.popleft()
        for dst in edges.get(n, []):
            if dst not in depth:
                depth[dst] = depth[n] + 1
                q.append(dst)
    deep_pages = [(u, d) for u, d in depth.items() if d > 3 and u in nodes]
    for u, d in deep_pages[:5]:
        findings.append(Finding(
            id="linkgraph.depth.high",
            severity=Severity.P2,
            title=f"Click depth {d} (target ≤3) on {u}",
            evidence=Evidence(url=u, value=d),
            recommendation="Add hub-page or navigation links to reduce click depth to ≤3.",
            effort=Effort.M,
            google_algo_ref="Site architecture / crawl depth",
        ))

    # Anchor text distribution
    anchor_counts = Counter([a for a in all_anchors if a])
    total_anchors = sum(anchor_counts.values())
    generic_count = sum(c for a, c in anchor_counts.items() if a in GENERIC_ANCHORS)
    generic_pct = round(100 * generic_count / total_anchors, 1) if total_anchors else 0
    if generic_pct > 30:
        findings.append(Finding(
            id="linkgraph.anchor.generic",
            severity=Severity.P3,
            title=f"{generic_pct}% of anchor text is generic ('click here', 'read more')",
            evidence=Evidence(url=ctx.base_url, value=generic_pct),
            recommendation="Use descriptive, keyword-informative anchors. Target <20% generic.",
            effort=Effort.M,
            google_algo_ref="Anchor text relevance",
        ))

    data = {
        "nodes": len(nodes),
        "edges": sum(len(v) for v in edges.values()),
        "orphans_count": len(orphans),
        "orphans_sample": orphans[:20],
        "max_depth": max(depth.values()) if depth else 0,
        "deep_pages_count": len(deep_pages),
        "generic_anchor_pct": generic_pct,
        "top_anchors": anchor_counts.most_common(10),
    }

    score = score_from_findings(100, findings)
    return SignalResult(name="linkgraph", score=score, findings=findings, data=data)
