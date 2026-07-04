# Legal Compliance Checklist / 开源合规检查

This document records the open-source compliance checks for Meridian Research Engine 2.0 / Meridian Research Engine 2.0.

## Repository checked

- Repository: `pencilyu1102-pixel/meridian-research-engine-v2`
- Current project name: Meridian Research Engine 2.0 / Meridian Research Engine 2.0
- Current license: MIT License
- Current status: private repository at the time of review

## Upstream project

- Original project name: AI Berkshire
- Original repository: https://github.com/xbtlin/ai-berkshire
- Original author / organization: xbtlin
- Original license: MIT License
- Original copyright notice: `Copyright (c) 2026 xbtlin`

## Files checked

| File / path | Status | Notes |
|---|---|---|
| `LICENSE` | Updated | Keeps upstream copyright `Copyright (c) 2026 xbtlin` and adds `Copyright (c) 2026 Meridian Research Engine 2.0 contributors`. |
| `README.md` | Present | Describes Meridian Research Engine 2.0 / Meridian Research Engine 2.0 and includes investment-risk disclaimers. README should add or link to the attribution block before public release. |
| `NOTICE` | Updated | Records upstream project name, URL, author, MIT license, derivative status, modification summary, trademark note, and disclaimer. |
| `COPYRIGHT` | Not found | No separate copyright file found. |
| `package.json` | Not found | No Node package metadata found. |
| `pyproject.toml` | Not found | No Python package metadata found. |
| `setup.py` | Not found | No Python setup metadata found. |
| `pom.xml` | Not found | No Maven metadata found. |
| `Cargo.toml` | Not found | No Rust package metadata found. |
| `requirements.txt` | Present | Contains runtime/test dependency metadata only; no author/license fields. |

## MIT License redistribution requirements

MIT License redistribution is generally permitted if these conditions are met:

1. Keep the original copyright notice.
2. Keep the MIT permission notice.
3. Do not remove upstream author attribution if upstream code remains.
4. Clearly distinguish this repository from the upstream/original project.
5. Do not imply official affiliation or endorsement.

Current status: basically satisfied for MIT license notice preservation, subject to final source-level and asset-level review.

## Completed compliance actions

- Added upstream copyright notice to `LICENSE`.
- Updated `NOTICE` with AI Berkshire attribution.
- Clearly stated this is an independent derivative project, not the official AI Berkshire project.
- Added modification summary for Meridian Research Engine 2.0.
- Added trademark / brand caution.
- Added financial disclaimer.

## Remaining manual checks before public release

- Confirm whether any upstream assets remain, including logos, screenshots, performance images, badges, or icons.
- Confirm whether any references to `AI Berkshire` remain outside attribution/legal context.
- Confirm whether any upstream examples showing real performance, real accounts, or named stock recommendations remain.
- Add a short `README.md` attribution section or link to `NOTICE` before making the repository public.
- If any source file contains an upstream copyright header, keep it intact and add new project copyright only alongside it.

## Recommended README attribution block

Add the following section to `README.md` after the opening project description or before `License`:

```markdown
## 来源说明 / Credits / Attribution

本项目为基于 MIT License 开源项目 [AI Berkshire](https://github.com/xbtlin/ai-berkshire) 的二次开发版本，并非原项目官方版本，也不代表原作者或维护者立场。

- 原项目名称：AI Berkshire
- 原项目地址：https://github.com/xbtlin/ai-berkshire
- 原作者 / 组织：xbtlin
- 原许可证：MIT License
- 原版权声明：Copyright (c) 2026 xbtlin

在原项目基础上，本项目进行了项目名称、投研流程、宏观周期、板块轮动、数据审计、点位精算、报告准出、示例和测试等方向的重构与扩展。

原项目的版权声明和 MIT License 授权声明已在 `LICENSE` 与 `NOTICE` 中保留。本项目新增内容的版权归 Meridian Research Engine 2.0 contributors 所有。
```

## Trademark and branding note

Do not use upstream logos, names, icons, screenshots, badges, or official marks in a way that may imply endorsement, affiliation, or official status. If any such materials remain, replace them or mark them clearly as third-party references.

## Financial disclaimer

Meridian Research Engine 2.0 is a research workflow and data-audit aid. It is not financial advice, not a broker, not an automated trading system, and not a source of guaranteed investment results.
