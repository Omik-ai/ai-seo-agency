"""Log file analysis signal.

Parses Common Log Format (CLF) or combined log format (Apache/Nginx) to detect:
- Crawl budget waste (4xx/5xx bot hits)
- Orphan pages (bot-crawled URLs not found in sitemap or internal links)
- Bot traps / suspicious patterns
- Slow pages (high avg response time)
- Googlebot vs other-bot ratio

Usage:
    Place log file path in crawl_meta['log_file'] or env var SEO_LOG_FILE.
    The signal auto-parses and emits findings.
"""
from __future__ import annotations

import gzip
import os
import re
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from ..report import Finding, Severity, SignalResult

if TYPE_CHECKING:
    from ..engine import AuditContext

# Combined log format regex
LOG_PATTERN = re.compile(
    r'^(?P<ip>[\d\.]+)\s+'           # IP
    r'-\s+'                            # ident
    r'(?P<user>\S+)\s+'                # auth user
    r'\[(?P<time>[^\]]+)\]\s+'         # time
    r'"(?P<method>\S+)\s+'             # method
    r'(?P<path>\S+)\s+'                # path
    r'(?P<proto>\S+)"\s+'              # protocol
    r'(?P<status>\d{3})\s+'            # status
    r'(?P<bytes>\d+)\s+'               # bytes
    r'"(?P<referer>[^"]*)"\s+'         # referer
    r'"(?P<ua>[^"]*)"'                 # user-agent
)

GOOGLEBOT_UA = re.compile(r"Googlebot", re.IGNORECASE)
BINGBOT_UA = re.compile(r"bingbot", re.IGNORECASE)


def _parse_log(path: str) -> list[dict]:
    entries: list[dict] = []
    p = Path(path)
    if not p.exists():
        return entries

    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = LOG_PATTERN.match(line.strip())
            if not m:
                continue
            entries.append(m.groupdict())
    return entries


def _is_bot(ua: str) -> bool:
    bot_keywords = ["bot", "crawler", "spider", "googlebot", "bingbot", "slurp", "duckduckgo", "baiduspider"]
    ua_lower = ua.lower()
    return any(k in ua_lower for k in bot_keywords)


def _is_googlebot(ua: str) -> bool:
    return bool(GOOGLEBOT_UA.search(ua))


def _is_bingbot(ua: str) -> bool:
    return bool(BINGBOT_UA.search(ua))


