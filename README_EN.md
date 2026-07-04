# Meridian Research Engine 2.0

中文说明见：[README.md](README.md)

Repository: `pencilyu1102-pixel/meridian-research-engine-v2`

> An AI-assisted global equity buy-side research framework integrating market adapters, industry adapters, fundamental driver models, competition share models, implied expectation reverse-engineering, and falsification-backed decision-making, all validated by the Gatekeeper v2.1 release-quality system.

### Core Design Philosophy

1. **Data validation** as foundation.
2. **Fundamental driver model** (revenue/gross margin/cost/cash flow/ROIC) and **competition share model** (TAM/SAM/SOM) as core.
3. **Implied expectation reverse-engineering** (what CAGR, margin, share, multiple is the current price discounting) as valuation framework.
4. **Bear case** and **falsification framework** (threshold + data source + trigger action) as decision feedback loop.
5. **Do not predict prices** — reverse-engineer what the current price is discounting.
6. Do not use a single valuation method for all companies — select **market adapters** (US/CN/HK/GL) and **industry adapters** (8 industry models) by market, industry, and business model.
7. All reports must pass **Gatekeeper v2.1** (three-tier check + three-grade release + 25 canonical sections) before delivery.

It is not a stock-picking system, not an automated trading system, not a fixed buy/sell signal generator, and not financial advice.

---

## Important disclaimer

This project does not provide investment advice, trading recommendations, price predictions, automated execution, or guaranteed returns.

All outputs are research workflow materials, data-audit aids, and decision-support drafts. Users must make their own decisions and bear their own risks.

This project is not suitable for:

- automatic order execution;
- short-term trading signals;
- replacing personal judgment;
- predicting prices;
- promising returns;
- buying or selling based on one metric;
- treating AI output as the final conclusion.

Public examples must use generic identifiers such as `SAMPLE`, `TICKER`, or `ABC`. Do not publish real account screenshots, private cost basis, private transaction records, or real personal position details.

---

## Quick start

Full local usage guide:

- [`docs/quickstart_usage.md`](docs/quickstart_usage.md)

Common commands:

```bash
git clone https://github.com/pencilyu1102-pixel/meridian-research-engine-v2.git
cd meridian-research-engine-v2
pip install -r requirements.txt
python -m pytest -q
python tools/macro_score.py --growth 1 --inflation 0 --liquidity 1 --credit 0 --earnings 1 --risk 0
python tools/price_level_engine.py --eps 10.00 --ticker SAMPLE --multiples 12,15,18,20
python tools/portfolio_cost.py examples/transactions_example.csv --ticker ABC
python tools/valuation_scenario.py --eps 10.00 --bear 12 --base 15 --bull 18
# Gatekeeper — two equivalent invocation styles:
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
python tools/report_gatekeeper.py --file reports/SAMPLE_research_report_zh.md --language zh
```

---

## Language rule

Reports must be generated in one selected language.

- Chinese user request: use the Chinese report template (25 canonical h2 sections).
- English user request: use the English report template (25 canonical h2 sections).
- Explicit language request overrides auto-detection.
- Tickers, commands, file paths, formulas, module names, and source names may remain in their original form.
- Section headings, table columns, explanatory paragraphs, conclusions, and review triggers must use the selected report language.

See:

- [`docs/language_policy.md`](docs/language_policy.md)

---

## Standard report template

Do not fill `templates/standard_research_report.md` directly. It is only a selector file.

Use language-specific templates:

- Chinese report: [`templates/standard_research_report_zh.md`](templates/standard_research_report_zh.md) (25 canonical h2 sections)
- English report: [`templates/standard_research_report_en.md`](templates/standard_research_report_en.md) (25 canonical h2 sections)

A standard report must separate four layers:

```text
Company view: Is this a good company?
Valuation view: Is the current price attractive?
Account view: Does the real portfolio allow action?
Review / Action status: Observe, review, wait, reduce risk, or insufficient data.
```

A good company is not automatically a good price. A good price is not automatically suitable for the current account.

**Template rules:**
- All `##` section headings must be preserved in final reports.
- If a section does not apply, write "not applicable + reason" — do not delete the section.
- Gatekeeper modes: `formal` (default), `core` (framework test), `smoke` (quick check).

---

## Word and PDF report export

Meridian Research Engine 2.0 uses Markdown as the canonical source format. Word and PDF are delivery formats.

Report export guide:

- [`docs/report_export.md`](docs/report_export.md)

