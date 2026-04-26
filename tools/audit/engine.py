"""AuditEngine — orchestrates fetch → signals → score → emit."""
from __future__ import annotations

import importlib
import pkgutil
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from .crawler import crawl
from .fetcher import FetchResult, HttpFetcher, RenderedFetcher, normalize_domain
from .report import AuditReport, RunMeta, SignalResult, iso_now
from .scoring import health_score


def _discover_signals() -> list[tuple[str, object]]:
    """Auto-import all signal modules from tools/audit/signals/."""
    from . import signals as signals_pkg
    pkg_path = Path(signals_pkg.__file__).parent
    discovered: dict[str, object] = {}
    for finder, name, ispkg in pkgutil.iter_modules([str(pkg_path)]):
        if ispkg or name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"{signals_pkg.__name__}.{name}")
            if hasattr(mod, "check"):
                discovered[name] = mod
        except Exception:
            continue
    # Preferred order for known signals; unknown signals appended alphabetically
    preferred = [
        "technical", "headings", "schema", "cwv", "eeat",
        "content", "linkgraph", "accessibility", "topical_authority",
        "serp", "aio", "geo", "backlinks", "snippets", "images",
    ]
    ordered: list[tuple[str, object]] = []
    seen = set()
    for name in preferred:
        if name in discovered:
            ordered.append((name, discovered[name]))
            seen.add(name)
    for name in sorted(discovered):
        if name not in seen:
            ordered.append((name, discovered[name]))
    return ordered


SIGNAL_ORDER = _discover_signals()


@dataclass
class EngineConfig:
    domain_input: str
    max_urls: int = 25
    out_dir: Path = Path("data/audits")
    no_psi: bool = False
    psi_key: str | None = None
    verbose: bool = False
    js_render: bool = False


@dataclass
class AuditContext:
    base_url: str            # https://host (no path)
    host: str                # bare host
    pages: list[FetchResult] = field(default_factory=list)
    crawl_meta: dict = field(default_factory=dict)
    config: EngineConfig | None = None
    warnings: list[str] = field(default_factory=list)


def log(cfg: EngineConfig, msg: str) -> None:
    if cfg.verbose:
        print(f"[audit] {msg}", flush=True)


class AuditEngine:
    def __init__(self, config: EngineConfig):
        self.config = config

    def run(self) -> AuditReport:
        cfg = self.config
        start_ts = time.time()
        run_id = "aud_" + uuid.uuid4().hex[:10]
        started_at = iso_now()

        base, host = normalize_domain(cfg.domain_input)
        log(cfg, f"target: {base} (host={host})")

        fetcher = RenderedFetcher() if cfg.js_render else HttpFetcher()
        log(cfg, f"fetcher: {'playwright' if cfg.js_render else 'http'}")
        log(cfg, f"crawling up to {cfg.max_urls} URLs...")
        pages, crawl_meta = crawl(base, host, cfg.max_urls, fetcher)
        log(cfg, f"crawled {len(pages)} pages (seeded via {crawl_meta.get('seeded_from')})")

        ctx = AuditContext(
            base_url=base, host=host, pages=pages, crawl_meta=crawl_meta, config=cfg,
        )
        # JS-rendering detection: SPA markers + low text-to-HTML ratio
        for p in pages:
            if not p.html:
                continue
            has_spa_marker = any(
                marker in p.html for marker in ('id="__next"', 'id="root"', 'id="app"', '__NEXT_DATA__', 'window.__remixContext')
            )
            # crude text density: strip tags roughly and check ratio
            text_len = len(re.sub(r"<[^>]+>", "", p.html).strip()) if has_spa_marker else 0
            if has_spa_marker and text_len < 800:
                ctx.warnings.append(
                    f"possible client-side rendering at {p.final_url}; results based on initial HTML"
                )
                break

        signals: list[SignalResult] = []
        category_scores: dict[str, int] = {}
        for name, mod in SIGNAL_ORDER:
            log(cfg, f"signal: {name}")
            try:
                result = mod.check(ctx)
            except Exception as e:  # don't let one signal break the whole audit
                log(cfg, f"  ! {name} errored: {e}")
                result = SignalResult(name=name, score=0, findings=[], data={"error": str(e)})
            signals.append(result)
            category_scores[name] = result.score if result.score is not None else 0

        hs = health_score(category_scores)
        finished_at = iso_now()
        duration_ms = int((time.time() - start_ts) * 1000)

        return AuditReport(
            schema_version="1.0",
            run=RunMeta(
                id=run_id,
                domain=host,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                engine_version="audit_engine@0.2.0",
                urls_crawled=len(pages),
                urls_requested=cfg.max_urls,
                js_rendered=cfg.js_render,
                warnings=ctx.warnings,
            ),
            health_score=hs,
            category_scores=category_scores,
            signals=signals,
        )
