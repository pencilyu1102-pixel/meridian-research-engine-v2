"""DataSource abstraction — unified fetch interface for external and local data.

All data enters the Meridian Research Engine through this layer.
Concrete adapters (including SyntheticDataSource) implement fetch().

Phase 6.1: Minimum viable interface.
  - FetchRequest / FetchFailure / DataSource / build_data_card
  - No network, credentials, caching, retry, or production adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Mapping

from tools.source_policy import (
    ALLOWED_SOURCE_TIERS,
    effective_permission,
)


class FetchFailureReason(str, Enum):
    """Classified reasons a DataSource may fail to fulfill a request."""

    NETWORK_ERROR = "NETWORK_ERROR"
    FIELD_MISSING = "FIELD_MISSING"
    PARSE_ERROR = "PARSE_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    TIMEOUT = "TIMEOUT"


@dataclass(frozen=True)
class FetchRequest:
    """Immutable request for a single data field.

    Carries symbol, field, tracing id, and optional temporal / context parameters.
    """

    symbol: str
    field: str
    request_id: str
    as_of: str | None = None
    period: str | None = None
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must be non-empty")
        if not self.field.strip():
            raise ValueError("field must be non-empty")
        if not self.request_id.strip():
            raise ValueError("request_id must be non-empty")


@dataclass(frozen=True)
class FetchFailure:
    """Structured failure returned when a DataSource cannot fulfill a request."""

    status: Literal["FETCH_FAILED"] = "FETCH_FAILED"
    reason: FetchFailureReason = FetchFailureReason.FIELD_MISSING
    detail: str = ""
    request_id: str = ""
    timestamp: str = ""
    retry_allowed: bool = False


class DataSource(ABC):
    """Abstract data source — all concrete adapters must implement fetch().

    Responsibilities:
      - Accept a FetchRequest.
      - Locate the raw record (in-memory, fixture, or future network).
      - Normalize and return a standard Data Card, or a FetchFailure.

    Explicitly NOT responsible for:
      - Formal conclusion admission  (→ source_policy / hardlock)
      - Report release               (→ gatekeeper)
      - Bundle validation            (→ gatekeeper)
      - Account locking/unlocking
    """

    source_name: str
    default_tier: str
    data_provenance: str

    def __init__(
        self,
        *,
        source_name: str,
        default_tier: str,
        data_provenance: str,
    ) -> None:
        if not source_name.strip():
            raise ValueError("source_name must be non-empty")
        if default_tier not in ALLOWED_SOURCE_TIERS:
            raise ValueError(
                f"default_tier must be one of {sorted(ALLOWED_SOURCE_TIERS)}, "
                f"got {default_tier!r}"
            )
        if not data_provenance.strip():
            raise ValueError("data_provenance must be non-empty")
        self.source_name = source_name
        self.default_tier = default_tier
        self.data_provenance = data_provenance

    @abstractmethod
    def fetch(self, request: FetchRequest) -> dict[str, Any] | FetchFailure:
        """Fetch a single field and return either a Data Card or a FetchFailure."""
        ...


def build_data_card(
    *,
    request: FetchRequest,
    value: Any,
    source_name: str,
    source_tier: str,
    timestamp: str,
    period: str,
    freshness_status: str,
    unit: str = "",
    currency: str = "",
    accounting_basis: str = "",
    requested_permission: str = "full",
    has_conflict: bool = False,
    notes: str = "",
    data_provenance: str,
) -> dict[str, Any]:
    """Build a standard Data Card from adapter-internal record fields.

    Permission is always capped through source_policy.effective_permission() —
    even if a fixture mistakenly requests 'full' for a B-tier source, the
    card's can_enter_conclusion will be clamped to 'reference_only'.

    Returns a dict with all REQUIRED_FIELDS required by data_card_registry,
    plus request_id and data_provenance for traceability.

    All parameters except unit/currency/accounting_basis/notes are required.
    freshness_status and timestamp MUST be provided explicitly — no defaults.
    """
    capped = effective_permission(source_tier, requested_permission)

    return {
        "field_name": request.field,
        "value": value,
        "source": source_name,
        "source_tier": source_tier,
        "timestamp": timestamp,
        "period": period,
        "unit": unit,
        "currency": currency,
        "accounting_basis": accounting_basis,
        "can_enter_conclusion": capped,
        "notes": notes,
        "freshness_status": freshness_status,
        "has_conflict": has_conflict,
        "request_id": request.request_id,
        "data_provenance": data_provenance,
    }
