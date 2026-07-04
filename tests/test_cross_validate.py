from decimal import Decimal

from tools.cross_validate import SourceValue, cross_validate_values


def test_cross_validate_consistent_values_with_explicit_tolerance():
    values = [
        SourceValue(source="source_a", value=Decimal("10.00")),
        SourceValue(source="source_b", value=Decimal("10.03")),
    ]

    # 不同数据类型应使用不同容差。
    result = cross_validate_values(values, tolerance="0.05")

    assert result["spread"] == Decimal("0.03")
    assert result["conflict"] is False


def test_cross_validate_default_tolerance_remains_strict():
    values = [
        SourceValue(source="source_a", value=Decimal("10.00")),
        SourceValue(source="source_b", value=Decimal("10.03")),
    ]

    result = cross_validate_values(values)

    assert result["spread"] == Decimal("0.03")
    assert result["conflict"] is True
