"""
lead_registry/storage.py

Storage layer for the Lead Registry.

RegistryStorage defines the interface: load_all() / save_all(). Only
one implementation exists today (CsvRegistryStorage), but the interface
is what makes swapping in a SQLite-backed storage later a small,
isolated change - LeadRegistry (in lead_registry.py) only ever talks to
this interface, never to CSV or SQL directly.

To migrate to SQLite later: write a SqliteRegistryStorage class below
that implements load_all()/save_all() against a database table with
the same columns as REGISTRY_FIELDNAMES, then construct
LeadRegistry(storage=SqliteRegistryStorage(...)) instead of the
default. Nothing in lead_registry.py or registry_sync.py would need to
change.
"""

import csv
import os
from abc import ABC, abstractmethod

from lead_registry.models import REGISTRY_FIELDNAMES


class RegistryStorage(ABC):
    """Interface for reading/writing the full set of lead registry rows."""

    @abstractmethod
    def load_all(self) -> list:
        """Return every registry row as a list of plain dicts."""
        raise NotImplementedError

    @abstractmethod
    def save_all(self, rows: list) -> None:
        """Overwrite the entire registry with the given list of plain dicts."""
        raise NotImplementedError


class CsvRegistryStorage(RegistryStorage):
    """CSV-backed implementation of RegistryStorage (today's storage)."""

    def __init__(self, path: str = "data/lead_registry.csv"):
        self.path = path

    def load_all(self) -> list:
        if not os.path.exists(self.path):
            return []
        with open(self.path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def save_all(self, rows: list) -> None:
        output_dir = os.path.dirname(self.path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REGISTRY_FIELDNAMES)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
