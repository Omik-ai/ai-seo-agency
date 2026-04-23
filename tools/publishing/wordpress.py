"""WordPress REST API publish adapter.

Supports both WordPress.com and self-hosted (wp-json).
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class WPCredentials:
    base_url: str      # e.g. https://example.com or https://example.wordpress.com
    username: str
    password: str      # app password for self-hosted, API key for .com
    is_com: bool = False


def _auth_headers(creds: WPCredentials) -> dict[str, str]:
    if creds.is_com:
        return {"Authorization": f"Bearer {creds.password}"}
    token = base64.b64encode(f"{creds.username}:{creds.password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _api_base(creds: WPCredentials) -> str:
    if creds.is_com:
        return f"https://public-api.wordpress.com/rest/v1.1/sites/{creds.base_url.replace('https://', '')}"
    return creds.base_url.rstrip("/") + "/wp-json/wp/v2"


def publish_post(
    creds: WPCredentials,
    title: str,
    content: str,
    status: str = "publish",
    categories: list[int] | None = None,
    tags: list[int] | None = None,
    excerpt: str = "",
    featured_media: int | None = None,
) -> dict[str, Any]:
    url = f"{_api_base(creds)}/posts"
    headers = {**_auth_headers(creds), "Content-Type": "application/json"}
    payload: dict[str, Any] = {
        "title": title,
        "content": content,
        "status": status,
        "excerpt": excerpt,
    }
    if categories:
        payload["categories"] = categories
    if tags:
        payload["tags"] = tags
    if featured_media:
        payload["featured_media"] = featured_media
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def update_post(
    creds: WPCredentials,
    post_id: int,
    **fields: Any,
) -> dict[str, Any]:
    url = f"{_api_base(creds)}/posts/{post_id}"
    headers = {**_auth_headers(creds), "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=fields, timeout=60)
    resp.raise_for_status()
    return resp.json()
