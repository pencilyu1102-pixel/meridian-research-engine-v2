"""Industry hard fields MVP checker for formal release gating."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

STATUS_PASS_FORMAL = "PASS_FORMAL"
STATUS_FAIL_INDUSTRY_HARD_FIELDS = "FAIL_INDUSTRY_HARD_FIELDS"
STATUS_FAIL_SOURCE_PERMISSION = "FAIL_SOURCE_PERMISSION"
ALLOWED_CONCLUSION_FLAGS = {"full", "reference_only", "blocked"}

INDUSTRY_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "CN_SEMICONDUCTOR_GROWTH": (
        "revenue_growth_driver",
        "gross_margin_trend",
        "r_and_d_intensity",
        "share_count_bridge",
        "valuation_anchor_type",
        "low_base_or_oneoff_flag",
    ),
    "US_MANAGED_CARE": (
        "mcr_or_mlr",
        "utilization_trend",
        "medicare_advantage",
        "insurance_segment",
        "health_services_segment",
        "pharmacy_or_care_services",
        "doj_risk",
        "cms_risk",
        "ftc_risk",
        "oig_risk",
        "sec_risk",
    ),
}


@dataclass(frozen=True)
class IndustryHardFieldsResult:
    status: str
    industry_adapter: str | None
    missing_fields: tuple[str, ...]
    field_count_required: int
    field_count_present: int
    violations: tuple[str, ...]
    details: dict[str, Any]

    @property
    def is_valid(self) -> bool:
        return self.status == STATUS_PASS_FORMAL

    def to_verdict(self) -> dict[str, Any]:
        return {
            "industry_adapter": self.industry_adapter,
            "status": self.status,
            "hardlock_status": self.status,
            "missing_fields": list(self.missing_fields),
            "field_count_required": self.field_count_required,
            "field_count_present": self.field_count_present,
            "violations": list(self.violations),
            "details": self.details,
        }


def load_industry_hard_fields(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise TypeError("Industry hard fields sidecar JSON must be an object")
    return loaded


def get_required_fields(industry_adapter: str) -> tuple[str, ...]:
    return INDUSTRY_REQUIRED_FIELDS.get(industry_adapter, ())


def check_industry_hard_fields(payload: Mapping[str, Any]) -> IndustryHardFieldsResult:
    industry_adapter = payload.get("industry_adapter")
    if not isinstance(industry_adapter, str) or not industry_adapter:
        return IndustryHardFieldsResult(
            status=STATUS_FAIL_INDUSTRY_HARD_FIELDS,
            industry_adapter=None,
            missing_fields=(),
            field_count_required=0,
            field_count_present=0,
            violations=("industry_adapter is required",),
            details={"fields": {}},
        )

    required_fields = get_required_fields(industry_adapter)
    if not required_fields:
        return IndustryHardFieldsResult(
            status=STATUS_FAIL_INDUSTRY_HARD_FIELDS,
            industry_adapter=industry_adapter,
            missing_fields=(),
            field_count_required=0,
            field_count_present=0,
            violations=(f"unknown industry_adapter: {industry_adapter}",),
            details={"fields": dict(payload.get("fields", {}))},
        )

    raw_fields = payload.get("fields", {})
    if not isinstance(raw_fields, Mapping):
        return IndustryHardFieldsResult(
            status=STATUS_FAIL_INDUSTRY_HARD_FIELDS,
            industry_adapter=industry_adapter,
            missing_fields=required_fields,
            field_count_required=len(required_fields),
            field_count_present=0,
            violations=("fields must be an object",),
            details={"fields": {}},
        )

    missing_fields: list[str] = []
    violations: list[str] = []
    normalized_fields: dict[str, dict[str, Any]] = {}
    present_count = 0

    for field_name in required_fields:
        raw_entry = raw_fields.get(field_name)
        if not isinstance(raw_entry, Mapping):
            missing_fields.append(field_name)
            violations.append(f"missing required industry hard field: {field_name}")
            normalized_fields[field_name] = {"present": False, "can_enter_conclusion": "missing"}
            continue

        present = bool(raw_entry.get("present", False))
        conclusion_flag = raw_entry.get("can_enter_conclusion")
        notes = raw_entry.get("notes")
        normalized_fields[field_name] = {
            "present": present,
            "can_enter_conclusion": conclusion_flag,
            "notes": notes,
        }

        if not present:
            missing_fields.append(field_name)
            violations.append(f"missing required industry hard field: {field_name}")
            continue

        present_count += 1

        if conclusion_flag not in ALLOWED_CONCLUSION_FLAGS:
            violations.append(f"unknown can_enter_conclusion for {field_name}: {conclusion_flag}")
            continue

        if conclusion_flag != "full":
            violations.append(
                f"industry hard field {field_name} cannot support formal conclusion: {conclusion_flag}"
            )

    status = STATUS_PASS_FORMAL if not violations else STATUS_FAIL_INDUSTRY_HARD_FIELDS
    return IndustryHardFieldsResult(
        status=status,
        industry_adapter=industry_adapter,
        missing_fields=tuple(missing_fields),
        field_count_required=len(required_fields),
        field_count_present=present_count,
        violations=tuple(violations),
        details={"fields": normalized_fields},
    )
