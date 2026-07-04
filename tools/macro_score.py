"""Lightweight macro six-factor score calculator.

The tool summarizes six macro factor scores into a normalized 0-100 score and
macro state. It is a research helper, not an investment recommendation engine.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping, Sequence

try:
    from .financial_rigor import format_decimal, to_decimal
except ImportError:  # pragma: no cover - allows direct CLI execution
    from financial_rigor import format_decimal, to_decimal


FACTOR_LABELS: dict[str, str] = {
    "growth": "Growth",
    "inflation": "Inflation",
    "liquidity": "Liquidity",
    "credit": "Credit",
    "earnings": "Earnings",
    "risk": "Risk appetite",
}

MIN_FACTOR_SCORE = Decimal("-2")
MAX_FACTOR_SCORE = Decimal("2")
RAW_SCORE_MIN = Decimal("-12")
RAW_SCORE_RANGE = Decimal("24")


@dataclass(frozen=True)
class MacroScore:
    """Macro score summary.

    Unit: factor scores are directional points from -2 to +2; normalized_score
    is a 0-100 index.
    """

    factor_scores: dict[str, Decimal]
    total_score: Decimal
    normalized_score: Decimal
    macro_state: str


def parse_factor_score(value: Decimal | int | str, field_name: str) -> Decimal:
    """Parse and validate one macro factor score.

    Unit: directional score from -2 to +2.
    """

    score = to_decimal(value, field_name)
    if score < MIN_FACTOR_SCORE or score > MAX_FACTOR_SCORE:
        raise ValueError(f"{field_name} must be between -2 and 2")
    return score


def classify_macro_state(normalized_score: Decimal | int | str) -> str:
    """Classify a normalized macro score.

    Unit: 0-100 macro score.
    """

    score = to_decimal(normalized_score, "normalized_score")
    if score >= Decimal("80"):
        return "宏观强顺风"
    if score >= Decimal("65"):
        return "宏观偏顺风"
    if score >= Decimal("50"):
        return "中性偏观察"
    if score >= Decimal("35"):
        return "宏观偏逆风"
    return "宏观强逆风"


def calculate_macro_score(factor_scores: Mapping[str, Decimal | int | str]) -> MacroScore:
    """Calculate total score, normalized score, and macro state.

    Unit: raw score ranges from -12 to +12; normalized score ranges from 0 to
    100.
    """

    scores = dict(factor_scores)
    if "risk" not in scores and "risk_appetite" in scores:
        scores["risk"] = scores["risk_appetite"]

    parsed = {
        factor: parse_factor_score(scores[factor], factor)
        for factor in FACTOR_LABELS
    }
    total = sum(parsed.values(), Decimal("0"))
    normalized = ((total - RAW_SCORE_MIN) / RAW_SCORE_RANGE * Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    return MacroScore(
        factor_scores=parsed,
        total_score=total,
        normalized_score=normalized,
        macro_state=classify_macro_state(normalized),
    )


def format_macro_score_table(score: MacroScore) -> str:
    """Render macro scores as a Markdown table."""

    lines = ["| Factor | Score |", "|---|---:|"]
    for factor, label in FACTOR_LABELS.items():
        lines.append(f"| {label} | {format_decimal(score.factor_scores[factor])} |")
    lines.extend(
        [
            "",
            f"Total score: {format_decimal(score.total_score)}",
            f"Normalized score: {format_decimal(score.normalized_score)}",
            f"Macro state: {score.macro_state}",
            "",
            "> Research score only. This is not financial advice and not a buy/sell signal.",
        ]
    )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate a macro six-factor score.")
    parser.add_argument("--growth", required=True, help="Growth score, -2 to 2")
    parser.add_argument("--inflation", required=True, help="Inflation score, -2 to 2")
    parser.add_argument("--liquidity", required=True, help="Liquidity score, -2 to 2")
    parser.add_argument("--credit", required=True, help="Credit score, -2 to 2")
    parser.add_argument("--earnings", required=True, help="Earnings score, -2 to 2")
    parser.add_argument("--risk", "--risk-appetite", dest="risk", required=True, help="Risk appetite score, -2 to 2")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    score = calculate_macro_score(
        {
            "growth": args.growth,
            "inflation": args.inflation,
            "liquidity": args.liquidity,
            "credit": args.credit,
            "earnings": args.earnings,
            "risk": args.risk,
        }
    )
    print(format_macro_score_table(score))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
