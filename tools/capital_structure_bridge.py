"""Capital structure bridge MVP checks for A-shares and US equities."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence

from tools.financial_rigor import calculate_market_cap, calculate_pe, to_decimal

STATUS_PASS_FORMAL = "PASS_FORMAL"
STATUS_FAIL_CAPITAL_BRIDGE = "FAIL_CAPITAL_BRIDGE"


@dataclass(frozen=True)
class CapitalBridgeResult:
    status: str
    violations: tuple[str, ...]
    warnings: tuple[str, ...]
    details: dict[str, Any]

    @property
    def is_valid(self) -> bool:
        return self.status == STATUS_PASS_FORMAL


REQUIRED_FIELDS = {"market", "fields_present"}
A_SHARE_CORE_FIELDS = {"current_price", "market_cap", "eps", "pe", "shares"}
US_MARKET_CAP_FIELDS = {"current_price", "market_cap", "current_shares"}
US_PE_FIELDS = {"current_price", "eps", "pe"}


def validate_capital_structure_bridge(payload: Mapping[str, Any]) -> CapitalBridgeResult:
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        return CapitalBridgeResult(
            status=STATUS_FAIL_CAPITAL_BRIDGE,
            violations=tuple(f"missing required field: {field}" for field in missing),
            warnings=(),
            details={},
        )

    market = payload["market"]
    fields_present = set(payload.get("fields_present", []))
    bridge_completed = bool(payload.get("bridge_completed", False))
    denominator_explanation = str(payload.get("denominator_explanation", "")).strip()
    share_basis_usage_explanation = str(payload.get("share_basis_usage_explanation", "")).strip()
    market_cap_tolerance_pct = _to_tolerance(payload.get("market_cap_tolerance_pct", "0.05"), "0.05")
    pe_tolerance_pct = _to_tolerance(payload.get("pe_tolerance_pct", "0.05"), "0.05")

    violations: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {"market": market}

    if market == "A_SHARE":
        if A_SHARE_CORE_FIELDS.issubset(fields_present) and not bridge_completed:
            violations.append("A-share report includes price/market cap/EPS/PE/shares without capital bridge")
        if payload.get("corporate_actions") and not bridge_completed:
            violations.append("corporate actions flagged but capital bridge not completed")

    elif market == "US_STOCK":
        if US_MARKET_CAP_FIELDS.issubset(fields_present):
            implied_market_cap = calculate_market_cap(payload["current_price"], payload["current_shares"])
            reported_market_cap = to_decimal(payload["market_cap"], "market_cap")
            market_cap_gap_pct = _relative_gap(implied_market_cap, reported_market_cap)
            details["market_cap_gap_pct"] = str(market_cap_gap_pct)
            if market_cap_gap_pct > market_cap_tolerance_pct:
                violations.append("market cap closure exceeds tolerance")

        if US_PE_FIELDS.issubset(fields_present):
            implied_pe = calculate_pe(payload["current_price"], payload["eps"])
            reported_pe = to_decimal(payload["pe"], "pe")
            pe_gap_pct = _relative_gap(implied_pe, reported_pe)
            details["pe_gap_pct"] = str(pe_gap_pct)
            if pe_gap_pct > pe_tolerance_pct and not denominator_explanation:
                violations.append("PE denominator mismatch exceeds tolerance without denominator explanation")

        if {"current_shares", "weighted_diluted_shares"}.issubset(fields_present) and not share_basis_usage_explanation:
            violations.append("current shares and weighted diluted shares both present without basis usage explanation")

    else:
        violations.append(f"unknown market: {market}")

    status = STATUS_PASS_FORMAL if not violations else STATUS_FAIL_CAPITAL_BRIDGE
    return CapitalBridgeResult(status=status, violations=tuple(violations), warnings=tuple(warnings), details=details)


def _to_tolerance(value: Any, default: str) -> Decimal:
    if value in (None, ""):
        value = default
    return to_decimal(value, "tolerance")


def _relative_gap(left: Decimal, right: Decimal) -> Decimal:
    if right == 0:
        return Decimal("0") if left == 0 else Decimal("1")
    return abs(left - right) / abs(right)
