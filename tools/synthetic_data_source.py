"""SyntheticDataSource — Phase 6.1 minimum implementation.

A DataSource adapter backed entirely by in-memory fixtures or JSON fixture files.
Always stamped with PROVENANCE_SYNTHETIC and never eligible for production use.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.data_source import (
    DataSource,
    FetchFailure,
    FetchFailureReason,
    FetchRequest,
    build_data_card,
)
from tools.source_policy import PROVENANCE_SYNTHETIC


class SyntheticDataSource(DataSource):
    """DataSource backed by synthetic fixture records — test-only, no production path."""

    def __init__(
        self,
        records: Sequence[Mapping[str, Any]] | None = None,
        fixture_path: str | Path | None = None,
        *,
        default_tier: str = "S",
    ) -> None:
        """Create a SyntheticDataSource.

        Provide *either* an in-memory list of records *or* a path to a JSON file.
        If both are given, fixture_path takes precedence.

        default_tier sets the source tier for ALL records from this instance.
        Fixture records MUST NOT carry their own source_tier — the tier is a
        property of the DataSource, not of individual records.

        Raises ValueError if fixture_path is given but does not exist or is not
        valid JSON, or if no records source is provided.
        """
        if fixture_path is not None:
            path = Path(fixture_path)
            if not path.exists():
                raise ValueError(f"Fixture path does not exist: {fixture_path}")
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("Synthetic fixture JSON must be a list of record objects")
            records = raw
        elif records is None:
            raise ValueError(
                "SyntheticDataSource requires either records= or fixture_path="
            )

        super().__init__(
            source_name="SyntheticDataSource",
            default_tier=default_tier,
            data_provenance=PROVENANCE_SYNTHETIC,
        )

        # Store all records and build lookup indexes.
        self._records: list[dict[str, Any]] = [dict(r) for r in records]

        # (symbol, field) → list of records (preserves all candidates)
        self._index: dict[tuple[str, str], list[dict[str, Any]]] = {}
        # (symbol, field, period) → single record (exact match)
        self._period_index: dict[tuple[str, str, str], dict[str, Any]] = {}

        for rec in self._records:
            symbol = str(rec.get("symbol", ""))
            field_name = str(rec.get("field", ""))
            period = str(rec.get("period", ""))

            key = (symbol, field_name)
            self._index.setdefault(key, []).append(rec)

            if period:
                period_key = (symbol, field_name, period)
                if period_key not in self._period_index:
                    self._period_index[period_key] = rec

    def fetch(self, request: FetchRequest) -> dict[str, Any] | FetchFailure:
        """Look up a record and return a Data Card or FetchFailure.

        Lookup rules:
          - request.period provided → exact match on (symbol, field, period).
          - request.period NOT provided and 1 candidate → return that record.
          - request.period NOT provided and 0 candidates → FIELD_MISSING.
          - request.period NOT provided and multiple candidates → PARSE_ERROR
            (ambiguous — caller must specify period).
        """
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        rec: dict[str, Any] | None = None

        # 1. Try period-aware exact match first
        if request.period:
            period_key = (request.symbol, request.field, request.period)
            rec = self._period_index.get(period_key)

        # 2. Without period, inspect symbol+field candidates
        if rec is None:
            key = (request.symbol, request.field)
            candidates = self._index.get(key, [])

            if len(candidates) == 0:
                rec = None
            elif len(candidates) == 1:
                rec = candidates[0]
            else:
                return FetchFailure(
                    status="FETCH_FAILED",
                    reason=FetchFailureReason.PARSE_ERROR,
                    detail=(
                        f"Ambiguous: {len(candidates)} records for "
                        f"symbol={request.symbol!r}, field={request.field!r} "
                        f"— period is required"
                    ),
                    request_id=request.request_id,
                    timestamp=now_ts,
                    retry_allowed=False,
                )

        # 3. Not found → FIELD_MISSING
        if rec is None:
            return FetchFailure(
                status="FETCH_FAILED",
                reason=FetchFailureReason.FIELD_MISSING,
                detail=(
                    f"No fixture record for symbol={request.symbol!r}, "
                    f"field={request.field!r}"
                    + (f", period={request.period!r}" if request.period else "")
                ),
                request_id=request.request_id,
                timestamp=now_ts,
                retry_allowed=False,
            )

        # 4. Validate required fields before building
        missing = []
        if "timestamp" not in rec:
            missing.append("timestamp")
        if "freshness_status" not in rec:
            missing.append("freshness_status")
        if missing:
            return FetchFailure(
                status="FETCH_FAILED",
                reason=FetchFailureReason.PARSE_ERROR,
                detail=(
                    f"Fixture record for symbol={request.symbol!r}, "
                    f"field={request.field!r} is missing required fields: "
                    + ", ".join(missing)
                ),
                request_id=request.request_id,
                timestamp=now_ts,
                retry_allowed=False,
            )

        # 5. Build Data Card from fixture record
        try:
            return build_data_card(
                request=request,
                value=rec.get("value"),
                source_name=self.source_name,
                source_tier=self.default_tier,
                timestamp=str(rec["timestamp"]),
                period=str(rec.get("period", "")),
                unit=str(rec.get("unit", "")),
                currency=str(rec.get("currency", "")),
                accounting_basis=str(rec.get("accounting_basis", "")),
                requested_permission=str(
                    rec.get("requested_permission", "reference_only")
                ),
                freshness_status=str(rec["freshness_status"]),
                has_conflict=bool(rec.get("has_conflict", False)),
                notes=str(rec.get("notes", "Synthetic fixture")),
                data_provenance=self.data_provenance,
            )
        except (KeyError, TypeError, ValueError) as exc:
            return FetchFailure(
                status="FETCH_FAILED",
                reason=FetchFailureReason.PARSE_ERROR,
                detail=f"Cannot build Data Card from fixture record: {exc}",
                request_id=request.request_id,
                timestamp=now_ts,
                retry_allowed=False,
            )
