"""
run_pipeline.py

Interactive entry point for the AI Sales Operating System.

Lets you run the full pipeline (Lead Discovery -> Contact Extraction ->
Lead Qualification -> Email Draft Generation) or any single stage on
its own, and view a summary of the Lead Registry - the persistent
master record of every lead the system has ever seen, kept up to date
across every run (see lead_registry/).

Every stage still writes its own CSV checkpoint file, exactly as
before:
    data/leads.csv
    data/leads_with_contacts.csv
    data/qualified_leads.csv
    data/email_drafts.csv

The Lead Registry (data/lead_registry.csv) is synced from those
checkpoints after each stage, so a lead's full history is tracked in
one place regardless of which stages you've run, or in what order.

This script never sends emails. Email Draft Generation only ever
produces drafts for human review.
"""

import csv
import os

from dotenv import load_dotenv

from lead_generation.lead_discovery import LeadDiscoveryRequest, Lead
from core import pipeline
from lead_registry.lead_registry import LeadRegistry
from lead_registry import registry_sync

# Load TAVILY_API_KEY / ANTHROPIC_API_KEY from a .env file
load_dotenv()

MENU_TEXT = """
==================================
AI SALES OPERATING SYSTEM
==================================

1. Run Full Pipeline
2. Lead Discovery
3. Contact Extraction
4. Lead Qualification
5. Email Draft Generation
6. View Registry Summary
0. Exit
"""


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def _read_csv_rows(path: str) -> list:
    """Read a CSV checkpoint into a list of dicts, or [] with a message if missing."""
    if not os.path.exists(path):
        print(f"[run_pipeline] Could not find {path}. Run the earlier stage(s) first.")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def prompt_discovery_request() -> LeadDiscoveryRequest:
    """Ask the user for Lead Discovery inputs, with sensible defaults on Enter."""
    print("\n-- Lead Discovery inputs (press Enter to accept the default) --")
    region = input("Region [Germany]: ").strip() or "Germany"
    industry = input("Industry [Automotive]: ").strip() or "Automotive"
    lead_count_raw = input("Lead count [10]: ").strip()
    lead_count = int(lead_count_raw) if lead_count_raw.isdigit() else 10
    product_category = input("Product category [Industrial sensors]: ").strip() or "Industrial sensors"
    target_type = input("Target type [End users only]: ").strip() or "End users only"

    return LeadDiscoveryRequest(
        region=region,
        industry=industry,
        lead_count=lead_count,
        product_category=product_category,
        target_type=target_type,
    )


# ----------------------------------------------------------------------
# Menu actions - one per menu option, each syncs the registry and
# prints a "✓ ... Complete" line so progress is always visible.
# ----------------------------------------------------------------------
def run_full_pipeline_menu(registry: LeadRegistry):
    request = prompt_discovery_request()

    leads = pipeline.run_lead_discovery_stage(request)
    if not leads:
        print("[run_pipeline] No leads discovered - stopping here.")
        return
    registry_sync.sync_lead_discovery(registry, pipeline.LEADS_CSV)
    print("✓ Lead Discovery Complete\n")

    enriched_rows = pipeline.run_contact_extraction_stage(leads)
    registry_sync.sync_contact_extraction(registry, pipeline.LEADS_WITH_CONTACTS_CSV)
    print("✓ Contact Extraction Complete\n")

    qualified_rows = pipeline.run_lead_qualification_stage(enriched_rows)
    registry_sync.sync_lead_qualification(registry, pipeline.QUALIFIED_LEADS_CSV)
    print("✓ Lead Qualification Complete\n")

    pipeline.run_email_generation_stage(qualified_rows)
    registry_sync.sync_email_generation(registry, pipeline.EMAIL_DRAFTS_CSV)
    print("✓ Email Draft Generation Complete\n")

    print("Pipeline Finished Successfully")


def run_lead_discovery_menu(registry: LeadRegistry):
    request = prompt_discovery_request()
    pipeline.run_lead_discovery_stage(request)
    registry_sync.sync_lead_discovery(registry, pipeline.LEADS_CSV)
    print("✓ Lead Discovery Complete")


def run_contact_extraction_menu(registry: LeadRegistry):
    rows = _read_csv_rows(pipeline.LEADS_CSV)
    if not rows:
        return
    leads = [Lead(**row) for row in rows]

    pipeline.run_contact_extraction_stage(leads)
    registry_sync.sync_contact_extraction(registry, pipeline.LEADS_WITH_CONTACTS_CSV)
    print("✓ Contact Extraction Complete")


def run_lead_qualification_menu(registry: LeadRegistry):
    rows = _read_csv_rows(pipeline.LEADS_WITH_CONTACTS_CSV)
    if not rows:
        return

    pipeline.run_lead_qualification_stage(rows)
    registry_sync.sync_lead_qualification(registry, pipeline.QUALIFIED_LEADS_CSV)
    print("✓ Lead Qualification Complete")


def run_email_generation_menu(registry: LeadRegistry):
    rows = _read_csv_rows(pipeline.QUALIFIED_LEADS_CSV)
    if not rows:
        return

    pipeline.run_email_generation_stage(rows)
    registry_sync.sync_email_generation(registry, pipeline.EMAIL_DRAFTS_CSV)
    print("✓ Email Draft Generation Complete")


def view_registry_summary(registry: LeadRegistry):
    summary = registry.get_summary()

    print("\n--- Lead Registry Summary ---")
    print(f"Total leads tracked: {summary['total']}")

    print("\nBy current stage:")
    for stage, count in summary["by_stage"].items():
        print(f"  {stage}: {count}")

    print("\nBy qualification status:")
    for status, count in summary["by_qualification_status"].items():
        print(f"  {status}: {count}")

    print("\nBy email status:")
    for status, count in summary["by_email_status"].items():
        print(f"  {status}: {count}")

    print(f"\nRegistry file: {registry.storage.path}")


# ----------------------------------------------------------------------
# Main menu loop
# ----------------------------------------------------------------------
def main():
    registry = LeadRegistry()

    actions = {
        "1": run_full_pipeline_menu,
        "2": run_lead_discovery_menu,
        "3": run_contact_extraction_menu,
        "4": run_lead_qualification_menu,
        "5": run_email_generation_menu,
        "6": view_registry_summary,
    }

    while True:
        print(MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Exiting. Goodbye!")
            break

        action = actions.get(choice)
        if not action:
            print("Invalid option, please try again.")
            continue

        try:
            action(registry)
        except ValueError as e:
            # e.g. a missing API key (ClaudeClient/TavilySearchProvider
            # raise ValueError) - show it clearly and return to the menu
            # instead of crashing the whole session.
            print(f"\n[run_pipeline] {e}")


if __name__ == "__main__":
    main()
