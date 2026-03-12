"""Lightweight in-tree compatibility helpers for retired TSDB tutorials."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimeRange:
    start_time: int
    end_time: int


@dataclass
class TSDBRecord:
    timestamp: int
    value: float
    tags: dict[str, Any] = field(default_factory=dict)


class SageTSDB:
    """Simple in-memory TSDB used to keep legacy tutorials runnable."""

    def __init__(self):
        self._records: list[TSDBRecord] = []

    @property
    def size(self) -> int:
        return len(self._records)

    def add(
        self, timestamp: int, value: float, tags: dict[str, Any] | None = None, **kwargs
    ):
        self._records.append(
            TSDBRecord(timestamp=timestamp, value=float(value), tags=tags or {})
        )

    def query(self, time_range: TimeRange):
        return [
            record
            for record in self._records
            if time_range.start_time <= record.timestamp <= time_range.end_time
        ]

    def get_stats(self) -> dict[str, Any]:
        values = [record.value for record in self._records]
        return {
            "size": len(self._records),
            "min_value": min(values) if values else None,
            "max_value": max(values) if values else None,
            "avg_value": (sum(values) / len(values)) if values else None,
        }
