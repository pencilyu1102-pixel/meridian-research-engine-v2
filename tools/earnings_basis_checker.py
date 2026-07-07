"""Earnings basis classification and MVP hardlock checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

ALLOWED_EARNINGS_BASIS = {
    "gaap_actual",
    "non_gaap_adjusted_actual",
    "management_guidance",
    "consensus_estimate",
    "aggregator_field",
}
DEFAULT_PERMISSION = {
    "gaap_actual": "full",
    "non_gaap_adjusted_actual": "reference_only",
    "management_guidance": "reference_only",
    "consensus_estimate": "reference_only",
    "aggregator_field": "reference_only",
}
STATUS_PASS_FORMAL = "PASS_FORMAL"
STATUS_FAIL_EARNINGS_BASIS = "FAIL_EARNINGS_BASIS"


@dataclass(frozen=True)
class EarningsBasisCheckResult:
    status: str
    basis: str | None
    permission: str
    violations: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return self.status == STATUS_PASS_FORMAL


def check_earnings_basis(entry: Mapping[str, object]) -> EarningsBasisCheckResult:
    basis = entry.get("basis")
    if not isinstance(basis, str) or not basis:
        return EarningsBasisCheckResult(
            status=STATUS_FAIL_EARNINGS_BASIS,
            basis=None,
            permission="blocked",
            violations=("earnings basis is required",),
        )

    if basis not in ALLOWED_EARNINGS_BASIS:
        return EarningsBasisCheckResult(
            status=STATUS_FAIL_EARNINGS_BASIS,
            basis=basis,
            permission="blocked",
            violations=(f"unknown earnings basis: {basis}",),
        )

    usage_context = entry.get("usage_context", "background")
    if not isinstance(usage_context, str) or not usage_context:
        usage_context = "background"

    explicit_approval = bool(entry.get("explicit_approval", False))
    verified = bool(entry.get("verified", False))
    has_gaap_anchor = bool(entry.get("has_gaap_anchor", False))

    violations: list[str] = []
    permission = DEFAULT_PERMISSION[basis]

    if basis == "gaap_actual":
        permission = "full"

    elif basis == "non_gaap_adjusted_actual":
        if explicit_approval and has_gaap_anchor:
            permission = "full"
        if usage_context in {"conclusion", "core_valuation", "trailing_eps"} and not has_gaap_anchor:
            violations.append("adjusted EPS cannot enter conclusion without GAAP comparison")

    elif basis == "management_guidance":
        permission = "reference_only"
        if usage_context == "trailing_eps":
            violations.append("guidance EPS cannot be used as trailing EPS")

    elif basis == "consensus_estimate":
        permission = "reference_only"
        if usage_context == "trailing_eps":
            violations.append("consensus estimate cannot be used as trailing EPS")

    elif basis == "aggregator_field":
        permission = "reference_only"
        if usage_context in {"core_valuation", "trailing_eps", "conclusion"} and not verified:
            violations.append("aggregator field must be source-verified before core valuation use")
        if verified and explicit_approval:
            permission = "full"

    if violations:
        return EarningsBasisCheckResult(
            status=STATUS_FAIL_EARNINGS_BASIS,
            basis=basis,
            permission=permission,
            violations=tuple(violations),
        )

    return EarningsBasisCheckResult(
        status=STATUS_PASS_FORMAL,
        basis=basis,
        permission=permission,
        violations=(),
    )
