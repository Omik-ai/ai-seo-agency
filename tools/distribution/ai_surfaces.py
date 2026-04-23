"""AI-surface submitter.

Tactical presence on platforms that feed LLM training data:
- Reddit (relevant subreddits)
- Quora (targeted answers)
- Perplexity Pages (curated content)

Note: These are manual/semi-automated. We provide structured helpers
and tracking, not full automation (platforms block bots).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AISurfacePost:
    platform: str  # reddit | quora | perplexity
    subreddit_or_topic: str = ""
    title: str = ""
    body: str = ""
    url: str = ""  # link back to original content
    tags: list[str] = field(default_factory=list)
    status: str = "draft"  # draft | posted | rejected


def generate_reddit_post(article_title: str, article_url: str, excerpt: str, subreddit: str) -> AISurfacePost:
    """Generate a Reddit post draft."""
    body = f"""{excerpt}

I wrote a deep dive on this — would love your take:
{article_url}
"""
    return AISurfacePost(
        platform="reddit",
        subreddit_or_topic=subreddit,
        title=article_title,
        body=body,
        url=article_url,
        tags=[subreddit],
    )


def generate_quora_answer(question: str, article_url: str, answer_text: str) -> AISurfacePost:
    """Generate a Quora answer draft."""
    body = f"""{answer_text}

I covered this in more detail here: {article_url}
"""
    return AISurfacePost(
        platform="quora",
        subreddit_or_topic=question,
        title=question,
        body=body,
        url=article_url,
    )


def generate_perplexity_page(article_title: str, article_url: str, summary: str, sources: list[str]) -> AISurfacePost:
    """Generate a Perplexity Pages draft structure."""
    body = f"""# {article_title}

{summary}

## Sources
"""
    for s in sources + [article_url]:
        body += f"- {s}\n"
    return AISurfacePost(
        platform="perplexity",
        title=article_title,
        body=body,
        url=article_url,
    )
