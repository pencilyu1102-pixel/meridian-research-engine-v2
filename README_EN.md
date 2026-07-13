# Meridian Research Engine 2.0

An AI-native, full-chain equity research workflow covering macro conditions, sectors, companies, valuation, portfolio constraints and risk.

Meridian Research Engine helps generate structured investment research reports and checks their data sources, accounting basis, valuation assumptions, competitive reasoning, opposing evidence and review conditions.

It is not an AI stock picker and does not predict prices. Its purpose is to help AI produce research that is **traceable, challengeable and reviewable.**

> It does not predict the future — it helps you see the present clearly.

---

## What a Meridian report includes

A fully gated research report covers at minimum:

| Layer | Content |
|---|---|
| Macro & Market | Macro cycle, liquidity, market pricing, sector rotation |
| Industry & Competition | Industry conditions, lifecycle, competitive landscape, share shifts |
| Company & Fundamentals | Revenue/profit/cash flow/ROIC driver trees, core variable ranking |
| Data & Accounting | Source, date, currency, unit, accounting basis, source tier |
| Valuation & Expectations | Three-scenario valuation (Bear/Base/Bull), implied expectation reverse-engineering |
| Risk & Falsification | Bear case, falsification conditions and thresholds |
| Four-Layer Judgment | Company view, valuation view, account view, review/action status |
| Quality Gatekeeping | Data Integrity Hardlock + Gatekeeper release check |
| Review Loop | Next-review triggers and variables to monitor |

Full reports use 25 canonical sections. Templates are in [`templates/`](templates/).

---

## Full research chain

```text
Research request
→ Market and industry adapter selection
→ Macro cycle and sector rotation analysis
→ Company fundamentals and competitive position
→ Valuation and implied expectations
→ Portfolio constraints and risk
→ Bear case and falsification conditions
→ Generate standard research report
→ Data Integrity Hardlock
→ Gatekeeper release check
→ Release status and review triggers
```

The goal: **prevent AI from jumping directly to a conclusion.** Every key judgment must carry data sources, opposing evidence, and falsification conditions.

---

## Two ways to use

### Path A: Generate a full research report

The repository provides `SKILL.md`, `agents/` (10 agent roles), `workflows/` (10 workflows), and `templates/` (17 templates) to guide an AI Agent through the full research chain.

> **Note:** A unified agent installer and end-to-end orchestration script are not yet available. Specific agent-host runtime instructions will be added in a future version. For now, users can manually load SKILL.md, the relevant workflow, and templates into a supported AI Agent environment.

### Path B: Gate-check an existing report

Use the Python tools to audit report structure and data integrity:

```bash
# Gatekeeper release-quality check (3-tier, 3-grade, 3-mode)
python tools/report_gatekeeper.py reports/REPORT.md --language en

# Data Integrity Hardlock
# Via Gatekeeper's --hardlock-file parameter or programmatic call

# Vague-phrase detection
python tools/contradiction_hunter.py reports/REPORT.md
```

The Gatekeeper checks section presence, language compliance, content depth, and 10 downgrade rules before delivery — preventing unqualified reports from being treated as final.

---

## SAMPLE release-gating demo

These examples show the gating process using generic `SAMPLE` identifiers — no real companies, prices, or investment advice:

- [`reports/SAMPLE_research_dashboard_zh.md`](reports/SAMPLE_research_dashboard_zh.md) — Release-gating dashboard
- [`reports/SAMPLE_research_report_zh.md`](reports/SAMPLE_research_report_zh.md) — Standard report template (contains TODO placeholders; Gatekeeper rejection is expected behavior)

**Offline demo:** Run `python scripts/run_demo.py` to experience the full chain (synthetic data → report → gatekeeping → release status). The demo yields `PASS_TEST_ONLY`, meaning the synthetic report passes all contracts (Data Card, Source Policy, Hardlock, Gatekeeper) but is **not production-release eligible** (`TEST_ONLY_NOT_RELEASABLE` / `LOCKED`). It does not validate real market data or represent any investment conclusion.

Core difference:

```text
Typical AI stock analysis: jumps to a conclusion.
Meridian Research Engine: checks whether the conclusion is qualified for delivery.
```

---

## Current capability boundaries

| Tier | Content |
|---|---|
| Runnable directly | Python calculation tools (macro scoring, price level engine, valuation scenarios, reverse DCF, etc.), Data Card, Data Integrity Hardlock, Gatekeeper |
| Completed via AI Agent workflow | Macro analysis, industry research, company fundamentals, competitive analysis, valuation modeling, bear case, full report generation |
| Not currently provided | Automated real-time data terminal, broker connectivity, auto-trading, return promises, unified agent installer |

---

