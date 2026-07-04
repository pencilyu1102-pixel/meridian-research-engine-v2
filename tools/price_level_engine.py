"""Price Level Engine CLI.

The engine builds valuation anchor tables from normalized EPS and valuation
multiples. It is a research map, not a buy/sell signal system.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Sequence

try:
    from .financial_rigor import calculate_price_from_multiple, format_decimal, to_decimal
except ImportError:  # pragma: no cover - allows direct CLI execution
    from financial_rigor import calculate_price_from_multiple, format_decimal, to_decimal


DEFAULT_MULTIPLES: tuple[str, ...] = (
    "16.0",
    "16.5",
    "17.0",
    "17.5",
    "18.0",
    "18.5",
    "19.0",
    "19.5",
    "20.0",
    "21.0",
    "22.0",
    "23.0",
)


@dataclass(frozen=True)
class ValuationAnchor:
    """One valuation multiple and its implied price."""

    multiple: Decimal
    price: Decimal


def parse_multiples(raw: str | Sequence[str] | None = None) -> tuple[Decimal, ...]:
    """Parse comma-separated valuation multiples into Decimal values."""

    values: Iterable[str]
    if raw is None:
        values = DEFAULT_MULTIPLES
    elif isinstance(raw, str):
        values = [part.strip() for part in raw.split(",") if part.strip()]
    else:
        values = raw

    multiples = tuple(to_decimal(value, "multiple") for value in values)
    if not multiples:
        raise ValueError("at least one multiple is required")
    return multiples


def build_valuation_anchor_table(
    normalized_eps: Decimal | int | str,
    multiples: Iterable[Decimal | int | str] | None = None,
) -> list[ValuationAnchor]:
    """Build valuation anchors from normalized EPS and multiples."""

    eps = to_decimal(normalized_eps, "normalized_eps")
    parsed_multiples = tuple(to_decimal(multiple, "multiple") for multiple in (multiples or parse_multiples()))
    return [
        ValuationAnchor(multiple=multiple, price=calculate_price_from_multiple(eps, multiple))
        for multiple in parsed_multiples
    ]


def format_multiple(multiple: Decimal) -> str:
    """Format a valuation multiple with at least one decimal place."""

    return f"{multiple.quantize(Decimal('0.0'))}x"


def format_anchor_table(anchors: Iterable[ValuationAnchor]) -> str:
    """Render valuation anchors as a Markdown table."""

    lines = ["| Multiple | Implied Price |", "|---:|---:|"]
    for anchor in anchors:
        lines.append(f"| {format_multiple(anchor.multiple)} | {format_decimal(anchor.price)} |")
    return "\n".join(lines)


def render_price_level_report(
    ticker: str,
    normalized_eps: Decimal | int | str,
    multiples: Iterable[Decimal | int | str] | None = None,
) -> str:
    """Render a Markdown report for the Price Level Engine."""

    eps = to_decimal(normalized_eps, "normalized_eps")
    anchors = build_valuation_anchor_table(eps, multiples)
    return "\n".join(
        [
            f"Ticker: {ticker.upper()}",
            f"Normalized EPS: {eps}",
            "",
            "## Valuation Anchor Table",
            "",
            format_anchor_table(anchors),
            "",
            "> Research map only. This is not financial advice and not a buy/sell signal.",
        ]
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a valuation anchor table from normalized EPS.")
    parser.add_argument("--eps", required=True, help="Normalized EPS, for example 10.00")
    parser.add_argument("--ticker", default="TICKER", help="Ticker symbol")
    parser.add_argument(
        "--multiples",
        help="Comma-separated valuation multiples, for example 16,16.5,17,18,19,20,22",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    multiples = parse_multiples(args.multiples) if args.multiples else parse_multiples()
    print(render_price_level_report(args.ticker, args.eps, multiples))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