Chinese report export:

```bash
mkdir -p reports
cp templates/standard_research_report_zh.md reports/SAMPLE_research_report_zh.md
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
pandoc reports/SAMPLE_research_report_zh.md -o reports/SAMPLE_research_report_zh.docx
```

English report export:

```bash
mkdir -p reports
cp templates/standard_research_report_en.md reports/SAMPLE_research_report_en.md
python tools/report_gatekeeper.py reports/SAMPLE_research_report_en.md --language en
pandoc reports/SAMPLE_research_report_en.md -o reports/SAMPLE_research_report_en.docx
```

PDF can be exported from Word / WPS, or generated with Pandoc if a local PDF engine is configured.

---

## Language rule

Reports must be generated in one selected language.

- Chinese user request: use the Chinese report template (25 canonical h2 sections).
- English user request: use the English report template (25 canonical h2 sections).
- Explicit language request overrides auto-detection.
- Tickers, commands, file paths, formulas, module names, and source names may remain in their original form.
- Section headings, table columns, explanatory paragraphs, conclusions, and review triggers must use the selected report language.

See:

- [`docs/language_policy.md`](docs/language_policy.md)

---

## Core module documentation

| Module | Doc | Purpose |
|---|---|---|
| Market adapters | [`docs/market_adapters.md`](docs/market_adapters.md) | US/CN/HK/GL market analysis priorities |
| Industry adapters | [`docs/industry_adapters.md`](docs/industry_adapters.md) | 8 industry revenue driver models |
| Fundamental driver model | [`docs/fundamental_driver_model.md`](docs/fundamental_driver_model.md) | Revenue/profit/cash flow/ROIC driver trees |
| Competition and share model | [`docs/competition_share_model.md`](docs/competition_share_model.md) | TAM/SAM/SOM, value chain, moats, competitor reverse-engineering |
| Implied expectation model | [`docs/implied_expectation_model.md`](docs/implied_expectation_model.md) | What CAGR/margin/multiple/share is priced in |
| Falsification framework | [`docs/falsification_framework.md`](docs/falsification_framework.md) | Core judgment falsification thresholds |
| Data quality checklist | [`docs/data_quality_checklist.md`](docs/data_quality_checklist.md) | 10 mandatory data validations |

---

## Gatekeeper v2 — Report release quality check

`tools/report_gatekeeper.py` is the content-level release audit system.

### Three-tier architecture

| Layer | Check | Purpose |
|---|---|---|
| Layer 0 | Section existence (25 canonical headings exact match) | No missing sections |
| Layer 1 | Language compliance + vague phrase detection | Clean language |
| Layer 2 | Content depth (core module required fields) | Non-empty reports |
| Layer 3 | 10 downgrade rules (up to hard lock) | Data completeness |

### Three operation modes

| Mode | Purpose | Scope |
|---|---|---|
| `formal` (default) | Formal release | All 25 sections exact + content depth + language + 10 rules |
| `core` | Framework test | 10 core modules fuzzy match + content depth |
| `smoke` | Quick check | 3 most-likely-missed modules (industry adapter, competition share, implied expectation) |

### Three grades

| Grade | Meaning |
|---|---|
| **FULL_PASS / 可准出** | All core data, valuation, driver model, competition model, falsification complete |
| **CORE_PASS_TEMPLATE_FAIL / 条件准出** | Core content passes, but section headers don't match canonical list |
| **HARD_LOCK_FAIL / 不可准出** | Missing price/market cap/financial data — cannot be released |

### 10 downgrade rules

1. No market adapter → max conditionally releasable
2. No industry adapter → max conditionally releasable
3. No fundamental driver model → max conditionally releasable
4. No competition and share model → max conditionally releasable
5. No implied expectation → max conditionally releasable
6. **Missing/outdated price, market cap, or shares → NOT RELEASABLE**
7. **Core data without source → NOT RELEASABLE**
8. Bear/Base/Bull without probability or trigger → max conditionally releasable
9. No falsification indicators → max conditionally releasable
10. Risks without thresholds and action → max conditionally releasable

### Commands

```bash
# Formal release (25 exact match + content depth)
python tools/report_gatekeeper.py reports/REPORT.md --language en

# Core module check (10 modules, alias fuzzy matching)
python tools/report_gatekeeper.py reports/REPORT.md --language en --mode core

# Smoke test (3 most-likely-missed modules)
python tools/report_gatekeeper.py reports/REPORT.md --language en --mode smoke
```

