"""
quality_gate.py

A strict "quality gate" that runs BEFORE normal rule-based scoring.

Sprint 3's keyword scoring was letting junk results through - Wikipedia
pages, YouTube videos, stock photo sites, PDF reports, directories,
lead-list/portal sites - simply because they happened to contain words
like "automotive", "manufacturing", or "OEM" somewhere in the text.

This module hard-rejects those obvious non-leads immediately, before a
single scoring point is calculated. Only leads that pass the gate move
on to scoring_rules.py.
"""

from urllib.parse import urlparse


# ----------------------------------------------------------------------
# Blocklists
# ----------------------------------------------------------------------

# Domains that are never real end-user company websites: encyclopedias,
# video sites, stock photo/media libraries, lead-data/contact-finder
# tools, industry portals, and social media platforms.
BLOCKED_DOMAINS = [
    "wikipedia.org",
    "youtube.com",
    "istockphoto.com",
    "shutterstock.com",
    "unsplash.com",
    "lusha.com",
    "zoominfo.com",
    "ensun.io",
    "marklines.com",
    "acea.auto",
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com",
]

# Words/phrases that, if found in the company name or notes, strongly
# suggest this is a directory/listing/media page rather than an actual
# company. Checked case-insensitively.
CONTENT_SITE_KEYWORDS = [
    "wikipedia",
    "youtube",
    "stock photo",
    "stock photos",
    "top 100",
    "directory",
    "listing",
    "portal",
    "company search",
    "sales leads",
    "industry report",
    "interactive map",
    "category:",
]


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def get_domain(url: str) -> str:
    """
    Extract a normalized domain (lowercase, no 'www.') from a URL.
    Returns "" if the URL is missing or can't be parsed.
    """
    if not url:
        return ""
    try:
        netloc = urlparse(url).netloc.lower()
        return netloc.replace("www.", "")
    except Exception:
        return ""


def is_blocked_domain(lead: dict) -> str:
    """
    Check the lead's website AND source_url against BLOCKED_DOMAINS.

    Returns a human-readable reason string if blocked, or "" if not.
    """
    website_domain = get_domain(lead.get("website", ""))
    source_domain = get_domain(lead.get("source_url", ""))

    for blocked in BLOCKED_DOMAINS:
        if blocked in website_domain or blocked in source_domain:
            return f"Domain matches blocked list ({blocked})"

    return ""


def is_pdf_result(lead: dict) -> str:
    """
    Check if source_url points directly at a PDF file (a report/document,
    not a company website).

    Returns a human-readable reason string if it's a PDF, or "" if not.
    """
    source_url = (lead.get("source_url", "") or "").lower()
    if source_url.endswith(".pdf"):
        return "Source URL is a PDF document, not a company website"
    return ""


def is_directory_or_content_site(lead: dict) -> str:
    """
    Check company_name and notes for words that suggest this is a
    directory/listing/media/report page rather than a real company.

    Returns a human-readable reason string if matched, or "" if not.
    """
    text = f"{lead.get('company_name', '') or ''} {lead.get('notes', '') or ''}".lower()

    for keyword in CONTENT_SITE_KEYWORDS:
        if keyword in text:
            return f"Company name/notes suggest a directory/listing/content page ('{keyword}')"

    return ""


def apply_quality_gate(lead: dict) -> str:
    """
    Run all hard-rejection checks on a lead, in order.

    Returns the first rejection reason found, or "" if the lead passes
    the quality gate and should proceed to normal scoring.
    """
    checks = [
        is_blocked_domain,
        is_pdf_result,
        is_directory_or_content_site,
    ]

    for check in checks:
        reason = check(lead)
        if reason:
            return reason

    return ""  # passed the quality gate
