# SEO Tools Integration

## MCP Server (Claude Code)

The `seo_mcp_server.py` provides real SEO tool integrations as MCP tools:

| Tool | Description | API Key Required? |
|------|-------------|-------------------|
| `gsc_search_analytics` | Google Search Console query data | Yes (Google Service Account) |
| `gsc_index_coverage` | Index coverage summary | Yes (Google Service Account) |
| `pagespeed_analyze` | PageSpeed Insights / Core Web Vitals | Optional (free tier available) |
| `validate_schema` | Extract & validate JSON-LD structured data | No |
| `analyze_robots_txt` | Parse and audit robots.txt | No |
| `parse_sitemap` | Parse XML sitemaps | No |
| `analyze_headers` | HTTP header SEO analysis | No |

### Setup

1. Install dependencies:
```bash
pip install mcp google-auth google-auth-oauthlib google-api-python-client requests
```

2. Set environment variables:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GSC_SITE_URL="https://example.com/"
export PAGESPEED_API_KEY="your-api-key"  # Optional, get free at console.cloud.google.com
export AHREFS_API_KEY="your-key"         # Optional
```

3. Add to Claude Code settings:
```json
{
  "mcpServers": {
    "seo-tools": {
      "command": "python3",
      "args": ["tools/seo_mcp_server.py"]
    }
  }
}
```

Or copy the full config from `tools/mcp-config.json`.

### Tools That Work Without API Keys

These tools work immediately with no setup:
- `validate_schema` — Fetches a URL and extracts/validates structured data
- `analyze_robots_txt` — Fetches and parses robots.txt
- `parse_sitemap` — Fetches and parses XML sitemaps
- `analyze_headers` — Analyzes HTTP response headers

### Google Search Console Setup

1. Create a Google Cloud project
2. Enable the Search Console API
3. Create a service account and download the JSON key
4. Add the service account email as a user in Search Console
5. Set `GOOGLE_APPLICATION_CREDENTIALS` to the key file path

### PageSpeed Insights Setup

1. Go to Google Cloud Console
2. Enable the PageSpeed Insights API
3. Create an API key (no OAuth needed)
4. Set `PAGESPEED_API_KEY` (optional — works without a key at lower rate limits)

## Using Without MCP (Any CLI Tool)

If your CLI tool doesn't support MCP, agents can still use these tools via bash:

```bash
# PageSpeed (no auth needed)
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&strategy=mobile"

# Robots.txt
curl https://example.com/robots.txt

# Sitemap
curl https://example.com/sitemap.xml
```

Agents should use `WebFetch` or equivalent tools for live URL analysis.
