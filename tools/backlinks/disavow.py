"""Disavow file generator.

Generates Google-compliant disavow.txt files from backlink profiles,
with heuristic toxic-link detection and manual review workflow.

Usage:
    from tools.backlinks.disavow import DisavowGenerator, ToxicHeuristics
    gen = DisavowGenerator()
    gen.load_profile(profile)
    gen.auto_flag(ToxicHeuristics())
    gen.write_disavow("disavow.txt")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from .fetcher import Backlink, BacklinkProfile


@dataclass
class ToxicHeuristics:
    """Configurable thresholds for toxic link detection."""
    # Domain-level patterns
    spam_keywords: list[str] = field(default_factory=lambda: [
        "porn", "xxx", "sex", "casino", "gambling", "viagra", "cialis",
        "payday", "loan", "debt", "insurance", "seo-service", "link-building",
        "buy-links", "cheap-links", "backlinks", "directory", "free-dir",
        "article-directory", "submit-article", "bookmark", "social-bookmark",
        "forum-profile", "blog-comment", "guestbook", "wiki-site",
    ])
    tld_blacklist: list[str] = field(default_factory=lambda: [
        ".tk", ".ml", ".ga", ".cf", ".top", ".xyz", ".click", ".link",
    ])
    # Authority thresholds
    min_domain_authority: int = 10
    max_anchor_exact_match_pct: float = 0.15  # per domain
    max_sitewide_links: int = 50  # more than this = likely footer/sidebar spam
    # Content signals
    flag_nofollow: bool = False  # usually don't disavow nofollow
    flag_foreign_language: bool = False  # risky; disabled by default


@dataclass
class FlaggedLink:
    backlink: Backlink
    reason: str
    severity: str  # high | medium | low
    disavow_entry: str  # domain:... or specific URL


class DisavowGenerator:
    """Build and export disavow files."""

    def __init__(self):
        self.flagged: list[FlaggedLink] = []
        self.whitelisted: set[str] = set()
        self.manual_additions: set[str] = set()

    def load_profile(self, profile: BacklinkProfile) -> None:
        """Load backlinks from a profile for analysis."""
        self.profile = profile
        self.backlinks = profile.backlinks

    def auto_flag(self, heuristics: ToxicHeuristics | None = None) -> list[FlaggedLink]:
        """Run heuristic detection and flag toxic links."""
        h = heuristics or ToxicHeuristics()
        self.flagged = []
        if not hasattr(self, "backlinks"):
            return self.flagged

        # Count sitewide links per domain
        domain_link_count: dict[str, int] = {}
        for bl in self.backlinks:
            dom = urlparse(bl.source_url).netloc.lower()
            domain_link_count[dom] = domain_link_count.get(dom, 0) + 1

        for bl in self.backlinks:
            reasons: list[str] = []
            severity = "low"
            dom = urlparse(bl.source_url).netloc.lower()

            # Skip if whitelisted
            if dom in self.whitelisted or bl.source_url in self.whitelisted:
                continue

            # Skip nofollow unless explicitly flagging
            if not bl.is_dofollow and not h.flag_nofollow:
                continue

            # Spam keyword in domain
            if any(kw in dom for kw in h.spam_keywords):
                reasons.append(f"spam keyword in domain: {dom}")
                severity = "high"

            # Bad TLD
            if any(dom.endswith(tld) for tld in h.tld_blacklist):
                reasons.append(f"suspicious TLD: {dom}")
                severity = "high"

            # Very low DA
            if bl.domain_authority is not None and bl.domain_authority < h.min_domain_authority:
                reasons.append(f"very low DA ({bl.domain_authority})")
                severity = max(severity, "medium")

            # Sitewide link spam
            if domain_link_count.get(dom, 0) > h.max_sitewide_links:
                reasons.append(f"sitewide links ({domain_link_count[dom]})")
                severity = max(severity, "medium")

            # Unnatural anchor
            anchor_lower = bl.anchor.lower().strip()
            if anchor_lower and len(anchor_lower.split()) >= 3:
                # 3+ word exact match anchors are often manipulative
                reasons.append(f"long exact-match anchor: '{anchor_lower[:40]}'")
                severity = max(severity, "medium")

            if reasons:
                # Prefer domain-level disavow for sitewide / spam domains
                if domain_link_count.get(dom, 0) > 3 or any(r.startswith("spam") or r.startswith("suspicious") for r in reasons):
                    entry = f"domain:{dom}"
                else:
                    entry = bl.source_url
                self.flagged.append(FlaggedLink(
                    backlink=bl,
                    reason="; ".join(reasons),
                    severity=severity,
                    disavow_entry=entry,
                ))

        return self.flagged

    def whitelist(self, domain_or_url: str) -> None:
        """Add a domain or URL to the whitelist (won't be disavowed)."""
        self.whitelisted.add(domain_or_url.lower().strip())
        # Remove any existing flags for this domain/URL
        self.flagged = [
            f for f in self.flagged
            if f.disavow_entry.lower() != domain_or_url.lower().strip()
            and not f.backlink.source_url.lower().startswith(domain_or_url.lower().strip())
        ]

    def add_manual(self, entry: str) -> None:
        """Manually add a disavow entry (domain:example.com or URL)."""
        self.manual_additions.add(entry.strip())

    def review_report(self) -> str:
        """Generate a human-readable review report before exporting."""
        lines: list[str] = []
        lines.append(f"# Disavow Review Report")
        lines.append(f"# Total backlinks analyzed: {len(getattr(self, 'backlinks', []))}")
        lines.append(f"# Flagged for disavow: {len(self.flagged)}")
        lines.append(f"# Whitelisted: {len(self.whitelisted)}")
        lines.append(f"# Manual additions: {len(self.manual_additions)}")
        lines.append("")

        if not self.flagged and not self.manual_additions:
            lines.append("# Nothing flagged. No disavow file needed.")
            return "\n".join(lines)

        lines.append("## HIGH severity")
        for f in self.flagged:
            if f.severity == "high":
                lines.append(f"# {f.backlink.source_url}")
                lines.append(f"#   Reason: {f.reason}")
                lines.append(f"#   Entry:  {f.disavow_entry}")
        lines.append("")

        lines.append("## MEDIUM severity")
        for f in self.flagged:
            if f.severity == "medium":
                lines.append(f"# {f.backlink.source_url}")
                lines.append(f"#   Reason: {f.reason}")
                lines.append(f"#   Entry:  {f.disavow_entry}")
        lines.append("")

        lines.append("## LOW severity")
        for f in self.flagged:
            if f.severity == "low":
                lines.append(f"# {f.backlink.source_url}")
                lines.append(f"#   Reason: {f.reason}")
                lines.append(f"#   Entry:  {f.disavow_entry}")
        lines.append("")

        if self.manual_additions:
            lines.append("## MANUAL additions")
            for entry in sorted(self.manual_additions):
                lines.append(f"# Entry: {entry}")

        return "\n".join(lines)

    def write_disavow(self, path: str | Path) -> Path:
        """Export the final disavow.txt file."""
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)

        entries: set[str] = set(self.manual_additions)
        for f in self.flagged:
            entries.add(f.disavow_entry)

        with open(out, "w", encoding="utf-8") as fh:
            fh.write("# Generated by AI SEO Agency disavow generator\n")
            fh.write("# Review carefully before submitting to Google Search Console\n")
            fh.write("# https://developers.google.com/search/docs/monitoring-tools/disavow-links\n")
            fh.write("\n")
            for entry in sorted(entries):
                fh.write(f"{entry}\n")

        return out

    def summary(self) -> dict[str, Any]:
        """Return a JSON-friendly summary."""
        return {
            "backlinks_analyzed": len(getattr(self, "backlinks", [])),
            "flagged_count": len(self.flagged),
            "high_severity": sum(1 for f in self.flagged if f.severity == "high"),
            "medium_severity": sum(1 for f in self.flagged if f.severity == "medium"),
            "low_severity": sum(1 for f in self.flagged if f.severity == "low"),
            "domain_disavows": sum(1 for f in self.flagged if f.disavow_entry.startswith("domain:")),
            "url_disavows": sum(1 for f in self.flagged if not f.disavow_entry.startswith("domain:")),
            "whitelisted": len(self.whitelisted),
            "manual_additions": len(self.manual_additions),
        }
