"""
scoring_rules.py

Reusable, rule-based scoring logic for qualifying leads.

No AI/LLM here - just simple keyword checks and point additions/subtractions,
based on business rules for Genuine Automation Products LLP (industrial
sensors sold to industrial END USERS, not distributors/traders/resellers).

Each "rule" function takes a lead dict and returns a (points, reason) tuple.
If the rule doesn't apply, it returns (0, None). Keeping each rule as a
small standalone function makes it easy to add, remove, or tweak one rule
without touching the others.
"""

# ----------------------------------------------------------------------
# Keyword lists (matched case-insensitively against combined lead text)
# ----------------------------------------------------------------------

MANUFACTURING_KEYWORDS = [
    "manufactur",       # matches "manufacturing" and "manufacturer"
    "factory",
    "plant",
    "production",
    "assembly",
    "oem",
    "automotive parts",
    "machine builder",
]

AUTOMOTIVE_KEYWORDS = ["automotive"]

DISTRIBUTOR_KEYWORDS = [
    "distributor",
    "reseller",
    "trader",
    "supplier",
    "dealer",
    "catalog",
    "online store",
]

DIRECTORY_KEYWORDS = [
    "directory",
    "listing",
    "job board",
    "jobs board",
    "news",
]

# Score bounds and qualification thresholds
MIN_SCORE = 0
MAX_SCORE = 100

QUALIFIED_THRESHOLD = 60
REVIEW_THRESHOLD = 40


# ----------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------
def _contains_any(text: str, keywords: list) -> bool:
    """Case-insensitive check: does `text` contain any of the keywords?"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def _combined_text(lead: dict) -> str:
    """
    Combine the free-text fields we care about (company name, notes,
    search query) into one lowercase-friendly string for keyword
    matching. Missing fields are treated as empty strings so this never
    crashes on incomplete rows.
    """
    parts = [
        lead.get("company_name", "") or "",
        lead.get("notes", "") or "",
        lead.get("search_query", "") or "",
    ]
    return " ".join(parts)


# ----------------------------------------------------------------------
# Positive scoring rules
# ----------------------------------------------------------------------
def score_manufacturing_signal(lead: dict):
    """+30 if notes/company/search query suggest a real manufacturing operation."""
    text = _combined_text(lead)
    if _contains_any(text, MANUFACTURING_KEYWORDS):
        return 30, "Mentions manufacturing/plant/production/assembly/OEM"
    return 0, None


def score_automotive_signal(lead: dict):
    """+20 if industry/search query suggests automotive."""
    text = _combined_text(lead)
    if _contains_any(text, AUTOMOTIVE_KEYWORDS):
        return 20, "Automotive-related industry/search query"
    return 0, None


def score_website_exists(lead: dict):
    """+15 if a website URL is present."""
    if (lead.get("website", "") or "").strip():
        return 15, "Website present"
    return 0, None


def score_emails_exist(lead: dict):
    """+15 if at least one email was found."""
    if (lead.get("emails", "") or "").strip():
        return 15, "Email(s) found"
    return 0, None


def score_phones_exist(lead: dict):
    """+10 if at least one phone number was found."""
    if (lead.get("phones", "") or "").strip():
        return 10, "Phone number(s) found"
    return 0, None


def score_contact_pages_exist(lead: dict):
    """+10 if at least one contact page was identified."""
    if (lead.get("contact_pages", "") or "").strip():
        return 10, "Contact page(s) identified"
    return 0, None


# ----------------------------------------------------------------------
# Negative scoring rules (risk flags)
# ----------------------------------------------------------------------
def score_distributor_risk(lead: dict):
    """-40 if notes/company/website suggest a distributor/reseller/trader/supplier."""
    text = _combined_text(lead) + " " + (lead.get("website", "") or "")
    if _contains_any(text, DISTRIBUTOR_KEYWORDS):
        return -40, "Looks like a distributor/reseller/trader/supplier"
    return 0, None


def score_directory_risk(lead: dict):
    """
    -20 if the website/source/notes look like a directory/listing/news/job
    board rather than an actual company website.
    """
    text = (
        _combined_text(lead)
        + " " + (lead.get("website", "") or "")
        + " " + (lead.get("source_url", "") or "")
    )
    if _contains_any(text, DIRECTORY_KEYWORDS):
        return -20, "Source looks like a directory/listing/news/job board, not a company site"
    return 0, None


def score_no_contact_penalty(lead: dict):
    """-20 if there is no email AND no phone number at all."""
    has_email = bool((lead.get("emails", "") or "").strip())
    has_phone = bool((lead.get("phones", "") or "").strip())
    if not has_email and not has_phone:
        return -20, "No email or phone number found"
    return 0, None


# All scoring rules in one place, so lead_qualifier.py can just loop over
# this list without needing to know each rule's name individually.
SCORING_RULES = [
    score_manufacturing_signal,
    score_automotive_signal,
    score_website_exists,
    score_emails_exist,
    score_phones_exist,
    score_contact_pages_exist,
    score_distributor_risk,
    score_directory_risk,
    score_no_contact_penalty,
]


# ----------------------------------------------------------------------
# Score -> status helpers
# ----------------------------------------------------------------------
def clamp_score(score: int) -> int:
    """Keep the score within [MIN_SCORE, MAX_SCORE]."""
    return max(MIN_SCORE, min(MAX_SCORE, score))


def qualification_status(score: int) -> str:
    """Map a final (clamped) score to a qualification status label."""
    if score >= QUALIFIED_THRESHOLD:
        return "Qualified"
    if score >= REVIEW_THRESHOLD:
        return "Review"
    return "Rejected"
