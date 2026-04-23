"""Tests for SERP signal (lightweight, no real network calls)."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

from tools.audit.signals.serp import check


def test_serp_brand_presence(ctx):
    mock_html = """
    <html><body>
    <div class="g"><h3>Example Brand</h3><a href="https://example.com/">link</a></div>
    <div class="kp-wholepage">Knowledge Panel</div>
    </body></html>
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, text=mock_html)
        result = check(ctx)
        ids = [f.id for f in result.findings]
        assert "serp.brand.no_knowledge_panel" not in ids
        assert result.data.get("brand_rank") is not None


def test_serp_no_brand_presence(ctx):
    mock_html = '<html><body><div class="g"><h3>Competitor</h3></div></body></html>'
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, text=mock_html)
        result = check(ctx)
        ids = [f.id for f in result.findings]
        assert "serp.brand.not_in_top10" in ids
