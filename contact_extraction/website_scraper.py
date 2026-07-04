"""
website_scraper.py

WebsiteScraper: fetches raw HTML from a URL.

This is the lowest-level building block of the Contact Extraction Agent.
It knows nothing about contact pages, emails, or leads - it just fetches
HTML and hands it back, or returns an empty string if anything goes wrong.
Keeping this simple and isolated makes it easy to test and reuse.
"""

import requests


class WebsiteScraper:
    """Fetches HTML content from a URL, with sensible defaults for scraping."""

    # A realistic browser User-Agent. Some sites block requests that use
    # the default python-requests User-Agent, so we pretend to be a normal
    # browser. We are only ever fetching public pages, same as a visitor
    # would in their browser.
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def __init__(self, timeout: int = 10):
        # timeout in seconds - avoids hanging forever on a slow/dead site
        self.timeout = timeout

    def fetch_html(self, url: str) -> str:
        """
        Fetch a page's HTML.

        Returns:
            The page's HTML as a string, or "" if the request fails for
            any reason (timeout, connection error, bad status code, etc).
            Callers should treat "" as "nothing found here" rather than
            crashing the whole pipeline over one bad website.
        """
        if not url:
            return ""

        try:
            response = requests.get(
                url,
                headers=self.DEFAULT_HEADERS,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            # Covers timeouts, connection errors, DNS failures, 4xx/5xx, etc.
            print(f"[WebsiteScraper] Could not fetch '{url}': {e}")
            return ""
