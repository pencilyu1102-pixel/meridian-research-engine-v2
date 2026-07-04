# Portfolio Cost Template

## Transaction Input

Required CSV fields:

```text
date,ticker,action,shares,price,fee
```

Allowed actions:

```text
BUY
SELL
```

## Output Fields

| Field | Meaning |
|---|---|
| ticker | Security ticker |
| total_bought_shares | Sum of bought shares |
| total_sold_shares | Sum of sold shares |
| remaining_shares | Bought shares minus sold shares |
| gross_buy_amount | Sum of buy shares times buy price |
| gross_sell_amount | Sum of sell shares times sell price |
| total_fees | Sum of transaction fees |
| net_invested_capital | gross_buy_amount minus gross_sell_amount plus total_fees |
| management_cost_per_share | net_invested_capital divided by remaining shares |

## CLI

```bash
python tools/portfolio_cost.py examples/transactions_example.csv --ticker ABC
```
