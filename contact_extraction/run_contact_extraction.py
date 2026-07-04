"""
run_contact_extraction.py

Runnable demo for Sprint 2: the Contact Extraction Agent.

For every lead in data/leads.csv, this script:
    1. Fetches the company's homepage.
    2. Finds likely contact/about/imprint pages on that homepage.
    3. Fetches those contact pages.
    4. Extracts any publicly visible emails and phone numbers from the
       homepage + contact pages combined.
    5. Writes an updated CSV (data/leads_with_contacts.csv) with the
       original lead fields plus: contact_pages, emails, phones.

Important: this only extracts information that is already publicly
published on the company's own website. It never guesses email
addresses (e.g. it does not build "first.last@domain.com" patterns).

Run it with:
    python -m contact_extraction.run_contact_extraction

Requires Sprint 1 to have already produced data/leads.csv.
"""

import csv
import os

from contact_extraction.website_scraper import WebsiteScraper
from contact_extraction.contact_page_finder import ContactPageFinder
from contact_extraction.email_extractor import EmailExtractor


INPUT_CSV = "data/leads.csv"
OUTPUT_CSV = "data/leads_with_contacts.csv"

# Columns we expect to already exist in leads.csv (from Sprint 1)
LEAD_FIELDS = ["company_name", "website", "country", "source_url", "search_query", "notes"]

# New columns this sprint adds
CONTACT_FIELDS = ["contact_pages", "emails", "phones"]

OUTPUT_FIELDNAMES = LEAD_FIELDS + CONTACT_FIELDS


class ContactExtractionAgent:
    """
    Orchestrates the Sprint 2 pipeline: scraper -> contact page finder ->
    email/phone extractor, for a single lead's website.
    """

    def __init__(self, scraper=None, page_finder=None, extractor=None):
        # Each collaborator can be swapped out (e.g. for testing with fakes).
        # By default we use the real implementations.
        self.scraper = scraper or WebsiteScraper()
        self.page_finder = page_finder or ContactPageFinder()
        self.extractor = extractor or EmailExtractor()

    def extract_contacts_for_website(self, website_url: str) -> dict:
        """
        Run the full pipeline for one website.

        Returns a dict: {"contact_pages": [...], "emails": [...], "phones": [...]}
        Never raises - if the site can't be reached, everything comes back empty.
        """
        if not website_url:
            return {"contact_pages": [], "emails": [], "phones": []}

        # Step 1: fetch homepage
        homepage_html = self.scraper.fetch_html(website_url)

        # Step 2: find candidate contact pages on the homepage
        contact_pages = self.page_finder.find_contact_pages(website_url, homepage_html)

        # Step 3: fetch each contact page's HTML
        all_html = homepage_html
        for page_url in contact_pages:
            page_html = self.scraper.fetch_html(page_url)
            all_html += "\n" + page_html

        # Step 4: extract emails + phones from everything we fetched
        emails = self.extractor.extract_emails(all_html)
        phones = self.extractor.extract_phones(all_html)

        return {
            "contact_pages": contact_pages,
            "emails": emails,
            "phones": phones,
        }


def read_leads(input_path: str) -> list:
    """Read leads.csv into a list of plain dicts."""
    if not os.path.exists(input_path):
        print(f"[run_contact_extraction] Could not find {input_path}. "
              f"Run Sprint 1's lead_generation.run_lead_discovery first.")
        return []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_leads_with_contacts(rows: list, output_path: str):
    """Write the enriched rows out to data/leads_with_contacts.csv."""
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Saved {len(rows)} leads (with contact info) to {output_path}")
    except OSError as e:
        print(f"[run_contact_extraction] Failed to write CSV to {output_path}: {e}")


def main():
    leads = read_leads(INPUT_CSV)
    if not leads:
        return

    agent = ContactExtractionAgent()
    enriched_rows = []

    for lead in leads:
        website = lead.get("website", "")
        print(f"Extracting contacts for: {lead.get('company_name', website)} ({website})")

        contacts = agent.extract_contacts_for_website(website)

        # Build the output row: original lead fields + new contact fields,
        # joining lists into single ";"-separated strings for CSV storage.
        row = {field: lead.get(field, "") for field in LEAD_FIELDS}
        row["contact_pages"] = "; ".join(contacts["contact_pages"])
        row["emails"] = "; ".join(contacts["emails"])
        row["phones"] = "; ".join(contacts["phones"])

        enriched_rows.append(row)

    save_leads_with_contacts(enriched_rows, OUTPUT_CSV)


if __name__ == "__main__":
    main()
