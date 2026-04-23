"""Tests for Notion publish adapter."""
from __future__ import annotations

from tools.publishing.notion import NotionCredentials, _headers, markdown_to_blocks


def test_headers_format():
    creds = NotionCredentials(token="secret_abc", database_id="db123")
    headers = _headers(creds)
    assert headers["Authorization"] == "Bearer secret_abc"
    assert headers["Notion-Version"] == "2022-06-28"


def test_markdown_to_blocks():
    md = "# Title\n\nParagraph\n\n- Item 1\n- Item 2"
    blocks = markdown_to_blocks(md)
    assert len(blocks) == 4
    assert blocks[0]["type"] == "heading_1"
    assert blocks[1]["type"] == "paragraph"
    assert blocks[2]["type"] == "bulleted_list_item"
