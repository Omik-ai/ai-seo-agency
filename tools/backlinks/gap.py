"""Link-gap computer.

Compares two backlink profiles (client vs competitor) and surfaces
missing link opportunities.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .fetcher import BacklinkProfile


@dataclass
class LinkGap:
    competitor_domain: str
    client_domain: str
    domains_client_missing: list[str] = field(default_factory=list)
    domains_client_has: list[str] = field(default_factory=list)
    shared_domains: list[str] = field(default_factory=list)
    gap_score: float = 0.0  # 0-100; higher = more urgent


def compute_gap(client: BacklinkProfile, competitor: BacklinkProfile) -> LinkGap:
    client_domains = {bl.source_url for bl in client.backlinks}
    comp_domains = {bl.source_url for bl in competitor.backlinks}

    missing = sorted(comp_domains - client_domains)
    shared = sorted(client_domains & comp_domains)
    client_only = sorted(client_domains - comp_domains)

    # Gap score: ratio of missing to competitor total, weighted by competitor diversity
    total_comp = len(comp_domains) or 1
    gap_score = round(len(missing) / total_comp * 100, 1)

    return LinkGap(
        competitor_domain=competitor.domain,
        client_domain=client.domain,
        domains_client_missing=missing,
        domains_client_has=client_only,
        shared_domains=shared,
        gap_score=gap_score,
    )
