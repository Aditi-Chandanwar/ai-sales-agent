"""
core/pipeline.py

Orchestrates the lead pipeline stages (Lead Discovery -> Contact
Extraction -> Lead Qualification -> Email Draft Generation) as
in-memory function calls, while still writing each stage's CSV
checkpoint file - the exact same files you'd get running each
package's own run_xxx.py script by hand:

    data/leads.csv               (Stage 1: Lead Discovery)
    data/leads_with_contacts.csv (Stage 2: Contact Extraction)
    data/qualified_leads.csv     (Stage 3: Lead Qualification)
    data/email_drafts.csv        (Stage 4: Email Draft Generation)

This module does NOT change how any individual agent works - it just
calls them in sequence. Every agent (lead_generation, contact_extraction,
lead_qualification, email_generation) still works completely on its
own, exactly as before. This keeps each stage's CSV as a checkpoint you
can inspect or resume from, per the project's architecture principles.

This module has no knowledge of the Lead Registry (see
lead_registry/) - registry updates and progress-checkmark UI live in
run_pipeline.py, so this file's only responsibility stays "run one
stage, write one CSV".
"""

import csv
import os
from dataclasses import asdict
from datetime import datetime, timezone

from lead_generation.lead_discovery import LeadDiscoveryAgent, LeadDiscoveryRequest
from contact_extraction.run_contact_extraction import ContactExtractionAgent
from lead_qualification.lead_qualifier import LeadQualificationAgent
from email_generation.email_generator import EmailGenerationAgent
from email_generation.run_email_generation import build_output_row, save_email_drafts


# Checkpoint file paths - identical to the ones each individual sprint
# script writes, so nothing changes for anyone still running a single
# stage on its own.
LEADS_CSV = "data/leads.csv"
LEADS_WITH_CONTACTS_CSV = "data/leads_with_contacts.csv"
QUALIFIED_LEADS_CSV = "data/qualified_leads.csv"
EMAIL_DRAFTS_CSV = "data/email_drafts.csv"

# Column groups, reused to build each checkpoint CSV's header
LEAD_FIELDS = ["company_name", "website", "country", "source_url", "search_query", "notes"]
CONTACT_FIELDS = ["contact_pages", "emails", "phones"]
QUALIFICATION_FIELDS = ["score", "qualification_status", "qualification_reason", "risk_flags"]


def _save_csv(rows: list, output_path: str, fieldnames: list):
    """Small shared helper: write a list of dicts to CSV, creating folders as needed."""
    if not rows:
        print(f"[pipeline] No rows to save to {output_path}.")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Saved {len(rows)} rows to {output_path}")


def run_lead_discovery_stage(request: LeadDiscoveryRequest, agent: LeadDiscoveryAgent = None) -> list:
    """
    Stage 1: discover leads and write data/leads.csv.

    `agent` can be injected for testing (e.g. with a fake search
    provider); defaults to a real LeadDiscoveryAgent.
    Returns a list of Lead objects.
    """
    print("\n=== Stage 1: Lead Discovery ===")
    agent = agent or LeadDiscoveryAgent()

    leads = agent.discover(request)
    agent.save_to_csv(leads, LEADS_CSV)
    return leads


def run_contact_extraction_stage(leads: list, agent: ContactExtractionAgent = None) -> list:
    """
    Stage 2: visit each lead's website and extract public contact info,
    writing data/leads_with_contacts.csv.

    `agent` can be injected for testing; defaults to a real
    ContactExtractionAgent.
    Returns a list of enriched lead dicts.
    """
    print("\n=== Stage 2: Contact Extraction ===")
    agent = agent or ContactExtractionAgent()

    enriched_rows = []
    for lead in leads:
        print(f"Extracting contacts for: {lead.company_name} ({lead.website})")
        contacts = agent.extract_contacts_for_website(lead.website)

        row = asdict(lead)
        row["contact_pages"] = "; ".join(contacts["contact_pages"])
        row["emails"] = "; ".join(contacts["emails"])
        row["phones"] = "; ".join(contacts["phones"])
        enriched_rows.append(row)

    _save_csv(enriched_rows, LEADS_WITH_CONTACTS_CSV, LEAD_FIELDS + CONTACT_FIELDS)
    return enriched_rows


def run_lead_qualification_stage(enriched_rows: list, agent: LeadQualificationAgent = None) -> list:
    """
    Stage 3: score and qualify leads (quality gate + rule-based scoring),
    writing data/qualified_leads.csv.

    `agent` can be injected for testing; defaults to a real
    LeadQualificationAgent.
    Returns a list of qualified lead dicts.
    """
    print("\n=== Stage 3: Lead Qualification ===")
    agent = agent or LeadQualificationAgent()

    qualified_rows = agent.qualify_leads(enriched_rows)

    fieldnames = LEAD_FIELDS + CONTACT_FIELDS + QUALIFICATION_FIELDS
    _save_csv(qualified_rows, QUALIFIED_LEADS_CSV, fieldnames)
    return qualified_rows


def run_email_generation_stage(qualified_rows: list, agent: EmailGenerationAgent = None) -> list:
    """
    Stage 4: draft a personalized email for every Qualified lead (Review
    and Rejected rows are skipped), writing data/email_drafts.csv.

    Reuses build_output_row()/save_email_drafts() from
    email_generation/run_email_generation.py directly, rather than
    reimplementing the CSV schema/defaults here - so the two entry
    points (this pipeline, and running that script standalone) can
    never drift out of sync with each other.

    `agent` can be injected for testing; defaults to a real
    EmailGenerationAgent. Never sends anything - drafts only.
    """
    print("\n=== Stage 4: Email Draft Generation ===")
    agent = agent or EmailGenerationAgent()

    qualified_only = [r for r in qualified_rows if r.get("qualification_status") == "Qualified"]
    skipped = len(qualified_rows) - len(qualified_only)
    print(f"{len(qualified_only)} Qualified leads found ({skipped} Review/Rejected skipped).")

    timestamp = datetime.now(timezone.utc).isoformat()
    output_rows = []
    for lead in qualified_only:
        print(f"Drafting email for: {lead.get('company_name', '(unknown)')}")
        draft = agent.generate_email_for_lead(lead)
        output_rows.append(build_output_row(lead, draft, timestamp))

    save_email_drafts(output_rows, EMAIL_DRAFTS_CSV)
    return output_rows
