from decimal import Decimal

import pytest

from tools.financial_rigor import (
    calculate_fcf_yield,
    calculate_market_cap,
    calculate_pe,
    calculate_price_from_multiple,
    normalize_eps,
)


def test_financial_rigor_returns_decimal_values():
    assert isinstance(calculate_market_cap("100", "20"), Decimal)
    assert calculate_market_cap("100", "20") == Decimal("2000")
    assert calculate_pe("100", "5") == Decimal("20")
    assert calculate_fcf_yield("50", "1000") == Decimal("0.05")
    assert normalize_eps("9.50", ["0.50"]) == Decimal("10.00")
    assert calculate_price_from_multiple("10.00", "12") == Decimal("120.00")


def test_financial_rigor_rejects_float_inputs():
    with pytest.raises(TypeError):
        calculate_price_from_multiple(10.00, "12")
