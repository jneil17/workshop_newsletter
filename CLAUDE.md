# CLAUDE.md - Workshop Newsletter Project Context

## Project Overview

This is a **unified event feed** for Databricks Customer Enablement workshops and events. A single `index.html` page shows a chronological, filterable feed of all upcoming events. Past events auto-hide based on today's date.

### Key Information
- **Live Domain**: [dbx4startups.com](https://dbx4startups.com)
- **Deployment**: AWS Amplify with automatic deployments from GitHub main branch
- **Repository**: https://github.com/jneil17/workshop_newsletter
- **Framework**: Static HTML with CDN-based resources (Tailwind CSS, Google Fonts, Font Awesome)

## Architecture

### Single Source of Truth
- **`databricks_workshops_EST.csv`** - Authoritative workshop schedule with columns:
  `Subject, Start Date, Start Time, End Date, End Time, All Day Event, Description, Location, Type, Category`
- **`Type`**: `Virtual` or `In-Person`
- **`Category`**: Topic tag used for filtering (see category list below)

### How Events Render
`index.html` contains a `EVENTS` JSON array in a `<script>` tag. Each event object:
```json
{
    "title": "Workshop Name",
    "date": "YYYY-MM-DD",
    "time": "2:00 PM EST",
    "endTime": "3:30 PM EST",
    "duration": "1.5 hrs",
    "type": "Virtual",
    "category": "Data Engineering",
    "description": "...",
    "highlights": ["bullet 1", "bullet 2"],
    "presenters": "Name (Title)",
    "location": "City, ST",
    "url": "https://events.databricks.com/..."
}
```
- `highlights`, `presenters`, `location` are optional
- JS filters events to `date >= today`, sorts chronologically, groups by month
- Format filter: All / Virtual / In-Person
- Category filter: multi-select pill buttons

### File Structure
```
├── databricks_workshops_EST.csv                    # Master data (CSV)
├── index.html                                      # Unified event feed (live page)
├── Databricks_Monthly_Enablement_Newsletter.html   # Feb 2026 archive
├── March_Enablement_Newsletter.html                # Mar 2026 archive
├── April_Enablement_Newsletter.html                # Apr 2026 archive
├── January_Enablement_Newsletter.html              # Jan 2026 archive
├── update-framework.py                             # Sync tool (legacy)
└── CLAUDE.md                                       # This file
```

## Adding New Events

1. Add a row to `databricks_workshops_EST.csv` with all columns including `Type` and `Category`
2. Add a corresponding object to the `EVENTS` array in `index.html`
3. Push to main - Amplify deploys automatically

## Categories & Colors

| Category | Badge Color | Icon |
|----------|-------------|------|
| SQL & Analytics | bg-amber-600 | fa-database |
| Generative AI | bg-purple-600 | fa-robot |
| Data Engineering | bg-blue-600 | fa-gears |
| Governance | bg-emerald-600 | fa-shield-halved |
| Development | bg-cyan-600 | fa-code |
| Machine Learning | bg-orange-600 | fa-brain |
| Getting Started | bg-slate-700 | fa-graduation-cap |
| Databases | bg-rose-600 | fa-server |
| AI Day | bg-red-600 | fa-location-dot |
| Industry Forum | bg-slate-600 | fa-building-columns |
| Conference | bg-slate-800 | fa-people-group |
| Cloud | bg-sky-600 | fa-cloud |
| Strategy | bg-gray-600 | fa-chart-line |

## Brand Colors
- **Lava**: #FF5F46, #FF3621
- **Navy**: #1B3139, #0B2026
- **Oat**: #F9F7F4, #EEEDE9

## Deployment
1. Git push to `main` triggers automatic AWS Amplify deployment
2. Changes appear live at dbx4startups.com within minutes

## Calendar Sync (sync_calendar.py)

Pushes events from `databricks_workshops_EST.csv` to the embedded Google Calendar (`c_779fc...@group.calendar.google.com`). Idempotent and rollback-safe.

**Standard workflow:**
```bash
python3 sync_calendar.py                       # dry-run preview (default, no API writes)
python3 sync_calendar.py --push                # apply inserts & updates
python3 sync_calendar.py --push --force        # also apply deletions
```

**Safety design:**
- Every event we create is tagged with `extendedProperties.private.source="workshop_csv"` and a stable `csv_id` (sha1 of subject + start date + start time).
- Re-runs match by `csv_id` — no duplicates, only insert/update/delete.
- Each `--push` writes `calendar_backups/pre_push_<ts>.json` and appends to `calendar_sync_log.jsonl`.
- Only events tagged by this script are ever touched. Manually-created calendar events are invisible to the tool.
- Deletions require `--force` (extra confirmation gate).

**Rollback:**
```bash
python3 sync_calendar.py --rollback-last       # undo most recent --push
python3 sync_calendar.py --delete-all-tagged --force   # nuclear: remove every csv-sourced event
```

**Test calendar:** `--calendar-id <some-test-cal-id> --push` to push to a personal scratch calendar before targeting the real one.

**Auth:** Uses gcloud application-default credentials. If token fails: `gcloud auth application-default login`.

**Note:** `calendar_sync_log.jsonl` and `calendar_backups/` are local state — keep them in `.gitignore` (audit log of past pushes; not for sharing).

## Marketing Email Scanner

When the user asks to check for new events or wants to update the site, run `check_marketing_emails.py` to scan the latest "EE & Startup Field Marketing Update" emails from Gmail. This surfaces new events not yet on the site.

```bash
python3 check_marketing_emails.py
```

- Searches Gmail for the most recent marketing update (last 14 days)
- Extracts events, filters out past ones, and compares against `index.html`
- Shows potential new events to suggest to the user
- **Do not auto-add events** — always present suggestions and let the user decide which to add
- Requires gcloud auth with Gmail scope (use `/google-auth` if needed)

## Archive Newsletters
Old monthly newsletters remain at their URLs. The header has a "Previous Newsletters" dropdown linking to them.