---

## Core capabilities

| Capability | Purpose |
|---|---|
| Macro cycle | 6-factor scoring (-2~+2), macro environment assessment |
| Sector rotation | 3-gate check (macro wind, industry conditions, valuation crowding) |
| Market adapters | 4 frameworks (US/CN/HK/GL) |
| Industry adapters | 8 industry revenue driver formulas |
| Fundamental driver model | Revenue/gross-margin/cost/cash flow/ROIC driver trees |
| Competition and share model | TAM/SAM/SOM + value chain + moats + competitor reverse-engineering |
| Implied expectation | Reverse-engineer CAGR, margin, share, multiple priced in |
| Data audit | Source, date, unit, currency, accounting basis reliability |
| Data meaning | Explain what data means instead of only listing numbers |
| 3-scenario valuation | Bear/Base/Bull + probability-weighted value |
| Price Level Engine | Multi-zone price anchors (valuation/market/account/trigger) |
| Portfolio execution | Separate company research from account-level action |
| Bear case | Actively search for strongest opposing evidence |
| Falsification framework | Core judgment thresholds + data sources + trigger actions |
| Report gatekeeper v2 | 3-tier + 3-grade + 3-mode release quality check |

---

## Why This Project Exists

If you ask AI:

```text
Can I buy this company now?
```

it is easy to receive an answer like:

```text
The company has solid long-term fundamentals, but there is short-term uncertainty, so investors should be cautious.
```

That kind of answer sounds complete, but it often fails to answer the questions that matter for actual research:

- Is the current macro environment favorable or unfavorable?
- Which sectors are receiving capital flows?
- Has the institutional consensus already been priced in?
- Are the data sources reliable?
- What do the data actually mean?
- Is there a margin of safety in valuation?
- Does the user's own account allow action?
- What would invalidate the conclusion?
- What variables should trigger the next review?

Meridian Research Engine 2.0 is not trying to answer whether AI can analyze. It is trying to make AI analysis more disciplined, auditable, and closer to a real research process.

---

## Standard research workflow

```text
Select market adapter (US/CN/HK/GL)
→ Select industry adapter (8 industry models)
→ Macro consensus + 6-factor macro scoring
→ Market pricing and consensus validation
→ Sector rotation + 3-gate check
→ Industry position
→ Company fundamentals (6 dimensions)
→ Data reliability audit (10 mandatory checks)
→ Key data cards + core variable ranking
→ Fundamental driver model (revenue → gross margin → cost → cash flow → ROIC)
→ Competition and share model (TAM/SAM/SOM → moats → competitor reverse-engineering)
→ Valuation and margin of safety (3 scenarios + probability-weighted value)
→ Implied expectation reverse-engineering
→ Price Level Engine
→ Portfolio execution
→ Bear case / reverse argument
→ Falsification framework (thresholds + triggers)
→ Four-layer judgment (company/valuation/account/review)
→ Final action framework (4 disciplines)
→ Maximum risk + next review triggers
→ Gatekeeper v2 release check
```

The goal: **prevent AI from jumping directly to a conclusion.**

A formal report must not only say:

```text
Long-term bullish, short-term volatile.
Valuation is reasonable, but risks should be monitored.
Buy if it drops to a round number.
Sell if it rises to a round number.
```

It must explain:

- why the judgment is made;
- which data support it;
- which data argue against it;
- what valuation logic the current price implies;
- whether the current account allows action;
- what would invalidate the conclusion;
- what to review next.

---

## Workflow entrypoints

| Entry point | Purpose |
|---|---|
| `/macro-sector-rotation` | Macro and sector-rotation analysis |
| `/stock-research` | Full single-company research |
| `/earnings-review` | Earnings review and attribution |
| `/news-pulse` | Price-move and news-pulse attribution |
| `/portfolio-review` | Portfolio review and account-execution check |
| `/qdii-review` | QDII / ETF review |
| `/industry-funnel` | Industry funnel screening |
| `/buy-checklist` | Pre-buy checklist |
| `/sell-checklist` | Pre-sell checklist |
| `/data-audit` | Dedicated data-reliability audit |

Examples:

```text
Run Meridian Research Engine 2.0 /macro-sector-rotation on the US stock market.
Output macro six-factor score, institutional consensus and disagreement, market-pricing validation, favorable sectors, pressured sectors, and next review indicators.
```

```text
Run Meridian Research Engine 2.0 /stock-research TICKER and use the English standard report template.
```

---

