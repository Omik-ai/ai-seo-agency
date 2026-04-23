"""Tests for AI-surface submitter."""
from __future__ import annotations

from tools.distribution.ai_surfaces import generate_reddit_post, generate_quora_answer, generate_perplexity_page


def test_reddit_post_generation():
    post = generate_reddit_post("My Article", "https://example.com", "Great excerpt", "seo")
    assert post.platform == "reddit"
    assert "https://example.com" in post.body
    assert post.subreddit_or_topic == "seo"


def test_quora_answer_generation():
    ans = generate_quora_answer("How to do SEO?", "https://example.com", "Start with research.")
    assert ans.platform == "quora"
    assert "https://example.com" in ans.body


def test_perplexity_page_generation():
    page = generate_perplexity_page("Guide", "https://example.com", "Summary", ["https://source.com"])
    assert page.platform == "perplexity"
    assert "https://example.com" in page.body
    assert "https://source.com" in page.body
