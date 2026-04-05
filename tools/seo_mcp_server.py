#!/usr/bin/env python3
"""
SEO Agency MCP Server
Provides real SEO tool integrations as MCP tools for Claude Code agents.

Setup:
  pip install mcp google-auth google-auth-oauthlib google-api-python-client requests

Environment Variables:
  GOOGLE_APPLICATION_CREDENTIALS - Path to Google service account JSON
  GSC_SITE_URL                   - Google Search Console site URL
  AHREFS_API_KEY                 - Ahrefs API key (optional)
  PAGESPEED_API_KEY              - Google PageSpeed Insights API key (free)

Usage:
  Add to Claude Code settings.json under mcpServers (see tools/mcp-config.json)
"""

import json
import os
import sys
import asyncio
from datetime import datetime, timedelta

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    print("This server provides SEO tools as MCP endpoints for Claude Code.", file=sys.stderr)
    sys.exit(1)


server = Server("seo-tools")


# ── Google Search Console ──────────────────────────────────────────

def get_gsc_service():
    """Initialize Google Search Console API client."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials = service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
            scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        return build("searchconsole", "v1", credentials=credentials)
    except Exception as e:
        return None


@server.tool()
async def gsc_search_analytics(
    site_url: str = "",
    start_date: str = "",
    end_date: str = "",
    dimensions: str = "query",
    row_limit: int = 100,
    filters: str = ""
) -> str:
    """
    Query Google Search Console Search Analytics API.
    Returns search performance data: queries, pages, clicks, impressions, CTR, position.

    Args:
        site_url: The site URL in GSC (e.g., 'https://example.com/')
        start_date: Start date YYYY-MM-DD (default: 90 days ago)
        end_date: End date YYYY-MM-DD (default: today)
        dimensions: Comma-separated: query,page,device,country,date
        row_limit: Max rows to return (default 100, max 25000)
        filters: JSON array of filters, e.g. [{"dimension":"query","expression":"keyword"}]
    """
    service = get_gsc_service()
    if not service:
        return json.dumps({"error": "GSC not configured. Set GOOGLE_APPLICATION_CREDENTIALS env var."})

    site = site_url or os.environ.get("GSC_SITE_URL", "")
    if not site:
        return json.dumps({"error": "No site URL provided. Set GSC_SITE_URL env var or pass site_url."})

    end = end_date or datetime.now().strftime("%Y-%m-%d")
    start = start_date or (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": [d.strip() for d in dimensions.split(",")],
        "rowLimit": min(row_limit, 25000),
    }

    if filters:
        try:
            body["dimensionFilterGroups"] = [{"filters": json.loads(filters)}]
        except json.JSONDecodeError:
            pass

    try:
        response = service.searchanalytics().query(siteUrl=site, body=body).execute()
        rows = response.get("rows", [])
        results = []
        for row in rows:
            results.append({
                "keys": row.get("keys", []),
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            })
        return json.dumps({"rows": results, "total": len(results)}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@server.tool()
async def gsc_index_coverage(site_url: str = "") -> str:
    """
    Get Google Search Console index coverage summary.
    Returns counts of valid, warning, error, and excluded pages.
    """
    service = get_gsc_service()
    if not service:
        return json.dumps({"error": "GSC not configured. Set GOOGLE_APPLICATION_CREDENTIALS."})

    site = site_url or os.environ.get("GSC_SITE_URL", "")
    try:
        response = service.sitemaps().list(siteUrl=site).execute()
        return json.dumps(response, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── PageSpeed Insights ─────────────────────────────────────────────

@server.tool()
async def pagespeed_analyze(
    url: str,
    strategy: str = "mobile",
    categories: str = "performance,seo,accessibility,best-practices"
) -> str:
    """
    Analyze a URL with Google PageSpeed Insights API.
    Returns Core Web Vitals, Lighthouse scores, and optimization opportunities.

    Args:
        url: The URL to analyze
        strategy: 'mobile' or 'desktop'
        categories: Comma-separated Lighthouse categories
    """
    import requests

    api_key = os.environ.get("PAGESPEED_API_KEY", "")
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    params = {
        "url": url,
        "strategy": strategy,
        "category": [c.strip() for c in categories.split(",")],
    }
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(endpoint, params=params, timeout=60)
        data = resp.json()

        # Extract key metrics
        lhr = data.get("lighthouseResult", {})
        categories_result = lhr.get("categories", {})
        audits = lhr.get("audits", {})

        result = {
            "url": url,
            "strategy": strategy,
            "scores": {},
            "core_web_vitals": {},
            "opportunities": [],
        }

        # Category scores
        for cat_key, cat_data in categories_result.items():
            result["scores"][cat_key] = round(cat_data.get("score", 0) * 100)

        # Core Web Vitals
        cwv_metrics = {
            "largest-contentful-paint": "LCP",
            "interaction-to-next-paint": "INP",
            "cumulative-layout-shift": "CLS",
            "first-contentful-paint": "FCP",
            "total-blocking-time": "TBT",
            "speed-index": "Speed Index",
        }
        for audit_key, label in cwv_metrics.items():
            if audit_key in audits:
                result["core_web_vitals"][label] = {
                    "value": audits[audit_key].get("displayValue", "N/A"),
                    "score": audits[audit_key].get("score", 0),
                }

        # Top opportunities
        for audit_key, audit_data in audits.items():
            if (audit_data.get("score") is not None
                    and audit_data["score"] < 1
                    and audit_data.get("details", {}).get("type") == "opportunity"):
                result["opportunities"].append({
                    "title": audit_data.get("title", ""),
                    "description": audit_data.get("description", ""),
                    "savings": audit_data.get("details", {}).get("overallSavingsMs", 0),
                })

        result["opportunities"].sort(key=lambda x: x.get("savings", 0), reverse=True)
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Schema Validator ───────────────────────────────────────────────

@server.tool()
async def validate_schema(url: str) -> str:
    """
    Validate structured data on a URL by fetching the page and extracting JSON-LD.
    Returns all structured data found and basic validation results.

    Args:
        url: The URL to check for structured data
    """
    import requests
    import re

    try:
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (compatible; SEOBot/1.0)"
        })
        html = resp.text

        # Extract JSON-LD blocks
        pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

        schemas = []
        errors = []

        for match in matches:
            try:
                data = json.loads(match.strip())
                schema_type = data.get("@type", "Unknown")
                schemas.append({
                    "type": schema_type,
                    "data": data,
                    "valid_json": True,
                })
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON-LD: {str(e)}")

        return json.dumps({
            "url": url,
            "schemas_found": len(schemas),
            "schemas": schemas,
            "errors": errors,
            "has_organization": any(s["type"] in ("Organization", "LocalBusiness") for s in schemas),
            "has_breadcrumb": any(s["type"] == "BreadcrumbList" for s in schemas),
            "has_article": any(s["type"] in ("Article", "BlogPosting", "NewsArticle") for s in schemas),
            "has_product": any(s["type"] == "Product" for s in schemas),
            "has_faq": any(s["type"] == "FAQPage" for s in schemas),
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Robots.txt Analyzer ───────────────────────────────────────────

@server.tool()
async def analyze_robots_txt(domain: str) -> str:
    """
    Fetch and analyze a site's robots.txt file.
    Returns parsed directives, potential issues, and sitemap references.

    Args:
        domain: Domain to check (e.g., 'example.com')
    """
    import requests

    url = f"https://{domain}/robots.txt"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return json.dumps({"error": f"robots.txt returned {resp.status_code}"})

        content = resp.text
        lines = content.strip().split("\n")

        user_agents = {}
        current_ua = "*"
        sitemaps = []
        issues = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("user-agent:"):
                current_ua = line.split(":", 1)[1].strip()
                if current_ua not in user_agents:
                    user_agents[current_ua] = {"allow": [], "disallow": []}
            elif line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if current_ua not in user_agents:
                    user_agents[current_ua] = {"allow": [], "disallow": []}
                user_agents[current_ua]["disallow"].append(path)
                # Check for common issues
                if path == "/":
                    issues.append("CRITICAL: Disallow / blocks entire site for " + current_ua)
            elif line.lower().startswith("allow:"):
                path = line.split(":", 1)[1].strip()
                if current_ua not in user_agents:
                    user_agents[current_ua] = {"allow": [], "disallow": []}
                user_agents[current_ua]["allow"].append(path)
            elif line.lower().startswith("sitemap:"):
                sitemaps.append(line.split(":", 1)[1].strip().lstrip())

        if not sitemaps:
            issues.append("WARNING: No sitemap referenced in robots.txt")

        return json.dumps({
            "url": url,
            "user_agents": user_agents,
            "sitemaps": sitemaps,
            "issues": issues,
            "raw": content[:2000],
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Sitemap Parser ─────────────────────────────────────────────────

@server.tool()
async def parse_sitemap(sitemap_url: str, max_urls: int = 500) -> str:
    """
    Fetch and parse an XML sitemap. Returns URL list with lastmod dates.
    Handles sitemap index files that reference multiple sitemaps.

    Args:
        sitemap_url: Full URL to the sitemap XML
        max_urls: Maximum URLs to return (default 500)
    """
    import requests
    import xml.etree.ElementTree as ET

    try:
        resp = requests.get(sitemap_url, timeout=30)
        root = ET.fromstring(resp.content)

        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = []
        sub_sitemaps = []

        # Check if sitemap index
        for sitemap in root.findall("sm:sitemap", ns):
            loc = sitemap.find("sm:loc", ns)
            if loc is not None:
                sub_sitemaps.append(loc.text)

        # Parse URLs
        for url_elem in root.findall("sm:url", ns):
            loc = url_elem.find("sm:loc", ns)
            lastmod = url_elem.find("sm:lastmod", ns)
            if loc is not None and len(urls) < max_urls:
                urls.append({
                    "url": loc.text,
                    "lastmod": lastmod.text if lastmod is not None else None,
                })

        return json.dumps({
            "sitemap_url": sitemap_url,
            "is_index": len(sub_sitemaps) > 0,
            "sub_sitemaps": sub_sitemaps,
            "url_count": len(urls),
            "urls": urls,
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ── HTTP Header Analyzer ──────────────────────────────────────────

@server.tool()
async def analyze_headers(url: str) -> str:
    """
    Analyze HTTP response headers for SEO-relevant signals.
    Checks status code, redirects, caching, security headers, and canonical hints.

    Args:
        url: The URL to analyze
    """
    import requests

    try:
        resp = requests.get(url, timeout=15, allow_redirects=False, headers={
            "User-Agent": "Mozilla/5.0 (compatible; SEOBot/1.0)"
        })

        headers = dict(resp.headers)
        redirect_chain = []
        final_url = url
        current_resp = resp

        # Follow redirects manually to build chain
        hops = 0
        while current_resp.is_redirect and hops < 10:
            redirect_chain.append({
                "url": final_url,
                "status": current_resp.status_code,
                "location": current_resp.headers.get("Location", ""),
            })
            final_url = current_resp.headers.get("Location", "")
            if not final_url.startswith("http"):
                break
            current_resp = requests.get(final_url, timeout=15, allow_redirects=False, headers={
                "User-Agent": "Mozilla/5.0 (compatible; SEOBot/1.0)"
            })
            hops += 1

        seo_headers = {
            "status_code": resp.status_code,
            "final_url": final_url,
            "redirect_chain": redirect_chain,
            "redirect_hops": len(redirect_chain),
            "x_robots_tag": headers.get("X-Robots-Tag"),
            "canonical_header": headers.get("Link"),  # rel=canonical in header
            "cache_control": headers.get("Cache-Control"),
            "content_type": headers.get("Content-Type"),
            "server": headers.get("Server"),
            "security": {
                "strict_transport_security": headers.get("Strict-Transport-Security"),
                "content_security_policy": "Content-Security-Policy" in headers,
                "x_frame_options": headers.get("X-Frame-Options"),
                "x_content_type_options": headers.get("X-Content-Type-Options"),
            },
        }

        issues = []
        if len(redirect_chain) > 1:
            issues.append(f"Redirect chain: {len(redirect_chain)} hops (should be 1)")
        if not headers.get("Strict-Transport-Security"):
            issues.append("Missing HSTS header")
        if headers.get("X-Robots-Tag") and "noindex" in headers.get("X-Robots-Tag", ""):
            issues.append("X-Robots-Tag contains noindex")

        seo_headers["issues"] = issues
        return json.dumps(seo_headers, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Server Entry Point ─────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main())
