"""Webflow CMS API publish adapter.

https://developers.webflow.com/docs/cms-api-reference
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class WebflowCredentials:
    token: str
    site_id: str
    collection_id: str | None = None


def _headers(creds: WebflowCredentials) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {creds.token}",
        "accept": "application/json",
        "content-type": "application/json",
    }


def list_collections(creds: WebflowCredentials) -> list[dict[str, Any]]:
    url = f"https://api.webflow.com/v2/sites/{creds.site_id}/collections"
    resp = requests.get(url, headers=_headers(creds), timeout=30)
    resp.raise_for_status()
    return resp.json().get("collections", [])


def publish_item(
    creds: WebflowCredentials,
    collection_id: str,
    fields: dict[str, Any],
    is_draft: bool = False,
) -> dict[str, Any]:
    url = f"https://api.webflow.com/v2/collections/{collection_id}/items"
    payload = {
        "fieldData": fields,
        "isDraft": is_draft,
    }
    resp = requests.post(url, headers=_headers(creds), json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def publish_post(
    creds: WebflowCredentials,
    collection_id: str,
    title: str,
    slug: str,
    content: str,
    excerpt: str = "",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    fields = {
        "name": title,
        "slug": slug,
        "post-body": content,
    }
    if excerpt:
        fields["post-summary"] = excerpt
    if tags:
        fields["tags"] = tags
    return publish_item(creds, collection_id, fields)