## Core Principles

```text
Look at the macro cycle before the company.
Look at sector rotation before industry position.
A good company is not automatically a good price.
A good price is not automatically suitable for the current account.
Reliable data still needs correct interpretation.
A research conclusion is not an operation instruction.
A price level is a review condition, not a buy/sell signal.
```

A complete judgment should be split into four layers:

```text
Company view: Is this a good company?
Valuation view: Is the current price attractive?
Account view: Does the real position, cost basis, and cash level allow action?
Trading view: Is the current state buy, sell, hold, wait, or review?
```

These layers must not be merged.

---

## Macro and Sector Rotation Engine

The Macro and Sector Rotation Engine translates the macro environment into auditable sector and industry research context.

It does not directly predict the economy. It combines three types of signals:

1. official and quasi-official macro data;
2. mainstream asset-manager and investment-bank views;
3. market pricing and high-frequency indicators.

The system reviews six macro factors:

| Factor | Core question |
|---|---|
| Growth | Is the economy accelerating, slowing, or diverging? |
| Inflation | Is inflation rising, falling, or sticky? |
| Liquidity | Is the central-bank environment easing, neutral, or tightening? |
| Credit | Is financing expanding or contracting? |
| Earnings | Are earnings expectations being revised up or down? |
| Risk appetite | Is the market taking risk or avoiding risk? |

Macro judgment must not directly generate a buy/sell conclusion. A sector has to pass three gates:

```text
Gate 1: Does the macro wind support it?
Gate 2: Is industry momentum verified?
Gate 3: Are valuation and trading crowding reasonable?
```

Only after all three gates pass should a sector enter the priority research list.

---

## Nine-Agent Research System

| Agent | Responsibility |
|---|---|
| Macro Consensus Agent | Collect official, institutional, and market-pricing macro signals; identify consensus, disagreement, and stale views. |
| Asset Rotation Agent | Judge fund flows, sector rotation, trading crowding, and whether market pricing already reflects institutional consensus. |
| Industry Position Agent | Assess industry stage, competitive structure, company alpha, and industry beta. |
| Company Fundamental Agent | Assess revenue quality, profit quality, cash-flow quality, and capital allocation quality. |
| Valuation & Margin Agent | Assess valuation level, margin of safety, and scenario valuation. |
| Portfolio Execution Agent | Review real holdings, cost basis, cash, margin, base position, and trading position. |
| Data Auditor Agent | Audit data source, accounting basis, timestamp, currency, unit, and reliability. |
| Bear Case Agent | Search for the strongest opposing evidence and attack the current conclusion. |
| Team Lead Agent | Integrate conflicts, assign weights, and form the final research memo. |

Each agent must answer more than a conclusion:

```text
What is the key data?
What does the data mean?
Is it improving or worsening versus the prior period?
How does it compare with history, expectations, and peers?
How does it affect valuation?
How does it affect portfolio action?
What change would invalidate the current view?
```

---

## Data Reliability Engineering

Every important data point should be audited for:

- source tier;
- data timestamp;
- currency;
- unit;
- accounting basis;
- one-time items;
- whether it is an estimate;
- whether it conflicts with other sources;
- whether it can enter the final conclusion.

| Tier | Source type | Use |
|---|---|---|
| S | Company filings, earnings releases, 10-K, 10-Q, 8-K, official macro data | Core factual basis |
| A | Exchange data, authoritative databases, official fund data | Market, valuation, and macro validation |
| B | Major financial media | Event context and market reaction |
| C | Broker research, consulting reports, third-party estimates | Industry sizing, share, and forecast data |
| D | Social media, forums, community discussion | Sentiment and leads only; not a factual basis |

If data conflict, check first:

```text
Are the dates consistent?
Are the currencies consistent?
Are the units consistent?
Are GAAP / Non-GAAP definitions consistent?
Are TTM / quarterly / annual definitions consistent?
Are one-time gains or expenses included?
Is this forecast data rather than actual data?
Is there a disclosure lag?
```

Do not simply average conflicting data points.

---

## Data Meaning Interpretation

This project rejects raw-data dumping.

Weak version:

```text
Revenue grew, margin improved, and capital expenditure increased.
```

Better version:

```text
Revenue growth shows that the core business is still growing, but rising capital expenditure may shift market attention from revenue growth to free-cash-flow conversion quality. This data can support continued research or holding, but it does not automatically support adding exposure.
```

Each key data point should answer:

