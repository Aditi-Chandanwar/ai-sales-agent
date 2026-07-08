"""
run_lead_qualification.py

Runnable demo for Sprint 3: Lead Qualification and Scoring Agent.

Reads data/leads_with_contacts.csv (Sprint 2 output), scores each lead
using simple rule-based logic (see scoring_rules.py), and writes
data/qualified_leads.csv with these new columns added:
    - score
    - qualification_status  (Qualified / Review / Rejected)
    - qualification_reason
    - risk_flags

Run it with:
    python -m lead_qualification.run_lead_qualification

If data/leads_with_contacts.csv doesn't exist yet (e.g. first-time
setup, before running Sprint 1/2), this script falls back to a small
built-in sample so you can still see how qualification works.
"""

import csv
import os

from lead_qualification.lead_qualifier import LeadQualificationAgent


INPUT_CSV = "data/leads_with_contacts.csv"
OUTPUT_CSV = "data/qualified_leads.csv"

# Original columns we expect from Sprint 1 + Sprint 2, in a sensible order.
# Used only for output column ordering - missing columns are handled
# gracefully (see save_qualified_leads).
ORIGINAL_FIELDS = [
    "company_name", "website", "country", "source_url", "search_query",
    "notes", "contact_pages", "emails", "phones",
]

NEW_FIELDS = ["score", "qualification_status", "qualification_reason", "risk_flags"]


def read_leads(input_path: str) -> list:
    """
    Read leads_with_contacts.csv into a list of dicts.

    If the file is missing, we don't crash - we fall back to a small
    built-in sample so first-time users can see the script work
    end-to-end before running Sprint 1/2 for real.
    """
    if not os.path.exists(input_path):
        print(f"[run_lead_qualification] Could not find {input_path}.")
        print("Using a small built-in sample instead, so you can see how this works.")
        print("Run Sprint 1 (lead_generation) and Sprint 2 (contact_extraction) "
              "first to qualify your real leads.\n")
        return _sample_leads()

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _sample_leads() -> list:
    """
    A tiny built-in sample demonstrating the quality gate:
        - Wikipedia page       -> hard-rejected (blocked domain)
        - YouTube video        -> hard-rejected (blocked domain)
        - PDF industry report  -> hard-rejected (.pdf source_url)
        - Mercedes-Benz plant  -> passes the gate, scores normally
    """
    return [
        {
            "company_name": "Automotive industry - Wikipedia",
            "website": "https://en.wikipedia.org/wiki/Automotive_industry",
            "country": "Germany",
            "source_url": "https://en.wikipedia.org/wiki/Automotive_industry",
            "search_query": "automotive manufacturing plants Germany",
            "notes": "Automotive manufacturing, OEM, production plants overview article",
            "contact_pages": "",
            "emails": "",
            "phones": "",
        },
        {
            "company_name": "Inside a Modern Automotive Assembly Plant (Video)",
            "website": "https://www.youtube.com/watch?v=abc123",
            "country": "Germany",
            "source_url": "https://www.youtube.com/watch?v=abc123",
            "search_query": "automotive assembly plants Germany",
            "notes": "Video tour of an automotive OEM production and assembly plant",
            "contact_pages": "",
            "emails": "",
            "phones": "",
        },
        {
            "company_name": "Global Automotive OEM Industry Report 2026",
            "website": "https://example-research.com/reports/automotive-oem-2026.pdf",
            "country": "Germany",
            "source_url": "https://example-research.com/reports/automotive-oem-2026.pdf",
            "search_query": "automotive OEM manufacturing plants Germany",
            "notes": "Industry report covering automotive manufacturing and production trends",
            "contact_pages": "",
            "emails": "",
            "phones": "",
        },
        {
            "company_name": "Mercedes-Benz Group AG",
            "website": "https://www.mercedes-benz.com",
            "country": "Germany",
            "source_url": "https://www.mercedes-benz.com/en/company/plants/",
            "search_query": "automotive assembly plants Germany",
            "notes": "Mercedes-Benz automotive manufacturing and vehicle assembly production plant",
            "contact_pages": "https://www.mercedes-benz.com/en/company/contact/",
            "emails": "media@mercedes-benz.com",
            "phones": "+49 711 17 0",
        },
    ]


def save_qualified_leads(rows: list, output_path: str):
    """Write the qualified leads out to data/qualified_leads.csv."""
    if not rows:
        print("[run_lead_qualification] No rows to save.")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Column order: known original fields that are actually present in this
    # data, then the new qualification fields, then anything unexpected
    # (handles missing/extra columns gracefully instead of crashing).
    fieldnames = [f for f in ORIGINAL_FIELDS if f in rows[0]] + NEW_FIELDS
    extra_fields = [f for f in rows[0].keys() if f not in fieldnames]
    fieldnames += extra_fields

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Saved {len(rows)} qualified leads to {output_path}")
    except OSError as e:
        print(f"[run_lead_qualification] Failed to write CSV to {output_path}: {e}")


def print_summary(rows: list, output_path: str):
    """Print a simple summary of qualification results."""
    total = len(rows)
    qualified = sum(1 for r in rows if r.get("qualification_status") == "Qualified")
    review = sum(1 for r in rows if r.get("qualification_status") == "Review")
    rejected = sum(1 for r in rows if r.get("qualification_status") == "Rejected")

    print("\n--- Lead Qualification Summary ---")
    print(f"Total leads:  {total}")
    print(f"Qualified:    {qualified}")
    print(f"Review:       {review}")
    print(f"Rejected:     {rejected}")
    print(f"Output file:  {output_path}")


def main():
    leads = read_leads(INPUT_CSV)
    if not leads:
        print("[run_lead_qualification] No leads to process.")
        return

    agent = LeadQualificationAgent()
    qualified_rows = agent.qualify_leads(leads)

    save_qualified_leads(qualified_rows, OUTPUT_CSV)
    print_summary(qualified_rows, OUTPUT_CSV)


if __name__ == "__main__":
    main()
