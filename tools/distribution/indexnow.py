"""IndexNow submitter.

Submits URLs to Bing/Yandex/IndexNow partners for instant indexing.
https://www.indexnow.org/documentation
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

INDEXNOW_HOSTS = [
    "https://api.indexnow.org",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow",
]


def _get_key() -> str:
    return os.getenv("INDEXNOW_KEY", "")


def _key_file_url(key: str, host: str) -> str:
    return f"{host}/{key}.txt"


def submit_single(url: str, host: str = "www.bing.com", key: str | None = None) -> dict[str, Any]:
    """Submit a single URL to IndexNow."""
    key = key or _get_key()
    if not key:
        raise RuntimeError("INDEXNOW_KEY env var required")
    payload = {
        "host": host,
        "key": key,
        "urlList": [url],
    }
    results = {}
    for endpoint in INDEXNOW_HOSTS:
        try:
            resp = requests.post(
                f"{endpoint}/IndexNow",
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=30,
            )
            results[endpoint] = {"status": resp.status_code, "body": resp.text[:500]}
        except Exception as e:
            results[endpoint] = {"error": str(e)}
    return results


def submit_bulk(urls: list[str], host: str = "www.bing.com", key: str | None = None) -> dict[str, Any]:
    """Submit up to 10,000 URLs to IndexNow."""
    if len(urls) > 10000:
        raise ValueError("IndexNow supports max 10,000 URLs per request")
    key = key or _get_key()
    if not key:
        raise RuntimeError("INDEXNOW_KEY env var required")
    payload = {
        "host": host,
        "key": key,
        "urlList": urls,
    }
    results = {}
    for endpoint in INDEXNOW_HOSTS:
        try:
            resp = requests.post(
                f"{endpoint}/IndexNow",
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=60,
            )
            results[endpoint] = {"status": resp.status_code, "body": resp.text[:500]}
        except Exception as e:
            results[endpoint] = {"error": str(e)}
    return results
