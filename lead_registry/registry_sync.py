"""
lead_registry/registry_sync.py

Syncs each pipeline stage's CSV checkpoint into the Lead Registry.

Kept separate from LeadRegistry itself: LeadRegistry only knows how to
get_or_create/update_stage one lead at a time. This module is the only
place that knows the specific column names each stage's CSV produces
(company_name/website/... for leads.csv, score/qualification_status/...
for qualified_leads.csv, etc) - so if a stage's CSV columns ever
change, only this file needs to change, not LeadRegistry.

Sync functions are read-only with respect to the stage CSVs - they
never modify leads.csv, leads_with_contacts.csv, qualified_leads.csv,
or email_drafts.csv. They only read from them to update the registry.
"""

import csv
import os
import sys

csv.field_size_limit(10_000_000)

from lead_registry.lead_registry import LeadRegistry


def _read_rows(csv_path: str) -> list:
    """Read a stage's CSV checkpoint into a list of dicts, or [] if it doesn't exist yet."""
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sync_lead_discovery(registry: LeadRegistry, csv_path: str = "data/leads.csv"):
    """
    Register every discovered lead in the registry (creates new records
    with a fresh Lead ID; existing companies - matched by domain - are
    left as-is here, since Lead Discovery doesn't change their status).
    """
    for row in _read_rows(csv_path):
        registry.get_or_create(
            company_name=row.get("company_name", ""),
            website=row.get("website", ""),
            country=row.get("country", ""),
        )


def sync_contact_extraction(registry: LeadRegistry, csv_path: str = "data/leads_with_contacts.csv"):
    """Update stage = Contact Extraction, and note whether public contact info was found."""
    for row in _read_rows(csv_path):
        has_email = bool((row.get("emails") or "").strip())
        has_phone = bool((row.get("phones") or "").strip())
        note = "Contact info found" if (has_email or has_phone) else "No public contact info found"

        registry.update_stage(
            website=row.get("website", ""),
            stage="Contact Extraction",
            notes=note,
        )


def sync_lead_qualification(registry: LeadRegistry, csv_path: str = "data/qualified_leads.csv"):
    """Update stage = Lead Qualification: lead_score, qualification_status, current_status."""
    for row in _read_rows(csv_path):
        registry.update_stage(
            website=row.get("website", ""),
            stage="Lead Qualification",
            current_status=row.get("qualification_status", ""),
            lead_score=row.get("score", ""),
            qualification_status=row.get("qualification_status", ""),
            notes=row.get("qualification_reason", ""),
        )


def sync_email_generation(registry: LeadRegistry, csv_path: str = "data/email_drafts.csv"):
    """Update stage = Email Draft Generation: current_status, email_status, follow_up_status."""
    for row in _read_rows(csv_path):
        registry.update_stage(
            website=row.get("website", ""),
            stage="Email Draft Generation",
            current_status=row.get("approval_status", ""),
            email_status=row.get("email_status", ""),
            follow_up_status=row.get("follow_up_status", ""),
        )
