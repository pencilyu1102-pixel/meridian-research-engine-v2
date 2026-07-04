#!/usr/bin/env python3
"""ROIC and ROE Calculator — CLI tool for financial metrics.

Computes:
  ROIC = NOPAT / Average Invested Capital
    NOPAT           = EBIT × (1 - tax_rate)
    Invested Capital = Total Debt + Total Equity - Cash
  ROE  = Net Income / Average Shareholders' Equity

Usage:
  python roic_roe_calculator.py \\
    --ebit 1000 --tax-rate 0.21 \\
    --total-debt 5000 --total-equity 8000 --cash 200 \\
    --net-income 600 --equity-start 7500 --equity-end 8500
"""

from __future__ import annotations

import argparse
import sys


def build_markdown_table(
    roic: str | None,
    roe: str | None,
    roic_note: str | None,
    roe_note: str | None,
) -> str:
    """Render results as a Markdown table."""
    lines = [
        "| Metric | Result |",
        "|--------|--------|",
    ]

    if roic is not None:
        lines.append(f"| ROIC | {roic} |")
    elif roic_note:
        lines.append(f"| ROIC | {roic_note} |")

    if roe is not None:
        lines.append(f"| ROE | {roe} |")
    elif roe_note:
        lines.append(f"| ROE | {roe_note} |")

    return "\n".join(lines)


def fmt_pct(value: float) -> str:
    """Format a decimal ratio as a percentage string."""
    return f"{value * 100:.2f}%"


def _require_roic_fields(args: argparse.Namespace) -> tuple[float, float, float, float, float]:
    """Return (ebit, tax_rate, total_debt, total_equity, cash) or raise."""
    missing: list[str] = []
    if args.ebit is None:
        missing.append("EBIT")
    if args.tax_rate is None:
        missing.append("tax_rate")
    if args.total_debt is None:
        missing.append("total_debt")
    if args.total_equity is None:
        missing.append("total_equity")
    if args.cash is None:
        missing.append("cash")
    if missing:
        raise ValueError(f"无法计算完整 ROIC，原因：缺少 {', '.join(missing)}")
    # All guaranteed non-None after the check
    assert args.ebit is not None
    assert args.tax_rate is not None
    assert args.total_debt is not None
    assert args.total_equity is not None
    assert args.cash is not None
    return (args.ebit, args.tax_rate, args.total_debt, args.total_equity, args.cash)


def _require_roe_fields(args: argparse.Namespace) -> tuple[float, float, float]:
    """Return (net_income, equity_start, equity_end) or raise."""
    missing: list[str] = []
    if args.net_income is None:
        missing.append("net_income")
    if args.equity_start is None:
        missing.append("equity_start")
    if args.equity_end is None:
        missing.append("equity_end")
    if missing:
        raise ValueError(f"无法计算完整 ROE，原因：缺少 {', '.join(missing)}")
    assert args.net_income is not None
    assert args.equity_start is not None
    assert args.equity_end is not None
    return (args.net_income, args.equity_start, args.equity_end)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate ROIC (Return on Invested Capital) and "
        "ROE (Return on Equity).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python roic_roe_calculator.py --ebit 1000 --tax-rate 0.21 "
            "--total-debt 5000 --total-equity 8000 --cash 200\n"
            "  python roic_roe_calculator.py --net-income 600 "
            "--equity-start 7500 --equity-end 8500\n"
        ),
    )

    parser.add_argument("--ebit", type=float, help="Earnings Before Interest & Taxes")
    parser.add_argument("--tax-rate", type=float, help="Effective tax rate (e.g. 0.21)")
    parser.add_argument("--total-debt", type=float, help="Total debt outstanding")
    parser.add_argument("--total-equity", type=float, help="Total shareholders' equity")
    parser.add_argument("--cash", type=float, help="Cash & cash equivalents")
    parser.add_argument("--net-income", type=float, help="Net income (Net Profit)")
    parser.add_argument(
        "--equity-start", type=float, help="Shareholders' equity at start of period"
    )
    parser.add_argument(
        "--equity-end", type=float, help="Shareholders' equity at end of period"
    )

    args = parser.parse_args()

    # ── ROIC ────────────────────────────────────────────────────────
    roic_str: str | None = None
    roic_note: str | None = None

    try:
        ebit, tax_rate, total_debt, total_equity, cash = _require_roic_fields(args)
        nopat = ebit * (1.0 - tax_rate)
        invested_capital = total_debt + total_equity - cash
        if invested_capital == 0.0:
            roic_note = "无法计算完整 ROIC，原因：Invested Capital 为零"
        else:
            roic_str = fmt_pct(nopat / invested_capital)
    except ValueError as exc:
        roic_note = str(exc)

    # ── ROE ─────────────────────────────────────────────────────────
    roe_str: str | None = None
    roe_note: str | None = None

    try:
        net_income, equity_start, equity_end = _require_roe_fields(args)
        avg_equity = (equity_start + equity_end) / 2.0
        if avg_equity == 0.0:
            roe_note = "无法计算完整 ROE，原因：平均股东权益为零"
        else:
            roe_str = fmt_pct(net_income / avg_equity)
    except ValueError as exc:
        roe_note = str(exc)

    # ── Output ──────────────────────────────────────────────────────
    output = build_markdown_table(roic_str, roe_str, roic_note, roe_note)
    print(output)


if __name__ == "__main__":
    main()
