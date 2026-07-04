"""
contact_page_finder.py

ContactPageFinder: given a homepage's HTML, finds links that are likely
to be "contact us" / "about" / "imprint" style pages, where a company
usually publishes public email addresses and phone numbers.

We deliberately keep this simple: look at every <a> tag, check if its
link text or URL contains a keyword we care about, and normalize the
URL so it's a full absolute link we can fetch later.
"""

from urllib.parse import urljoin
from bs4 import BeautifulSoup


class ContactPageFinder:
    """Finds candidate contact-page URLs from a homepage's HTML."""

    # Keywords that suggest a page might have contact details.
    # Checked against both the link text and the URL itself (lowercased).
    CONTACT_KEYWORDS = [
        "contact",
        "contact-us",
        "about",
        "company",
        "imprint",
        "locations",
    ]

    def __init__(self, max_pages: int = 3):
        # Cap how many candidate contact pages we return per website, so
        # we don't end up scraping an entire site for one lead.
        self.max_pages = max_pages

    def find_contact_pages(self, base_url: str, homepage_html: str) -> list:
        """
        Look through the homepage HTML for links that look like contact
        pages, and return a deduplicated, capped list of absolute URLs.
        """
        if not homepage_html:
            return []

        soup = BeautifulSoup(homepage_html, "html.parser")

        candidate_urls = []
        seen = set()

        for link in soup.find_all("a", href=True):
            href = link["href"]
            link_text = link.get_text(strip=True).lower()

            # Check keyword match in either the visible link text or the URL itself
            haystack = f"{link_text} {href.lower()}"
            if not any(keyword in haystack for keyword in self.CONTACT_KEYWORDS):
                continue

            # Turn relative links (e.g. "/contact") into full absolute URLs
            absolute_url = urljoin(base_url, href)

            if absolute_url in seen:
                continue
            seen.add(absolute_url)

            candidate_urls.append(absolute_url)

            # Stop early once we have enough candidates
            if len(candidate_urls) >= self.max_pages:
                break

        return candidate_urls
