#!/usr/bin/env python3
"""
sync_calendar.py — Sync databricks_workshops_EST.csv to Google Calendar.

Idempotent, taggable, rollback-safe. See CLAUDE.md "Calendar Sync" section.

    python3 sync_calendar.py                        # dry-run (default)
    python3 sync_calendar.py --push                 # apply changes
    python3 sync_calendar.py --push --force         # allow deletions
    python3 sync_calendar.py --rollback-last        # undo most recent --push
    python3 sync_calendar.py --delete-all-tagged --force   # nuclear cleanup
    python3 sync_calendar.py --calendar-id <id> --push     # push to test calendar

Design:
  • Each managed event carries extendedProperties.private.source="workshop_csv"
    plus a stable csv_id (sha1 of subject+start_date+start_time, 16 chars).
  • Re-runs match by csv_id — no duplicates, only insert/update/delete.
  • Pre-push snapshot saved to ./calendar_backups/pre_push_<ts>.json.
  • Every API change is appended to ./calendar_sync_log.jsonl (per-sync-id).
  • Rollback replays the most recent sync_id in reverse.
"""

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing dependency: pip install requests")
    sys.exit(1)

DEFAULT_CALENDAR_ID = "c_779fc1659357328eadc3f875c0cf022f28fa77c77ace313848f36461c4ee1882@group.calendar.google.com"
DEFAULT_CSV = "databricks_workshops_EST.csv"
SOURCE_TAG = "workshop_csv"
TIMEZONE = "America/New_York"  # CSV times are EST/EDT
QUOTA_PROJECT = "gcp-sandbox-field-eng"
LOG_FILE = Path("calendar_sync_log.jsonl")
BACKUP_DIR = Path("calendar_backups")
API_ROOT = "https://www.googleapis.com/calendar/v3"


def get_access_token():
    try:
        r = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"ERROR: gcloud token unavailable: {e}\n"
              f"Run: gcloud auth application-default login")
        sys.exit(1)


def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "x-goog-user-project": QUOTA_PROJECT,
        "Content-Type": "application/json",
    }


def csv_id(subject, start_date, start_time):
    raw = f"{subject}|{start_date}|{start_time}"
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def parse_csv_dt(date_str, time_str):
    return datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %I:%M %p").strftime("%Y-%m-%dT%H:%M:%S")


def csv_row_to_event(row):
    cid = csv_id(row["Subject"], row["Start Date"], row["Start Time"])
    description = (row.get("Description") or "").strip()
    location = (row.get("Location") or "").strip()
    if location.startswith("http"):
        description = f"{description}\n\nRegister: {location}".strip()
        location = ""
    body = {
        "summary": row["Subject"].strip(),
        "description": description,
        "start": {"dateTime": parse_csv_dt(row["Start Date"], row["Start Time"]), "timeZone": TIMEZONE},
        "end":   {"dateTime": parse_csv_dt(row["End Date"],   row["End Time"]),   "timeZone": TIMEZONE},
        "extendedProperties": {"private": {"source": SOURCE_TAG, "csv_id": cid}},
    }
    if location:
        body["location"] = location
    return cid, body


def read_csv(path, upcoming_only=True):
    today = datetime.now().date()
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("Subject"):
                continue
            if upcoming_only:
                try:
                    if datetime.strptime(row["Start Date"], "%m/%d/%Y").date() < today:
                        continue
                except ValueError:
                    continue
            rows.append(row)
    return rows


