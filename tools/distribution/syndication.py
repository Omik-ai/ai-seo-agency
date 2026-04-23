"""Canonical-aware syndication worker.

Cross-posts content to Medium, Dev.to, Hashnode, LinkedIn articles,
always pointing canonical back to the original.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class SyndicationTarget:
    name: str
    enabled: bool
    api_key_env: str
    api_endpoint: str


TARGETS = {
    "medium": SyndicationTarget(
        name="medium",
        enabled=True,
        api_key_env="MEDIUM_API_TOKEN",
        api_endpoint="https://api.medium.com/v1",
    ),
    "devto": SyndicationTarget(
        name="devto",
        enabled=True,
        api_key_env="DEVTO_API_KEY",
        api_endpoint="https://dev.to/api",
    ),
}


@dataclass
class Article:
    title: str
    content: str  # HTML or markdown
    canonical_url: str
    tags: list[str]
    author_id: str | None = None


def syndicate_medium(article: Article) -> dict[str, Any]:
    token = os.getenv(TARGETS["medium"].api_key_env)
    if not token:
        return {"success": False, "error": "MEDIUM_API_TOKEN not set"}
    base = TARGETS["medium"].api_endpoint
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Get user ID
    me_resp = requests.get(f"{base}/me", headers=headers, timeout=30)
    if me_resp.status_code != 200:
        return {"success": False, "error": me_resp.text}
    user_id = me_resp.json().get("data", {}).get("id")

    payload = {
        "title": article.title,
        "contentFormat": "html",
        "content": article.content,
        "canonicalUrl": article.canonical_url,
        "tags": article.tags[:5],
        "publishStatus": "public",
    }
    post_resp = requests.post(
        f"{base}/users/{user_id}/posts",
        headers=headers,
        json=payload,
        timeout=60,
    )
    return {"success": post_resp.status_code in (200, 201), "response": post_resp.json()}


def syndicate_devto(article: Article) -> dict[str, Any]:
    token = os.getenv(TARGETS["devto"].api_key_env)
    if not token:
        return {"success": False, "error": "DEVTO_API_KEY not set"}
    base = TARGETS["devto"].api_endpoint
    headers = {"api-key": token, "Content-Type": "application/json"}
    payload = {
        "article": {
            "title": article.title,
            "body_markdown": article.content,
            "canonical_url": article.canonical_url,
            "tags": article.tags[:4],
            "published": True,
        }
    }
    resp = requests.post(f"{base}/articles", headers=headers, json=payload, timeout=60)
    return {"success": resp.status_code in (200, 201), "response": resp.json()}


def syndicate(article: Article, targets: list[str] | None = None) -> dict[str, Any]:
    """Syndicate article to selected targets."""
    targets = targets or ["medium", "devto"]
    results = {}
    for t in targets:
        if t == "medium":
            results[t] = syndicate_medium(article)
        elif t == "devto":
            results[t] = syndicate_devto(article)
        else:
            results[t] = {"success": False, "error": f"Unknown target: {t}"}
    return results
