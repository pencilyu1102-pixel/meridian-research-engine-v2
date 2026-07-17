"""DataSource Execution Runner — unified fetch → validate → admission pipeline.

Phase 6.3: Minimum viable runner that wires DataSource.fetch() through
Data Card Registry validation and Source Policy admission, returning
a structured, serializable result.

Explicitly NOT responsible for:
  - Production release decisions
  - Account locking/unlocking
  - Hardlock / Gatekeeper verdicts
  - Retry, caching, or network management
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Sequence

from tools.data_card_registry import validate_data_card
from tools.data_source import DataSource, FetchFailure, FetchRequest
from tools.source_policy import check_source_admission


class DataSourceRunStatus(str, Enum):
    """Four mutually exclusive states a single fetch can resolve to."""

    CARD_VALIDATED = "CARD_VALIDATED"
    FETCH_FAILED = "FETCH_FAILED"
    CONTRACT_FAILED = "CONTRACT_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@dataclass(frozen=True)
class DataSourceRunResult:
    """Structured result of a single fetch → validate → admission cycle."""

    status: DataSourceRunStatus
    request_id: str
    symbol: str
    field: str

    card: dict[str, Any] | None = None
    failure: FetchFailure | None = None

    validation_status: str | None = None
    effective_permission: str | None = None
    can_enter_conclusion: bool = False
    can_enter_primary_valuation: bool = False

    violations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        result: dict[str, Any] = {
            "status": self.status.value,
            "request_id": self.request_id,
            "symbol": self.symbol,
            "field": self.field,
            "can_enter_conclusion": self.can_enter_conclusion,
            "can_enter_primary_valuation": self.can_enter_primary_valuation,
            "violations": list(self.violations),
        }
        if self.card is not None:
            result["card"] = self.card
        if self.failure is not None:
            result["failure"] = {
                "status": self.failure.status,
                "reason": self.failure.reason.value,
                "detail": self.failure.detail,
                "request_id": self.failure.request_id,
                "timestamp": self.failure.timestamp,
                "retry_allowed": self.failure.retry_allowed,
            }
        if self.validation_status is not None:
            result["validation_status"] = self.validation_status
        if self.effective_permission is not None:
            result["effective_permission"] = self.effective_permission
        return result


@dataclass(frozen=True)
class DataSourceBatchResult:
    """Aggregate result for a batch of fetch requests through one DataSource."""

    results: tuple[DataSourceRunResult, ...]
    total: int
    validated_count: int
    fetch_failed_count: int
    contract_failed_count: int
    validation_failed_count: int

    @classmethod
    def from_results(
        cls,
        results: Sequence[DataSourceRunResult],
    ) -> "DataSourceBatchResult":
        """Build a DataSourceBatchResult from a sequence of run results.

        Counts are derived from the results — never accepted from callers.
        """
        res_tuple = tuple(results)
        counts = {
            DataSourceRunStatus.CARD_VALIDATED: 0,
            DataSourceRunStatus.FETCH_FAILED: 0,
            DataSourceRunStatus.CONTRACT_FAILED: 0,
            DataSourceRunStatus.VALIDATION_FAILED: 0,
        }
        for r in res_tuple:
            counts[r.status] += 1
        return cls(
            results=res_tuple,
            total=len(res_tuple),
            validated_count=counts[DataSourceRunStatus.CARD_VALIDATED],
            fetch_failed_count=counts[DataSourceRunStatus.FETCH_FAILED],
            contract_failed_count=counts[DataSourceRunStatus.CONTRACT_FAILED],
            validation_failed_count=counts[DataSourceRunStatus.VALIDATION_FAILED],
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "results": [r.to_dict() for r in self.results],
            "total": self.total,
            "validated_count": self.validated_count,
            "fetch_failed_count": self.fetch_failed_count,
            "contract_failed_count": self.contract_failed_count,
            "validation_failed_count": self.validation_failed_count,
        }


# ── Single request ──────────────────────────────────────────────────────


def run_fetch(
    source: DataSource,
    request: FetchRequest,
) -> DataSourceRunResult:
    """Execute a single fetch through a DataSource, validate, and return structured result.

    Each request calls source.fetch() exactly once.
    No retry, fallback, or second fetch.
    """
    response = source.fetch(request)
    contract_violations: list[str] = []

    # ── FetchFailure branch ─────────────────────────────────────────
    if isinstance(response, FetchFailure):
        if response.request_id != request.request_id:
            contract_violations.append(
                f"FetchFailure request_id mismatch: expected {request.request_id!r}, "
                f"got {response.request_id!r}"
            )
        if contract_violations:
            return DataSourceRunResult(
                status=DataSourceRunStatus.CONTRACT_FAILED,
                request_id=request.request_id,
                symbol=request.symbol,
                field=request.field,
                failure=response,
                violations=tuple(contract_violations),
            )
        return DataSourceRunResult(
            status=DataSourceRunStatus.FETCH_FAILED,
            request_id=request.request_id,
            symbol=request.symbol,
            field=request.field,
            failure=response,
        )

    # ── Data Card branch ────────────────────────────────────────────
    if isinstance(response, dict):
        card = response

        # Check request–response binding
        if card.get("request_id") != request.request_id:
            contract_violations.append(
                f"Card request_id mismatch: expected {request.request_id!r}, "
                f"got {card.get('request_id')!r}"
            )
        if card.get("field_name") != request.field:
            contract_violations.append(
                f"Card field_name mismatch: expected {request.field!r}, "
                f"got {card.get('field_name')!r}"
            )
        if card.get("data_provenance") != source.data_provenance:
            contract_violations.append(
                f"Card provenance mismatch: expected {source.data_provenance!r}, "
                f"got {card.get('data_provenance')!r}"
            )

        if contract_violations:
            return DataSourceRunResult(
                status=DataSourceRunStatus.CONTRACT_FAILED,
                request_id=request.request_id,
                symbol=request.symbol,
                field=request.field,
                card=card,
                violations=tuple(contract_violations),
            )

        # Registry validation — external provenance only validates, never overwrites
        validation = validate_data_card(
            card,
            data_provenance=source.data_provenance,
        )
        if not validation.is_valid:
            return DataSourceRunResult(
                status=DataSourceRunStatus.VALIDATION_FAILED,
                request_id=request.request_id,
                symbol=request.symbol,
                field=request.field,
                card=card,
                validation_status=validation.status,
                violations=validation.violations,
            )

        # Source Policy admission
        permission = check_source_admission(
            card,
            data_provenance=source.data_provenance,
        )

        return DataSourceRunResult(
            status=DataSourceRunStatus.CARD_VALIDATED,
            request_id=request.request_id,
            symbol=request.symbol,
            field=request.field,
            card=card,
            validation_status=validation.status,
            effective_permission=permission.effective_permission,
            can_enter_conclusion=permission.can_enter_conclusion,
            can_enter_primary_valuation=permission.can_enter_primary_valuation,
            violations=permission.violations,
        )

    # ── Illegal response type ───────────────────────────────────────
    return DataSourceRunResult(
        status=DataSourceRunStatus.CONTRACT_FAILED,
        request_id=request.request_id,
        symbol=request.symbol,
        field=request.field,
        violations=(
            f"Unsupported response type from DataSource.fetch(): {type(response).__name__}",
        ),
    )


# ── Batch ───────────────────────────────────────────────────────────────


def run_batch(
    source: DataSource,
    requests: Sequence[FetchRequest],
) -> DataSourceBatchResult:
    """Execute a batch of requests through one DataSource.

    1. Fail-fast on duplicate request_ids within the batch.
    2. Execute each request sequentially, preserving input order.
    3. Aggregate results by status.
    """
    if not requests:
        return DataSourceBatchResult.from_results([])

    # Fail-fast duplicate check
    seen: set[str] = set()
    for req in requests:
        if req.request_id in seen:
            raise ValueError(
                f"Duplicate request_id in batch: {req.request_id!r}"
            )
        seen.add(req.request_id)

    results: list[DataSourceRunResult] = []
    for req in requests:
        results.append(run_fetch(source, req))

    return DataSourceBatchResult.from_results(results)
