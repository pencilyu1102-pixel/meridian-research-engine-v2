"""Metadata guardrails for valuation tools — delegates to tools.source_policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tools.source_policy import (
    ALLOWED_PERMISSIONS,
    ALLOWED_SOURCE_TIERS,
    STATUS_FAIL_SOURCE_PERMISSION,
    STATUS_PASS_FORMAL,
    check_source_admission,
)

STATUS_PASS_TEST_ONLY = "PASS_TEST_ONLY"
STATUS_CALC_ONLY_NOT_FOR_CONCLUSION = "CALC_ONLY_NOT_FOR_CONCLUSION"

REQUIRED_METADATA_FIELDS = ("basis", "period", "source_tier", "can_enter_conclusion", "freshness_status", "has_conflict")


@dataclass(frozen=True)
class ToolMetadataVerdict:
    status: str
    violations: tuple[str, ...]
    provenance: dict[str, Any]

    @property
    def can_enter_formal_conclusion(self) -> bool:
        return self.status == STATUS_PASS_FORMAL


def evaluate_tool_metadata(
    metadata: Mapping[str, Any] | None,
    *,
    data_provenance: str | None = None,
) -> ToolMetadataVerdict:
    if not metadata:
        return ToolMetadataVerdict(
            status=STATUS_CALC_ONLY_NOT_FOR_CONCLUSION,
            violations=("missing metadata: basis, period, source_tier, can_enter_conclusion",),
            provenance={"provided": False, "missing_fields": list(REQUIRED_METADATA_FIELDS)},
        )

    normalized = {key: metadata.get(key) for key in REQUIRED_METADATA_FIELDS}
    missing = [key for key, value in normalized.items() if value in (None, "")]
    if missing:
        return ToolMetadataVerdict(
            status=STATUS_CALC_ONLY_NOT_FOR_CONCLUSION,
            violations=(f"missing metadata fields: {', '.join(missing)}",),
            provenance={"provided": True, **normalized, "missing_fields": missing},
        )

    source_tier = str(normalized["source_tier"])
    if source_tier not in ALLOWED_SOURCE_TIERS:
        return ToolMetadataVerdict(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=(f"unknown source_tier: {source_tier}",),
            provenance={"provided": True, **normalized, "missing_fields": []},
        )

    conclusion_permission = str(normalized["can_enter_conclusion"])
    if conclusion_permission not in ALLOWED_PERMISSIONS:
        return ToolMetadataVerdict(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=(f"unknown can_enter_conclusion: {conclusion_permission}",),
            provenance={"provided": True, **normalized, "missing_fields": []},
        )

    # Delegate to unified policy
    card = {
        "field_name": metadata.get("field_name", "unknown"),
        "source_tier": source_tier,
        "can_enter_conclusion": conclusion_permission,
        "freshness_status": metadata.get("freshness_status", "unknown"),
        "has_conflict": metadata.get("has_conflict", False),
    }
    sp = check_source_admission(card, data_provenance=data_provenance)
    if sp.violations:
        return ToolMetadataVerdict(
            status=STATUS_FAIL_SOURCE_PERMISSION,
            violations=sp.violations,
            provenance={"provided": True, **normalized, "missing_fields": []},
        )

    if conclusion_permission != "full":
        return ToolMetadataVerdict(
            status=STATUS_CALC_ONLY_NOT_FOR_CONCLUSION,
            violations=(f"can_enter_conclusion={conclusion_permission} is not formal-release eligible",),
            provenance={"provided": True, **normalized, "missing_fields": []},
        )

    return ToolMetadataVerdict(
        status=STATUS_PASS_FORMAL,
        violations=(),
        provenance={"provided": True, **normalized, "missing_fields": []},
    )


def render_metadata_block(verdict: ToolMetadataVerdict) -> str:
    lines = [
        "",
        "## Tool Metadata Guard",
        "",
        f"- **status:** {verdict.status}",
    ]
    for violation in verdict.violations:
        lines.append(f"- **violation:** {violation}")
    provenance = verdict.provenance
    if provenance:
        lines.append(f"- **basis:** {provenance.get('basis', 'N/A')}")
        lines.append(f"- **period:** {provenance.get('period', 'N/A')}")
        lines.append(f"- **source_tier:** {provenance.get('source_tier', 'N/A')}")
        lines.append(f"- **can_enter_conclusion:** {provenance.get('can_enter_conclusion', 'N/A')}")
    return "\n".join(lines)
