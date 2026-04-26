# Data Retention Policy

> Version: 1.0  
> Effective: 2026-04-26  
> Scope: All AI SEO Agency tools, audits, and client deliverables  
> Owner: SEO Strategist / Compliance agent

---

## 1. Principles

1. **Minimal collection** — We only store data required to produce audits and run campaigns.
2. **Client ownership** — Clients own their audit data; we are custodians.
3. **Auto-expiry** — Data has a TTL by default; deletion is automatic unless explicitly extended.
4. **Right to erasure** — Any client can request full deletion with 48-hour SLA.

---

## 2. Data Categories & Retention Periods

| Category | Storage Location | Default Retention | Max Retention | Encryption |
|---|---|---|---|---|
| Audit JSON / Markdown | `data/audits/` | 90 days | 2 years | At-rest (file-system) |
| Crawl snapshots (raw HTML) | `data/crawls/` | 14 days | 90 days | None (ephemeral) |
| PageSpeed Insights raw API | `data/psi/` | 30 days | 1 year | None |
| Backlink profiles (fetched) | `data/backlinks/` | 90 days | 1 year | None |
| Outreach CRM (SQLite) | `data/backlinks.db` | Life of contract + 1 year | 3 years | None |
| Server access logs (if ingested) | `data/logs/` or env-specified | 30 days | 90 days | None |
| Task state / Ledger | `state/tasks/`, `state/ledger.md` | 2 years | 5 years | None |
| API keys / credentials | Environment variables / `.env` | N/A (never committed) | N/A | N/A |

---

## 3. Audit Data Lifecycle

### Creation
- Each audit run generates a JSON + Markdown pair in `data/audits/`.
- File names are slugified domains (e.g. `example-com-audit.json`).
- Task files in `state/tasks/` reference these deliverables.

### Active Phase (0 – 90 days)
- Data is considered active and may be referenced in follow-up audits.
- Agents may read historical audits for delta comparisons.

### Archive Phase (90 days – 2 years)
- Automatically moved to `data/archive/audits/YYYY-MM/` if retention extension is enabled.
- Compressed with gzip.
- Not loaded by default into active tooling.

### Deletion Phase (> 2 years or on client request)
- Hard delete. No soft-delete / trashcan.
- Confirmed by checksum manifest before and after deletion.

---

## 4. Crawl Snapshot TTL

Raw HTML snapshots are the largest data consumer.

- **Default**: 14 days.
- **Rationale**: HTML changes frequently; old snapshots mislead delta analysis.
- **Override**: Set `CRAWL_TTL_DAYS` env var or pass `snapshot_ttl=` to crawler.
- **Cleanup**: Run `python tools/audit/cleanup.py --older-than 14` via cron weekly.

---

## 5. Backlink & Outreach Data

- Fetched backlink profiles are refreshed on each campaign cycle; stale dumps are purged.
- The SQLite CRM (`data/backlinks.db`) retains prospect history for relationship continuity.
- On client offboarding, export their CRM slice to CSV, hand over, then `DELETE` their rows.

---

## 6. Log File Ingestion

- Server logs are **never** stored permanently by default.
- If ingested for audit (`SEO_LOG_FILE` or `crawl_meta['log_file']`), parsed aggregates are kept; raw logs are streamed and discarded.
- Do not commit log files to git. They are in `.gitignore`.

---

## 7. Right to Erasure (GDPR / CCPA / Client Request)

1. Client sends request to `compliance@agency.local` (or opens GitHub issue tagged `privacy`).
2. Within **48 hours**:
   - Identify all data associated with the domain/email.
   - Delete audit files, crawl snapshots, PSI data, and backlink exports.
   - Scrub ledger references (replace with `[redacted]`).
   - If outreach CRM contains the client domain, export then delete rows.
3. Respond with deletion manifest (list of files/rows removed + timestamps).

---

## 8. Automated Cleanup

A weekly cron runs:

```bash
# /etc/cron.d/ai-seo-agency-cleanup
0 3 * * 0 luciousfox cd /home/luciousfox/Projects/ai-seo-agency && \
  python3 tools/audit/cleanup.py \
    --audit-ttl 90 \
    --crawl-ttl 14 \
    --psi-ttl 30 \
    --dry-run >> /var/log/ai-seo-cleanup.log 2>&1
```

Remove `--dry-run` after verification.

---

## 9. Exceptions

| Exception | Approval | Duration | Audit Trail |
|---|---|---|---|
| Legal hold | CEO / Legal | Until hold lifted | GitHub issue + label |
| Benchmark dataset | SEO Strategist | 1 year | `data/retention-exceptions.json` |
| Research corpus | SEO Strategist + Client consent | Per study | Signed DUA on file |

---

## 10. Responsibilities

| Role | Responsibility |
|---|---|
| **SEO Strategist** | Reviews retention schedule quarterly; approves exceptions. |
| **Technical SEO agent** | Implements cleanup scripts; monitors disk usage. |
| **Client Manager** | Handles erasure requests; communicates with clients. |
| **QA Validator** | Audits deletion manifests for completeness. |

---

## 11. Policy Updates

- Amendments are PRs against this file.
- Major changes (retention extension, new categories) require strategist approval.
- Minor fixes (typos, contact updates) can be patched by any agent.

---

*Last updated: 2026-04-26*
