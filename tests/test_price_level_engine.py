from decimal import Decimal

from tools.price_level_engine import build_valuation_anchor_table, render_price_level_report


def test_price_level_engine_calculates_required_generic_anchors():
    anchors = build_valuation_anchor_table("10.00", ["12", "16"])
    by_multiple = {anchor.multiple: anchor.price for anchor in anchors}

    assert by_multiple[Decimal("12")] == Decimal("120.00")
    assert by_multiple[Decimal("16")] == Decimal("160.00")


def test_price_level_engine_outputs_markdown_table():
    report = render_price_level_report("SAMPLE", "10.00", ["12", "16"])

    assert "Ticker: SAMPLE" in report
    assert "| Multiple | Implied Price |" in report
    assert "| 12.0x | 120.00 |" in report
    assert "| 16.0x | 160.00 |" in report
