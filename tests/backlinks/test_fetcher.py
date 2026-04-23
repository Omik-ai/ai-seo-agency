"""Tests for backlink fetcher (unit tests, no real API calls)."""
from __future__ import annotations

from tools.backlinks.fetcher import BacklinkProfile


def test_backlink_profile_dataclass():
    profile = BacklinkProfile(domain="example.com", total_backlinks=100, unique_domains=50)
    assert profile.domain == "example.com"
    assert profile.total_backlinks == 100
    assert profile.dofollow_ratio == 0.0
