"""Tests for accessibility signal."""
from __future__ import annotations

from tests.conftest import make_page
from tools.audit.signals.accessibility import check


def test_missing_alt(ctx):
    html = '<html lang="en"><body><img src="a.jpg"><img src="b.jpg" alt="ok"></body></html>'
    ctx.pages = [make_page("https://example.com/", html, 200)]
    result = check(ctx)
    ids = [f.id for f in result.findings]
    assert "accessibility.image.no_alt" in ids
    assert result.score is None


def test_missing_form_label(ctx):
    html = '<html lang="en"><body><input name="email" type="email"></body></html>'
    ctx.pages = [make_page("https://example.com/", html, 200)]
    result = check(ctx)
    ids = [f.id for f in result.findings]
    assert "accessibility.form.no_label" in ids


def test_missing_lang(ctx):
    html = "<html><body></body></html>"
    ctx.pages = [make_page("https://example.com/", html, 200)]
    result = check(ctx)
    ids = [f.id for f in result.findings]
    assert "accessibility.html.no_lang" in ids


def test_no_skip_link(ctx):
    html = '<html lang="en"><body><main>content</main></body></html>'
    ctx.pages = [make_page("https://example.com/", html, 200)]
    result = check(ctx)
    ids = [f.id for f in result.findings]
    assert "accessibility.navigation.no_skip_link" in ids


def test_empty_headings(ctx):
    html = '<html lang="en"><body><h1></h1><h2>   </h2></body></html>'
    ctx.pages = [make_page("https://example.com/", html, 200)]
    result = check(ctx)
    ids = [f.id for f in result.findings]
    assert "accessibility.heading.empty" in ids


def test_good_page_no_findings(ctx):
    html = (
        '<html lang="en">'
        '<body>'
        '<a href="#main" class="skip-link">Skip</a>'
        '<main id="main">'
        '<h1>Title</h1>'
        '<img src="a.jpg" alt="desc">'
        '<label for="email">Email</label><input id="email" name="email">'
        '</main>'
        '</body></html>'
    )
    ctx.pages = [make_page("https://example.com/", html, 200)]
    result = check(ctx)
    assert len(result.findings) == 0
