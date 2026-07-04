"""Lightweight source reliability audit."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence


VALID_TIERS = {"S", "A", "B", "C", "D"}


@dataclass(frozen=True)
class SourceAuditResult:
    source: str
    tier: str
    can_enter_conclusion: bool
    issues: tuple[str, ...]


def audit_source(
    source: str,
    tier: str,
    timestamp: str,
    unit: str,
    currency: str,
    accounting_basis: str,
    period_basis: str,
    has_conflict: bool = False,
) -> SourceAuditResult:
    """Audit whether a source is complete enough to support a conclusion."""

    normalized_tier = tier.upper()
    issues: list[str] = []
    if normalized_tier not in VALID_TIERS:
        issues.append("invalid source tier")
    for field_name, value in (
        ("timestamp", timestamp),
        ("unit", unit),
        ("currency", currency),
        ("accounting_basis", accounting_basis),
        ("period_basis", period_basis),
    ):
        if not value:
            issues.append(f"missing {field_name}")
    if has_conflict:
        issues.append("conflicting source data")
    can_enter = normalized_tier in {"S", "A", "B"} and not issues
    return SourceAuditResult(source=source, tier=normalized_tier, can_enter_conclusion=can_enter, issues=tuple(issues))


def render_source_audit(result: SourceAuditResult) -> str:
    """Render source audit result as Markdown."""

    issues = ", ".join(result.issues) if result.issues else "None"
    return "\n".join(
        [
            "| Field | Value |",
            "|---|---|",
            f"| source | {result.source} |",
            f"| tier | {result.tier} |",
            f"| can_enter_conclusion | {result.can_enter_conclusion} |",
            f"| issues | {issues} |",
        ]
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit source reliability metadata.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--tier", required=True)
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--currency", required=True)
    parser.add_argument("--accounting-basis", required=True)
    parser.add_argument("--period-basis", required=True)
    parser.add_argument("--has-conflict", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    result = audit_source(
        source=args.source,
        tier=args.tier,
        timestamp=args.timestamp,
        unit=args.unit,
        currency=args.currency,
        accounting_basis=args.accounting_basis,
        period_basis=args.period_basis,
        has_conflict=args.has_conflict,
    )
    print(render_source_audit(result))
    return 0 if result.can_enter_conclusion else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
