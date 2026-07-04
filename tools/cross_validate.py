"""Cross-validate numeric data points from multiple sources."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

try:
    from .financial_rigor import to_decimal
except ImportError:  # pragma: no cover - allows direct CLI execution
    from financial_rigor import to_decimal


@dataclass(frozen=True)
class SourceValue:
    source: str
    value: Decimal


def parse_source_value(raw: str) -> SourceValue:
    """Parse SOURCE=VALUE input."""

    if "=" not in raw:
        raise ValueError("source value must use SOURCE=VALUE format")
    source, value = raw.split("=", 1)
    return SourceValue(source=source.strip(), value=to_decimal(value.strip(), "value"))


def cross_validate_values(values: Sequence[SourceValue], tolerance: Decimal | int | str = "0.01") -> dict[str, object]:
    """Return conflict status for a set of source values."""

    if not values:
        raise ValueError("at least one source value is required")
    tolerance_decimal = to_decimal(tolerance, "tolerance")
    observed = [item.value for item in values]
    minimum = min(observed)
    maximum = max(observed)
    conflict = maximum - minimum > tolerance_decimal
    return {
        "count": len(values),
        "min": minimum,
        "max": maximum,
        "spread": maximum - minimum,
        "conflict": conflict,
    }


def render_validation(result: dict[str, object]) -> str:
    """Render cross-validation result as Markdown."""

    return "\n".join(
        [
            "| Field | Value |",
            "|---|---:|",
            f"| count | {result['count']} |",
            f"| min | {result['min']} |",
            f"| max | {result['max']} |",
            f"| spread | {result['spread']} |",
            f"| conflict | {result['conflict']} |",
        ]
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cross-validate values from multiple sources.")
    parser.add_argument("--value", action="append", required=True, help="SOURCE=VALUE. Repeat for multiple sources.")
    parser.add_argument("--tolerance", default="0.01")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    values = [parse_source_value(raw) for raw in args.value]
    print(render_validation(cross_validate_values(values, args.tolerance)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
