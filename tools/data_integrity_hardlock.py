"""Aggregate Data Integrity Hardlock verdicts across MVP modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

STATUS_PASS_FORMAL = "PASS_FORMAL"
STATUS_FAIL_DATA_HARDLOCK = "FAIL_DATA_HARDLOCK"
STATUS_FAIL_INDUSTRY_HARD_FIELDS = "FAIL_INDUSTRY_HARD_FIELDS"
PASS_STATUSES = {"PASS_FORMAL"}
DEGRADE_STATUSES = {"PASS_TEST_ONLY", "CALC_ONLY_NOT_FOR_CONCLUSION"}


@dataclass(frozen=True)
class HardlockAggregateResult:
    status: str
    violations: tuple[str, ...]
    details: dict[str, Any]

    @property
    def is_valid(self) -> bool:
        return self.status == STATUS_PASS_FORMAL


def aggregate_hardlock_verdicts(verdicts: Mapping[str, Mapping[str, Any]]) -> HardlockAggregateResult:
    failing: list[tuple[str, str, tuple[str, ...]]] = []
    degradations: list[tuple[str, str, tuple[str, ...]]] = []
    module_statuses: dict[str, str] = {}
    combined_violations: list[str] = []

    for module_name, verdict in verdicts.items():
        status = str(verdict.get("status", ""))
        violations = tuple(str(item) for item in verdict.get("violations", ()))
        module_statuses[module_name] = status
        if status in PASS_STATUSES:
            continue
        if status in DEGRADE_STATUSES:
            degradations.append((module_name, status, violations))
            combined_violations.extend(f"{module_name}: {item}" for item in violations)
            continue
        failing.append((module_name, status, violations))
        combined_violations.extend(f"{module_name}: {item}" for item in violations)

    if not failing and not degradations:
        return HardlockAggregateResult(
            status=STATUS_PASS_FORMAL,
            violations=(),
            details={
                "module_statuses": module_statuses,
                "release_tier": "formal_releasable",
            },
        )

    if len(failing) == 1 and not degradations:
        _, status, violations = failing[0]
        return HardlockAggregateResult(
            status=status,
            violations=violations,
            details={
                "module_statuses": module_statuses,
                "release_tier": "not_releasable",
            },
        )

    return HardlockAggregateResult(
        status=STATUS_FAIL_DATA_HARDLOCK,
        violations=tuple(combined_violations) if combined_violations else ("one or more hardlock modules did not pass",),
        details={
            "module_statuses": module_statuses,
            "release_tier": "not_releasable",
        },
    )
