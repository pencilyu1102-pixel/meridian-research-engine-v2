"""Data card registry and validation helpers for Data Integrity Hardlock."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

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
)
ALLOWED_SOURCE_TIERS = {"A", "B", "C", "D"}
ALLOWED_CONCLUSION_FLAGS = {"full", "reference_only", "blocked"}
STATUS_FAIL_DATA_CARD_MISSING = "FAIL_DATA_CARD_MISSING"
STATUS_FAIL_SOURCE_PERMISSION = "FAIL_SOURCE_PERMISSION"
STATUS_PASS_FORMAL = "PASS_FORMAL"


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

    def validate(self, field_name: str) -> DataCardValidationResult:
        card = self.get(field_name)
        if card is None:
            return DataCardValidationResult(
                status=STATUS_FAIL_DATA_CARD_MISSING,
                violations=(f"missing data card for field: {field_name}",),
                card=None,
            )
        return validate_data_card(card)

    def conclusion_permission(self, field_name: str) -> ConclusionPermission:
        validation = self.validate(field_name)
        if not validation.is_valid or validation.card is None:
            return ConclusionPermission(False, False, validation.status)
        return permission_from_card(validation.card)


def validate_data_card(card: Mapping[str, Any]) -> DataCardValidationResult:
    missing_fields = [field for field in REQUIRED_FIELDS if field not in card]
    if missing_fields:
        return DataCardValidationResult(
            status=STATUS_FAIL_DATA_CARD_MISSING,
            violations=tuple(f"missing required field: {field}" for field in missing_fields),
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
    if conclusion_flag not in ALLOWED_CONCLUSION_FLAGS:
        return DataCardValidationResult(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=(f"unknown can_enter_conclusion: {conclusion_flag}",),
            card=dict(card),
        )

    return DataCardValidationResult(
        status=STATUS_PASS_FORMAL,
        violations=(),
        card=dict(card),
    )


def permission_from_card(card: Mapping[str, Any]) -> ConclusionPermission:
    conclusion_flag = card["can_enter_conclusion"]
    if conclusion_flag == "full":
        return ConclusionPermission(True, True, "full")
    if conclusion_flag == "reference_only":
        return ConclusionPermission(False, False, "reference_only")
    return ConclusionPermission(False, False, "blocked")
