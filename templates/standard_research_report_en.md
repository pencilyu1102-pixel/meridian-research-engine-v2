# Standard Research Report Template v2.0.0-beta

> Purpose: structured research, data audit, reverse valuation, portfolio review, and repeatable investment workflow. This template is not investment advice.  
> Usage rule: formal reports must keep all level-2 section headings. If a section is not applicable, write "Not applicable + reason" rather than deleting it.  
> Gatekeeper modes: `formal` for official release, `core` for framework testing, and `smoke` for quick checks.

---

# {{TICKER_OR_ASSET_NAME}} Research Report

- Report date: {{YYYY-MM-DD}}
- Ticker / Asset: {{TICKER}}
- Market: {{US Equity / China A-Share / Hong Kong Equity / Global / Other}}
- Industry adapter: {{Semiconductor & Hardware / Software SaaS Cloud / Internet Platform / Consumer & Retail / Cyclical Energy Materials / Financials / Healthcare Biotech / Utilities REITs / Mixed Business}}
- Researcher: {{NAME_OR_TEAM}}
- Data cut-off: {{YYYY-MM-DD HH:MM TZ}}
- Report status: Draft / Review / Final
- Report language: English
- Gatekeeper mode: formal / core / smoke

---

## Report gatekeeper

| Check item | Status | Notes |
|---|---|---|
| Data source checked | TODO | Company filings, exchange data, market data, and third-party data are verifiable |
| Data date checked | TODO | Price, market cap, financials, and consensus dates are aligned |
| Currency and units checked | TODO | USD / CNY / HKD; million / billion / trillion; ordinary share / ADS / H-share |
| Market adapter completed | TODO | Market selected and applicability of fields explained |
| Industry adapter completed | TODO | Industry model selected and revenue formula stated |
| Macro section completed | TODO | Macro six-factor score is consistent with market adapter |
| Sector section completed | TODO | Industry momentum, crowding, and fund flow reviewed |
| Fundamental driver model completed | TODO | Revenue, gross margin, opex, cash flow, ROIC/ROE |
| Competition and share model completed | TODO | TAM/SAM/SOM, value chain, moat, competitors |
| Valuation section completed | TODO | Normalized base, scenarios, reverse valuation, implied expectations |
| Market implied expectations completed | TODO | CAGR, margin, share, and multiple implied by current price |
| Portfolio execution completed | TODO | Account constraints, position size, margin, single-stock limit |
| Bear case completed | TODO | Both bear and bull disconfirming cases included |
| Falsification framework completed | TODO | Thresholds, data source, and action defined |
| Review triggers completed | TODO | Earnings, valuation, competition, fund flow, and risk events |
| Language consistency checked | TODO | No bilingual headings |

Gatekeeper conclusion:

```text
TODO: Ready / Conditional review only / Not ready

Hardlock rules:
- Missing valid price, market cap, core financial sources, revenue, or EPS: Not ready.
- Conflicting currency, share count, or valuation basis without correction: Not ready.
- Missing market adapter, industry adapter, fundamental drivers, competition/share model, implied expectations, or falsification framework: Conditional review only at best.
```

---

## One-sentence conclusion

```text
TODO: Use one precise sentence covering company view, valuation view, market implied expectations, account constraint, and review status.
```

```text
Company view: TODO
Valuation view: TODO
Market expectation view: TODO
Account view: TODO
Review status: TODO
```

---

## Decision weight table

| Module | Weight | Current view | Confidence | Key evidence |
|---|---:|---|---|---|
| Macro cycle | TODO | TODO | TODO | TODO |
| Market adapter and fund flow | TODO | TODO | TODO | TODO |
| Sector rotation | TODO | TODO | TODO | TODO |
| Industry lifecycle | TODO | TODO | TODO | TODO |
| Business quality | TODO | TODO | TODO | TODO |
| Fundamental driver model | TODO | TODO | TODO | TODO |
| Competition and share model | TODO | TODO | TODO | TODO |
| Data reliability | TODO | TODO | TODO | TODO |
| Valuation and margin of safety | TODO | TODO | TODO | TODO |
| Portfolio execution | TODO | TODO | TODO | TODO |
| Bear case and falsification | TODO | TODO | TODO | TODO |

