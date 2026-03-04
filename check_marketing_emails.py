#!/usr/bin/env python3
"""
Check Marketing Emails for New Workshop Events
================================================
Searches Gmail for the most recent "EE & Startup Field Marketing Update" email,
extracts events, and compares against existing events in index.html.

Usage:
    python3 check_marketing_emails.py

Requires: gcloud auth application-default credentials with Gmail scope.
"""

import subprocess
import json
import base64
import re
import sys
import os
import warnings
from datetime import datetime, date

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Year to assume for dates (current year)
CURRENT_YEAR = date.today().year


def get_access_token():
    """Get gcloud access token."""
    result = subprocess.run(
        ["gcloud", "auth", "application-default", "print-access-token"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def gmail_api(endpoint, token):
    """Make a Gmail API call."""
    result = subprocess.run(
        ["curl", "-s", endpoint,
         "-H", f"Authorization: Bearer {token}",
         "-H", "x-goog-user-project: gcp-sandbox-field-eng"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)


def search_emails(token, query, max_results=5):
    """Search Gmail for messages matching query."""
    import urllib.parse
    encoded_query = urllib.parse.quote(query)
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={encoded_query}&maxResults={max_results}"
    return gmail_api(url, token)


def get_message_text(token, message_id):
    """Get the plain text body of a message."""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full"
    msg = gmail_api(url, token)

    # Extract subject and date from headers
    headers = {}
    for header in msg.get("payload", {}).get("headers", []):
        if header["name"] in ("Subject", "Date"):
            headers[header["name"]] = header["value"]

    # Find text/plain part
    def find_text_part(payload):
        if "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    return part["body"].get("data", "")
                result = find_text_part(part)
                if result:
                    return result
        elif payload.get("mimeType") == "text/plain":
            return payload["body"].get("data", "")
        return ""

    data = find_text_part(msg.get("payload", {}))
    text = ""
    if data:
        text = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    return headers, text


def parse_event_date(date_text):
    """Try to parse a date string like 'March 3' or 'Mar 17' into a date object."""
    date_text = date_text.strip()
    # Remove range part (e.g., "Mar 9-11" -> "Mar 9")
    date_text = re.sub(r'(\d{1,2})\s*-\s*\d{1,2}', r'\1', date_text)
    for fmt in (f"%B %d {CURRENT_YEAR}", f"%b %d {CURRENT_YEAR}"):
        try:
            parsed = datetime.strptime(f"{date_text} {CURRENT_YEAR}", fmt)
            return date(CURRENT_YEAR, parsed.month, parsed.day)
        except ValueError:
            continue
    return None


def extract_events_from_email(text):
    """Extract event entries from the marketing email text."""
    events = []

    # Find only future-looking sections (skip "Past Programs" section)
    past_idx = text.find("Past Programs")
    if past_idx > 0:
        text = text[:past_idx]

    # Pattern to match [Date - Location] Title or [Date] Title
    # Captures the full line after the bracket to get the complete title
    simple_pattern = r'\[((?:Jan|Feb|Mar|March|Apr|April|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2}[^\]]*)\]\s*(.+)'

    seen = set()
    for match in re.finditer(simple_pattern, text):
        date_str = match.group(1).strip()
        raw_title = match.group(2).strip()

        # Clean up title - remove trailing links, registration info, etc.
        title = raw_title
        # Remove " - Reg Page", " - Registration Page & Field Resources", etc.
        title = re.split(r'\s+[-–]\s+(?:Reg(?:istration)?\s*Page|Registration Page|Field FAQ|Dashboard|Sales\s+(?:Handbook|Playbook))', title)[0]
        # Remove trailing URLs
        title = re.sub(r'\s*<https?://[^>]+>', '', title)
        # Remove "| go/something" suffixes
        title = re.sub(r'\s*\|\s*go/\S+', '', title)
        # Remove trailing pipes and dashes
        title = re.sub(r'\s*[\|]\s*$', '', title)
        title = re.sub(r'\s*[-–]\s*$', '', title)
        # Remove emoji prefixes
        title = re.sub(r'^[🚨\s]+', '', title)
        title = title.strip()

        # Skip entries that are URLs, very short, or clearly not events
        if len(title) < 5:
            continue
        if title.startswith("<http") or title.startswith("http"):
            continue
        if "NOMINATE" in title.upper() or "COMING SOON" in title.upper():
            continue

        # Skip duplicates (by first 30 chars lowercase)
        key = title.lower()[:30]
        if key in seen:
            continue
        seen.add(key)

        # Determine if in-person based on location in date string
        location = None
        is_in_person = False
        loc_match = re.search(r'[-–]\s*([A-Z][a-zA-Z\s,\.]+)$', date_str)
        if loc_match:
            loc = loc_match.group(1).strip()
            if not re.match(r'^\d', loc) and len(loc) > 2:
                location = loc
                is_in_person = True
                date_str = date_str[:loc_match.start()].strip()

        # Parse date and skip past events
        event_date = parse_event_date(date_str)
        if event_date and event_date < date.today():
            continue

        event_type = "In-Person" if is_in_person else "Virtual"
        category = categorize_event(title)

        events.append({
            "date_text": date_str,
            "date_parsed": event_date,
            "title": title,
            "type": event_type,
            "location": location,
            "category": category,
        })

    # Sort by date
    events.sort(key=lambda e: e["date_parsed"] or date.max)

    return events


def categorize_event(title):
    """Guess category from event title."""
    title_lower = title.lower()
    if "ai day" in title_lower:
        return "AI Day"
    if "forum" in title_lower:
        return "Industry Forum"
    if "sql" in title_lower or "analytics" in title_lower or "bi " in title_lower or "legacy bi" in title_lower:
        return "SQL & Analytics"
    if "lakeflow" in title_lower or "data engineering" in title_lower or "etl" in title_lower or "pipeline" in title_lower:
        return "Data Engineering"
    if "generat" in title_lower or "agent" in title_lower or "gen ai" in title_lower or "agentic" in title_lower:
        return "Generative AI"
    if "governance" in title_lower or "unity catalog" in title_lower:
        return "Governance"
    if "intro" in title_lower or "getting started" in title_lower:
        return "Getting Started"
    if "machine learning" in title_lower or "ml " in title_lower:
        return "Machine Learning"
    if "apps" in title_lower or "development" in title_lower:
        return "Development"
    if "lakebase" in title_lower or "database" in title_lower or "postgres" in title_lower:
        return "Databases"
    if "azure" in title_lower or "aws" in title_lower or "gcp" in title_lower or "google cloud" in title_lower or "cloud" in title_lower:
        return "Cloud"
    if "summit" in title_lower or "conference" in title_lower or "gtc" in title_lower or "gartner" in title_lower:
        return "Conference"
    if "roadmap" in title_lower or "strategy" in title_lower or "executive" in title_lower or "vision" in title_lower:
        return "Strategy"
    if "user group" in title_lower:
        return "Conference"
    return "Unknown"


def get_existing_events(index_path):
    """Extract existing event titles from index.html."""
    with open(index_path, "r") as f:
        content = f.read()

    titles = []
    for match in re.finditer(r'title:\s*"([^"]+)"', content):
        titles.append(match.group(1).lower().strip())
    return titles


def title_similarity(t1, t2):
    """Simple word overlap similarity."""
    # Remove common filler words
    stop = {"on", "the", "a", "an", "with", "for", "and", "in", "to", "of", "&", "-"}
    w1 = set(t1.lower().split()) - stop
    w2 = set(t2.lower().split()) - stop
    if not w1 or not w2:
        return 0
    intersection = w1 & w2
    return len(intersection) / min(len(w1), len(w2))


def is_event_already_listed(event, existing_titles):
    """Check if an event is already in the existing events."""
    title_lower = event["title"].lower().strip()
    for existing_title in existing_titles:
        if title_similarity(title_lower, existing_title) > 0.6:
            return True
    return False


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(script_dir, "index.html")

    print("=" * 70)
    print("  Workshop Newsletter - Marketing Email Event Scanner")
    print("=" * 70)
    print()

    # Get auth token
    print("Authenticating with Gmail...")
    token = get_access_token()
    if not token:
        print("ERROR: Could not get access token. Run: gcloud auth application-default login")
        sys.exit(1)

    # Search for recent emails
    print("Searching for 'EE & Startup Field Marketing Update' emails...")
    results = search_emails(token, 'subject:"EE & Startup Field Marketing Update" newer_than:14d')

    messages = results.get("messages", [])
    if not messages:
        print("No recent marketing update emails found (checked last 14 days).")
        print("Try running again next week!")
        sys.exit(0)

    # Read the most recent email
    msg_id = messages[0]["id"]
    print(f"Found {len(messages)} email(s). Reading most recent...")
    headers, text = get_message_text(token, msg_id)

    print(f"  Subject: {headers.get('Subject', 'N/A')}")
    print(f"  Date:    {headers.get('Date', 'N/A')}")
    print()

    # Extract events from email
    email_events = extract_events_from_email(text)
    print(f"Extracted {len(email_events)} future events from email.")

    # Get existing events from index.html
    existing_titles = get_existing_events(index_path)
    print(f"Found {len(existing_titles)} existing events on the site.")
    print()

    # Compare and find new events
    new_events = []
    already_listed = []
    for event in email_events:
        if is_event_already_listed(event, existing_titles):
            already_listed.append(event)
        else:
            new_events.append(event)

    # Print results
    if new_events:
        print("=" * 70)
        print(f"  POTENTIAL NEW EVENTS ({len(new_events)} found)")
        print("  Review these and decide which to add to the site.")
        print("=" * 70)
        for i, event in enumerate(new_events, 1):
            date_display = event["date_text"]
            if event["date_parsed"]:
                date_display += f" ({event['date_parsed'].strftime('%Y-%m-%d')})"
            print(f"\n  {i}. {event['title']}")
            print(f"     Date:     {date_display}")
            print(f"     Type:     {event['type']}")
            if event["location"]:
                print(f"     Location: {event['location']}")
            print(f"     Category: {event['category']}")
    else:
        print("=" * 70)
        print("  No new events found - site looks up to date!")
        print("=" * 70)

    if already_listed:
        print(f"\n  ({len(already_listed)} events already on the site - skipped)")

    print()
    print("-" * 70)
    print("To add events, update databricks_workshops_EST.csv and the")
    print("EVENTS array in index.html, then push to main.")
    print("-" * 70)


if __name__ == "__main__":
    main()
