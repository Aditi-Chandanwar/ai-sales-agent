"""
email_generator.py

EmailGenerationAgent: for one qualified lead, builds a prompt (via
prompt_builder.py) and calls Claude (via ClaudeClient below) to draft a
personalized outreach email.

IMPORTANT: This module ONLY drafts emails. It never sends anything -
there is no SMTP, Gmail, or Outlook code anywhere in this file or
package. Every draft this agent produces is meant for human review.
"""

import os
import requests

from email_generation import prompt_builder
from email_generation import email_templates


class ClaudeClient:
    """
    Thin wrapper around the Claude Messages API, used only to generate
    the text of an email draft. Mirrors the same pattern as
    TavilySearchProvider in lead_generation/search_provider.py: read the
    key from the environment, never hardcode it, fail loudly if it's
    missing, and never raise on a bad request (return "" instead).
    """

    BASE_URL = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_VERSION = "2023-06-01"

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        # Model is configurable via .env (CLAUDE_MODEL) in case it needs
        # to change later without editing code.
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. Please add it to your .env file "
                "(see .env.example)."
            )

    def generate_text(self, prompt: str, max_tokens: int = 600) -> str:
        """
        Send a prompt to Claude and return the plain text response.

        Returns "" on any failure (network error, bad status, unparseable
        response) so a single failed call never crashes a whole batch of
        leads - the caller falls back to a static template instead.
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            response = requests.post(self.BASE_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"[ClaudeClient] Request failed: {e}")
            return ""
        except ValueError as e:
            print(f"[ClaudeClient] Could not parse response: {e}")
            return ""

        # The Messages API returns a list of content blocks; join the text ones.
        content_blocks = data.get("content", [])
        text_parts = [block.get("text", "") for block in content_blocks if block.get("type") == "text"]
        return "\n".join(text_parts).strip()


class EmailGenerationAgent:
    """
    Drafts one personalized email per qualified lead.

    Only calls prompt_builder (to build the prompt) and ClaudeClient
    (to get text back) - no scoring, filtering, or CSV logic lives here,
    keeping this class's responsibility to "turn one lead into one
    draft".
    """

    def __init__(self, claude_client: ClaudeClient = None):
        # Allow dependency injection for testing with a fake client
        self.claude_client = claude_client or ClaudeClient()

    def generate_email_for_lead(self, lead: dict) -> dict:
        """
        Draft a subject + body for one lead.

        Returns {"subject": ..., "email_draft": ...}. Falls back to a
        safe static template (email_templates.py) if Claude is
        unavailable or returns something we can't parse, so the lead
        still gets a reviewable draft either way.
        """
        prompt = prompt_builder.build_email_prompt(lead)
        raw_response = self.claude_client.generate_text(prompt)

        subject, body = self._parse_response(raw_response)

        if not subject or not body:
            subject, body = self._fallback_draft(lead)

        return {"subject": subject, "email_draft": body}

    def _parse_response(self, raw_response: str):
        """
        Split Claude's expected "Subject: ...\\n\\n<body>" response into
        (subject, body). Returns ("", "") if it can't find a subject
        line, signaling the caller to use the fallback template.
        """
        if not raw_response:
            return "", ""

        lines = raw_response.splitlines()
        subject = ""
        body_start = 0

        for i, line in enumerate(lines):
            if line.strip().lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                body_start = i + 1
                break

        body = "\n".join(lines[body_start:]).strip()
        return subject, body

    def _fallback_draft(self, lead: dict):
        """A safe, static draft used only if Claude couldn't be reached or parsed."""
        company_name = (lead.get("company_name") or "").strip() or "your company"

        subject = email_templates.FALLBACK_SUBJECT_TEMPLATE
        body = email_templates.FALLBACK_BODY_TEMPLATE.format(company_name=company_name)
        return subject, body
