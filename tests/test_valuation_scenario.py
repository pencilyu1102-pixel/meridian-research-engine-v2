from decimal import Decimal

from tools.valuation_scenario import calculate_valuation_scenarios, format_scenario_table


def test_valuation_scenario_outputs_three_prices():
    scenario = calculate_valuation_scenarios(
        base_eps="10.00",
        bear_multiple="12",
        base_multiple="14",
        bull_multiple="16",
    )

    assert scenario.bear_case_price == Decimal("120.00")
    assert scenario.base_case_price == Decimal("140.00")
    assert scenario.bull_case_price == Decimal("160.00")


def test_valuation_scenario_outputs_markdown_table():
    scenario = calculate_valuation_scenarios("10.00", "12", "14", "16")
    table = format_scenario_table(scenario)

    assert "| Bear case price | 120.00 |" in table
    assert "| Base case price | 140.00 |" in table
    assert "| Bull case price | 160.00 |" in table