Overall grade:

```text
TODO: Research candidate / Portfolio review / Wait / Reject / Not enough data
```

---

## Market and industry adapters

### Market adapter

| Field | Selection or view | Applicability | Reason |
|---|---|---|---|
| Market | TODO | applicable | US Equity / China A-Share / Hong Kong Equity / Global / Other |
| Primary currency | TODO | applicable | Currency used for financials and valuation |
| Accounting basis | TODO | applicable | GAAP / Non-GAAP / IFRS / China GAAP |
| Rates and liquidity | TODO | applicable / not_applicable / uncertain | Impact on valuation multiples and risk appetite |
| Policy and regulation | TODO | applicable / not_applicable / uncertain | Market- or industry-specific regulation |
| Crowding and fund flow | TODO | applicable / not_applicable / uncertain | Especially important for A-share, HK, and thematic trades |
| Dividends and buybacks | TODO | applicable / not_applicable / uncertain | Especially important for US, HK, and mature companies |
| FX exposure | TODO | applicable / not_applicable / uncertain | Cross-border revenue, ADRs, HK listings, global companies |
| Special structure | TODO | applicable / not_applicable / uncertain | ADS, A/H, dual listing, VIE, REITs, etc. |

### Industry adapter

| Field | Content |
|---|---|
| Primary industry adapter | TODO |
| Secondary industry adapter | TODO, required for mixed businesses |
| Adapter confidence | High / Medium / Low |
| Reason for selection | TODO |
| Main revenue formula | TODO, e.g. Revenue = Volume × ASP × Mix |
| Required industry metrics | TODO |
| Not applicable metrics | TODO, with reason |

---

## Macro six-factor score

| Factor | Score (-2 to +2) | Evidence | Meaning |
|---|---:|---|---|
| Growth | TODO | TODO | TODO |
| Inflation | TODO | TODO | TODO |
| Liquidity | TODO | TODO | TODO |
| Credit | TODO | TODO | TODO |
| Earnings | TODO | TODO | TODO |
| Risk appetite | TODO | TODO | TODO |

```text
Raw score: TODO
Normalized score: TODO
Macro state: TODO
Market adapter note: TODO
```

---

## Market pricing and consensus validation

| Question | Answer | Evidence |
|---|---|---|
| What is the current market consensus? | TODO | TODO |
| Has the consensus been priced in? | TODO | TODO |
| What is not fully reflected? | TODO | TODO |
| What may be over-reflected? | TODO | TODO |
| Where may the market be wrong? | TODO | TODO |
| What data would change this view? | TODO | TODO |

Conclusion:

```text
TODO: Not reflected / Partially reflected / Fully reflected / Over-reflected / Unclear
```

---

## Sector rotation and three-gate check

### Sector view

| Sector or theme | Current status | Evidence | Risk |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

### Three-gate check

| Gate | Result | Reason |
|---|---|---|
| Gate 1: Macro support | TODO | TODO |
| Gate 2: Industry momentum | TODO | TODO |
| Gate 3: Valuation, crowding, share, and growth quality | TODO | TODO |

Conclusion:

```text
TODO: Pass / Partial pass / Fail / Watch only
```

---

## Data reliability review

| Data point | Value | Source | Source grade | Date | Unit and currency | Use in conclusion? |
|---|---:|---|---|---|---|---|
| Latest share price | TODO | TODO | TODO | TODO | TODO | TODO |
| Market cap / enterprise value | TODO | TODO | TODO | TODO | TODO | TODO |
| Share count / ADS ratio | TODO | TODO | TODO | TODO | TODO | TODO |
| Revenue | TODO | TODO | TODO | TODO | TODO | TODO |
| EPS / net income / FCF | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO | TODO |

Conflict checks:

