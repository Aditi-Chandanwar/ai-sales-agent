"""
email_templates.py

Static, reusable text building blocks for outreach emails.

Two purposes:
1. `COMPANY_NAME` / `COMPANY_BLURB` are the ONLY facts about Genuine
   Automation Products LLP that get fed into the Claude prompt (see
   prompt_builder.py). Keeping them here, in one place, means the LLM
   is never asked to "remember" or invent company facts - it's always
   given the same short, accurate description.
2. `FALLBACK_SUBJECT_TEMPLATE` / `FALLBACK_BODY_TEMPLATE` are a safe,
   static email used ONLY if the Claude API call fails or is
   unavailable, so a lead still gets a reviewable draft instead of
   nothing at all.
"""

COMPANY_NAME = "Genuine Automation Products LLP"

COMPANY_BLURB = (
    "Genuine Automation Products LLP is an industrial automation company "
    "specializing in industrial sensors (inductive, capacitive, "
    "photoelectric, magnetic, ultrasonic, and fluid level sensors) and "
    "related automation components."
)

CLOSING_SIGNATURE = "Best regards,\nSales Team\nGenuine Automation Products LLP"

# Used only if the Claude API call fails or returns nothing.
FALLBACK_SUBJECT_TEMPLATE = "Introduction from Genuine Automation Products LLP"

FALLBACK_BODY_TEMPLATE = (
    "Dear {company_name} Team,\n\n"
    "My name is [Your Name] from Genuine Automation Products LLP.\n\n"
    + COMPANY_BLURB + "\n\n"
    "I'd welcome the opportunity for a brief discussion to learn more "
    "about your operations and see if there's a good fit to explore "
    "further.\n\n"
    + CLOSING_SIGNATURE
)
