"""
search_provider.py

Thin wrapper around the Tavily Search API.

The rest of the app (lead_discovery.py) should not need to know anything
about HTTP requests, request payloads, or Tavily-specific error handling.
It just calls `.search(query)` and gets back a clean list of results.
"""

import os
import requests


class TavilySearchProvider:
    """Handles all communication with the Tavily Search API."""

    # Tavily's search endpoint
    BASE_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str = None):
        """
        api_key can be passed directly (handy for tests), but in normal
        usage it is read from the TAVILY_API_KEY environment variable,
        which is loaded from a .env file via python-dotenv.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

        if not self.api_key:
            raise ValueError(
                "TAVILY_API_KEY not found. Please add it to your .env file "
                "(see .env.example)."
            )

    def search(self, query: str, max_results: int = 10) -> list:
        """
        Run a single search query against Tavily.

        Returns:
            A list of dicts like: [{"title": ..., "url": ..., "content": ...}, ...]
            Returns an empty list if the request fails, so a single bad
            query never crashes the whole agent.
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
        }

        try:
            response = requests.post(self.BASE_URL, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            # Network errors, timeouts, bad status codes, etc.
            print(f"[TavilySearchProvider] Search failed for query '{query}': {e}")
            return []
        except ValueError as e:
            # response.json() failed to parse
            print(f"[TavilySearchProvider] Could not parse response for '{query}': {e}")
            return []

        raw_results = data.get("results", [])

        # Normalize each result into a simple, predictable shape so the
        # rest of the app doesn't need to know about Tavily's response format.
        cleaned_results = []
        for r in raw_results:
            cleaned_results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            })

        return cleaned_results
