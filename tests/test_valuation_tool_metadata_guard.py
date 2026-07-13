from tools.price_level_engine import render_price_level_report
from tools.reverse_dcf import build_output
from tools.tool_metadata_guard import (
    STATUS_CALC_ONLY_NOT_FOR_CONCLUSION,
    STATUS_PASS_FORMAL,
    evaluate_tool_metadata,
)
from tools.valuation_scenario import calculate_valuation_scenarios, format_scenario_table


def test_valuation_scenario_bare_numeric_input_is_calc_only_not_for_conclusion():
    scenario = calculate_valuation_scenarios("10.00", "12", "14", "16")
    table = format_scenario_table(scenario)

    assert scenario.metadata_verdict is not None
    assert scenario.metadata_verdict.status == STATUS_CALC_ONLY_NOT_FOR_CONCLUSION
    assert "CALC_ONLY_NOT_FOR_CONCLUSION" in table


def test_price_level_engine_bare_numeric_input_is_calc_only_not_for_conclusion():
    report = render_price_level_report("SAMPLE", "10.00", ["12", "16"])

    assert "CALC_ONLY_NOT_FOR_CONCLUSION" in report


def test_reverse_dcf_missing_key_metadata_is_calc_only_not_for_conclusion():
    output = build_output(
        market_cap=100000,
        net_cash=5000,
        revenue=20000,
        ev=95000,
        implied_cagr=0.12,
        implied_fcf_margin=None,
        terminal_growth=0.03,
        forecast_years=5,
        discount_rate=0.10,
        reported_cagr=None,
        reported_fcf_margin=None,
        cagr_note=None,
        margin_note=None,
        metadata={"basis": "gaap_actual"},
    )

    assert "CALC_ONLY_NOT_FOR_CONCLUSION" in output


def test_complete_metadata_input_can_pass_formal_and_transmit_provenance():
    metadata = {
        "basis": "gaap_actual",
        "period": "TTM",
        "source_tier": "A",
        "can_enter_conclusion": "full",
        "freshness_status": "current",
        "has_conflict": False,
    }
    verdict = evaluate_tool_metadata(metadata)
    scenario = calculate_valuation_scenarios("10.00", "12", "14", "16", metadata=metadata)
    table = format_scenario_table(scenario)

    assert verdict.status == STATUS_PASS_FORMAL
    assert scenario.metadata_verdict is not None
    assert scenario.metadata_verdict.status == STATUS_PASS_FORMAL
    assert "- **basis:** gaap_actual" in table
    assert "- **period:** TTM" in table
    assert "- **source_tier:** A" in table
    assert "- **can_enter_conclusion:** full" in table
