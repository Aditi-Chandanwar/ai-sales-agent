"""
lead_registry/models.py

LeadRecord: one row in the master Lead Registry - the persistent record
of a single company across every pipeline run, keyed by its website
domain (see lead_registry.py).
"""

from dataclasses import dataclass, fields


@dataclass
class LeadRecord:
    lead_id: str
    company_name: str
    website: str
    country: str = ""
    discovery_date: str = ""
    last_updated: str = ""
    current_stage: str = ""
    current_status: str = ""
    lead_score: str = ""
    qualification_status: str = ""
    email_status: str = ""
    follow_up_status: str = ""
    notes: str = ""


# Column order for the registry CSV, derived directly from the
# dataclass fields so storage.py and models.py can never drift apart.
REGISTRY_FIELDNAMES = [f.name for f in fields(LeadRecord)]
