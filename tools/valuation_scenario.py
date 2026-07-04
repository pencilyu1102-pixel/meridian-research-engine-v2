"""Three-scenario valuation calculator."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

try:
    from .financial_rigor import calculate_price_from_multiple, format_decimal, to_decimal
except ImportError:  # pragma: no cover - allows direct CLI execution
    from financial_rigor import calculate_price_from_multiple, format_decimal, to_decimal


@dataclass(frozen=True)
class ValuationScenario:
    bear_case_price: Decimal
    base_case_price: Decimal
    bull_case_price: Decimal


def calculate_valuation_scenarios(
    base_eps: Decimal | int | str,
    bear_multiple: Decimal | int | str,
    base_multiple: Decimal | int | str,
    bull_multiple: Decimal | int | str,
) -> ValuationScenario:
    """Calculate bear, base, and bull case prices from EPS and multiples."""

    eps = to_decimal(base_eps, "base_eps")
    return ValuationScenario(
        bear_case_price=calculate_price_from_multiple(eps, bear_multiple),
        base_case_price=calculate_price_from_multiple(eps, base_multiple),
        bull_case_price=calculate_price_from_multiple(eps, bull_multiple),
    )


def format_scenario_table(scenario: ValuationScenario) -> str:
    """Render valuation scenarios as a Markdown table."""

    return "\n".join(
        [
            "| Scenario | Price |",
            "|---|---:|",
            f"| Bear case price | {format_decimal(scenario.bear_case_price)} |",
            f"| Base case price | {format_decimal(scenario.base_case_price)} |",
            f"| Bull case price | {format_decimal(scenario.bull_case_price)} |",
        ]
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate three-scenario valuation prices.")
    parser.add_argument("--eps", required=True, help="Base or normalized EPS")
    parser.add_argument("--bear", required=True, help="Bear case valuation multiple")
    parser.add_argument("--base", required=True, help="Base case valuation multiple")
    parser.add_argument("--bull", required=True, help="Bull case valuation multiple")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    scenario = calculate_valuation_scenarios(args.eps, args.bear, args.base, args.bull)
    print(format_scenario_table(scenario))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
