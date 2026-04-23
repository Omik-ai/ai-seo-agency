"""Tests for Ghost publish adapter."""
from __future__ import annotations

from tools.publishing.ghost import GhostCredentials, _headers


def test_headers_contain_auth():
    creds = GhostCredentials(admin_url="https://example.com/ghost", api_key="id:secret")
    headers = _headers(creds)
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Ghost ")
