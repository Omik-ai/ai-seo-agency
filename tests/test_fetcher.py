"""Tests for fetcher module."""
from __future__ import annotations

from tools.audit.fetcher import HttpFetcher, normalize_domain


def test_normalize_domain():
    assert normalize_domain("example.com") == ("https://example.com", "example.com")
    assert normalize_domain("http://example.com") == ("http://example.com", "example.com")
    assert normalize_domain("https://example.com/path") == ("https://example.com", "example.com")


def test_http_fetcher_success():
    fetcher = HttpFetcher()
    # This makes a real network request; in CI we may mock
    result = fetcher.fetch("https://example.com")
    assert result.status == 200
    assert result.final_url == "https://example.com"
    assert result.html is not None
    assert result.content_length > 0


def test_fetcher_robots_allow():
    fetcher = HttpFetcher()
    assert fetcher.robots_allows("https://example.com/page") is True