```text
Data fact: what is the number?
Data source: where did it come from and what is its source tier?
Data meaning: what does it indicate?
Marginal change: is it better or worse than the prior period?
Relative comparison: how does it compare with history, expectations, and peers?
Valuation impact: does it raise or lower valuation tolerance?
Action impact: does it support buy, hold, trim, or only observe?
Invalidation condition: what would overturn the interpretation?
```

---

## Valuation and Margin of Safety

Valuation must explain how the value range is derived, instead of only saying that valuation is reasonable.

At minimum, it should answer:

```text
Is the anchor PE, forward PE, FCF yield, EV/EBITDA, or something else?
How is normalized EPS / FCF calculated?
Where does the current valuation sit versus history, peers, and business quality?
Which variables drive bear, base, and bull cases?
What would move the valuation range up or down?
```

A valuation conclusion can describe margin of safety and tolerance. It cannot replace account-level action.

---

## Price Level Engine

The Price Level Engine does not output mechanical buy/sell signals such as:

```text
Buy when the price drops to a round number.
Sell when the price rises to a round number.
```

It helps split a price zone into five dimensions:

```text
1. Valuation anchor: what normalized EPS / FCF multiple does the price imply?
2. Market anchor: is the price near trading congestion, support, or resistance?
3. Personal cost anchor: is it near the user's own cost, management cost, or trading-position cost?
4. Position constraint: do current weight, cash, and margin allow action?
5. Fundamental trigger: do key business data support the validity of this zone?
```

The same price can mean very different things to different investors:

```text
User A has no position and enough cash; the price may only enter the watch zone.
User B is already concentrated and cash-light; the only reasonable action may be to wait.
User C has a low cost basis and heavy exposure; adding risk may be inappropriate.
User D uses margin; risk reduction may come first.
```

Core rule:

```text
Price is a necessary condition, not a sufficient condition.
```

---

## Portfolio Execution

Even if a company is good, the report still has to answer:

```text
How much does the user currently hold?
What is the account cost basis?
What is the management cost?
Is there already a base position?
Is it a trading position?
What is the cash ratio?
Is margin being used?
Can the account tolerate further downside?
Would the position become too large after action?
```

Management-cost formula:

```text
Management cost = invested capital remaining in the current position - realized gains
Management cost per share = management cost / remaining shares
```

`tools/portfolio_cost.py` calculates aggregate management cost for portfolio-management review. It is not tax-lot cost and not FIFO / LIFO tax accounting.

---

## Bear Case and Report Gatekeeper

The bear case is not decoration. It must actively attack the main conclusion:

```text
If the view is positive, what is the strongest negative evidence?
If the view is cautious, what is the strongest positive evidence?
If the view is to continue holding, is that a lazy decision?
Which data changes would overturn the current conclusion?
```

The Report Gatekeeper checks whether a report is ready to be used. At minimum, it checks:

- required sections;
- whether data have source, date, basis, unit, and currency;
- vague conclusions;
- whether company, valuation, account, and trading judgments are mixed together;
- whether account-level actions are output without account data;
- whether invalidation conditions and review triggers are preserved.

---

## Report gatekeeper

Chinese report:

```bash
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
```

English report:

```bash
python tools/report_gatekeeper.py reports/SAMPLE_research_report_en.md --language en
```

The gatekeeper checks: 25 canonical section headings, vague phrases, bilingual heading mixing, and key data field completeness.

---

## Repository structure

```text
meridian-research-engine-v2/
├── README.md                  # This file (Chinese)
├── README_EN.md               # English README
├── CHANGELOG.md               # Version changelog
├── SKILL.md                   # Agent skill file
├── LICENSE                    # MIT License
├── NOTICE                     # Original project copyright
├── requirements.txt           # Python dependencies
├── test_comprehensive.py      # Comprehensive test suite
│
├── agents/                    # Research agent definitions (10 agents)
├── workflows/                 # Workflow templates (10 workflows)
├── templates/                 # Report templates (17 templates)
├── tools/                     # Core tools (14 CLI tools)
├── examples/                  # Example data (5 files)
├── tests/                     # Unit tests (7 test files)
├── reports/                   # Report output directory
│
└── docs/                      # Documentation (18 doc files)
    ├── quickstart_usage.md
    ├── market_adapters.md              
    ├── industry_adapters.md            
    ├── fundamental_driver_model.md     
    ├── competition_share_model.md      
    ├── implied_expectation_model.md    
    ├── falsification_framework.md      
    ├── data_quality_checklist.md       
    ├── language_policy.md
    ├── report_export.md
    ├── macro_sector_rotation.md
    ├── data_reliability.md
    ├── architecture.md
    ├── methodology.md
    ├── legal_compliance.md
    ├── disclaimer.md
    └── price_level_engine.md
```