## v2.2 Data provenance and release gating

### Source Policy

Every data point entering a research conclusion must carry a **Data Card** classified by source reliability into five tiers:

| Tier | Max Permission | Conclusion-Eligible | Typical Sources |
|------|---------------|---------------------|-----------------|
| **S** | `full` | ✅ Yes | SEC EDGAR / HKEX filings / audited financials |
| **A** | `full` | ✅ Yes | Bloomberg / FactSet / official statistics |
| **B** | `reference_only` | Reference only | Sell-side research / industry media / aggregators |
| **C** | `reference_only` | Reference only | Unverified aggregators / social media |
| **D** | `blocked` | ❌ No | Unknown origin / anonymous / untraceable |

Each Data Card must include the following required metadata:

```text
basis             — accounting basis (gaap_actual / non_gaap / management_guidance)
period            — data period (TTM / FY2024 / Q1 2025)
source_tier       — source tier (S / A / B / C / D)
can_enter_conclusion — requested permission (full / reference_only / blocked)
freshness_status  — data freshness (current / stale / unknown)
has_conflict      — conflicting data exists (true / false)
```

Any `freshness_status` value outside `{current, stale, unknown}` is rejected. Conflicting data (`has_conflict=true`) or stale data cannot enter formal conclusions.

**Valuation denominator** (`valuation_denominator`) is a critical field requiring an S/A-tier Data Card with `full` permission.

### Data Integrity Hardlock

Formal release requires passing four data integrity layers:

```text
No card, no conclusion.
No basis, no formal valuation.
No bridge, no PE.
No industry hard fields, no FULL_PASS.
```

### Gatekeeper release statuses

| Status | Meaning | Formal Release | Test-OK |
|--------|---------|---------------|---------|
| `PASS_FORMAL` | All Data Cards, Source Policy, and Hardlock pass | ✅ | ✅ |
| `PASS_TEST_ONLY` | Contract integrity passes, but data is synthetic/test | ❌ | ✅ |
| `FAIL_DATA_HARDLOCK` | Data hardlock failed | ❌ | ❌ |

Synthetic data (`data_provenance=SYNTHETIC_FIXTURE`) can at most receive `PASS_TEST_ONLY` — never production-release eligible.

### Report Binding and Validation (Validator)

`scripts/validate_agent_report.py` runs three checks before Gatekeeper:

1. **Binding**: report metadata (research_id, symbol, market, as_of_date, bundle_sha256) must match the Research Bundle
2. **Bundle Hash**: all external files referenced by the Bundle (data_cards, industry_fields) participate in a recursive hash; any content change alters the hash
3. **Path safety**: absolute paths and parent-directory escapes are rejected

```bash
python scripts/validate_agent_report.py \
  --report outputs/agent_demo/SAMPLE_MANAGED_CARE_agent_report_bound_zh.md \
  --bundle examples/full_chain_sample/research_bundle.json \
  --output validation_result.json
```

A binding failure prevents Gatekeeper invocation — mismatched reports never enter the gating pipeline.

---

## Quick start

```bash
git clone https://github.com/pencilyu1102-pixel/meridian-research-engine-v2.git
cd meridian-research-engine-v2
pip install -r requirements.txt

# Run all tests (127 passed)
python -m pytest -q

# Macro six-factor scoring
python tools/macro_score.py --growth 1 --inflation 0 --liquidity 1 --credit 0 --earnings 1 --risk 0

# Price Level Engine
python tools/price_level_engine.py --eps 10.00 --ticker SAMPLE --multiples 12,15,18,20

# Gatekeeper (two equivalent styles)
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
python tools/report_gatekeeper.py --file reports/SAMPLE_research_report_zh.md --language zh
```

> These are standalone calculation and gatekeeping tools, not a full AI report generator. A complete research report requires an AI Agent working with SKILL.md, workflows, and templates.

```bash
# Offline full-chain demo (synthetic data → report → Hardlock → Gatekeeper)
python scripts/run_demo.py

# Report binding validation (Validator → Hardlock → Gatekeeper)
python scripts/validate_agent_report.py \
  --report outputs/agent_demo/SAMPLE_MANAGED_CARE_agent_report_bound_zh.md \
  --bundle examples/full_chain_sample/research_bundle.json \
  --output validation_result.json
```

Full installation, testing, and tool documentation: [`docs/quickstart_usage.md`](docs/quickstart_usage.md).

---

## Who this is for

**For:** Researchers and investors who want AI to produce research with sources, opposing evidence, and review conditions.

**Not for:** Users seeking instant stock picks, buy/sell signals, or automated trading systems.

---

## Project boundaries

This project does **not**:

