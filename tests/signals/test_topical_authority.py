"""Tests for topical authority signal."""
from __future__ import annotations

from tests.conftest import make_page
from tools.audit.signals.topical_authority import check


def test_cluster_detection(ctx):
    html_a = '<html><body><h1>SEO Tips</h1><p>Search engine optimization is important.</p></body></html>'
    html_b = '<html><body><h1>SEO Tools</h1><p>Tools for SEO professionals.</p></body></html>'
    ctx.pages = [
        make_page("https://example.com/blog/seo-tips", html_a, 200),
        make_page("https://example.com/blog/seo-tools", html_b, 200),
    ]
    result = check(ctx)
    assert "blog" in result.data["topics"]
    assert result.data["topic_page_counts"]["blog"] == 2


def test_low_internal_density_finding(ctx):
    html = '<html><body><h1>Post</h1><p>Content.</p><a href="https://external.com">ext</a></body></html>'
    ctx.pages = [
        make_page("https://example.com/blog/post-1", html, 200),
        make_page("https://example.com/blog/post-2", html, 200),
    ]
    result = check(ctx)
    ids = [f.id for f in result.findings]
    assert "topical_authority.low_internal_density" in ids
