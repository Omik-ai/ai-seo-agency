"""Tests for syndication worker."""
from __future__ import annotations

from tools.distribution.syndication import Article, syndicate


def test_syndicate_unknown_target():
    article = Article(title="Test", content="Hello", canonical_url="https://example.com", tags=["test"])
    result = syndicate(article, targets=["unknown"])
    assert result["unknown"]["success"] is False
