"""Three-scenario valuation calculator."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Sequence

try:
    from .financial_rigor import calculate_price_from_multiple, format_decimal, to_decimal
    from .tool_metadata_guard import ToolMetadataVerdict, evaluate_tool_metadata, render_metadata_block
except ImportError:  # pragma: no cover - allows direct CLI execution
    from financial_rigor import calculate_price_from_multiple, format_decimal, to_decimal
    from tool_metadata_guard import ToolMetadataVerdict, evaluate_tool_metadata, render_metadata_block


@dataclass(frozen=True)
class ValuationScenario:
    bear_case_price: Decimal
    base_case_price: Decimal
    bull_case_price: Decimal
    metadata_verdict: ToolMetadataVerdict | None = None


def calculate_valuation_scenarios(
    base_eps: Decimal | int | str,
    bear_multiple: Decimal | int | str,
    base_multiple: Decimal | int | str,
    bull_multiple: Decimal | int | str,
    metadata: Mapping[str, Any] | None = None,
) -> ValuationScenario:
    """Calculate bear, base, and bull case prices from EPS and multiples."""

    eps = to_decimal(base_eps, "base_eps")
    metadata_verdict = evaluate_tool_metadata(metadata)
    return ValuationScenario(
        bear_case_price=calculate_price_from_multiple(eps, bear_multiple),
        base_case_price=calculate_price_from_multiple(eps, base_multiple),
        bull_case_price=calculate_price_from_multiple(eps, bull_multiple),
        metadata_verdict=metadata_verdict,
    )


def format_scenario_table(scenario: ValuationScenario) -> str:
    """Render valuation scenarios as a Markdown table."""

    lines = [
        "| Scenario | Price |",
        "|---|---:|",
        f"| Bear case price | {format_decimal(scenario.bear_case_price)} |",
        f"| Base case price | {format_decimal(scenario.base_case_price)} |",
        f"| Bull case price | {format_decimal(scenario.bull_case_price)} |",
    ]
    if scenario.metadata_verdict is not None:
        lines.append(render_metadata_block(scenario.metadata_verdict))
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate three-scenario valuation prices.")
    parser.add_argument("--eps", required=True, help="Base or normalized EPS")
    parser.add_argument("--bear", required=True, help="Bear case valuation multiple")
    parser.add_argument("--base", required=True, help="Base case valuation multiple")
    parser.add_argument("--bull", required=True, help="Bull case valuation multiple")
    parser.add_argument("--basis", help="Data basis, e.g. gaap_actual")
    parser.add_argument("--period", help="Data period, e.g. TTM or FY2025")
    parser.add_argument("--source-tier", help="Source tier, one of A/B/C/D")
    parser.add_argument("--can-enter-conclusion", help="Conclusion permission: full/reference_only/blocked")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    metadata = {
        "basis": args.basis,
        "period": args.period,
        "source_tier": args.source_tier,
        "can_enter_conclusion": args.can_enter_conclusion,
    }
    scenario = calculate_valuation_scenarios(args.eps, args.bear, args.base, args.bull, metadata=metadata)
    print(format_scenario_table(scenario))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
