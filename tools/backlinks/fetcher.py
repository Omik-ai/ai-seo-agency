"""Backlink fetchers — DataForSEO + GSC Links API.

DataForSEO: https://docs.dataforseo.com/v3/backlinks/
GSC Links: https://developers.google.com/webmaster-tools/api/reference/rest/v3/sites.links/list
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
class Backlink:
    source_url: str
    target_url: str
    anchor: str = ""
    is_dofollow: bool = True
    domain_authority: int | None = None
    first_seen: str | None = None
    last_seen: str | None = None
    source_platform: str | None = None  # blog, news, directory, social, etc.


@dataclass
class BacklinkProfile:
    domain: str
    total_backlinks: int = 0
    unique_domains: int = 0
    dofollow_ratio: float = 0.0
    anchor_texts: dict[str, int] = field(default_factory=dict)
    top_referrers: list[dict] = field(default_factory=list)
    backlinks: list[Backlink] = field(default_factory=list)


def _dataforseo_auth() -> tuple[str, str]:
    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    if not login or not password:
        raise RuntimeError("DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD env vars required")
    return (login, password)


def fetch_dataforseo(domain: str, limit: int = 1000) -> BacklinkProfile:
    """Fetch backlink profile from DataForSEO Backlinks API."""
    auth = _dataforseo_auth()
    url = "https://api.dataforseo.com/v3/backlinks/backlinks/live"
    payload = [{
        "target": domain,
        "mode": "as_is",
        "filters": [],
        "limit": limit,
    }]
    resp = requests.post(url, json=payload, auth=auth, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    tasks = data.get("tasks", [])
    if not tasks:
        return BacklinkProfile(domain=domain)
    result = tasks[0].get("result", [{}])[0]
    items = result.get("items", [])

    profile = BacklinkProfile(domain=domain)
    profile.total_backlinks = result.get("total_count", len(items))
    seen_domains = set()
    dofollow_count = 0
    anchor_counter: dict[str, int] = {}

    for item in items:
        bl = Backlink(
            source_url=item.get("domain", ""),
            target_url=item.get("url_to", ""),
            anchor=item.get("anchor", ""),
            is_dofollow=item.get("dofollow", True),
            domain_authority=item.get("domain_rank", None),
            first_seen=item.get("first_seen", None),
            last_seen=item.get("last_seen", None),
            source_platform=item.get("backlink_spam_score", None) and "unknown",
        )
        profile.backlinks.append(bl)
        seen_domains.add(bl.source_url)
        if bl.is_dofollow:
            dofollow_count += 1
        if bl.anchor:
            anchor_counter[bl.anchor] = anchor_counter.get(bl.anchor, 0) + 1

    profile.unique_domains = len(seen_domains)
    if profile.backlinks:
        profile.dofollow_ratio = round(dofollow_count / len(profile.backlinks) * 100, 1)
    profile.anchor_texts = dict(sorted(anchor_counter.items(), key=lambda x: x[1], reverse=True)[:20])

    # Top referrers by domain authority
    by_da = {}
    for bl in profile.backlinks:
        by_da[bl.source_url] = max(by_da.get(bl.source_url, 0) or 0, bl.domain_authority or 0)
    profile.top_referrers = [
        {"domain": d, "domain_authority": da}
        for d, da in sorted(by_da.items(), key=lambda x: x[1] or 0, reverse=True)[:20]
    ]

    return profile


def fetch_gsc_links(site_url: str, credentials_path: str | None = None) -> BacklinkProfile:
    """Fetch backlink profile from Google Search Console Links API.

    Requires Google OAuth2 service-account credentials.
    """
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:
        raise RuntimeError("google-auth and google-api-python-client required for GSC links") from e

    creds_path = credentials_path or os.getenv("GSC_CREDENTIALS_PATH")
    if not creds_path:
        raise RuntimeError("GSC_CREDENTIALS_PATH env var or credentials_path arg required")

    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )
    service = build("webmasters", "v3", credentials=credentials)

    profile = BacklinkProfile(domain=site_url)
    # GSC Links API returns sample URLs linking to the site
    response = service.sites().links().list(siteUrl=site_url).execute()
    sample_urls = response.get("sampleUrls", [])

    seen_domains = set()
    for url in sample_urls:
        bl = Backlink(source_url=url, target_url=site_url)
        profile.backlinks.append(bl)
        seen_domains.add(urlparse(url).netloc)

    profile.total_backlinks = len(profile.backlinks)
    profile.unique_domains = len(seen_domains)
    return profile


def fetch_backlinks(domain: str, source: str = "dataforseo", **kwargs: Any) -> BacklinkProfile:
    """Unified fetcher. source = 'dataforseo' | 'gsc'."""
    if source == "dataforseo":
        return fetch_dataforseo(domain, **kwargs)
    if source == "gsc":
        return fetch_gsc_links(domain, **kwargs)
    raise ValueError(f"Unknown backlink source: {source}")
