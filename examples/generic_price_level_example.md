# Generic Price Level Example

This example uses a fictional ticker and fictional assumptions. It is only a demonstration of how the Price Level Engine calculates valuation anchors.

## Assumption

```text
Ticker: SAMPLE
Normalized EPS: 10.00
Valuation multiples: 12x, 14x, 16x
```

## Valuation Anchor Table

| Multiple | Formula | Implied Price |
|---:|---|---:|
| 12x | 10.00 * 12 | 120.00 |
| 14x | 10.00 * 14 | 140.00 |
| 16x | 10.00 * 16 | 160.00 |

## Interpretation Rules

- The table is a valuation-anchor calculation, not an investment recommendation.
- The same price can imply different actions for different investors.
- Any account-level interpretation must consider personal holdings, cost basis, cash, position size, risk limits, and fundamental conditions.
- A valuation anchor is invalid if the normalized EPS assumption, business quality, or required return changes materially.

## CLI

```bash
python tools/price_level_engine.py --eps 10.00 --ticker SAMPLE --multiples 12,14,16
```
