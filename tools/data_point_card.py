"""Create a Markdown data point card."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class DataPointCard:
    data_point: str
    source: str
    source_tier: str
    timestamp: str
    unit: str
    currency: str
    accounting_basis: str
    period_basis: str
    can_enter_conclusion: str
    meaning: str
    invalidation_condition: str


def render_data_point_card(card: DataPointCard) -> str:
    """Render a data point card as Markdown."""

    rows = [
        ("Data point", card.data_point),
        ("Source", card.source),
        ("Source tier", card.source_tier),
        ("Timestamp", card.timestamp),
        ("Unit", card.unit),
        ("Currency", card.currency),
        ("Accounting basis", card.accounting_basis),
        ("Period basis", card.period_basis),
        ("Can enter conclusion", card.can_enter_conclusion),
    ]
    lines = ["# Data Point Card", "", "| Field | Value |", "|---|---|"]
    lines.extend(f"| {field} | {value} |" for field, value in rows)
    lines.extend(["", "## Meaning", card.meaning, "", "## Invalidation Condition", card.invalidation_condition])
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a Markdown data point card.")
    parser.add_argument("--data-point", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-tier", required=True)
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--unit", default="")
    parser.add_argument("--currency", default="")
    parser.add_argument("--accounting-basis", default="")
    parser.add_argument("--period-basis", default="")
    parser.add_argument("--can-enter-conclusion", default="Conditional")
    parser.add_argument("--meaning", required=True)
    parser.add_argument("--invalidation-condition", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    print(render_data_point_card(DataPointCard(**vars(args))))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
