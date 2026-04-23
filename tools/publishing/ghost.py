"""Ghost Admin API publish adapter.

https://ghost.org/docs/admin-api/
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class GhostCredentials:
    admin_url: str     # e.g. https://example.com/ghost
    api_key: str       # Admin API key: <id>:<secret>
    version: str = "v5.0"


def _token(creds: GhostCredentials) -> str:
    id_part, secret = creds.api_key.split(":")
    iat = int(time.time())
    header = json.dumps({"alg": "HS256", "typ": "JWT", "kid": id_part}, separators=(",", ":"))
    payload = json.dumps({"iat": iat, "exp": iat + 300, "aud": "/admin/"}, separators=(",", ":"))
    def b64(s: str) -> str:
        import base64
        return base64.urlsafe_b64encode(s.encode()).decode().rstrip("=")
    msg = f"{b64(header)}.{b64(payload)}"
    sig = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    import base64
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{msg}.{sig_b64}"


def _headers(creds: GhostCredentials) -> dict[str, str]:
    return {
        "Authorization": f"Ghost {_token(creds)}",
        "Content-Type": "application/json",
        "Accept-Version": creds.version,
    }


def publish_post(
    creds: GhostCredentials,
    title: str,
    html: str,
    status: str = "published",
    tags: list[str] | None = None,
    excerpt: str = "",
    feature_image: str | None = None,
    canonical_url: str | None = None,
) -> dict[str, Any]:
    url = creds.admin_url.rstrip("/") + "/ghost/api/admin/posts/?source=html"
    post = {
        "title": title,
        "html": html,
        "status": status,
        "excerpt": excerpt,
    }
    if feature_image:
        post["feature_image"] = feature_image
    if canonical_url:
        post["canonical_url"] = canonical_url
    payload = {"posts": [post]}
    if tags:
        payload["posts"][0]["tags"] = [{"name": t} for t in tags]
    resp = requests.post(url, headers=_headers(creds), json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()
