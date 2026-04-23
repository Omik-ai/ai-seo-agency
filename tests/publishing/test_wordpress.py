"""Tests for WordPress publish adapter."""
from __future__ import annotations

from tools.publishing.wordpress import WPCredentials, _api_base, _auth_headers


def test_api_base_selfhosted():
    creds = WPCredentials(base_url="https://example.com", username="u", password="p")
    assert _api_base(creds) == "https://example.com/wp-json/wp/v2"


def test_api_base_com():
    creds = WPCredentials(base_url="https://example.wordpress.com", username="u", password="p", is_com=True)
    assert _api_base(creds) == "https://public-api.wordpress.com/rest/v1.1/sites/example.wordpress.com"


def test_auth_headers_com():
    creds = WPCredentials(base_url="https://example.com", username="u", password="token", is_com=True)
    headers = _auth_headers(creds)
    assert headers["Authorization"] == "Bearer token"
