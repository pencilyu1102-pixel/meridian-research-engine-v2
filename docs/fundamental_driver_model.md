# Fundamental Driver Model / 基本面驱动模型

## 1. Revenue Growth Decomposition

Revenue Growth = Industry Growth + Penetration + Share Gain + Price + Product Mix + M&A + One-Off

Every dollar of revenue growth must be attributed to a source. This decomposition separates **alpha** (company-specific execution) from **beta** (industry tailwinds) and forces the analyst to judge sustainability.

### Growth Source Analysis Table

| Source | Contribution (ppt) | Evidence | Sustainability | Risk |
|--------|-------------------|----------|----------------|------|
| **Industry Growth** | TAM growth rate × revenue base | Industry reports, macro forecasts, segment growth rates | Depends on structural vs cyclical drivers | Regulatory change, substitution, demand shock |
| **Penetration** | New customers / new geographies | Customer count growth, geographic revenue split, expansion metrics | High if early in S-curve; low if market is mature | Market saturation, competitive response |
| **Share Gain** | Outperformance vs peers | Market share data, competitive win/loss analysis, share-of-wallet trends | Medium — competitors will respond | Pricing war, competitor innovation |
| **Price** | ASP changes net of mix | Same-store pricing, contract renewal rates, price elasticity tests | Low unless pricing power is structural (moat-based) | Volume offset, customer churn, regulation |
| **Product Mix** | Shift to higher/lower-value products | Revenue per unit, product tier breakdown, attach rates | Medium — depends on innovation pipeline | Cannibalization, R&D miss |
| **M&A** | Acquired revenue (net of divestitures) | Purchase consideration, revenue contribution of acquired assets, earnout performance | Low — deal synergy is hard to sustain | Integration risk, goodwill impairment, multiple paid |
| **One-Off** | Non-recurring items | Contract settlements, asset sales, catch-up license fees | Very low | Misleading base effect |

### Key Questions

- **Industry beta or company alpha?** Is the company growing because the tide is rising (industry growth) or because it is taking share and expanding TAM on its own merits?
- **Quality of growth?** Price-driven growth with no volume is fragile. Share gain in a commoditized market is expensive. Penetration of an unsaturated TAM is the most valuable.
- **Sustainable without leverage?** Is growth funded by debt, equity dilution, or organic cash flow? Organic FCF-funded growth compounds; levered growth de-risks only when ROIC > WACC.

---

## 2. Margin Driver Tree

### Gross Margin

```
Gross Margin = (Revenue − COGS) / Revenue
```

Cost drivers within COGS:

| Cost Driver | Description | Typical Impact |
|-------------|-------------|----------------|
| **Materials** | Raw material / input costs (commodities, components, energy) | Direct pass-through or hedge-dependent |
| **Labor** | Direct labor (wages, benefits, overtime) | Geography-dependent; wage inflation risk |
| **Efficiency** | Yield rates, automation level, capacity utilization | Improves with scale; degrades with complexity |
| **Technology** | Software amortization, cloud infrastructure, IP licensing | Mix-dependent; can create step-change improvement |
| **Logistics** | Freight, warehousing, last-mile delivery | Driver for e-commerce / physical goods |
| **Tariffs** | Import/export duties, trade barriers | Geopolitical vector; can be structural or temporary |

### Operating Margin

```
Operating Margin = Gross Margin − R&D% − S&M% − G&A%
```

| Component | Description | Leverage Type |
|-----------|-------------|---------------|
| **R&D (R&D%)** | Research & development as % of revenue | Discretionary: can be cut to boost short-term margins at the cost of moat durability |
| **S&M (S&M%)** | Sales & marketing as % of revenue | Scale leverage: should decline as brand awareness grows; watch for customer acquisition cost (CAC) inflation |
| **G&A (G&A%)** | General & administrative as % of revenue | Structural leverage: should trend to a fixed floor as revenue scales |

### Key Questions

- **Structural or cyclical leverage?** Are margin improvements coming from genuine operating leverage (fixed cost base being spread over growing revenue) or from a cyclical tailwind (low input costs, favorable FX)?
- **SBC inflation?** Is stock-based compensation (SBC) masking true labor cost? Add back SBC to G&A to understand cash-based operating margin. High SBC inflates GAAP margins and dilutes shareholders.

---

## 3. Cash Flow Driver Tree

```
OCF  = Net Income + Non-Cash Charges − Change in Working Capital
FCF  = OCF − Capital Expenditures (Capex)
```

### Cash Conversion

