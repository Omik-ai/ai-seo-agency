"""Topical authority signal.

Builds a topic-cluster graph from URL paths + content.
Checks internal link density within clusters, content freshness,
and entity consistency across pages.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from urllib.parse import urlparse

from tools.audit.report import Finding, SignalResult, Severity, Evidence, Effort
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.audit.engine import AuditContext


def _path_topic(url: str) -> str:
    """Extract topic slug from URL path."""
    path = urlparse(url).path.strip("/")
    parts = [p for p in path.split("/") if p and not re.match(r"^\d+$", p)]
    if not parts:
        return "root"
    # Use first path segment as topic (e.g. /blog/seo-tips -> blog)
    return parts[0].lower()


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    stop = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "to", "of",
        "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "during", "before", "after", "above", "below", "between", "under",
        "again", "further", "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "each", "few", "more", "most", "other", "some",
        "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
        "very", "just", "and", "but", "if", "or", "because", "until", "while",
        "this", "that", "these", "those", "you", "your", "it", "its", "they",
        "them", "their", "what", "which", "who", "whom", "whose", "i", "me",
        "my", "we", "our", "he", "him", "his", "she", "her",
    }
    return [w for w in words if w not in stop and len(w) > 2]


def _tfidf(docs: list[list[str]]) -> list[dict[str, float]]:
    """Compute TF-IDF vectors for each document."""
    if not docs:
        return []
    df = Counter()
    for doc in docs:
        unique = set(doc)
        for term in unique:
            df[term] += 1
    n = len(docs)
    vectors = []
    for doc in docs:
        tf = Counter(doc)
        total = len(doc) or 1
        vec = {}
        for term, count in tf.items():
            idf = math.log((n + 1) / (df[term] + 1)) + 1
            vec[term] = (count / total) * idf
        vectors.append(vec)
    return vectors


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two sparse vectors."""
    shared = set(a) & set(b)
    if not shared:
        return 0.0
    dot = sum(a[k] * b[k] for k in shared)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def check(ctx: AuditContext) -> SignalResult:
    findings: list[Finding] = []

    # --- 1. Topic clustering from URL paths ---
    topic_pages: dict[str, list] = defaultdict(list)
    for p in ctx.pages:
        if not p.html or p.status >= 400:
            continue
        topic = _path_topic(p.final_url)
        topic_pages[topic].append(p)

    # --- 2. Internal link density per topic ---
    topic_link_density: dict[str, float] = {}
    for topic, pages in topic_pages.items():
        if len(pages) < 2:
            continue
        topic_urls = {p.final_url for p in pages}
        internal_links = 0
        total_links = 0
        for p in pages:
            if not p.soup:
                continue
            for a in p.soup.find_all("a", href=True):
                href = a["href"]
                total_links += 1
                if href in topic_urls or href.startswith("/" + topic + "/"):
                    internal_links += 1
        if total_links > 0:
            topic_link_density[topic] = round(internal_links / total_links * 100, 1)
        else:
            topic_link_density[topic] = 0.0

    # --- 3. Content similarity within topics ---
    topic_cohesion: dict[str, float] = {}
    for topic, pages in topic_pages.items():
        if len(pages) < 2:
            continue
        docs = []
        for p in pages:
            soup = p.soup
            text = soup.get_text(separator=" ", strip=True) if soup else ""
            docs.append(_tokenize(text))
        vectors = _tfidf(docs)
        sims = []
        for i in range(len(vectors)):
            for j in range(i + 1, len(vectors)):
                sims.append(_cosine(vectors[i], vectors[j]))
        if sims:
            topic_cohesion[topic] = round(sum(sims) / len(sims) * 100, 1)
        else:
            topic_cohesion[topic] = 0.0

    # --- 4. Content freshness per topic ---
    topic_freshness: dict[str, float] = {}
    now = ctx.config.__dict__.get("__now__", 0) if ctx.config else 0
    if not now:
        import time as tmod
        now = int(tmod.time())
    for topic, pages in topic_pages.items():
        ages = []
        for p in pages:
            if p.soup:
                for meta in p.soup.find_all("meta"):
                    if meta.get("property") == "article:published_time":
                        val = meta.get("content", "")
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                            ages.append((now - dt.timestamp()) / 86400)
                        except Exception:
                            pass
                    elif meta.get("name") == "date":
                        val = meta.get("content", "")
                        try:
                            from datetime import datetime
                            dt = datetime.strptime(val, "%Y-%m-%d")
                            ages.append((now - dt.timestamp()) / 86400)
                        except Exception:
                            pass
        if ages:
            topic_freshness[topic] = round(sum(ages) / len(ages), 0)
        else:
            topic_freshness[topic] = -1

    # --- 5. Findings generation ---
    for topic, density in topic_link_density.items():
        if density < 30:
            findings.append(Finding(
                id="topical_authority.low_internal_density",
                severity=Severity.P2,
                title=f"Topic '{topic}' has low internal link density ({density}%)",
                evidence=Evidence(url=topic, value={"density": density}),
                recommendation="Add more internal links between pages in the same topic cluster.",
                effort=Effort.M,
                google_algo_ref="Helpful Content System / Topical Authority",
            ))

    for topic, cohesion in topic_cohesion.items():
        if cohesion < 20:
            findings.append(Finding(
                id="topical_authority.low_cohesion",
                severity=Severity.P2,
                title=f"Topic '{topic}' pages are semantically disconnected ({cohesion}% cohesion)",
                evidence=Evidence(url=topic, value={"cohesion": cohesion}),
                recommendation="Unify terminology and cover sub-topics consistently across cluster pages.",
                effort=Effort.M,
                google_algo_ref="Helpful Content System / Topical Authority",
            ))

    for topic, age in topic_freshness.items():
        if age > 730:  # > 2 years
            findings.append(Finding(
                id="topical_authority.stale_cluster",
                severity=Severity.P2,
                title=f"Topic '{topic}' has stale content (avg {int(age)} days old)",
                evidence=Evidence(url=topic, value={"avg_age_days": age}),
                recommendation="Refresh pillar content and update supporting articles.",
                effort=Effort.M,
                google_algo_ref="Freshness / Query Deserves Freshness",
            ))

    data = {
        "topics": list(topic_pages.keys()),
        "topic_page_counts": {k: len(v) for k, v in topic_pages.items()},
        "internal_link_density": topic_link_density,
        "topic_cohesion": topic_cohesion,
        "topic_freshness": topic_freshness,
    }

    return SignalResult(
        name="topical_authority",
        findings=findings,
        score=None,
        data=data,
    )
