#!/usr/bin/env python3
"""Cash Flow Driver — CLI tool for decomposing and assessing cash flow components.

Decomposes:
  OCF, CapEx, Working Capital changes (receivables, inventory, prepayments),
  FCF, FCF Margin, FCF Conversion.

Displays a Markdown table with columns:
  项目 | 当前值 | 对现金流影响 | 判断

Usage:
  python cash_flow_driver.py \
    --ocf 1500 --capex -800 \
    --receivables-change 200 --inventory-change -50 --prepayments-change 30 \
    --revenue 10000 --net-income 600
"""

from __future__ import annotations

import argparse
import sys


# ── Helpers ──────────────────────────────────────────────────────────────


def fmt_num(value: float) -> str:
    """Format a number with thousand separators and 2 decimal places."""
    sign = "-" if value < 0 else ""
    v = abs(value)
    return f"{sign}{v:,.2f}"


def fmt_pct(value: float) -> str:
    """Format a decimal ratio as a percentage string."""
    return f"{value * 100:.2f}%"


def judge_sign(value: float, *, invert: bool = False) -> str:
    """Determine 判断 (judgment) based on sign.

    invert=True : a negative value is considered positive for cash flow
                  (e.g. a decrease in receivables frees up cash).
    """
    effective = -value if invert else value
    if effective > 0:
        return "正面"
    if effective < 0:
        return "负面"
    return "中性"


def impact_tag(inflow: bool) -> str:
    """Short label for cash-flow impact direction."""
    return "现金流入 ▲" if inflow else "现金流出 ▼"


# ── Row builder ──────────────────────────────────────────────────────────


def _row(
    name: str,
    raw_value: float | None,
    impact: str,
    judgment: str,
) -> str:
    val = fmt_num(raw_value) if raw_value is not None else "—"
    return f"| {name} | {val} | {impact} | {judgment} |"


def build_table(
    ocf: float | None,
    capex: float | None,
    receivables_change: float | None,
    inventory_change: float | None,
    prepayments_change: float | None,
    revenue: float | None,
    net_income: float | None,
) -> str:
    """Build the Markdown table."""
    lines = [
        "| 项目 | 当前值 | 对现金流影响 | 判断 |",
        "|------|--------|-------------|------|",
    ]

    # ── OCF ──────────────────────────────────────────────────────────
    if ocf is not None:
        lines.append(_row("经营活动现金流 (OCF)", ocf, impact_tag(ocf >= 0), judge_sign(ocf)))

    # ── CapEx ────────────────────────────────────────────────────────
    if capex is not None:
        # CapEx is typically negative (cash outflow). A more negative Capex
        # means more investment → more cash outflow.
        lines.append(_row("资本支出 (CapEx)", capex, impact_tag(capex >= 0), judge_sign(capex)))

    # ── Working capital changes ──────────────────────────────────────
    # Positive change = more cash tied up (bad for cash flow)
    # Negative change = cash freed up (good for cash flow)
    if receivables_change is not None:
        inflow = receivables_change <= 0  # decrease → cash in
        lines.append(
            _row(
                "应收账款变动 (Receivables)",
                receivables_change,
                impact_tag(inflow),
                judge_sign(receivables_change, invert=True),
            )
        )

    if inventory_change is not None:
        inflow = inventory_change <= 0
        lines.append(
            _row(
                "存货变动 (Inventory)",
                inventory_change,
                impact_tag(inflow),
                judge_sign(inventory_change, invert=True),
            )
        )

    if prepayments_change is not None:
        inflow = prepayments_change <= 0
        lines.append(
            _row(
                "预付款项变动 (Prepayments)",
                prepayments_change,
                impact_tag(inflow),
                judge_sign(prepayments_change, invert=True),
            )
        )

    # ── FCF ──────────────────────────────────────────────────────────
    if ocf is not None and capex is not None:
        fcf = ocf + capex  # capex is negative, so OCF + (-abs) = OCF - abs
        lines.append(_row("自由现金流 (FCF)", fcf, impact_tag(fcf >= 0), judge_sign(fcf)))

        # ── FCF Margin ──────────────────────────────────────────────
        if revenue is not None and revenue != 0:
            fcf_margin = fcf / revenue
            lines.append(
                _row("FCF 利润率 (FCF Margin)", fcf_margin, impact_tag(fcf_margin >= 0), judge_sign(fcf_margin))
            )
        elif revenue is not None:
            lines.append("| FCF 利润率 (FCF Margin) | — (营收为零) | — | — |")

        # ── FCF Conversion ──────────────────────────────────────────
        if net_income is not None and net_income != 0:
            fcf_conversion = fcf / net_income
            # Judgment for FCF Conversion:
            #  > 1   → 正面 (generates more FCF than net income)
            #  0~1  → 中性 (positive but less than net income)
            #  < 0  → 需关注 (FCF negative while net income positive, or vice versa)
            if fcf_conversion > 1:
                conv_judgment = "正面"
            elif fcf_conversion >= 0:
                conv_judgment = "中性"
            else:
                conv_judgment = "需关注"
            lines.append(
                _row("FCF 转化率 (FCF Conversion)", fcf_conversion, impact_tag(fcf_conversion >= 0), conv_judgment)
            )
        elif net_income is not None:
            lines.append("| FCF 转化率 (FCF Conversion) | — (净利润为零) | — | — |")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="现金流动分解工具 — 分析 OCF、CapEx、营运资本变动与 FCF。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python cash_flow_driver.py --ocf 1500 --capex -800 \\\n"
            "    --receivables-change 200 --inventory-change -50 \\\n"
            "    --prepayments-change 30 --revenue 10000 --net-income 600\n"
            "\n"
            "注意:\n"
            "  CapEx 通常为负值（现金流出）。\n"
            "  应收 / 存货 / 预付款变动：正值=增加(资金占用)，负值=减少(资金释放)。\n"
        ),
    )

    parser.add_argument(
        "--ocf", type=float, help="经营活动现金流 (Operating Cash Flow)"
    )
    parser.add_argument(
        "--capex", type=float, help="资本支出 (Capital Expenditure，通常为负值)"
    )
    parser.add_argument(
        "--receivables-change",
        type=float,
        help="应收账款变动 (正=增加，负=减少)",
    )
    parser.add_argument(
        "--inventory-change",
        type=float,
        help="存货变动 (正=增加，负=减少)",
    )
    parser.add_argument(
        "--prepayments-change",
        type=float,
        help="预付款项变动 (正=增加，负=减少)",
    )
    parser.add_argument("--revenue", type=float, help="营业收入 (Revenue)")
    parser.add_argument(
        "--net-income", type=float, help="净利润 (Net Income)"
    )

    args = parser.parse_args()

    # Validate at least one useful argument
    provided = {
        k: v
        for k, v in {
            "OCF": args.ocf,
            "CapEx": args.capex,
            "Receivables Change": args.receivables_change,
            "Inventory Change": args.inventory_change,
            "Prepayments Change": args.prepayments_change,
            "Revenue": args.revenue,
            "Net Income": args.net_income,
        }.items()
        if v is not None
    }
    if not provided:
        parser.print_help()
        sys.exit(1)

    output = build_table(
        ocf=args.ocf,
        capex=args.capex,
        receivables_change=args.receivables_change,
        inventory_change=args.inventory_change,
        prepayments_change=args.prepayments_change,
        revenue=args.revenue,
        net_income=args.net_income,
    )
    print(output)


if __name__ == "__main__":
    main()
