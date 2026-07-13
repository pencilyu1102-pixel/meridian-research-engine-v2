"""Unified source-tier admission policy — single authority for all modules.

All other modules (data_card_registry, source_audit, tool_metadata_guard)
must import from here rather than maintaining their own tier/permission sets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

# ── Allowed tiers (S through D) ────────────────────────────────────────
ALLOWED_SOURCE_TIERS: set[str] = {"S", "A", "B", "C", "D"}

# ── Tier → maximum conclusion permission ───────────────────────────────
# Cards may request a lower permission level but never exceed this cap.
TIER_MAX_PERMISSION: dict[str, str] = {
    "S": "full",
    "A": "full",
    "B": "reference_only",
    "C": "reference_only",
    "D": "blocked",
}

# ── Permissions ─────────────────────────────────────────────────────────
ALLOWED_PERMISSIONS: set[str] = {"full", "reference_only", "blocked"}

ALLOWED_FRESHNESS_STATUSES: set[str] = {"current", "stale", "unknown"}

# ── Critical fields that require full permission ───────────────────────
CRITICAL_FIELDS: set[str] = {
    "current_price",
    "market_cap",
    "eps_ttm",
    "eps",
    "revenue_ttm",
    "shares_outstanding",
    "current_shares",
    "valuation_denominator",
}

# ── Synthetic data provenance marker ────────────────────────────────────
PROVENANCE_SYNTHETIC = "SYNTHETIC_FIXTURE"

# ── Statuses ────────────────────────────────────────────────────────────
STATUS_PASS_FORMAL = "PASS_FORMAL"
STATUS_PASS_TEST_ONLY = "PASS_TEST_ONLY"
STATUS_FAIL_SOURCE_PERMISSION = "FAIL_SOURCE_PERMISSION"
STATUS_FAIL_DATA_CARD_MISSING = "FAIL_DATA_CARD_MISSING"


@dataclass(frozen=True)
class SourcePermission:
    """Result of checking whether a card's tier + permission + freshness
    combination is admissible for conclusion entry."""

    effective_permission: str      # the actual permission after policy caps
    can_enter_conclusion: bool
    can_enter_primary_valuation: bool
    violations: tuple[str, ...]


def effective_permission(source_tier: str, requested_permission: str) -> str:
    """Return the effective permission after applying tier caps.

    B-tier requesting 'full' → capped to 'reference_only'.
    D-tier requesting anything → capped to 'blocked'.
    """
    tier = source_tier.upper()
    if tier not in ALLOWED_SOURCE_TIERS:
        return "blocked"
    maximum = TIER_MAX_PERMISSION.get(tier, "blocked")
    # Lower of the two: if maximum is 'reference_only' and requested is 'full',
    # effective is 'reference_only'.
    perm_order = {"blocked": 0, "reference_only": 1, "full": 2}
    req = requested_permission if requested_permission in ALLOWED_PERMISSIONS else "blocked"
    if perm_order.get(req, 0) <= perm_order.get(maximum, 0):
        return req
    return maximum


def check_source_admission(
    card: Mapping[str, Any],
    *,
    data_provenance: str | None = None,
) -> SourcePermission:
    """Unified admission check for a single data card.

    Checks tier → permission cap, freshness, conflicts, and synthetic boundary.
    """
    violations: list[str] = []

    source_tier = str(card.get("source_tier", "")).upper()
    requested = str(card.get("can_enter_conclusion", "blocked"))

    if source_tier not in ALLOWED_SOURCE_TIERS:
        violations.append(f"unknown source_tier: {source_tier}")
        eff = "blocked"
    else:
        eff = effective_permission(source_tier, requested)

        # Tier-permission policy violations
        # Compare ORIGINAL requested permission against tier maximum,
        # NOT the clamped effective_permission.
        tier_max = TIER_MAX_PERMISSION.get(source_tier, "blocked")
        perm_order = {"blocked": 0, "reference_only": 1, "full": 2}
        req_ord = perm_order.get(requested, 0) if requested in ALLOWED_PERMISSIONS else 0
        if req_ord > perm_order.get(tier_max, 0):
            if source_tier == "D":
                violations.append("D-tier cannot enter conclusion (max: blocked)")
            elif source_tier in ("B", "C"):
                violations.append(f"{source_tier}-tier cannot request full (max: reference_only)")

    # ── Freshness ──
    freshness = str(card.get("freshness_status", "unknown")).lower()
    if freshness not in ALLOWED_FRESHNESS_STATUSES:
        violations.append(
            f"freshness_status='{freshness}' is not allowed (valid: {sorted(ALLOWED_FRESHNESS_STATUSES)})"
        )
    if freshness == "stale" and eff == "full":
        violations.append("stale data cannot enter formal conclusion")
    if freshness == "unknown" and eff == "full":
        violations.append("unknown freshness cannot enter formal conclusion")

    # ── Conflict ──
    has_conflict = bool(card.get("has_conflict", False))
    if has_conflict and eff == "full":
        violations.append("conflicting data cannot enter formal conclusion")

    # ── Synthetic lock ──
    # Synthetic boundary is enforced at the hardlock aggregate level
    # (build_hardlock_from_bundle), not at individual card validation.
    # Individual cards from synthetic fixtures may pass structure validation
    # but the aggregate verdict will be capped at PASS_TEST_ONLY.

    can_enter = eff == "full" and not violations
    can_enter_primary = can_enter

    # Critical fields require full + no violations
    field_name = str(card.get("field_name", ""))
    if field_name in CRITICAL_FIELDS and not can_enter:
        violations.append(f"critical field '{field_name}' requires full permission for conclusion")

    return SourcePermission(
        effective_permission=eff,
        can_enter_conclusion=can_enter,
        can_enter_primary_valuation=can_enter_primary,
        violations=tuple(violations),
    )
