"""Shared pytest fixtures for ai-seo-agency test suite."""
from __future__ import annotations

import pytest

from tools.audit.fetcher import FetchResult
from tools.audit.engine import AuditContext, EngineConfig


@pytest.fixture
def engine_config() -> EngineConfig:
    return EngineConfig(
        domain_input="example.com",
        max_urls=5,
        no_psi=True,
        verbose=False,
    )


@pytest.fixture
def sample_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Example Page — Primary Keyword</title>
    <meta name="description" content="A solid meta description for CTR.">
    <link rel="canonical" href="https://example.com/page">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Example Page",
        "author": {"@type": "Person", "name": "Jane Doe", "sameAs": "https://twitter.com/janedoe"},
        "datePublished": "2024-01-15",
        "dateModified": "2024-06-20",
        "publisher": {"@type": "Organization", "name": "Example Inc", "logo": {"@type": "ImageObject", "url": "https://example.com/logo.png"}}
    }
    </script>
</head>
<body>
    <header><nav>Home</nav></header>
    <main>
        <article>
            <h1>Primary Keyword Guide</h1>
            <p>By <span class="author">Jane Doe</span></p>
            <h2>What is Primary Keyword?</h2>
            <p>This is a paragraph with enough words to pass thin content checks easily because it explains the topic in depth.</p>
            <h2>How to Use Primary Keyword</h2>
            <p>Another paragraph with substantial content and good readability for the target audience.</p>
            <h3>Step One</h3>
            <p>Detailed step content goes here with multiple sentences to increase word count naturally.</p>
            <h3>Step Two</h3>
            <p>More detailed content that provides real value to readers searching for this information.</p>
        </article>
    </main>
    <footer>Contact: hello@example.com</footer>
</body>
</html>
"""


@pytest.fixture
def sample_pages(sample_html) -> list[FetchResult]:
    return [
        FetchResult(
            url="https://example.com/",
            final_url="https://example.com/",
            status=200,
            html=sample_html,
            headers={"Content-Type": "text/html", "Strict-Transport-Security": "max-age=31536000"},
        ),
        FetchResult(
            url="https://example.com/page",
            final_url="https://example.com/page",
            status=200,
            html=sample_html.replace("Primary Keyword", "Secondary Topic"),
            headers={"Content-Type": "text/html"},
        ),
    ]


@pytest.fixture
def audit_context(engine_config, sample_pages) -> AuditContext:
    return AuditContext(
        base_url="https://example.com",
        host="example.com",
        pages=sample_pages,
        crawl_meta={
            "robots_raw": "User-agent: *\\nDisallow: /admin\\nSitemap: https://example.com/sitemap.xml",
            "robots_disallows": ["/admin"],
            "sitemap_url_count": 12,
            "seeded_from": "sitemap",
        },
        config=engine_config,
    )


@pytest.fixture
def bad_html() -> str:
    return """<!DOCTYPE html>
<html>
<head><title>Short</title></head>
<body>
    <h1>First H1</h1>
    <h1>Second H1</h1>
    <h3>Skipped h2</h3>
    <h2></h2>
    <p>Thin.</p>
</body>
</html>
"""
