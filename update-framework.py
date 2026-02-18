#!/usr/bin/env python3
"""
Workshop Newsletter Update Framework

This script provides automated synchronization between Databricks event pages
and the workshop newsletter CSV/HTML files.

Dependencies:
    pip install requests beautifulsoup4

Usage:
    python update-framework.py --workshop "End-to-End AI" --url "https://events.databricks.com/..."
    python update-framework.py --check-all  # Check all workshop URLs for updates
    python update-framework.py --sync-csv   # Sync CSV descriptions with event pages
"""

import sys
import csv
import re
import json
import argparse
from datetime import datetime
from urllib.parse import urlparse

# Check for required dependencies
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install required packages:")
    print("pip install requests beautifulsoup4")
    sys.exit(1)


class WorkshopUpdateFramework:
    def __init__(self):
        self.csv_file = "databricks_workshops_EST.csv"
        self.newsletter_files = [
            "Databricks_Monthly_Enablement_Newsletter.html",
            "February_Enablement_Newsletter.html",
            "March_Enablement_Newsletter.html",
            "April_Enablement_Newsletter.html"
        ]

    def fetch_webpage_content(self, url):
        """Fetch and parse content from a Databricks event webpage."""
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract relevant information
            content = {
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'agenda': self._extract_agenda(soup),
                'presenters': self._extract_presenters(soup),
                'features': self._extract_features(soup)
            }

            return content

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _extract_title(self, soup):
        """Extract workshop title from webpage."""
        title_selectors = [
            'h1', '.event-title', '.workshop-title',
            '[data-testid="event-title"]'
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()

        return None

    def _extract_description(self, soup):
        """Extract detailed description from webpage."""
        desc_selectors = [
            '.event-description', '.workshop-description',
            '[data-testid="event-description"]', '.content p'
        ]

        for selector in desc_selectors:
            elements = soup.select(selector)
            if elements:
                return ' '.join([elem.get_text().strip() for elem in elements])

        return None

    def _extract_presenters(self, soup):
        """Extract presenter information from webpage."""
        presenter_patterns = [
            r'Presenter[s]?:\s*(.+?)(?:\n|<|$)',
            r'Speaker[s]?:\s*(.+?)(?:\n|<|$)',
            r'Host[s]?:\s*(.+?)(?:\n|<|$)'
        ]

        page_text = soup.get_text()

        for pattern in presenter_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_features(self, soup):
        """Extract workshop features/agenda items from webpage."""
        features = []

        # Look for bulleted lists, agenda items, etc.
        list_selectors = ['ul li', 'ol li', '.agenda-item', '.feature']

        for selector in list_selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 2:  # Only if substantial content
                features = [elem.get_text().strip() for elem in elements[:6]]
                break

        return features

    def read_csv_workshops(self):
        """Read current workshops from CSV file."""
        workshops = []

        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    workshops.append(row)
        except FileNotFoundError:
            print(f"CSV file {self.csv_file} not found!")
            return []

        return workshops

    def update_csv_workshop(self, workshop_name, new_description):
        """Update a specific workshop description in the CSV file."""
        workshops = []
        updated_count = 0

        # Read all workshops
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                workshops = list(reader)
        except FileNotFoundError:
            print(f"CSV file {self.csv_file} not found!")
            return False

        # Update matching workshops
        for workshop in workshops:
            if workshop.get('Subject', '').strip() == workshop_name.strip():
                workshop['Description'] = new_description
                updated_count += 1

        # Write back to file
        if updated_count > 0:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=workshops[0].keys())
                writer.writeheader()
                writer.writerows(workshops)

            print(f"Updated {updated_count} instances of '{workshop_name}' in CSV")
            return True
        else:
            print(f"No workshops found matching '{workshop_name}'")
            return False

    def generate_html_content(self, webpage_content):
        """Generate HTML content based on webpage information."""
        if not webpage_content:
            return None

        # Generate description paragraph
        description = webpage_content.get('description', '')

        # Generate features list
        features = webpage_content.get('features', [])
        features_html = ''
        if features:
            features_items = ''.join([f'<li>• {feature}</li>' for feature in features])
            features_html = f'''
                    <div class="bg-oat-light rounded p-4 mb-4">
                        <div class="font-semibold text-navy-800 mb-2">Workshop features:</div>
                        <ul class="text-sm text-gray-700 space-y-1">
                            {features_items}
                        </ul>
                    </div>'''

        # Generate presenters section
        presenters = webpage_content.get('presenters', '')
        presenters_html = ''
        if presenters:
            presenters_html = f'''
                    <div class="bg-gray-50 rounded p-3 mb-4 text-sm">
                        <div class="font-semibold text-navy-800 mb-1">Presenters:</div>
                        <div class="text-gray-700">{presenters}</div>
                    </div>'''

        return {
            'description': description,
            'features_html': features_html,
            'presenters_html': presenters_html
        }

    def check_workshop_for_updates(self, workshop_name):
        """Check if a specific workshop needs updates by comparing with webpage."""
        workshops = self.read_csv_workshops()
        workshop_entries = [w for w in workshops if w.get('Subject', '').strip() == workshop_name.strip()]

        if not workshop_entries:
            print(f"Workshop '{workshop_name}' not found in CSV")
            return False

        # Get the URL from first entry (assuming all use same URL)
        url = workshop_entries[0].get('Location', '').strip()
        if not url:
            print(f"No URL found for workshop '{workshop_name}'")
            return False

        print(f"Checking {url} for updates...")
        webpage_content = self.fetch_webpage_content(url)

        if not webpage_content:
            print("Could not fetch webpage content")
            return False

        # Compare current CSV description with webpage
        current_desc = workshop_entries[0].get('Description', '').strip()
        webpage_desc = webpage_content.get('description', '').strip()

        # Simple comparison - could be enhanced with more sophisticated matching
        similarity_threshold = 0.5  # Adjust as needed

        if len(webpage_desc) > len(current_desc) * 1.2:  # Webpage has significantly more content
            print(f"UPDATE RECOMMENDED: Webpage has more detailed content")
            print(f"Current CSV: {current_desc[:100]}...")
            print(f"Webpage: {webpage_desc[:100]}...")
            return True
        else:
            print("Content appears to be in sync")
            return False

    def sync_all_workshops(self):
        """Check all workshops for potential updates."""
        workshops = self.read_csv_workshops()
        unique_workshops = {}

        # Group by workshop name
        for workshop in workshops:
            name = workshop.get('Subject', '').strip()
            if name not in unique_workshops:
                unique_workshops[name] = workshop

        print(f"Checking {len(unique_workshops)} unique workshops for updates...")

        for name, workshop in unique_workshops.items():
            print(f"\n--- Checking {name} ---")
            self.check_workshop_for_updates(name)

    def backup_files(self):
        """Create backup of current files before making changes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        import shutil
        try:
            shutil.copy(self.csv_file, f"{self.csv_file}.backup_{timestamp}")
            print(f"Created backup: {self.csv_file}.backup_{timestamp}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")


def main():
    parser = argparse.ArgumentParser(description='Workshop Newsletter Update Framework')
    parser.add_argument('--workshop', help='Workshop name to check/update')
    parser.add_argument('--url', help='URL of event page to sync from')
    parser.add_argument('--check-all', action='store_true', help='Check all workshops for updates')
    parser.add_argument('--sync-csv', action='store_true', help='Sync CSV descriptions with event pages')
    parser.add_argument('--backup', action='store_true', help='Create backup of files')

    args = parser.parse_args()

    framework = WorkshopUpdateFramework()

    if args.backup:
        framework.backup_files()

    if args.check_all:
        framework.sync_all_workshops()

    elif args.workshop and args.url:
        # Fetch content from URL and update specific workshop
        webpage_content = framework.fetch_webpage_content(args.url)
        if webpage_content and webpage_content.get('description'):
            framework.update_csv_workshop(args.workshop, webpage_content['description'])
        else:
            print("Could not extract content from webpage")

    elif args.workshop:
        # Check specific workshop for updates
        framework.check_workshop_for_updates(args.workshop)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()