- Predict short-term stock prices;
- Generate buy/sell signals;
- Automate trading;
- Promise returns;
- Replace the user's own investment judgment;
- Display real positions, real cost basis, real price levels, or real trading recommendations in the public repository.

It focuses on the research process itself: Is the data reliable? Are the assumptions clear? Is the valuation explainable? Is the bear case strong enough? Are the review conditions defined?

---

## Core methodology and nine-agent system

The project is built around a global equity buy-side research framework. Core methodology docs:

| Module | Doc | Purpose |
|---|---|---|
| Market adapters | [`docs/market_adapters.md`](docs/market_adapters.md) | US/CN/HK/GL market analysis frameworks |
| Industry adapters | [`docs/industry_adapters.md`](docs/industry_adapters.md) | 8 industry revenue driver formulas |
| Fundamental driver model | [`docs/fundamental_driver_model.md`](docs/fundamental_driver_model.md) | Revenue/profit/cash flow/ROIC driver trees |
| Competition & share model | [`docs/competition_share_model.md`](docs/competition_share_model.md) | TAM/SAM/SOM + value chain + moats |
| Implied expectation model | [`docs/implied_expectation_model.md`](docs/implied_expectation_model.md) | What is priced into the current price |
| Falsification framework | [`docs/falsification_framework.md`](docs/falsification_framework.md) | Thresholds + data sources + trigger actions |
| Data quality checklist | [`docs/data_quality_checklist.md`](docs/data_quality_checklist.md) | 10 mandatory data validations |

The research system is powered by 9 agent roles: Macro Consensus, Asset Rotation, Industry Position, Company Fundamental, Valuation & Margin, Portfolio Execution, Data Auditor, Bear Case, and Team Lead. See [`agents/`](agents/).

Core principles:

```text
Look at the macro cycle before the company.
Look at sector rotation before industry position.
A good company is not automatically a good price.
A good price is not automatically suitable for the current account.
Reliable data still needs correct interpretation.
Every core conclusion must be falsifiable — risk statements without thresholds and actions are not complete risk analysis.
```

---

## v2.1.0-alpha: Data Integrity Hardlock

The current version upgrades release gating from structure-level to data-integrity level. Formal release now requires both **Data Integrity Hardlock** (four layers: Data Card / Earnings Basis / Capital Structure Bridge / Industry Hard Fields) and Gatekeeper structure checks.

```text
No card, no conclusion.
No basis, no formal valuation.
No bridge, no PE.
No industry hard fields, no FULL_PASS.
```

---

## Current version and roadmap

| Field | Value |
|---|---|
| Current version | **v2.2.0-beta** (feat/v2.2-full-chain-research-ux) |
| Initial release | v2.0.0-beta |
| Next milestone | v2.3.0 (Validation Lab integration) |
| Repository | pencilyu1102-pixel/meridian-research-engine-v2 |

| Version | Date | Key Changes |
|---|---|---|
| **v2.2.0-beta** | 2026-07 | Source Policy SABCD unified admission, Validator report binding & Bundle Hash, PASS_TEST_ONLY release system, valuation_denominator critical field, invalid freshness rejection |
| **v2.1.0-alpha** | 2026-07 | Data Integrity Hardlock: 4-layer hardlock + 10 downgrade rules, Data Card/Earnings Basis/Capital Bridge/Industry Hard Fields |
| **v2.0.1-beta** | 2026-07 | CI hardening, public SAMPLE boundary enforcement, Gatekeeper CLI compatibility fixes |
| **v2.0.0-beta** | 2026-07 | Initial launch: market/industry adapters, fundamental drivers, competition share, implied expectations, falsification framework, Gatekeeper v2.1, 25-section templates, comprehensive test suite |

See [CHANGELOG.md](CHANGELOG.md).

---

## Credits

The original upstream project is the MIT-licensed open-source project `xbtlin/ai-berkshire`. Ada Pan and topgunsyang-dotcom co-created, reorganized, and extended the workflow around AI-assisted equity research, data audit, macro-cycle analysis, sector rotation, bear-case reasoning, falsification framework, and Gatekeeper release checks.

This project is not the official AI Berkshire project and does not represent any broker, investment adviser, financial institution, or company. The original upstream copyright notice and MIT License terms are retained in [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

---

## Final reminder

The purpose of Meridian Research Engine is not to make AI more persuasive. Its purpose is to make AI **harder** to persuade you too easily.

```text
See the bigger trend. Identify rotation. Verify data. Understand variables.
Identify risks. Control position size. Preserve cash. Wait for opportunities worth taking risk for.
```

Often, the best investment action is neither buy nor sell, but: **Do not act before you understand.**

---

## License

MIT License. See [`LICENSE`](LICENSE).

---

中文说明见：[README.md](README.md)
