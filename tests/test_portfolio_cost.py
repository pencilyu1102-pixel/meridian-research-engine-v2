from decimal import Decimal

from tools.portfolio_cost import calculate_portfolio_cost, format_portfolio_cost_table


def test_portfolio_cost_calculates_remaining_shares_and_management_cost():
    cost = calculate_portfolio_cost("examples/transactions_example.csv", ticker="ABC")

    assert cost.remaining_shares == Decimal("11")
    assert cost.gross_buy_amount == Decimal("1400")
    assert cost.gross_sell_amount == Decimal("440")
    assert cost.total_fees == Decimal("3")
    assert cost.net_invested_capital == Decimal("963")
    assert cost.management_cost_per_share == Decimal("963") / Decimal("11")


def test_portfolio_cost_outputs_markdown_table():
    cost = calculate_portfolio_cost("examples/transactions_example.csv", ticker="ABC")
    table = format_portfolio_cost_table(cost)

    assert "| remaining_shares | 11 |" in table
    assert "| management_cost_per_share | 87.55 |" in table
