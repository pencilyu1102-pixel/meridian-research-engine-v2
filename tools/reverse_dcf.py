#!/usr/bin/env python3
"""Reverse DCF Calculator — reverse-engineer what current market cap implies about growth.

Solves for the implied revenue CAGR (when --fcf-margin is given) or implied FCF
Margin (when --cagr is given) such that the Net Present Value (NPV) of projected
free cash flows equals the current Enterprise Value.

Enterprise Value = Market Cap — Net Cash

The model projects:
  - Revenue growing at CAGR over N forecast years
  - FCF = Revenue × FCF Margin
  - Terminal Value via Gordon Growth Model:
      TV = Final FCF × (1 + g) / (r — g)

Usage:
  # Solve for implied Revenue CAGR (need --fcf-margin):
  python reverse_dcf.py \
    --market-cap 100000 --net-cash 5000 \
    --revenue 20000 --fcf-margin 0.20 \
    --terminal-growth 0.03 --discount-rate 0.10 --forecast-years 5

  # Solve for implied FCF Margin (need --cagr):
  python reverse_dcf.py \
    --market-cap 100000 --net-cash 5000 \
    --revenue 20000 --cagr 0.15 \
    --terminal-growth 0.03 --discount-rate 0.10 --forecast-years 5

  # Compare against reported assumptions:
  python reverse_dcf.py \
    --market-cap 100000 --net-cash 5000 \
    --revenue 20000 --fcf-margin 0.20 \
    --reported-cagr 0.12 --reported-fcf-margin 0.18
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional


# ── Helpers ──────────────────────────────────────────────────────────


def fmt_pct(value: float) -> str:
    """Format a decimal ratio as a percentage string."""
    return f"{value * 100:.2f}%"


def fmt_billion(value: float) -> str:
    """Format a value in millions/billions for display.

    Values ≥ 1000 are shown in billions; smaller values in millions.
    """
    if abs(value) >= 1000:
        return f"${value / 1000:,.2f}B"
    return f"${value:,.2f}M"


# ── Core DCF model ───────────────────────────────────────────────────


def project_fcf_npv(
    revenue: float,
    cagr: float,
    fcf_margin: float,
    discount_rate: float,
    terminal_growth: float,
    forecast_years: int,
) -> tuple[float, float, float, list[float]]:
    """Compute the NPV of projected FCFs plus terminal value.

    Args:
        revenue: Current (LTM) revenue.
        cagr: Projected revenue CAGR (decimal).
        fcf_margin: Free Cash Flow margin (decimal).
        discount_rate: Discount rate / WACC (decimal).
        terminal_growth: Perpetuity growth rate (decimal).
        forecast_years: Number of explicit forecast years.

    Returns:
        (total_npv, fcf_npv, tv_npv, yearly_fcfs)
    """
    yearly_fcfs: list[float] = []
    fcf_npv = 0.0

    for t in range(1, forecast_years + 1):
        rev_t = revenue * (1.0 + cagr) ** t
        fcf_t = rev_t * fcf_margin
        yearly_fcfs.append(fcf_t)
        fcf_npv += fcf_t / (1.0 + discount_rate) ** t

    # Terminal value via Gordon Growth Model
    final_fcf = yearly_fcfs[-1]
    tv = final_fcf * (1.0 + terminal_growth) / (discount_rate - terminal_growth)
    tv_npv = tv / (1.0 + discount_rate) ** forecast_years

    return fcf_npv + tv_npv, fcf_npv, tv_npv, yearly_fcfs


# ── Solvers ──────────────────────────────────────────────────────────


def solve_cagr(
    ev: float,
    revenue: float,
    fcf_margin: float,
    discount_rate: float,
    terminal_growth: float,
    forecast_years: int,
) -> Optional[float]:
    """Solve for the revenue CAGR that equates NPV to Enterprise Value.

    Uses binary search over [-50%, +99%]. Returns None when the target EV
    is outside the achievable NPV range.
    """
    lo, hi = -0.50, 0.99  # —50% … +99% CAGR

    npv_lo, _, _, _ = project_fcf_npv(
        revenue, lo, fcf_margin, discount_rate, terminal_growth, forecast_years
    )
    npv_hi, _, _, _ = project_fcf_npv(
        revenue, hi, fcf_margin, discount_rate, terminal_growth, forecast_years
    )

    if ev < npv_lo or ev > npv_hi:
        return None  # Outside solvable range

    for _ in range(200):  # Enough for ~1e-12 precision
        mid = (lo + hi) / 2.0
        npv_mid, _, _, _ = project_fcf_npv(
            revenue, mid, fcf_margin, discount_rate, terminal_growth, forecast_years
        )
        if abs(npv_mid - ev) < 0.01:  # Within $10K
            return mid
        if npv_mid < ev:
            lo = mid  # Need higher growth → raise floor
        else:
            hi = mid  # Need lower growth → lower ceiling

    return (lo + hi) / 2.0


def solve_fcf_margin(
    ev: float,
    revenue: float,
    cagr: float,
    discount_rate: float,
    terminal_growth: float,
    forecast_years: int,
) -> float:
    """Solve for the FCF Margin analytically.

    Because FCF scales linearly with margin, this is a closed-form
    solution: margin = EV / (sum of discounted revenue contributions).
    """
    # Sum of discounted revenues for the explicit forecast period
    sum_disc_rev = 0.0
    for t in range(1, forecast_years + 1):
        rev_t = revenue * (1.0 + cagr) ** t
        sum_disc_rev += rev_t / (1.0 + discount_rate) ** t

    # Discounted terminal revenue contribution
    final_rev = revenue * (1.0 + cagr) ** forecast_years
    tv_factor = final_rev * (1.0 + terminal_growth) / (discount_rate - terminal_growth)
    disc_tv = tv_factor / (1.0 + discount_rate) ** forecast_years

    total_factor = sum_disc_rev + disc_tv
    if total_factor == 0.0:
        return 0.0
    return ev / total_factor


# ── Output builder ───────────────────────────────────────────────────


def build_output(
    market_cap: float,
    net_cash: float,
    revenue: float,
    ev: float,
    implied_cagr: Optional[float],
    implied_fcf_margin: Optional[float],
    terminal_growth: float,
    forecast_years: int,
    discount_rate: float,
    reported_cagr: Optional[float],
    reported_fcf_margin: Optional[float],
    cagr_note: Optional[str],
    margin_note: Optional[str],
) -> str:
    """Build the full Markdown output table."""
    lines = [
        "## Reverse DCF Analysis",
        "",
        "### Input Parameters",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        f"| Market Cap | {fmt_billion(market_cap)} |",
        f"| Net Cash (—Debt) | {fmt_billion(net_cash)} |",
        f"| Enterprise Value (EV) | {fmt_billion(ev)} |",
        f"| Current Revenue (LTM) | {fmt_billion(revenue)} |",
        f"| Forecast Period | {forecast_years} years |",
        f"| Discount Rate (WACC) | {fmt_pct(discount_rate)} |",
        f"| Terminal Growth Rate | {fmt_pct(terminal_growth)} |",
        "",
    ]

    # ── Market-Implied Results ────────────────────────────────────
    lines.append("### Market-Implied Results")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")

    # Implied Revenue CAGR
    if implied_cagr is not None:
        lines.append(f"| **当前市值隐含收入 CAGR** | **{fmt_pct(implied_cagr)}** |")
    elif cagr_note:
        lines.append(f"| 当前市值隐含收入 CAGR | {cagr_note} |")

    # Implied FCF Margin
    if implied_fcf_margin is not None:
        lines.append(f"| **当前市值隐含 FCF Margin** | **{fmt_pct(implied_fcf_margin)}** |")
    elif margin_note:
        lines.append(f"| 当前市值隐含 FCF Margin | {margin_note} |")

    # Terminal Revenue Scale
    if implied_cagr is not None:
        terminal_rev = revenue * (1.0 + implied_cagr) ** forecast_years
        lines.append(
            f"| **当前市值隐含终局规模** "
            f"| **{fmt_billion(terminal_rev)}** "
            f"（Year {forecast_years} Revenue） |"
        )
    elif implied_fcf_margin is not None and reported_cagr is not None:
        terminal_rev = revenue * (1.0 + reported_cagr) ** forecast_years
        lines.append(
            f"| 当前市值隐含终局规模 "
            f"| {fmt_billion(terminal_rev)} "
            f"（Year {forecast_years} Revenue, using reported CAGR） |"
        )

    # Valuation Multiple
    if ev > 0.0 and revenue > 0.0:
        lines.append(f"| **当前市值隐含估值倍数** | **{ev / revenue:.2f}x** （EV / Revenue） |")

    # ── Assumption Comparison ─────────────────────────────────────
    diffs: list[str] = []
    if reported_cagr is not None and implied_cagr is not None:
        diff = implied_cagr - reported_cagr
        direction = "高于" if diff > 1e-9 else ("低于" if diff < -1e-9 else "持平")
        diffs.append(
            f"| 收入 CAGR | 市场隐含 {fmt_pct(implied_cagr)} "
            f"| 报告假设 {fmt_pct(reported_cagr)} "
            f"| {direction} {fmt_pct(abs(diff)) if abs(diff) > 1e-9 else ''}|"
        )
    if reported_fcf_margin is not None and implied_fcf_margin is not None:
        diff = implied_fcf_margin - reported_fcf_margin
        direction = "高于" if diff > 1e-9 else ("低于" if diff < -1e-9 else "持平")
        diffs.append(
            f"| FCF Margin | 市场隐含 {fmt_pct(implied_fcf_margin)} "
            f"| 报告假设 {fmt_pct(reported_fcf_margin)} "
            f"| {direction} {fmt_pct(abs(diff)) if abs(diff) > 1e-9 else ''}|"
        )

    if diffs:
        lines.append("")
        lines.append("### 报告假设与市场隐含假设的差异")
        lines.append("")
        lines.append("| 指标 | 市场隐含值 | 报告假设值 | 差异 |")
        lines.append("|------|-----------|-----------|------|")
        lines.extend(diffs)

    lines.append("")
    return "\n".join(lines)


# ── Entry point ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Reverse DCF Calculator — reverse-engineer what current market cap "
            "implies about growth. Solves for implied revenue CAGR (when "
            "--fcf-margin is given) or implied FCF Margin (when --cagr is given)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Solve for implied Revenue CAGR (need --fcf-margin):\n"
            "  python reverse_dcf.py --market-cap 100000 --net-cash 5000 \\\n"
            "    --revenue 20000 --fcf-margin 0.20 \\\n"
            "    --terminal-growth 0.03 --discount-rate 0.10 --forecast-years 5\n"
            "\n"
            "  # Solve for implied FCF Margin (need --cagr):\n"
            "  python reverse_dcf.py --market-cap 100000 --net-cash 5000 \\\n"
            "    --revenue 20000 --cagr 0.15 \\\n"
            "    --terminal-growth 0.03 --discount-rate 0.10 --forecast-years 5\n"
            "\n"
            "  # With reported assumptions for comparison:\n"
            "  python reverse_dcf.py --market-cap 100000 --net-cash 5000 \\\n"
            "    --revenue 20000 --fcf-margin 0.20 \\\n"
            "    --reported-cagr 0.12 --reported-fcf-margin 0.18\n"
        ),
    )

    # ── Required input parameters ────────────────────────────────
    parser.add_argument(
        "--market-cap",
        type=float,
        required=True,
        help="Current market capitalization (same units as --revenue and --net-cash)",
    )
    parser.add_argument(
        "--net-cash",
        type=float,
        required=True,
        help=(
            "Net cash = Cash & equivalents − Total debt. "
            "Positive = net cash; negative = net debt."
        ),
    )
    parser.add_argument(
        "--revenue",
        type=float,
        required=True,
        help="Current (LTM) revenue (same units as --market-cap)",
    )

    # ── Assumptions (one of these must be provided) ───────────────
    parser.add_argument(
        "--fcf-margin",
        type=float,
        default=None,
        help=(
            "Assumed FCF margin as decimal (e.g. 0.20 for 20%%). "
            "Required when --cagr is not given.  The tool solves for "
            "the CAGR that makes NPV = EV."
        ),
    )
    parser.add_argument(
        "--cagr",
        type=float,
        default=None,
        help=(
            "Assumed revenue CAGR as decimal (e.g. 0.15 for 15%%). "
            "Required when --fcf-margin is not given.  The tool solves "
            "for the FCF Margin that makes NPV = EV."
        ),
    )

    # ── Model parameters ──────────────────────────────────────────
    parser.add_argument(
        "--terminal-growth",
        type=float,
        default=0.03,
        help="Terminal (perpetuity) growth rate (default: 0.03)",
    )
    parser.add_argument(
        "--discount-rate",
        type=float,
        default=0.10,
        help="Discount rate / WACC (default: 0.10)",
    )
    parser.add_argument(
        "--forecast-years",
        type=int,
        default=5,
        help="Number of explicit forecast years (default: 5)",
    )

    # ── Comparison (optional) ─────────────────────────────────────
    parser.add_argument(
        "--reported-cagr",
        type=float,
        default=None,
        help=(
            "Reported / assumed CAGR for comparison "
            "(e.g. company guidance of 0.12 for 12%%)"
        ),
    )
    parser.add_argument(
        "--reported-fcf-margin",
        type=float,
        default=None,
        help=(
            "Reported / assumed FCF margin for comparison "
            "(e.g. 0.20 for 20%%)"
        ),
    )

    args = parser.parse_args()

    # ── Validation ────────────────────────────────────────────────
    if args.fcf_margin is None and args.cagr is None:
        print(
            "Error: Either --fcf-margin or --cagr must be provided.\n"
            "  --fcf-margin: Solve for implied CAGR\n"
            "  --cagr:       Solve for implied FCF Margin\n"
            "Use --help for details.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.discount_rate <= args.terminal_growth:
        print(
            f"Error: Discount rate ({fmt_pct(args.discount_rate)}) must be greater "
            f"than terminal growth rate ({fmt_pct(args.terminal_growth)}).",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.forecast_years < 1:
        print("Error: --forecast-years must be at least 1.", file=sys.stderr)
        sys.exit(1)

    if args.revenue <= 0.0:
        print("Error: --revenue must be positive.", file=sys.stderr)
        sys.exit(1)

    # Enterprise Value = Market Cap − Net Cash
    ev = args.market_cap - args.net_cash

    if ev <= 0.0:
        print(
            f"Warning: Enterprise Value = {fmt_billion(ev)} — "
            f"non-positive EV may indicate net cash exceeds market cap.",
            file=sys.stderr,
        )

    # ── Solve ──────────────────────────────────────────────────────
    implied_cagr: Optional[float] = None
    implied_fcf_margin: Optional[float] = None
    cagr_note: Optional[str] = None
    margin_note: Optional[str] = None

    if args.fcf_margin is not None:
        # ── Mode 1: solve for implied CAGR ────────────────────────
        if args.fcf_margin <= 0.0 or args.fcf_margin >= 1.0:
            print(
                f"Warning: FCF margin of {fmt_pct(args.fcf_margin)} seems unusual.",
                file=sys.stderr,
            )

        ans = solve_cagr(
            ev,
            args.revenue,
            args.fcf_margin,
            args.discount_rate,
            args.terminal_growth,
            args.forecast_years,
        )
        if ans is None:
            cagr_note = (
                "无法求解——市值对应的增长率超出可解范围"
                "（<-50% 或 >99%），请检查输入数值"
            )
        else:
            implied_cagr = ans

        # If user also passed --cagr (for dual display), compute the
        # margin implied by THAT CAGR alongside the CAGR result.
        if args.cagr is not None:
            implied_fcf_margin = solve_fcf_margin(
                ev,
                args.revenue,
                args.cagr,
                args.discount_rate,
                args.terminal_growth,
                args.forecast_years,
            )

    elif args.cagr is not None:
        # ── Mode 2: solve for implied FCF Margin ──────────────────
        if args.cagr <= -1.0 or args.cagr >= 2.0:
            print(
                f"Warning: CAGR of {fmt_pct(args.cagr)} seems unusual.",
                file=sys.stderr,
            )

        implied_fcf_margin = solve_fcf_margin(
            ev,
            args.revenue,
            args.cagr,
            args.discount_rate,
            args.terminal_growth,
            args.forecast_years,
        )

    # ── Output ──────────────────────────────────────────────────────
    output = build_output(
        args.market_cap,
        args.net_cash,
        args.revenue,
        ev,
        implied_cagr,
        implied_fcf_margin,
        args.terminal_growth,
        args.forecast_years,
        args.discount_rate,
        args.reported_cagr,
        args.reported_fcf_margin,
        cagr_note,
        margin_note,
    )
    print(output)


if __name__ == "__main__":
    main()