| Component | Description | Signal |
|-----------|-------------|--------|
| **Net Income (NI)** | Starting point | Quality-adjusted NI removes one-off gains/losses |
| **Non-Cash Charges** | D&A, SBC, deferred taxes, impairments | Large gap between NI and OCF suggests low earnings quality |
| **Working Capital** | Δ(AR + Inventory − AP − Accrued Liabilities) | Negative ΔWC (cash generation) is a positive signal; positive ΔWC (cash consumption) signals growth funding need |

### Capital Expenditure

| Capex Type | Description | Implication |
|------------|-------------|-------------|
| **Maintenance Capex** | Required to keep existing operations running | Necessary for current cash flow sustainability |
| **Growth Capex** | Investment in new capacity, geographies, products | Creates future cash flow; must earn > WACC |

### Key Questions

- **Convert earnings to cash?** A company that reports high net income but generates low OCF (e.g., due to aggressive revenue recognition, ballooning receivables) has low earnings quality. Target: OCF / NI > 1.0.
- **Maintenance or growth capex?** Distinguishing the two is critical. If most capex is maintenance, FCF is structurally lower than it appears. If growth capex has stalled, future growth is at risk.
- **Working capital trend?** Companies that can operate with negative working capital (e.g., subscription models, retailers with fast inventory turns) have an intrinsic cash advantage.
- **FCF sufficient for dividends / buybacks?** Dividend and buyback sustainability = FCF / (dividends + buybacks) > 1.0. A ratio below 1.0 means the company is borrowing or diluting to return capital.

---

## 4. ROIC / ROE Tree

```
ROIC = NOPAT / Invested Capital
ROE  = Net Income / Equity
```

### ROIC Decomposition

| Level | Formula | Insight |
|-------|---------|---------|
| **NOPAT** | EBIT × (1 − Tax Rate) | Operating profitability after tax — the cash return the business generates |
| **Invested Capital** | Total Debt + Total Equity − Cash & Equivalents (or Operating Assets − Operating Liabilities) | The total capital base deployed in the business |
| **ROIC** | NOPAT / Invested Capital | The true return on each dollar invested in operations |

### ROE Decomposition (DuPont)

```
ROE = (NI / Revenue) × (Revenue / Assets) × (Assets / Equity)
     ↑                    ↑                    ↑
  Net Margin           Asset Turnover       Financial Leverage
```

| Leg | What It Measures | High Reading | Low Reading |
|-----|------------------|--------------|-------------|
| **Net Margin** | Profitability per dollar of revenue | Pricing power & cost control | Commodity pressure, high fixed costs |
| **Asset Turnover** | Revenue generated per dollar of assets | Asset-light, high velocity (software, retail) | Asset-heavy (utilities, industrials) |
| **Financial Leverage** | Assets funded per dollar of equity | Levered returns (can amplify ROE in good times) | Risk of insolvency in downturns |

### Key Questions

- **ROIC > WACC?** This is the fundamental test of value creation. If ROIC < WACC, the company is destroying value regardless of revenue growth. Spread = ROIC − WACC.
- **ROE from earnings quality or leverage?** A high ROE driven entirely by financial leverage (debt) is fragile. Sustained ROE should come from high net margins and asset efficiency, not from leverage.
- **Improving or deteriorating?** Track ROIC and ROE over a 5-year rolling window. Improving trends suggest competitive advantage widening; deteriorating trends suggest competitive pressure or capital misallocation.

---

## 5. Unified Output

Every fundamental research report **must** include a completed Growth Source Breakdown Table as a core output. This table synthesizes the entire driver model into a single, quantitative view of where growth came from, how sustainable it is, and what risks threaten it.

### Growth Source Breakdown Table (Required Output)

| Source | Contribution (ppt) | Evidence | Sustainability | Risk |
|--------|-------------------|----------|----------------|------|
| Industry Growth | | | | |
| Penetration | | | | |
| Share Gain | | | | |
| Price | | | | |
| Product Mix | | | | |
| M&A | | | | |
| One-Off | | | | |
| **Total Revenue Growth** | **Sum = Reported Growth** | | | |

### Supporting Checks (Must Be Answered in Every Report)

1. **Growth Quality**: What fraction of growth is organic (Industry + Penetration + Share Gain + Price + Product Mix) vs inorganic / non-recurring (M&A + One-Off)?
2. **Margin Trajectory**: Is margin expansion structural (operating leverage, mix shift) or cyclical (input cost tailwind, one-off savings)?
3. **Cash Flow Adequacy**: Does the business self-fund its growth? FCF conversion rate? Capex intensity trend?
4. **Return on Capital**: Is the company earning above its cost of capital? Are returns sustainable or mean-reverting?

These four checks, combined with the Growth Source Breakdown Table, form the **minimum viable fundamental analysis** output for every research report.
