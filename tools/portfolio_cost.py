"""Portfolio cost calculator.

Input CSV fields:
date,ticker,action,shares,price,fee
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Sequence

try:
    from .financial_rigor import format_decimal, to_decimal
except ImportError:  # pragma: no cover - allows direct CLI execution
    from financial_rigor import format_decimal, to_decimal


@dataclass(frozen=True)
class PortfolioCost:
    ticker: str
    total_bought_shares: Decimal
    total_sold_shares: Decimal
    remaining_shares: Decimal
    gross_buy_amount: Decimal
    gross_sell_amount: Decimal
    total_fees: Decimal
    net_invested_capital: Decimal
    management_cost_per_share: Decimal | None


def calculate_portfolio_cost_from_rows(rows: Iterable[dict[str, str]], ticker: str | None = None) -> PortfolioCost:
    """Calculate remaining shares and management cost from transaction rows."""

    selected_ticker = ticker.upper() if ticker else None
    total_bought_shares = Decimal("0")
    total_sold_shares = Decimal("0")
    gross_buy_amount = Decimal("0")
    gross_sell_amount = Decimal("0")
    total_fees = Decimal("0")
    output_ticker: str | None = selected_ticker
    matched_rows = 0

    for row in rows:
        row_ticker = row["ticker"].upper()
        if selected_ticker and row_ticker != selected_ticker:
            continue
        matched_rows += 1
        output_ticker = output_ticker or row_ticker
        action = row["action"].upper()
        shares = to_decimal(row["shares"], "shares")
        price = to_decimal(row["price"], "price")
        fee = to_decimal(row.get("fee", "0"), "fee")
        amount = shares * price
        total_fees += fee

        if action == "BUY":
            total_bought_shares += shares
            gross_buy_amount += amount
        elif action == "SELL":
            total_sold_shares += shares
            gross_sell_amount += amount
        else:
            raise ValueError(f"unsupported action: {action}")

    if matched_rows == 0:
        raise ValueError("no matching transactions found")

    remaining_shares = total_bought_shares - total_sold_shares
    net_invested_capital = gross_buy_amount - gross_sell_amount + total_fees
    management_cost_per_share = None
    if remaining_shares != 0:
        management_cost_per_share = net_invested_capital / remaining_shares

    return PortfolioCost(
        ticker=output_ticker or "UNKNOWN",
        total_bought_shares=total_bought_shares,
        total_sold_shares=total_sold_shares,
        remaining_shares=remaining_shares,
        gross_buy_amount=gross_buy_amount,
        gross_sell_amount=gross_sell_amount,
        total_fees=total_fees,
        net_invested_capital=net_invested_capital,
        management_cost_per_share=management_cost_per_share,
    )


def calculate_portfolio_cost(csv_path: str | Path, ticker: str | None = None) -> PortfolioCost:
    """Load a transaction CSV and calculate portfolio cost."""

    with Path(csv_path).open(newline="", encoding="utf-8") as csv_file:
        return calculate_portfolio_cost_from_rows(csv.DictReader(csv_file), ticker=ticker)


def _format_shares(value: Decimal) -> str:
    normalized = value.normalize()
    return format(normalized, "f")


def format_portfolio_cost_table(cost: PortfolioCost) -> str:
    """Render portfolio cost as a Markdown table."""

    rows = [
        ("ticker", cost.ticker),
        ("total_bought_shares", _format_shares(cost.total_bought_shares)),
        ("total_sold_shares", _format_shares(cost.total_sold_shares)),
        ("remaining_shares", _format_shares(cost.remaining_shares)),
        ("gross_buy_amount", format_decimal(cost.gross_buy_amount)),
        ("gross_sell_amount", format_decimal(cost.gross_sell_amount)),
        ("total_fees", format_decimal(cost.total_fees)),
        ("net_invested_capital", format_decimal(cost.net_invested_capital)),
        (
            "management_cost_per_share",
            "N/A" if cost.management_cost_per_share is None else format_decimal(cost.management_cost_per_share),
        ),
    ]
    lines = ["| Field | Value |", "|---|---:|"]
    lines.extend(f"| {field} | {value} |" for field, value in rows)
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate portfolio management cost from transaction CSV.")
    parser.add_argument("csv_path", help="Path to transactions CSV")
    parser.add_argument("--ticker", help="Ticker filter, for example ABC")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    cost = calculate_portfolio_cost(args.csv_path, ticker=args.ticker)
    print(format_portfolio_cost_table(cost))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
