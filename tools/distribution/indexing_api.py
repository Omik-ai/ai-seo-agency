"""Google Indexing API submitter.

Requests immediate indexing for new/changed URLs.
https://developers.google.com/search/apis/indexing-api/v3/quickstart
"""
from __future__ import annotations

import json
import os
from typing import Any

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build


def _get_credentials() -> service_account.Credentials:
    path = os.getenv("GSC_CREDENTIALS_PATH")
    if not path:
        raise RuntimeError("GSC_CREDENTIALS_PATH env var required")
    return service_account.Credentials.from_service_account_file(
        path,
        scopes=["https://www.googleapis.com/auth/indexing"],
    )


def submit_url(url: str, action: str = "URL_UPDATED") -> dict[str, Any]:
    """Submit a single URL to Google Indexing API.

    action: URL_UPDATED | URL_DELETED
    """
    creds = _get_credentials()
    service = build("indexing", "v3", credentials=creds)
    body = {"url": url, "type": action}
    try:
        response = service.urlNotifications().publish(body=body).execute()
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}


def submit_bulk(urls: list[str], action: str = "URL_UPDATED") -> list[dict[str, Any]]:
    """Submit multiple URLs. Rate-limited by Google (200/day quota)."""
    results = []
    for url in urls:
        results.append(submit_url(url, action))
    return results
