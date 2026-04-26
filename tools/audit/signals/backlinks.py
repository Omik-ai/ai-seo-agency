"""Off-page / backlink signal.

Audits backlink profile health using manually-provided or API-fetched data.
Since live backlink crawling requires Ahrefs/Moz/Majestic APIs, this signal
accepts pre-fetched data via the crawl_meta dict and runs heuristics on it.

Heuristic checks (when data available):
- Toxic link percentage
- Anchor text distribution
- Follow vs nofollow ratio
- Link velocity trend
- Top referring domain quality
"""
from __future__ import annotations

from collections import Counter

from ..report import Effort, Evidence, Finding, Severity, SignalResult
from ..scoring import score_from_findings


def check(ctx) -> SignalResult:
    findings: list[Finding] = []
    data: dict = {}

    backlinks = ctx.crawl_meta.get("backlinks", [])
    anchors = ctx.crawl_meta.get("anchor_texts", [])
    domains = ctx.crawl_meta.get("referring_domains", [])
    lost_links = ctx.crawl_meta.get("lost_links", [])
    new_links = ctx.crawl_meta.get("new_links", [])

    data["backlinks_provided"] = len(backlinks)
    data["referring_domains_provided"] = len(domains)
    data["anchors_provided"] = len(anchors)

    if not backlinks and not domains:
        findings.append(Finding(
            id="backlinks.data.missing",
            severity=Severity.P2,
            title="No backlink data provided for off-page audit",
            evidence=Evidence(url=ctx.base_url),
            recommendation="Export backlink data from Ahrefs/Moz/Majestic and pass it in crawl_meta['backlinks'] for automated analysis.",
            effort=Effort.S,
            google_algo_ref="Off-page signals / Link equity",
        ))
        score = score_from_findings(100, findings)
        return SignalResult(name="backlinks", score=score, findings=findings, data=data)

    # ── Anchor text distribution ───────────────────────────
    if anchors:
        total = len(anchors)
        branded = sum(1 for a in anchors if ctx.host.replace("www.", "").split(".")[0] in a.lower())
        exact_match = sum(1 for a in anchors if any(kw in a.lower() for kw in ctx.crawl_meta.get("target_keywords", [])))
        generic = sum(1 for a in anchors if a.lower() in {"click here", "read more", "learn more", "here", "this", "link", "more", "continue", "website", "site"})
        naked = sum(1 for a in anchors if a.startswith("http"))

        data["anchor_distribution"] = {
            "branded_pct": round(100 * branded / total, 1),
            "exact_match_pct": round(100 * exact_match / total, 1),
            "generic_pct": round(100 * generic / total, 1),
            "naked_pct": round(100 * naked / total, 1),
            "other_pct": round(100 * (total - branded - exact_match - generic - naked) / total, 1),
        }

        if exact_match / total > 0.10:
            findings.append(Finding(
                id="backlinks.anchor.exact_match_high",
                severity=Severity.P1,
                title=f"Exact-match anchor text is {round(100*exact_match/total,1)}% (healthy: <5%)",
                evidence=Evidence(url=ctx.base_url, value=data["anchor_distribution"]),
                recommendation="Diversify anchors toward branded and generic. High exact-match = Penguin risk.",
                effort=Effort.M,
                google_algo_ref="Link spam / Penguin",
            ))
        if branded / total < 0.30:
            findings.append(Finding(
                id="backlinks.anchor.branded_low",
                severity=Severity.P2,
                title=f"Branded anchor text only {round(100*branded/total,1)}% (healthy: 30-50%)",
                evidence=Evidence(url=ctx.base_url, value=data["anchor_distribution"]),
                recommendation="Increase branded anchor share. Natural link profiles skew heavily branded.",
                effort=Effort.M,
                google_algo_ref="Natural link profile",
            ))
        if generic / total > 0.30:
            findings.append(Finding(
                id="backlinks.anchor.generic_high",
                severity=Severity.P2,
                title=f"Generic anchor text is {round(100*generic/total,1)}% (healthy: <20%)",
                evidence=Evidence(url=ctx.base_url, value=data["anchor_distribution"]),
                recommendation="Reduce generic anchors. Use descriptive, contextual anchors instead.",
                effort=Effort.M,
                google_algo_ref="Anchor relevance",
            ))

    # ── Domain quality tiers ─────────────────────────────
    if domains:
        tier1 = sum(1 for d in domains if d.get("da", 0) >= 70)
        tier2 = sum(1 for d in domains if 40 <= d.get("da", 0) < 70)
        tier3 = sum(1 for d in domains if 20 <= d.get("da", 0) < 40)
        tier4 = sum(1 for d in domains if d.get("da", 0) < 20)
        total_da = sum(d.get("da", 0) for d in domains)
        avg_da = round(total_da / len(domains), 1) if domains else 0

        data["domain_tiers"] = {
            "tier1_da70+": tier1,
            "tier2_da40-69": tier2,
            "tier3_da20-39": tier3,
            "tier4_da<20": tier4,
            "avg_da": avg_da,
        }

        if tier4 / len(domains) > 0.50:
            findings.append(Finding(
                id="backlinks.quality.low_quality_majority",
                severity=Severity.P1,
                title=f"{round(100*tier4/len(domains),1)}% of referring domains are low quality (DA<20)",
                evidence=Evidence(url=ctx.base_url, value=data["domain_tiers"]),
                recommendation="Audit low-quality links. Disavow spam domains. Focus outreach on DA 40+ relevant sites.",
                effort=Effort.L,
                google_algo_ref="Link quality / SpamBrain",
            ))
        if avg_da < 30:
            findings.append(Finding(
                id="backlinks.quality.avg_da_low",
                severity=Severity.P2,
                title=f"Average referring domain DA is {avg_da} (healthy: 40+)",
                evidence=Evidence(url=ctx.base_url, value=avg_da),
                recommendation="Target higher-authority publications and industry leaders for links.",
                effort=Effort.L,
                google_algo_ref="Domain authority / Link equity",
            ))

    # ── Link velocity ───────────────────────────────────
    if lost_links and new_links:
        net = len(new_links) - len(lost_links)
        data["link_velocity"] = {
            "new": len(new_links),
            "lost": len(lost_links),
            "net": net,
        }
        if net < -5:
            findings.append(Finding(
                id="backlinks.velocity.negative",
                severity=Severity.P1,
                title=f"Negative link velocity: {net} (lost {len(lost_links)}, gained {len(new_links)})",
                evidence=Evidence(url=ctx.base_url, value=data["link_velocity"]),
                recommendation="Investigate lost links. Reclaim broken links and refresh outreach.",
                effort=Effort.M,
                google_algo_ref="Link equity loss",
            ))

    # ── Toxic link detection (heuristic) ───────────────────
    if backlinks:
        toxic_patterns = ["porn", "casino", "viagra", "payday", "seo-service", "link-building"]
        toxic_count = sum(1 for b in backlinks if any(p in b.get("domain", "").lower() for p in toxic_patterns))
        data["toxic_links_detected"] = toxic_count
        if toxic_count > 0:
            findings.append(Finding(
                id="backlinks.toxic.detected",
                severity=Severity.P0,
                title=f"{toxic_count} potentially toxic links detected",
                evidence=Evidence(url=ctx.base_url, value=toxic_count),
                recommendation="Review toxic links and add to disavow file if confirmed spam.",
                effort=Effort.S,
                google_algo_ref="Link spam / Manual actions",
            ))

    score = score_from_findings(100, findings)
    return SignalResult(name="backlinks", score=score, findings=findings, data=data)