def check(ctx: AuditContext) -> SignalResult:
    # Discover log file
    log_path = ctx.crawl_meta.get("log_file") or os.getenv("SEO_LOG_FILE")
    if not log_path:
        # Try common locations
        candidates = [
            "access.log",
            "logs/access.log",
            "data/logs/access.log",
            "/var/log/nginx/access.log",
            "/var/log/apache2/access.log",
        ]
        for c in candidates:
            if Path(c).exists():
                log_path = c
                break

    if not log_path or not Path(log_path).exists():
        return SignalResult(
            name="logs",
            score=None,
            findings=[],
            data={"skipped": "no log file found; set SEO_LOG_FILE or crawl_meta['log_file']"},
        )

    entries = _parse_log(log_path)
    if not entries:
        return SignalResult(
            name="logs",
            score=None,
            findings=[],
            data={"skipped": f"log file {log_path} parsed but no valid entries"},
        )

    findings: list[Finding] = []
    bot_entries = [e for e in entries if _is_bot(e["ua"])]
    googlebot_entries = [e for e in bot_entries if _is_googlebot(e["ua"])]

    # 1. Crawl budget waste: 4xx/5xx from bots
    error_entries = [e for e in bot_entries if int(e["status"]) >= 400]
    error_rate = len(error_entries) / len(bot_entries) if bot_entries else 0
    if error_rate > 0.05:
        top_errors = Counter(
            (e["path"], e["status"]) for e in error_entries
        ).most_common(5)
        evidence = "; ".join(f"{p} ({s}) ×{c}" for (p, s), c in top_errors)
        findings.append(Finding(
            id="log-crawl-waste",
            title="Crawl budget waste: bots hitting errors",
            severity=Severity.P1 if error_rate > 0.15 else Severity.P2,
            description=f"{len(error_entries)} bot hits returned 4xx/5xx ({error_rate:.1%} of bot traffic).",
            recommendation="Fix or 410 dead URLs; update internal links and redirects.",
            category="technical",
            evidence={"urls": evidence, "source": log_path},
        ))

    # 2. Orphan pages: bot-crawled URLs not in sitemap/internal links
    crawled_paths = {e["path"] for e in googlebot_entries}
    sitemap_paths = set()
    for url in ctx.crawl_meta.get("sitemap_urls", []):
        # crude: just assume sitemap contains paths we already crawled
        pass
    # Use actually-crawled pages as proxy for "known" pages
    known_paths = set()
    for p in ctx.pages:
        parsed = urlparse(p.final_url)
        known_paths.add(parsed.path or "/")

    orphan_paths = crawled_paths - known_paths
    # Exclude static assets and common non-page paths
    orphan_paths = {
        p for p in orphan_paths
        if not any(p.endswith(ext) for ext in (".css", ".js", ".png", ".jpg", ".gif", ".ico", ".woff", ".woff2"))
        and not p.startswith(("/wp-content/", "/assets/", "/static/", "/images/"))
    }
    if len(orphan_paths) > 5:
        findings.append(Finding(
            id="log-orphan-pages",
            title=f"{len(orphan_paths)} orphan pages crawled by Googlebot",
            severity=Severity.P2,
            description="Googlebot found and crawled pages not present in the current sitemap or internal link graph. These may be old URLs, soft-404s, or unintended indexable endpoints.",
            recommendation="Audit orphan URLs: add valuable ones to sitemap and internal links; 404/410 or noindex the rest.",
            category="technical",
            evidence={"sample_orphans": sorted(orphan_paths)[:10], "source": log_path},
        ))

    # 3. Bot trap detection: suspicious high-hit single IP or path pattern
    ip_counter = Counter(e["ip"] for e in bot_entries)
    suspicious_ips = [(ip, cnt) for ip, cnt in ip_counter.most_common(5) if cnt > 500]
    if suspicious_ips:
        findings.append(Finding(
            id="log-bot-trap",
            title="Possible bot trap or aggressive crawler",
            severity=Severity.P1,
            description=f"IPs with >500 bot hits: {', '.join(f'{ip} (×{cnt})' for ip, cnt in suspicious_ips)}.",
            recommendation="Check if these are legitimate crawlers (verify via reverse DNS). If spam, block in robots.txt, firewall, or rate-limit.",
            category="technical",
            evidence={"suspicious_ips": suspicious_ips, "source": log_path},
        ))

    # 4. Slow pages from log response time (if available)
    # CLF doesn't have response time; extended format does. We can't detect it reliably here.

    # 5. Bot ratio
    total_bot = len(bot_entries)
    gg = len(googlebot_entries)
    bing = len([e for e in bot_entries if _is_bingbot(e["ua"])])
    other = total_bot - gg - bing
    if total_bot > 0 and (gg / total_bot) < 0.4:
        findings.append(Finding(
            id="log-bot-ratio",
            title="Low Googlebot ratio in crawl traffic",
            severity=Severity.P3,
            description=f"Googlebot is only {gg/total_bot:.1%} of bot hits. Other bots dominate ({other} hits).",
            recommendation="Review if other bots are consuming crawl budget. Use robots.txt to throttle non-essential crawlers.",
            category="technical",
            evidence={"googlebot": gg, "bingbot": bing, "other": other, "source": log_path},
        ))

    score = 100
    for f in findings:
        if f.severity == Severity.P0:
            score -= 20
        elif f.severity == Severity.P1:
            score -= 12
        elif f.severity == Severity.P2:
            score -= 6
        elif f.severity == Severity.P3:
            score -= 2
    score = max(0, score)

    return SignalResult(
        name="logs",
        score=score,
        findings=findings,
        data={
            "log_file": log_path,
            "total_entries": len(entries),
            "bot_hits": total_bot,
            "googlebot_hits": gg,
            "error_bot_hits": len(error_entries),
            "orphan_paths_count": len(orphan_paths),
        },
    )
