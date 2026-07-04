"""
email_extractor.py

EmailExtractor: pulls email addresses and phone numbers out of raw HTML
text using regular expressions.

We only extract what is publicly visible on the page - no guessing of
private/unlisted addresses, and no attempt to construct emails from
patterns like "first.last@domain.com". If it's not written on the page,
we don't report it.
"""

import re


class EmailExtractor:
    """Extracts public emails and phone numbers from page text using regex."""

    # Standard email pattern: local-part@domain.tld
    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    )

    # A fairly permissive phone number pattern - matches sequences of
    # digits, spaces, dashes, dots, and parentheses, with an optional
    # leading "+". This is deliberately loose because phone formats vary
    # a lot by country (e.g. German, US, Indian formats all look different).
    PHONE_PATTERN = re.compile(
        r"\+?\(?\d[\d\s().\-]{7,}\d"
    )

    # Emails commonly found in demo/template content or that we shouldn't
    # report as real contacts. Add more as you notice them during testing.
    FAKE_EMAIL_BLOCKLIST = {
        "example@example.com",
        "test@example.com",
        "your-email@example.com",
        "name@example.com",
        "email@example.com",
        "info@example.com",
    }

    def extract_emails(self, html_text: str) -> list:
        """Find all email addresses in the given text, deduplicated and filtered."""
        if not html_text:
            return []

        found = self.EMAIL_PATTERN.findall(html_text)

        cleaned = []
        seen = set()
        for email in found:
            email_lower = email.lower()

            # Skip obvious placeholder/fake emails
            if email_lower in self.FAKE_EMAIL_BLOCKLIST:
                continue

            # Skip duplicates (case-insensitive)
            if email_lower in seen:
                continue
            seen.add(email_lower)

            cleaned.append(email)

        return cleaned

    def extract_phones(self, html_text: str) -> list:
        """Find all phone-number-like strings in the given text, deduplicated."""
        if not html_text:
            return []

        found = self.PHONE_PATTERN.findall(html_text)

        cleaned = []
        seen = set()
        for phone in found:
            # Normalize whitespace for dedup comparison, but keep original formatting
            normalized = " ".join(phone.split())

            # Skip anything that's mostly not digits (rare, but guards against
            # matching things like long dates or IDs that slipped through)
            digit_count = sum(c.isdigit() for c in normalized)
            if digit_count < 7:
                continue

            dedup_key = re.sub(r"\D", "", normalized)  # digits only, for comparison
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            cleaned.append(normalized)

        return cleaned
