"""
lead_registry/lead_registry.py

LeadRegistry: the persistent master database of every lead the system
has ever discovered, keyed by company website domain so the same
company is recognized across multiple pipeline runs instead of
duplicated.

Storage is pluggable (see storage.py) - LeadRegistry only calls
storage.load_all() / storage.save_all(), so replacing CSV with SQLite
later means writing one new storage class, not touching this file.
"""

from datetime import datetime, timezone
from urllib.parse import urlparse

from lead_registry.models import LeadRecord, REGISTRY_FIELDNAMES
from lead_registry.storage import RegistryStorage, CsvRegistryStorage


def _normalize_domain(url: str) -> str:
    """
    Normalize a website URL/domain for matching (lowercase, no 'www.').
    Same normalization approach used elsewhere in the project (e.g.
    lead_generation/lead_discovery.py, lead_qualification/quality_gate.py).
    """
    if not url:
        return ""
    try:
        netloc = urlparse(url).netloc.lower()
        if not netloc:
            # url may already be a bare domain (e.g. "example.com")
            # rather than a full URL with a scheme.
            netloc = url.lower().strip().strip("/")
        return netloc.replace("www.", "")
    except Exception:
        return url.lower()


def _now() -> str:
    """Current UTC timestamp, ISO format - used for discovery_date/last_updated."""
    return datetime.now(timezone.utc).isoformat()


class LeadRegistry:
    """The master lead database. One record per unique company domain."""

    def __init__(self, storage: RegistryStorage = None):
        # Storage can be injected (e.g. a fake for testing, or a future
        # SqliteRegistryStorage); defaults to the real CSV-backed storage.
        self.storage = storage or CsvRegistryStorage()
        self._records = self._load_records()

    # ------------------------------------------------------------------
    # Loading / persisting
    # ------------------------------------------------------------------
    def _load_records(self) -> dict:
        """Load all rows from storage into memory, keyed by domain."""
        rows = self.storage.load_all()
        records = {}
        for row in rows:
            domain = _normalize_domain(row.get("website", ""))
            if not domain:
                continue
            records[domain] = row
        return records

    def _persist(self):
        """Save every in-memory record back to storage."""
        self.storage.save_all(list(self._records.values()))

    def _generate_next_id(self) -> str:
        """
        Generate the next Lead ID (e.g. L000001), based on the highest
        numeric ID already present in the registry. Simple and correct
        for a single-writer CSV-backed registry; a SQLite storage layer
        could later use an auto-increment column instead.
        """
        max_num = 0
        for row in self._records.values():
            lead_id = row.get("lead_id", "") or ""
            digits = lead_id.lstrip("L")
            if digits.isdigit():
                max_num = max(max_num, int(digits))
        return f"L{max_num + 1:06d}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_or_create(self, company_name: str, website: str, country: str = "") -> dict:
        """
        Find the existing record for this company (matched by website
        domain) or create a new one with a fresh Lead ID.

        Always returns a plain dict (the registry's row format), so
        callers don't need to know about LeadRecord internals.
        """
        domain = _normalize_domain(website)

        if domain and domain in self._records:
            return self._records[domain]

        record = LeadRecord(
            lead_id=self._generate_next_id(),
            company_name=company_name,
            website=website,
            country=country,
            discovery_date=_now(),
            last_updated=_now(),
            current_stage="Lead Discovery",
            current_status="New",
        )
        row = {field_name: getattr(record, field_name) for field_name in REGISTRY_FIELDNAMES}

        if domain:
            self._records[domain] = row
            self._persist()

        return row

    def update_stage(self, website: str, stage: str, **fields_to_update):
        """
        Update the record matching this website's domain: sets
        current_stage and last_updated, plus any other registry fields
        passed as keyword arguments (e.g. lead_score="85",
        qualification_status="Qualified", notes="...").

        Does nothing if no record exists yet for this domain - a
        record should already exist from Lead Discovery via
        get_or_create() before any later stage tries to update it.
        """
        domain = _normalize_domain(website)
        if not domain or domain not in self._records:
            return

        row = self._records[domain]
        row["current_stage"] = stage
        row["last_updated"] = _now()

        for key, value in fields_to_update.items():
            if value is not None and key in REGISTRY_FIELDNAMES:
                row[key] = value

        self._persist()

    def get_all(self) -> list:
        """Return every registry row as a list of plain dicts."""
        return list(self._records.values())

    def get_summary(self) -> dict:
        """
        Simple counts for a CLI summary (and, later, a dashboard):
        total leads tracked, plus breakdowns by current_stage,
        qualification_status, and email_status.
        """
        rows = self.get_all()

        def _count_by(key):
            counts = {}
            for row in rows:
                value = row.get(key, "") or "(none)"
                counts[value] = counts.get(value, 0) + 1
            return counts

        return {
            "total": len(rows),
            "by_stage": _count_by("current_stage"),
            "by_qualification_status": _count_by("qualification_status"),
            "by_email_status": _count_by("email_status"),
        }