```text
Time consistency: TODO
Currency consistency: TODO
Unit consistency: TODO
Accounting-basis consistency: TODO
Period-basis consistency: TODO
Share-count consistency: TODO
Valuation-basis consistency: TODO
One-off items: TODO
Actual or forecast: TODO
Peer-comparison basis: TODO
```

Data reliability conclusion:

```text
TODO: S / A / B / C / D, with reason
```

---

## Key data cards

### Data card 1: {{DATA_POINT}}

| Field | Content |
|---|---|
| Data fact | TODO |
| Source and grade | TODO |
| Meaning | TODO |
| Driver type | Industry beta / Company alpha / Pricing / Share gain / Mix upgrade / One-off / Accounting / Cyclical |
| Marginal change | TODO |
| Relative comparison | TODO |
| Sustainability | High / Medium / Low / Unclear |
| Valuation impact | EPS uplift / Multiple expansion / Lower risk premium / One-off / Multiple pressure |
| Portfolio or review impact | TODO |
| Invalidation condition | TODO |

### Data card 2: {{DATA_POINT}}

| Field | Content |
|---|---|
| Data fact | TODO |
| Source and grade | TODO |
| Meaning | TODO |
| Driver type | TODO |
| Marginal change | TODO |
| Relative comparison | TODO |
| Sustainability | TODO |
| Valuation impact | TODO |
| Portfolio or review impact | TODO |
| Invalidation condition | TODO |

---

## Core variable ranking

| Rank | Variable | Current value | Driver layer | Current direction | Lead/lag | Importance | Tracking frequency | Falsification threshold | Data source |
|---:|---|---:|---|---|---|---|---|---|---|
| 1 | TODO | TODO | Revenue / margin / cash flow / valuation / share / policy / fund flow | TODO | Leading / coincident / lagging | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

---

## Industry position

```text
TODO: Explain industry stage, competitive structure, industry beta, company alpha, profit-pool position, and lifecycle.
```

| Item | View | Evidence |
|---|---|---|
| Industry stage | Introduction / Growth / Mature / Decline / Cycle trough / Cycle peak | TODO |
| Industry beta | High / Medium / Low | TODO |
| Company alpha | High / Medium / Low | TODO |
| Profit-pool position | Core / Midstream / Peripheral / Unclear | TODO |
| Supply-demand structure | TODO | TODO |
| Pricing trend | TODO | TODO |

---

## Competition and share model

### Market boundary

| Layer | Definition | Value or view | Source | Confidence |
|---|---|---|---|---:|---|---|
| TAM | TODO | TODO | TODO | TODO |
| SAM | TODO | TODO | TODO | TODO |
| SOM | TODO | TODO | TODO | TODO |

### Value chain and profit pool

```text
Upstream suppliers → Company → Channel/platform → Customers → End users
TODO
```

| Question | View | Evidence |
|---|---|---|
| Who captures the largest profit pool? | TODO | TODO |
| Who controls scarce resources? | TODO | TODO |
| Who controls customer access? | TODO | TODO |
| Is the company in the core profit pool? | TODO | TODO |

### Moat and competitive advantages

| Advantage type | Exists? | Quantitative evidence | Trend | Durability |
|---|---|---|---|---|
| Cost advantage | TODO | TODO | Strengthening / Stable / Weakening | TODO |
| Technology advantage | TODO | TODO | TODO | TODO |
| Network effect | TODO | TODO | TODO | TODO |
| Brand advantage | TODO | TODO | TODO | TODO |
| Channel advantage | TODO | TODO | TODO | TODO |
| Data advantage | TODO | TODO | TODO | TODO |
| License/regulatory barrier | TODO | TODO | TODO | TODO |
| Ecosystem lock-in | TODO | TODO | TODO | TODO |

### Competitor reverse check

| Competitor | Strength | Weakness | Threat to company | Monitoring indicator |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

### Share-change model

```text
Company revenue = Market size × Penetration × Company share × Price/Take rate × Product mix
```

