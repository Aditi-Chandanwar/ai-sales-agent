"""
prompt_builder.py

Builds the exact prompt sent to Claude for drafting one outreach email.

Kept isolated from email_generator.py so the prompt itself can be
reviewed or tuned without touching any API-calling code.

Personalization uses ONLY these fields, per the project's data rules:
    - company_name
    - country
    - industry (best-effort, see _guess_industry below)
    - qualification_reason

The prompt explicitly tells Claude what NOT to do (pricing, quotes,
compatibility promises, invented facts/needs) so every draft stays
safe for a human to review before sending.
"""

from email_generation import email_templates


def _guess_industry(lead: dict) -> str:
    """
    Best-effort industry label for personalization.

    The pipeline doesn't have a dedicated "industry" column yet - the
    closest available signal is the search_query that discovered this
    lead (e.g. "automotive assembly plants Germany"). We pass this to
    Claude labeled as "industry / context" so it's used as a hint, not
    presented as a hard fact.
    """
    return (lead.get("search_query") or "").strip() or "their industry"


def build_email_prompt(lead: dict) -> str:
    """
    Build the full prompt string for one lead. Returns plain text ready
    to send as a single user message to Claude.
    """
    company_name = (lead.get("company_name") or "").strip() or "the company"
    country = (lead.get("country") or "").strip() or "their country"
    industry_hint = _guess_industry(lead)
    qualification_reason = (lead.get("qualification_reason") or "").strip() or "Not specified"

    prompt = f"""You are drafting a short, professional, first-contact outreach email on behalf of {email_templates.COMPANY_NAME}.

COMPANY BACKGROUND (use only this - do not invent any other facts):
{email_templates.COMPANY_BLURB}

LEAD INFORMATION (personalize using ONLY these facts):
- Company name: {company_name}
- Country: {country}
- Industry / context: {industry_hint}
- Why this lead was qualified: {qualification_reason}

WRITE AN EMAIL THAT INCLUDES:
1. A subject line
2. A professional greeting
3. A short introduction
4. A very brief introduction of {email_templates.COMPANY_NAME}
5. A mention of industrial automation expertise
6. A mention of sensors / automation products
7. An invitation to a brief discussion
8. A professional closing

STRICT RULES - DO NOT:
- Mention pricing or cost
- Mention quotations or quotes
- Promise or imply technical compatibility with their specific equipment
- Invent any facts about {company_name} beyond what is given above
- Invent any customer needs or problems they haven't stated

FORMAT YOUR RESPONSE EXACTLY LIKE THIS (no extra commentary before or after):
Subject: <subject line>

<email body>"""

    return prompt
