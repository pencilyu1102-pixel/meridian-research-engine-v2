# Price Level Engine

Price Level Engine is one of the core modules of Meridian Research Engine 2.0. It builds research price maps. It is not a buy/sell signal system.

## Methodology

加减仓点位不能靠整数心理位。

The map must combine five factors:

1. valuation anchor;
2. trading congestion or support/resistance;
3. personal cost anchor;
4. position constraint;
5. fundamental trigger condition.

## Output Structure

1. 正常化 EPS / FCF 估值锚；
2. 估值倍数对应股价表；
3. 成交密集区和阻力支撑；
4. 个人成本锚；
5. 价格共振区；
6. 加仓触发条件；
7. 减仓触发条件；
8. 点位失效条件；
9. 最终交易地图。

## CLI

```bash
python tools/price_level_engine.py --eps 10.00 --ticker SAMPLE
```

Custom multiples:

```bash
python tools/price_level_engine.py --eps 10.00 --ticker SAMPLE --multiples 12,14,16
```

## Interpretation Rule

The valuation table is only an anchor. The same price can mean different things to different investors. A level should not become actionable unless personal holdings, cost basis, cash, position size, risk limits, and fundamental conditions also pass.