| Variable | Current view | 3-5 year assumption | Evidence | Falsification condition |
|---|---|---|---|---|
| Market size | TODO | TODO | TODO | TODO |
| Penetration | TODO | TODO | TODO | TODO |
| Company share | TODO | TODO | TODO | TODO |
| Price / Take rate | TODO | TODO | TODO | TODO |
| Product mix | TODO | TODO | TODO | TODO |

---

## Company fundamentals

| Dimension | View | Evidence |
|---|---|---|
| Revenue quality | TODO | TODO |
| Profit quality | TODO | TODO |
| Cash-flow quality | TODO | TODO |
| Balance-sheet quality | TODO | TODO |
| Capital allocation | TODO | TODO |
| Management execution | TODO | TODO |

Company fundamentals conclusion:

```text
TODO
```

---

## Fundamental driver model

### Revenue driver tree

```text
Revenue growth = Industry growth + Penetration gain + Share gain + Pricing + Mix upgrade + M&A + One-off factors
```

| Growth source | Contribution view | Evidence | Sustainability | Risk |
|---|---|---|---|---|
| Industry growth | High/Medium/Low | TODO | TODO | TODO |
| Penetration gain | High/Medium/Low | TODO | TODO | TODO |
| Share gain | High/Medium/Low | TODO | TODO | TODO |
| Pricing | High/Medium/Low | TODO | TODO | TODO |
| Mix upgrade | High/Medium/Low | TODO | TODO | TODO |
| M&A | Yes/No | TODO | TODO | TODO |
| One-off factors | Yes/No | TODO | Not sustainable | TODO |

### Margin and profit drivers

| Item | Current value | Trend | Driver | View |
|---|---:|---|---|---|
| Gross margin | TODO | TODO | TODO | TODO |
| Sales and marketing ratio | TODO | TODO | TODO | TODO |
| R&D ratio | TODO | TODO | TODO | TODO |
| G&A ratio | TODO | TODO | TODO | TODO |
| Operating margin | TODO | TODO | TODO | TODO |
| Net margin | TODO | TODO | TODO | TODO |

### Cash-flow driver tree

| Item | Current value | YoY/QoQ | Cash-flow impact | View |
|---|---:|---:|---|---|
| Operating cash flow | TODO | TODO | TODO | TODO |
| CapEx | TODO | TODO | TODO | TODO |
| Receivables change | TODO | TODO | TODO | TODO |
| Inventory change | TODO | TODO | TODO | TODO |
| Prepayments change | TODO | TODO | TODO | TODO |
| Free cash flow | TODO | TODO | TODO | TODO |
| FCF margin | TODO | TODO | TODO | TODO |
| FCF conversion | TODO | TODO | TODO | TODO |

### ROIC / ROE drivers

| Metric | Current value | Calculation basis | View |
|---|---:|---|---|
| ROIC | TODO | NOPAT / Average Invested Capital | TODO |
| ROE | TODO | Net income / Average equity | TODO |
| ROIC vs WACC | TODO | TODO | TODO |
| DuPont ROE breakdown | TODO | Net margin × Turnover × Leverage | TODO |

---

## Valuation and margin of safety

### Normalized base

```text
Normalized EPS / FCF basis: TODO
Adjustment items: TODO
Reason for normalization: TODO
```

### Scenario valuation

| Scenario | Key assumption | Probability | Multiple or yield | Implied value | Trigger |
|---|---|---:|---:|---:|---|
| Bear | TODO | TODO | TODO | TODO | TODO |
| Base | TODO | TODO | TODO | TODO | TODO |
| Bull | TODO | TODO | TODO | TODO | TODO |

Probability-weighted value:

```text
TODO: Bear × probability + Base × probability + Bull × probability
```

---

## Market implied expectations

| Implied assumption in current price | Market-implied value | Report view | Gap | Evidence |
|---|---:|---:|---|---|
| Future revenue CAGR | TODO | TODO | TODO | TODO |
| Long-term gross margin | TODO | TODO | TODO | TODO |
| Long-term net margin / FCF margin | TODO | TODO | TODO | TODO |
| Market share | TODO | TODO | TODO | TODO |
| Valuation multiple | TODO | TODO | TODO | TODO |
| ROIC / ROE | TODO | TODO | TODO | TODO |