|---

## Who this is for

**For:**
- Investors who want AI-assisted research without AI-generated fluff.
- Users who need an integrated framework covering macro, sector, company, and account-level analysis.
- Users who value data audit, bear case arguments, and disciplined review.
- Active portfolio holders who need account-aware research.
- Anyone building a long-term investment research workflow.

**Not for:**
- Automated stock picks or trading signals.
- "What should I buy today — what will go up tomorrow" type queries.
- Users unwilling to verify data and conduct regular reviews.

---

## Roadmap

**Completed:**
- [x] Standard report templates (CN/EN, 25 canonical sections)
- [x] Report language detection and separate CN/EN templates
- [x] Word / PDF report export documentation
- [x] English README
- [x] Quick-start and usage documentation
- [x] Automated test workflow (GitHub Actions)
- [x] Restore and lock workflow entrypoint documentation
- [x] Global framework: market adapters (US/CN/HK/GL) + industry adapters (8 models)
- [x] Fundamental driver model (revenue/gross margin/cost/cash flow/ROIC driver trees)
- [x] Competition and share model (TAM/SAM/SOM + value chain + moats + competitor reverse-engineering)
- [x] Implied expectation reverse-engineering model
- [x] Falsification framework (thresholds + data sources + trigger actions)
- [x] Data quality checklist (10 mandatory validations)
- [x] Gatekeeper v2 (3-tier/3-grade/3-mode + 10 downgrade rules)
- [x] Comprehensive test suite (test_comprehensive.py)

**To do:**
- [ ] Improve the data-source registry
- [ ] Add automatic Data Point Card generation
- [ ] Add data cross-validation tooling
- [ ] Add a macro-view card generator
- [ ] Add helper logic for whether market pricing already reflects institutional consensus
- [ ] Add QDII premium and subscription-limit checks
- [ ] Add portfolio concentration risk reports
- [ ] Add automated Word / PDF export commands

---

## Version info

Current version: **v1.0-beta** (Meridian Research Engine 2.0 initial release)

| Version | Date | Key Changes |
|---|---|---|
| (upstream) v1.1-pricelevel | Upstream initial | 9-agent architecture, Price Level Engine, basic Gatekeeper |
| **v1.0-beta** | 2026-07-03 | **Meridian Research Engine 2.0 initial release** |

See [CHANGELOG.md](CHANGELOG.md).

---

## Credits / Attribution

This project is a fork of [**pencilyu1102-pixel/golden-research-engine**](https://github.com/pencilyu1102-pixel/golden-research-engine), whose upstream is the MIT-licensed open-source project [AI Berkshire](https://github.com/xbtlin/ai-berkshire) by xbtlin. It is not the official project and does not represent the upstream authors or maintainers.

| Level | Repository | Description |
|---|---|---|
| Root upstream | [`xbtlin/ai-berkshire`](https://github.com/xbtlin/ai-berkshire) | MIT License, original author xbtlin |
| Direct upstream | [`pencilyu1102-pixel/golden-research-engine`](https://github.com/pencilyu1102-pixel/golden-research-engine) | Derivative with global framework v1.0 |
| **This repo** | **`pencilyu1102-pixel/meridian-research-engine-v2`** | **This fork, v1.0-beta** |

Based on the upstream projects, this fork has been extended with global framework upgrades: market/industry adapters, fundamental driver model, competition share model, Gatekeeper v2 release validation, standardized report templates, and comprehensive testing.

The upstream copyright notice and MIT permission notice are retained in `LICENSE` and `NOTICE`. New project contributions are copyrighted by Meridian Research Engine 2.0 contributors.

---

## Final Reminder

The purpose of Meridian Research Engine 2.0 is not to make AI more persuasive.

Its purpose is to make AI harder to persuade you too easily.

A truly mature research system does not always produce an exciting conclusion. It helps you:

```text
see the bigger trend;
identify rotation;
verify data;
understand variables;
identify risks;
control position size;
preserve cash;
wait for opportunities that are actually worth taking risk for.
```

Often, the best investment action is neither buy nor sell, but:

```text
Do not act before you understand.
```

---

## License

MIT License. See [`LICENSE`](LICENSE).
