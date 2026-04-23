"""Notion API publish adapter.

Publishes content as Notion pages under a target database.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class NotionCredentials:
    token: str
    database_id: str


def _headers(creds: NotionCredentials) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {creds.token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }


def publish_page(
    creds: NotionCredentials,
    title: str,
    content_blocks: list[dict[str, Any]],
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = "https://api.notion.com/v1/pages"
    payload: dict[str, Any] = {
        "parent": {"database_id": creds.database_id},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
        },
        "children": content_blocks,
    }
    if properties:
        payload["properties"].update(properties)
    resp = requests.post(url, headers=_headers(creds), json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def markdown_to_blocks(markdown: str) -> list[dict[str, Any]]:
    """Crude markdown-to-Notion-block converter."""
    blocks: list[dict[str, Any]] = []
    for line in markdown.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]},
            })
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]},
            })
        elif line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]},
            })
        elif line.startswith("- "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]},
            })
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]},
            })
    return blocks