Conclusion:

```text
TODO: What has the current price already priced in? Does the report agree? Where is the market wrong?
```

---

## Price Level Engine

| Price zone | Valuation anchor | Market anchor | Account constraint | Required business trigger | Interpretation |
|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO |

Core rule:

```text
Price is a condition, not a signal.
```

---

## Portfolio execution

This section must be completed before any account-level action language is used.

| Item | Value | Notes |
|---|---:|---|
| Current shares | TODO | TODO |
| Original cost | TODO | TODO |
| Account cost | TODO | TODO |
| Management cost | TODO | TODO |
| Realized gain/loss | TODO | TODO |
| Current weight | TODO | TODO |
| Cash level | TODO | TODO |
| Margin use | TODO | TODO |
| Single-position limit | TODO | TODO |

Portfolio execution conclusion:

```text
TODO: Account action allowed / Not allowed / Need more data / Review only
```

---

## Bear case

Strongest opposing view:

```text
TODO
```

| Bear-case factor | Probability | Impact | Evidence | Monitoring trigger |
|---|---:|---:|---|---|
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

What would prove the positive view wrong?

```text
TODO
```

What would prove the negative view wrong?

```text
TODO
```

---

## Falsification framework

| Core thesis | Falsification indicator | Threshold | Data source | Triggered action |
|---|---|---:|---|---|
| TODO | TODO | TODO | TODO | Revise model / Downgrade rating / Position review / Exit research |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

Principle:

```text
Every core thesis must be falsifiable. A risk warning without threshold and action is not a complete risk analysis.
```

---

## Four-layer judgment

```text
Company judgment: TODO
Valuation judgment: TODO
Account judgment: TODO
Review judgment: TODO
```

Do not merge these four layers.

---

## Final action framework

Use conditional language only. Do not output mechanical buy/sell instructions.

| Discipline type | Condition | Status | Action | Reason |
|---|---|---|---|---|
| Valuation discipline | TODO | TODO | TODO | TODO |
| Fundamental discipline | TODO | TODO | TODO | TODO |
| Competition discipline | TODO | TODO | TODO | TODO |
| Fund-flow discipline | TODO | TODO | TODO | TODO |

Final framework:

```text
TODO: Portfolio review / Wait / Review zone / Research candidate / Reduce risk / Not enough data
```

---

## Maximum risk

| Risk type | Description | Probability | Potential impact | Leading indicator | Action |
|---|---|---:|---|---|---|
| Fundamental risk | TODO | TODO | TODO | TODO | TODO |
| Valuation risk | TODO | TODO | TODO | TODO | TODO |
| Competition risk | TODO | TODO | TODO | TODO | TODO |
| Financial-quality risk | TODO | TODO | TODO | TODO | TODO |
| Liquidity risk | TODO | TODO | TODO | TODO | TODO |
| Policy/regulatory risk | TODO | TODO | TODO | TODO | TODO |
| Black-swan risk | TODO | TODO | TODO | TODO | TODO |

Single biggest risk:

```text
TODO: Identify the single most important risk that can change the entire thesis.
```

---

## Next review triggers

| Trigger | Threshold or event | Review type | Model to update | Why it matters |
|---|---|---|---|---|
| TODO | TODO | Earnings / valuation / competition / fund flow / risk event | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

Next review date:

```text
TODO
```

---

## Appendix

### Source list

| Source | Link or reference | Grade | Used for |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

### Calculation notes

```text
TODO: State EPS, FCF, ROIC, ROE, EV, share count, currency, reverse DCF, and probability-weighted valuation basis.
```

### Not-applicable fields

| Field | Reason not applicable |
|---|---|
| TODO | TODO |

### Open-source and disclaimer note

```text
This report format belongs to Meridian Research Engine 2.0.
The project is an independent derivative project based in part on AI Berkshire under the MIT License.
This report is a research workflow output only and is not investment advice.
```
