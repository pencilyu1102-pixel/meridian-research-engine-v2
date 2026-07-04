# Legal Compliance Checklist / 开源合规检查

This document records the open-source compliance checks for Meridian Research Engine 2.0 / 经纬投研引擎 2.0.

## Repository checked

- Repository: `pencilyu1102-pixel/meridian-research-engine-v2`
- Current project name: Meridian Research Engine 2.0 / 经纬投研引擎 2.0
- Current public-facing release: `v2.0.0-beta`
- Current license: MIT License
- Current status: private repository at the time of review

## Source hierarchy / 来源层级

### 1. Original upstream

- Original upstream: `xbtlin/ai-berkshire`
- Original project name: AI Berkshire
- Original repository: https://github.com/xbtlin/ai-berkshire
- Original author / organization: xbtlin
- Original license: MIT License
- Original copyright notice: `Copyright (c) 2026 xbtlin`

### 2. Co-created working base

- Co-created working base: `topgunsyang-dotcom/argus-research-engine`
- Description: a co-created working base developed by Ada Pan and topgunsyang-dotcom around AI-assisted equity research workflow, macro-cycle analysis, sector rotation, data audit, bear-case reasoning, falsification framework, and Gatekeeper release checks.

### 3. Current project

- Current project: `pencilyu1102-pixel/meridian-research-engine-v2`
- Current project name: Meridian Research Engine 2.0 / 经纬投研引擎 2.0
- Current release positioning: initial public-facing release `v2.0.0-beta`

## Compliance statements / 合规声明

1. The upstream MIT License copyright notice and permission notice must be retained.
2. The current project is not the official upstream project and does not represent xbtlin or upstream maintainers.
3. The current project is not a simple republication of topgunsyang-dotcom's repository; it is an independent initial release formed after co-created reorganization by Ada Pan and topgunsyang-dotcom.
4. The current project does not represent any broker, investment adviser, exchange, data provider, financial institution, or company.

## Files checked

| File / path | Status | Notes |
|---|---|---|
| `LICENSE` | Updated | Keeps upstream copyright `Copyright (c) 2026 xbtlin` and adds `Copyright (c) 2026 Meridian Research Engine contributors`. |
| `README.md` | Updated | Uses the `v2.0.0-beta` initial-release positioning and includes the project-origin section. |
| `README_EN.md` | Updated | Mirrors the initial-release positioning and English project-origin section. |
| `NOTICE` | Updated | Records upstream project, co-created working base, independence notice, MIT license compliance notes, and disclaimer. |
| `COPYRIGHT` | Not found | No separate copyright file found. |
| `requirements.txt` | Present | Contains dependency metadata only; no author/license fields. |

## MIT License redistribution requirements

MIT License redistribution is generally permitted if these conditions are met:

1. Keep the original copyright notice.
2. Keep the MIT permission notice.
3. Do not remove upstream author attribution if upstream code remains.
4. Clearly distinguish this repository from the upstream/original project.
5. Do not imply official affiliation or endorsement.

Current status: satisfied at the repository-documentation layer, subject to final source-level and asset-level review before any public release.

## Remaining manual checks before public release

- Confirm whether any upstream assets remain, including logos, screenshots, performance images, badges, or icons.
- Confirm whether any references to `AI Berkshire` outside attribution/legal context remain appropriate.
- Confirm whether any public examples still imply real account data, real position records, or direct stock recommendations.
- Keep upstream source notices intact if any file still carries an upstream copyright header.

## Financial disclaimer

Meridian Research Engine 2.0 is a research workflow and data-audit aid. It is not financial advice, not a broker, not an automated trading system, and not a source of guaranteed investment results.
