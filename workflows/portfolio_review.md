# Portfolio Review Workflow

## Purpose

Review a real account with cost basis, current weights, cash, margin, and concentration constraints.

## Steps

1. Load holdings and transactions.
2. Calculate management cost with `tools/portfolio_cost.py`.
3. Classify each position as base position, trading position, watch-only, or blocked.
4. Portfolio Execution Agent checks cash, margin, concentration, and drawdown tolerance.
5. Valuation & Margin Agent and Price Level Engine update price maps for key holdings.
6. Bear Case Agent checks whether "hold" is a lazy decision.
7. Team Lead Agent outputs account-level constraints and review triggers.

## Output

- Position table.
- Cost table.
- Weight constraints.
- Add/trim condition map.
- Maximum risk and next review condition.
