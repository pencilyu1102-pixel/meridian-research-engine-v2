"""Decimal-based financial calculation helpers.

All core calculations use :class:`decimal.Decimal`. Passing floats is rejected
because binary floating-point values can silently introduce financial rounding
noise.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable


MONEY_QUANT = Decimal("0.01")
RATIO_QUANT = Decimal("0.0001")


def to_decimal(value: Decimal | int | str, field_name: str = "value") -> Decimal:
    """Convert a string, integer, or Decimal into Decimal.

    Unit: preserves the unit of the input value. Floats are rejected so core
    financial calculations do not depend on binary floating-point arithmetic.
    """

    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        raise TypeError(f"{field_name} must be Decimal, int, or str, not float")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} is not a valid Decimal value: {value!r}") from exc


def quantize_money(value: Decimal | int | str) -> Decimal:
    """Round a currency amount to cents.

    Unit: currency units, rounded to 0.01.
    """

    return to_decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def calculate_market_cap(share_price: Decimal | int | str, shares_outstanding: Decimal | int | str) -> Decimal:
    """Calculate market capitalization.

    Formula: share price in currency per share * shares outstanding = currency.
    """

    return to_decimal(share_price, "share_price") * to_decimal(shares_outstanding, "shares_outstanding")


def calculate_pe(share_price: Decimal | int | str, eps: Decimal | int | str) -> Decimal:
    """Calculate price-to-earnings ratio.

    Formula: share price in currency per share / EPS in currency per share = multiple.
    """

    eps_decimal = to_decimal(eps, "eps")
    if eps_decimal == 0:
        raise ZeroDivisionError("eps cannot be zero when calculating PE")
    return to_decimal(share_price, "share_price") / eps_decimal


def calculate_fcf_yield(free_cash_flow: Decimal | int | str, market_cap: Decimal | int | str) -> Decimal:
    """Calculate free-cash-flow yield.

    Formula: free cash flow in currency / market capitalization in currency = ratio.
    """

    market_cap_decimal = to_decimal(market_cap, "market_cap")
    if market_cap_decimal == 0:
        raise ZeroDivisionError("market_cap cannot be zero when calculating FCF yield")
    return to_decimal(free_cash_flow, "free_cash_flow") / market_cap_decimal


def normalize_eps(
    reported_eps: Decimal | int | str,
    adjustments: Iterable[Decimal | int | str] | None = None,
) -> Decimal:
    """Normalize EPS by adding explicit per-share adjustments.

    Unit: currency per share. Positive adjustments increase normalized EPS;
    negative adjustments reduce normalized EPS.
    """

    normalized = to_decimal(reported_eps, "reported_eps")
    if adjustments:
        for index, adjustment in enumerate(adjustments, start=1):
            normalized += to_decimal(adjustment, f"adjustment_{index}")
    return normalized


def calculate_price_from_multiple(normalized_eps: Decimal | int | str, multiple: Decimal | int | str) -> Decimal:
    """Calculate implied share price from normalized EPS and valuation multiple.

    Formula: normalized EPS in currency per share * valuation multiple = price
    in currency per share.
    """

    return to_decimal(normalized_eps, "normalized_eps") * to_decimal(multiple, "multiple")


def format_decimal(value: Decimal, places: str = "0.01") -> str:
    """Format a Decimal with fixed quantization for display."""

    return str(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))
