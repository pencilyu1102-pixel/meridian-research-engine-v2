# Changelog

## v2.0.1-beta — Homepage and Research Dashboard Refinement

- Refined README first-screen positioning to emphasize Meridian Research Engine 2.0 as an AI research audit and report-gatekeeping engine.
- Added `reports/SAMPLE_research_dashboard_zh.md` as a public research gatekeeping dashboard demo.
- Added `reports/SAMPLE_research_dashboard.json` as a structured dashboard example.
- Improved GitHub homepage readability without changing the core methodology.
- Preserved the non-recommendation, non-trading, non-price-prediction, and public SAMPLE-only boundaries.
- Clarified that the project checks whether an AI research conclusion is qualified for delivery rather than generating buy/sell signals.

## v2.0.0-beta — Initial launch / 首发版本

- Established Meridian Research Engine 2.0｜经纬投研引擎 2.0 as the initial launch version.
- Clarified the project as a non-recommendation AI-assisted equity research workflow.
- Preserved upstream MIT attribution to xbtlin/ai-berkshire.
- Clarified the co-created working base by Ada Pan and topgunsyang-dotcom.
- Added Gatekeeper v2.1 report release checks.
- Added data audit, bear-case reasoning, falsification framework, and privacy boundary.
- Added public sample policy using SAMPLE / TICKER / ABC identifiers only.

## Internal cleanup after v2.0.0-beta

- `v2.0.1-beta-cleanup`: CI, test, compliance, and public-sample-boundary cleanup on the development branch.
- Fixed remaining canonical section wording inconsistencies.
- Prevented the legacy comprehensive script from being collected as a pytest test function.
- Clarified SAMPLE report Gatekeeper expectations and retained positional / `--file` CLI compatibility.
- Reviewed public/private report boundary and private-data ignore rules.

## Upstream reference history

- `(upstream) v1.1-pricelevel`: 9-agent architecture, Price Level Engine, and early Gatekeeper building blocks from the upstream line.
- Co-created working-base stage before the current Meridian Research Engine 2.0 initial release.
