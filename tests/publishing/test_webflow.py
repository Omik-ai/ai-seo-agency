"""Tests for Webflow publish adapter."""
from __future__ import annotations

from tools.publishing.webflow import WebflowCredentials, _headers


def test_headers_format():
    creds = WebflowCredentials(token="tk", site_id="site123")
    headers = _headers(creds)
    assert headers["Authorization"] == "Bearer tk"
