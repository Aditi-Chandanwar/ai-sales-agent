"""
lead_discovery.py

LeadDiscoveryAgent: the core Sprint 1 agent.

Given business search criteria (region, industry, etc.), it:
    1. Builds a handful of search query variants, biased toward finding
       end-user factories rather than distributors/traders.
    2. Runs each query through a search provider (Tavily).
    3. Cleans + deduplicates the results by website domain.
    4. Saves the final leads to a CSV file.

Business context (Genuine Automation Products LLP):
    Sells industrial sensors (inductive, capacitive, photoelectric,
    magnetic, ultrasonic, fluid level) to END USERS - i.e. factories and
    manufacturers that actually use sensors in their production lines,
    NOT distributors, traders, or resellers of sensors.
"""

import os
import csv
from dataclasses import dataclass, asdict, fields
from urllib.parse import urlparse

from lead_generation.search_provider import TavilySearchProvider


# ----------------------------------------------------------------------
# Data models
# ----------------------------------------------------------------------
# Using dataclasses instead of plain dicts gives us:
#   - Clear, self-documenting fields (no guessing what keys a dict has)
#   - IDE autocomplete + typo protection
#   - A natural place to add validation/behavior later (Sprint 2+)

@dataclass
class LeadDiscoveryRequest:
    """Input parameters for a lead discovery run."""
    region: str
    industry: str
    lead_count: int
    product_category: str
    target_type: str


@dataclass
class Lead:
    """A single discovered lead (one company)."""
    company_name: str
    website: str
    country: str
    source_url: str
    search_query: str
    notes: str


# CSV column order, kept in one place so save_to_csv() and Lead stay in sync
CSV_FIELDNAMES = [f.name for f in fields(Lead)]


class LeadDiscoveryAgent:
    """Finds and saves potential end-user company leads."""

    def __init__(self, search_provider=None):
        # A search_provider can be injected (useful for testing with a fake
        # provider). By default we use the real Tavily-backed provider.
        self.search_provider = search_provider or TavilySearchProvider()

    # ------------------------------------------------------------------
    # Step 1: Build search queries
    # ------------------------------------------------------------------
    def build_queries(self, request: LeadDiscoveryRequest) -> list:
        """
        Build several differently-worded search queries to widen coverage.

        These are biased toward END USERS (factories/plants that actually
        USE sensors) rather than generic "manufacturers" queries, which
        tend to also surface distributors, traders, and suppliers of the
        industry's own products.
        """
        region = request.region
        industry = request.industry

        queries = [
            f"{industry} assembly plants {region}",
            f"{industry} manufacturing plants {region}",
            f"{industry} production facilities {region}",
            f"{industry} component manufacturers {region}",
            f"industrial automation users {industry} {region}",
            f"factories using industrial sensors {industry} {region}",
        ]

        return queries

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_domain(self, url):
        """Extract a normalized domain (e.g. 'example.com') used for dedup."""
        try:
            netloc = urlparse(url).netloc.lower()
            return netloc.replace("www.", "")
        except Exception:
            return url

    def _guess_company_name(self, title, domain):
        """
        Simple heuristic for a company name: prefer the page title,
        fall back to the domain if no title is available.
        """
        if title:
            return title.strip()
        return domain

    def _get_normalized_website(self, domain):
        """
        Build a full, normalized website URL (with scheme) from a bare
        domain, e.g. 'example.com' -> 'https://example.com'.

        This is what we store on the Lead (website field) so it's ready
        to click/use directly. Dedup itself still uses the bare domain
        (see _get_domain) so 'https://example.com' and
        'https://www.example.com/careers' are still treated as the same
        company.
        """
        return f"https://{domain}"

    # ------------------------------------------------------------------
    # Step 2 & 3: Search + dedupe
    # ------------------------------------------------------------------
    def discover(self, request: LeadDiscoveryRequest) -> list:
        """
        Main entry point. Takes a LeadDiscoveryRequest, runs multiple
        searches, merges + dedups the results by domain, and returns a
        list of Lead objects.
        """
        queries = self.build_queries(request)

        seen_domains = set()
        leads = []

        for query in queries:
            print(f"Searching: {query}")
            results = self.search_provider.search(query, max_results=request.lead_count)

            for r in results:
                url = r.get("url", "")
                if not url:
                    continue

                domain = self._get_domain(url)
                if not domain or domain in seen_domains:
                    continue  # skip duplicate company/website

                seen_domains.add(domain)

                lead = Lead(
                    company_name=self._guess_company_name(r.get("title", ""), domain),
                    website=self._get_normalized_website(domain),
                    country=request.region,
                    source_url=url,
                    search_query=query,
                    # Short snippet for a human to sanity-check the lead later
                    notes=(r.get("content", "")[:200] + "...") if r.get("content") else "",
                )
                leads.append(lead)

                if len(leads) >= request.lead_count:
                    break

            if len(leads) >= request.lead_count:
                break

        print(f"Found {len(leads)} unique leads.")
        return leads

    # ------------------------------------------------------------------
    # Step 4: Save to CSV
    # ------------------------------------------------------------------
    def save_to_csv(self, leads: list, output_path="data/leads.csv"):
        """Write a list of Lead objects out to a CSV file, creating folders as needed."""
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()
                for lead in leads:
                    # asdict() turns the Lead dataclass into a plain dict
                    # so csv.DictWriter can consume it.
                    writer.writerow(asdict(lead))
            print(f"Saved {len(leads)} leads to {output_path}")
        except OSError as e:
            print(f"[LeadDiscoveryAgent] Failed to write CSV to {output_path}: {e}")
