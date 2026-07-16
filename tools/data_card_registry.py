"""Data card registry and validation — delegates source policy to tools.source_policy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.source_policy import (
    ALLOWED_PERMISSIONS,
    ALLOWED_SOURCE_TIERS,
    STATUS_FAIL_DATA_CARD_MISSING,
    STATUS_FAIL_SOURCE_PERMISSION,
    STATUS_PASS_FORMAL,
    check_source_admission,
)

REQUIRED_FIELDS: tuple[str, ...] = (
    "field_name",
    "value",
    "source",
    "source_tier",
    "timestamp",
    "period",
    "unit",
    "currency",
    "accounting_basis",
    "can_enter_conclusion",
    "notes",
    "freshness_status",
    "has_conflict",
    "request_id",
    "data_provenance",
)


@dataclass(frozen=True)
class DataCardValidationResult:
    status: str
    violations: tuple[str, ...]
    card: dict[str, Any] | None = None

    @property
    def is_valid(self) -> bool:
        return self.status == STATUS_PASS_FORMAL


@dataclass(frozen=True)
class ConclusionPermission:
    can_enter_conclusion: bool
    can_enter_primary_valuation: bool
    reason: str


class DataCardRegistry:
    """Store and validate data cards loaded from sidecar JSON fixtures."""

    def __init__(self, cards: Sequence[Mapping[str, Any]]):
        self._cards: dict[str, dict[str, Any]] = {}
        for raw_card in cards:
            card = dict(raw_card)
            field_name = card.get("field_name")
            if isinstance(field_name, str) and field_name:
                self._cards[field_name] = card

    @classmethod
    def from_json_file(cls, path: str | Path) -> "DataCardRegistry":
        loaded = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(loaded, list):
            raise TypeError("Data card sidecar JSON must be a list of objects")
        return cls(loaded)

    def get(self, field_name: str) -> dict[str, Any] | None:
        return self._cards.get(field_name)

    def validate(self, field_name: str, *, data_provenance: str | None = None) -> DataCardValidationResult:
        card = self.get(field_name)
        if card is None:
            return DataCardValidationResult(
                status=STATUS_FAIL_DATA_CARD_MISSING,
                violations=(f"missing data card for field: {field_name}",),
                card=None,
            )
        return validate_data_card(card, data_provenance=data_provenance)

    def conclusion_permission(self, field_name: str, *, data_provenance: str | None = None) -> ConclusionPermission:
        validation = self.validate(field_name, data_provenance=data_provenance)
        if not validation.is_valid or validation.card is None:
            return ConclusionPermission(False, False, validation.status)
        sp = check_source_admission(validation.card, data_provenance=data_provenance)
        return ConclusionPermission(
            can_enter_conclusion=sp.can_enter_conclusion,
            can_enter_primary_valuation=sp.can_enter_primary_valuation,
            reason="; ".join(sp.violations) if sp.violations else sp.effective_permission,
        )


def validate_data_card(
    card: Mapping[str, Any],
    *,
    data_provenance: str | None = None,
) -> DataCardValidationResult:
    """Validate a data card: required fields, tier, permission, and admission policy."""
    missing_fields = [field for field in REQUIRED_FIELDS if field not in card]
    if missing_fields:
        return DataCardValidationResult(
            status=STATUS_FAIL_DATA_CARD_MISSING,
            violations=tuple(f"missing required field: {field}" for field in missing_fields),
            card=dict(card),
        )

    # Require request_id and data_provenance to be non-empty strings
    for trace_field in ("request_id", "data_provenance"):
        val = card.get(trace_field)
        if not isinstance(val, str) or not val.strip():
            return DataCardValidationResult(
                status=STATUS_FAIL_DATA_CARD_MISSING,
                violations=(f"{trace_field} must be a non-empty string",),
                card=dict(card),
            )

    source_tier = card.get("source_tier")
    if source_tier not in ALLOWED_SOURCE_TIERS:
        return DataCardValidationResult(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=(f"unknown source_tier: {source_tier}",),
            card=dict(card),
        )

    conclusion_flag = card.get("can_enter_conclusion")
    if conclusion_flag not in ALLOWED_PERMISSIONS:
        return DataCardValidationResult(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=(f"unknown can_enter_conclusion: {conclusion_flag}",),
            card=dict(card),
        )

    # Provenance consistency: external expected must match Card field; never overwrite
    if data_provenance is not None and data_provenance != card.get("data_provenance"):
        return DataCardValidationResult(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=(
                f"data_provenance mismatch: expected {data_provenance!r}, "
                f"card has {card.get('data_provenance')!r}",
            ),
            card=dict(card),
        )

    # Delegate to unified source policy
    sp = check_source_admission(card, data_provenance=data_provenance)
    if sp.violations:
        return DataCardValidationResult(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=sp.violations,
            card=dict(card),
        )

    return DataCardValidationResult(
        status=STATUS_PASS_FORMAL,
        violations=(),
        card=dict(card),
    )
