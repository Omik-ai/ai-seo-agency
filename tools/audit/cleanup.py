#!/usr/bin/env python3
"""Data retention cleanup utility.

Removes audit files, crawl snapshots, and PSI data older than configured TTLs.
Run with --dry-run first.

Usage:
    python3 tools/audit/cleanup.py --audit-ttl 90 --crawl-ttl 14 --psi-ttl 30 --dry-run
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


def _parse_age(path: Path) -> int | None:
    """Return age in days, or None if stat fails."""
    try:
        mtime = path.stat().st_mtime
        return (datetime.now() - datetime.fromtimestamp(mtime)).days
    except OSError:
        return None


def _collect_old_files(root: Path, ttl_days: int, pattern: str = "*") -> list[Path]:
    if not root.exists():
        return []
    old: list[Path] = []
    for p in root.rglob(pattern):
        if p.is_dir():
            continue
        age = _parse_age(p)
        if age is not None and age > ttl_days:
            old.append(p)
    return old


def _delete(paths: list[Path], dry_run: bool) -> int:
    total_bytes = 0
    for p in paths:
        size = p.stat().st_size
        if dry_run:
            print(f"[dry-run] would delete: {p} ({size:,} bytes, {_parse_age(p)} days old)")
        else:
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                print(f"deleted: {p} ({size:,} bytes)")
            except OSError as e:
                print(f"error deleting {p}: {e}", file=sys.stderr)
                continue
        total_bytes += size
    return total_bytes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SEO agency data retention cleanup")
    ap.add_argument("--audit-ttl", type=int, default=90, help="Days to retain audit deliverables")
    ap.add_argument("--crawl-ttl", type=int, default=14, help="Days to retain crawl snapshots")
    ap.add_argument("--psi-ttl", type=int, default=30, help="Days to retain PSI raw API responses")
    ap.add_argument("--log-ttl", type=int, default=30, help="Days to retain parsed log aggregates")
    ap.add_argument("--dry-run", action="store_true", help="Print what would be deleted without removing")
    args = ap.parse_args(argv)

    repo = Path(__file__).resolve().parent.parent.parent
    targets = [
        (repo / "data" / "audits", args.audit_ttl, "*.json"),
        (repo / "data" / "audits", args.audit_ttl, "*.md"),
        (repo / "data" / "crawls", args.crawl_ttl, "*"),
        (repo / "data" / "psi", args.psi_ttl, "*.json"),
        (repo / "data" / "logs", args.log_ttl, "*.log"),
    ]

    grand_total = 0
    for root, ttl, pattern in targets:
        paths = _collect_old_files(root, ttl, pattern)
        if paths:
            print(f"\n# {root} (TTL {ttl} days) — {len(paths)} files")
            grand_total += _delete(paths, args.dry_run)

    print(f"\n{'[dry-run] ' if args.dry_run else ''}Total: {grand_total:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
