"""
run_email_generation.py

Runnable demo for Sprint 4: Email Draft Generation Agent.

Reads data/qualified_leads.csv, processes ONLY rows where
qualification_status == "Qualified" (Review and Rejected leads are
skipped), drafts a personalized email per lead using Claude, and
writes data/email_drafts.csv - ready for a human to review and
approve.

IMPORTANT: This script NEVER sends emails. There is no SMTP, Gmail, or
Outlook code anywhere in this package. Every row starts with
approval_status = "Pending Review" and email_status = "Not Sent".

Run it with:
    python -m email_generation.run_email_generation

Requires a .env file with ANTHROPIC_API_KEY set (see .env.example).

If data/qualified_leads.csv doesn't exist yet, this falls back to a
small built-in sample - including one non-Qualified lead, to
demonstrate that Review/Rejected rows are correctly skipped.
"""

import csv
import os
from datetime import datetime, timezone

from email_generation.email_generator import EmailGenerationAgent


INPUT_CSV = "data/qualified_leads.csv"
OUTPUT_CSV = "data/email_drafts.csv"

# Final column order for the dashboard-ready output CSV. This schema is
# designed so a future dashboard can track drafts pending review,
# approved emails, sent emails, follow-ups, and conversions.
OUTPUT_FIELDNAMES = [
    "company_name",
    "website",
    "email",
    "country",
    "lead_score",
    "qualification_reason",
    "subject",
    "email_draft",
    "approval_status",
    "email_status",
    "draft_created_at",
    "approved_by",
    "sent_at",
    "follow_up_status",
    "notes",
]


def read_qualified_leads(input_path: str) -> list:
    """
    Read qualified_leads.csv and return ONLY rows where
    qualification_status == "Qualified". Filtering happens here so
    nothing downstream has to remember to check the status again.
    """
    if not os.path.exists(input_path):
        print(f"[run_email_generation] Could not find {input_path}.")
        print("Using a small built-in sample instead, so you can see how this works.")
        print("Run Sprints 1-3 first to draft emails for your real qualified leads.\n")
        rows = _sample_leads()
    else:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    qualified_rows = [r for r in rows if r.get("qualification_status") == "Qualified"]

    skipped = len(rows) - len(qualified_rows)
    print(f"Loaded {len(rows)} leads total - {len(qualified_rows)} Qualified, "
          f"{skipped} skipped (Review/Rejected).")

    return qualified_rows


def _sample_leads() -> list:
    """
    A tiny built-in sample: one Qualified lead (should get a draft) and
    one Rejected lead (should be skipped entirely).
    """
    return [
        {
            "company_name": "Mercedes-Benz Group AG",
            "website": "https://www.mercedes-benz.com",
            "country": "Germany",
            "search_query": "automotive assembly plants Germany",
            "emails": "media@mercedes-benz.com",
            "score": "100",
            "qualification_status": "Qualified",
            "qualification_reason": (
                "Positive: Mentions manufacturing/plant/production/assembly/OEM; "
                "Automotive-related industry/search query; Website present; "
                "Email(s) found; Phone number(s) found; Contact page(s) identified"
            ),
        },
        {
            "company_name": "AutoParts Distributor GmbH",
            "website": "https://autoparts-distributor.example.com",
            "country": "Germany",
            "search_query": "automotive component manufacturers Germany",
            "emails": "",
            "score": "5",
            "qualification_status": "Rejected",
            "qualification_reason": (
                "Risks: Looks like a distributor/reseller/trader/supplier; "
                "No email or phone number found"
            ),
        },
    ]


def _first_email(emails_field: str) -> str:
    """qualified_leads.csv stores multiple emails as '; '-joined; use the first one."""
    if not emails_field:
        return ""
    return emails_field.split(";")[0].strip()


def build_output_row(lead: dict, draft: dict, timestamp: str) -> dict:
    """
    Combine the lead's data + the generated draft into one dashboard-
    ready row, with default tracking fields for the future dashboard.
    """
    return {
        "company_name": lead.get("company_name", ""),
        "website": lead.get("website", ""),
        "email": _first_email(lead.get("emails", "")),
        "country": lead.get("country", ""),
        "lead_score": lead.get("score", ""),
        "qualification_reason": lead.get("qualification_reason", ""),
        "subject": draft["subject"],
        "email_draft": draft["email_draft"],
        "approval_status": "Pending Review",
        "email_status": "Not Sent",
        "draft_created_at": timestamp,
        "approved_by": "",
        "sent_at": "",
        "follow_up_status": "Not Started",
        "notes": "",
    }


def save_email_drafts(rows: list, output_path: str):
    """Write the email draft rows out to data/email_drafts.csv."""
    if not rows:
        print("[run_email_generation] No rows to save.")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Saved {len(rows)} email drafts to {output_path}")
    except OSError as e:
        print(f"[run_email_generation] Failed to write CSV to {output_path}: {e}")


def main():
    qualified_leads = read_qualified_leads(INPUT_CSV)

    if not qualified_leads:
        print("[run_email_generation] No Qualified leads to draft emails for.")
        return

    agent = EmailGenerationAgent()
    timestamp = datetime.now(timezone.utc).isoformat()

    output_rows = []
    for lead in qualified_leads:
        print(f"Drafting email for: {lead.get('company_name', '(unknown)')}")
        draft = agent.generate_email_for_lead(lead)
        output_rows.append(build_output_row(lead, draft, timestamp))

    save_email_drafts(output_rows, OUTPUT_CSV)

    print("\nAll drafts saved with approval_status = 'Pending Review' and "
          "email_status = 'Not Sent'.")
    print("Nothing has been sent. Review data/email_drafts.csv before taking any action.")


if __name__ == "__main__":
    main()