def list_existing_events(token, calendar_id, time_min=None):
    url = f"{API_ROOT}/calendars/{calendar_id}/events"
    params = {
        "privateExtendedProperty": f"source={SOURCE_TAG}",
        "maxResults": 2500,
        "singleEvents": "true",
        "showDeleted": "false",
    }
    if time_min:
        params["timeMin"] = time_min
    items, page_token = [], None
    while True:
        if page_token:
            params["pageToken"] = page_token
        r = requests.get(url, headers=headers(token), params=params)
        r.raise_for_status()
        data = r.json()
        items.extend(data.get("items", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return {ev["extendedProperties"]["private"]["csv_id"]: ev
            for ev in items
            if ev.get("extendedProperties", {}).get("private", {}).get("csv_id")}


def _norm_dt(s):
    return s[:19] if s and "T" in s else (s or "")


def diff_plan(csv_rows, existing):
    to_insert, to_update = [], []
    seen = set()
    for row in csv_rows:
        cid, body = csv_row_to_event(row)
        seen.add(cid)
        if cid in existing:
            ex = existing[cid]
            changed = (
                ex.get("summary") != body["summary"]
                or (ex.get("description") or "") != body["description"]
                or _norm_dt(ex.get("start", {}).get("dateTime")) != body["start"]["dateTime"]
                or _norm_dt(ex.get("end", {}).get("dateTime")) != body["end"]["dateTime"]
                or (ex.get("location") or "") != body.get("location", "")
            )
            if changed:
                to_update.append((cid, ex, body))
        else:
            to_insert.append((cid, body))
    to_delete = [(cid, ex) for cid, ex in existing.items() if cid not in seen]
    return to_insert, to_update, to_delete


def write_log(entries):
    with LOG_FILE.open("a") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def write_backup(tag, snapshot):
    BACKUP_DIR.mkdir(exist_ok=True)
    p = BACKUP_DIR / f"{tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    p.write_text(json.dumps(snapshot, indent=2))
    return p


def _strip_readonly(ev):
    for k in ("etag", "iCalUID", "kind", "created", "updated", "htmlLink", "id", "status", "creator", "organizer"):
        ev.pop(k, None)
    return ev


def dry_run(token, calendar_id, csv_path):
    rows = read_csv(csv_path, upcoming_only=True)
    time_min = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = list_existing_events(token, calendar_id, time_min=time_min)
    to_insert, to_update, to_delete = diff_plan(rows, existing)
    print(f"\nDRY RUN — no changes will be applied")
    print(f"Calendar:           {calendar_id}")
    print(f"CSV upcoming rows:  {len(rows)}")
    print(f"Tagged on calendar: {len(existing)}")
    print(f"\nWould insert ({len(to_insert)}):")
    for _, body in to_insert:
        print(f"  + {body['summary']}  {body['start']['dateTime']}")
    print(f"\nWould update ({len(to_update)}):")
    for _, _ex, body in to_update:
        print(f"  ~ {body['summary']}  {body['start']['dateTime']}")
    print(f"\nWould delete ({len(to_delete)}):")
    for _, ex in to_delete:
        print(f"  - {ex.get('summary')}  {ex.get('start', {}).get('dateTime')}")


def push(token, calendar_id, csv_path, force=False):
    rows = read_csv(csv_path, upcoming_only=True)
    time_min = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = list_existing_events(token, calendar_id, time_min=time_min)
    to_insert, to_update, to_delete = diff_plan(rows, existing)
    print(f"\nPlan: insert={len(to_insert)} update={len(to_update)} delete={len(to_delete)}")
    if to_delete and not force:
        print("\nDELETIONS detected — pass --force to apply.")
        for _, ex in to_delete[:10]:
            print(f"  - would delete: {ex.get('summary')} {ex.get('start', {}).get('dateTime')}")
        return

    backup_path = write_backup("pre_push", list(existing.values()))
    print(f"Backup: {backup_path}")

    sync_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_entries = []

    for cid, body in to_insert:
        r = requests.post(f"{API_ROOT}/calendars/{calendar_id}/events", headers=headers(token), json=body)
        r.raise_for_status()
        ev = r.json()
        print(f"  + {body['summary']}  {body['start']['dateTime']}")
        log_entries.append({"sync_id": sync_id, "op": "insert", "csv_id": cid, "event_id": ev["id"], "after": body})

    for cid, ex, body in to_update:
        r = requests.put(f"{API_ROOT}/calendars/{calendar_id}/events/{ex['id']}", headers=headers(token), json=body)
        r.raise_for_status()
        print(f"  ~ {body['summary']}  {body['start']['dateTime']}")
        log_entries.append({"sync_id": sync_id, "op": "update", "csv_id": cid, "event_id": ex["id"], "before": ex, "after": body})

    if force:
        for cid, ex in to_delete:
            r = requests.delete(f"{API_ROOT}/calendars/{calendar_id}/events/{ex['id']}", headers=headers(token))
            if r.status_code in (200, 204, 410):
                print(f"  - {ex.get('summary')}  {ex.get('start', {}).get('dateTime')}")
                log_entries.append({"sync_id": sync_id, "op": "delete", "csv_id": cid, "event_id": ex["id"], "before": ex})
            else:
                r.raise_for_status()

    write_log(log_entries)
    print(f"\nDone. {len(log_entries)} ops logged to {LOG_FILE} (sync_id={sync_id})")


def rollback_last(token, calendar_id):
    if not LOG_FILE.exists() or not LOG_FILE.read_text().strip():
        print("No log entries to roll back.")
        return
    entries = [json.loads(l) for l in LOG_FILE.read_text().strip().splitlines()]
    # Skip prior rollback markers
    real = [e for e in entries if e.get("op") != "rollback"]
    if not real:
        print("Nothing to undo.")
        return
    last_sync_id = real[-1]["sync_id"]
    batch = [e for e in real if e["sync_id"] == last_sync_id]
    print(f"Rolling back sync_id={last_sync_id} ({len(batch)} ops)...")

    for e in reversed(batch):
        op = e["op"]
        if op == "insert":
            r = requests.delete(f"{API_ROOT}/calendars/{calendar_id}/events/{e['event_id']}", headers=headers(token))
            print(f"  undo insert: {e['event_id']} -> {r.status_code}")
        elif op == "update":
            body = _strip_readonly(dict(e["before"]))
            r = requests.put(f"{API_ROOT}/calendars/{calendar_id}/events/{e['event_id']}",
                             headers=headers(token), json=body)
            r.raise_for_status()
            print(f"  undo update: restored {e['event_id']}")
        elif op == "delete":
            body = _strip_readonly(dict(e["before"]))
            r = requests.post(f"{API_ROOT}/calendars/{calendar_id}/events", headers=headers(token), json=body)
            r.raise_for_status()
            print(f"  undo delete: recreated csv_id={e['csv_id']}")

    with LOG_FILE.open("a") as f:
        f.write(json.dumps({"sync_id": last_sync_id, "op": "rollback",
                            "ts": datetime.now().isoformat()}) + "\n")
    print(f"\nRollback complete (sync_id={last_sync_id}).")


def delete_all_tagged(token, calendar_id, force=False):
    existing = list_existing_events(token, calendar_id)
    print(f"Found {len(existing)} tagged events.")
    if not force:
        print("Pass --force to actually delete.")
        for _, ex in list(existing.items())[:10]:
            print(f"  - would delete: {ex.get('summary')} {ex.get('start', {}).get('dateTime')}")
        return
    backup_path = write_backup("pre_delete_all", list(existing.values()))
    print(f"Backup: {backup_path}")
    for _, ex in existing.items():
        r = requests.delete(f"{API_ROOT}/calendars/{calendar_id}/events/{ex['id']}", headers=headers(token))
        if r.status_code in (200, 204, 410):
            print(f"  - {ex.get('summary')}")
    print(f"\nDone. Backup: {backup_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--calendar-id", default=DEFAULT_CALENDAR_ID)
    parser.add_argument("--push", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--force", action="store_true", help="Allow destructive ops")
    parser.add_argument("--rollback-last", action="store_true")
    parser.add_argument("--delete-all-tagged", action="store_true")
    args = parser.parse_args()

    token = get_access_token()

    if args.rollback_last:
        rollback_last(token, args.calendar_id)
    elif args.delete_all_tagged:
        delete_all_tagged(token, args.calendar_id, force=args.force)
    elif args.push:
        push(token, args.calendar_id, args.csv, force=args.force)
    else:
        dry_run(token, args.calendar_id, args.csv)


if __name__ == "__main__":
    main()
