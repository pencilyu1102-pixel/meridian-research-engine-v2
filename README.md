# 经纬投研引擎 2.0

一套从宏观、行业、公司、估值到仓位与风险的 AI 原生全链路投研工作流。

经纬投研引擎可以生成结构完整的投研分析报告，并对报告中的数据来源、财务口径、估值假设、竞争判断、反方证据和复盘条件进行校核。

它不是 AI 荐股机，也不替你预测股价。它要解决的是：**如何让 AI 完成一份有依据、可追溯、可反驳、可复盘的投研报告。**

> 它不替你预测未来，只帮你把当下看清楚。

---

## 一份经纬报告最终包含什么

一份通过校核的完整投研报告至少包含以下内容：

| 层级 | 内容 |
|---|---|
| 宏观与市场 | 宏观周期、流动性、市场定价与板块轮动判断 |
| 行业与竞争 | 行业景气、生命周期、竞争格局与份额变化 |
| 公司与基本面 | 收入/利润/现金流/ROIC 驱动拆解、核心变量排序 |
| 数据与口径 | 来源、日期、币种、单位、财务口径、来源等级 |
| 估值与预期 | 三情景估值（Bear/Base/Bull）、市场隐含预期反推 |
| 风险与证伪 | 反向论证（Bear Case）、证伪条件与阈值 |
| 四层判断 | 公司判断、估值判断、账户判断、复盘判断 |
| 质量校核 | Data Integrity Hardlock + Gatekeeper 准出状态 |
| 复盘闭环 | 下次复盘条件与触发变量 |

完整报告使用 25 个规范章节模板，详见 [`templates/`](templates/) 目录。

---

## 完整分析链路

```text
研究请求
→ 市场与行业适配
→ 宏观周期与板块轮动分析
→ 公司基本面与竞争格局
→ 估值与市场隐含预期
→ 账户约束与风险
→ 反向论证与证伪条件
→ 生成标准投研报告
→ Data Integrity Hardlock
→ Gatekeeper 准出校验
→ 准出状态与复盘条件
```

这个流程的目标是：**防止 AI 直接跳到结论。** 每个关键判断必须有数据来源、反方证据和证伪条件。

---

## 两种使用方式

### 路径 A：生成完整投研报告

仓库提供 `SKILL.md`、`agents/`（10 个 Agent 角色）、`workflows/`（10 个工作流）和 `templates/`（17 个模板），用于指导 AI Agent 按照固定分析顺序完成全链路研究。

> **说明：** 当前尚无统一的 Agent 安装器或端到端编排脚本。AI Agent 的具体宿主运行说明将在后续版本补充。现阶段，用户可将 SKILL.md、对应 workflow 和模板手动加载到支持的 AI Agent 环境中使用。

### 路径 B：校核已有报告

使用现有 Python 工具对已有报告进行结构和数据校核：

```bash
# Gatekeeper 准出检查（三层 + 三档 + 三模式）
python tools/report_gatekeeper.py reports/REPORT.md --language zh

# 数据完整性硬锁
# 通过 Gatekeeper 的 --hardlock-file 参数或程序化调用

# 空泛短语检测
python tools/contradiction_hunter.py reports/REPORT.md
```

Gatekeeper 会在报告交付前检查章节存在性、语言合规性、内容深度和 10 条准出降级规则，确保不合格的报告不会被当作正式交付。

---

## SAMPLE 研究准出展示

以下示例展示了经纬投研引擎的准出流程，使用虚拟标识 `SAMPLE`，不包含真实公司、价格或投资建议：

- [`reports/SAMPLE_research_dashboard_zh.md`](reports/SAMPLE_research_dashboard_zh.md) — 研究准出仪表盘
- [`reports/SAMPLE_research_report_zh.md`](reports/SAMPLE_research_report_zh.md) — 标准报告模板（含 TODO 占位符，被 Gatekeeper 拒绝属于预期行为）

**离线 Demo：** 运行 `python scripts/run_demo.py` 可体验完整链路（虚构数据 → 报告 → 校核 → 准出）。Demo 得到 `PASS_TEST_ONLY` 表示合成报告的数据卡、来源策略、Hardlock 和 Gatekeeper 合约均已通过，但 **不具备生产准出资格**（`TEST_ONLY_NOT_RELEASABLE` / `LOCKED`）。它不验证真实市场数据，也不代表任何投资结论。

核心区别：

```text
普通 AI 股票分析：直接给结论。
经纬投研引擎：先检查结论是否有资格被交付。
```

---

## 当前能力边界

| 层级 | 内容 |
|---|---|
| 当前可直接运行 | Python 计算工具（宏观评分、点位精算、估值场景、反向 DCF 等）、Data Card、Data Integrity Hardlock、Gatekeeper |
| 通过 AI Agent 工作流完成 | 宏观分析、行业研究、公司基本面、竞争格局、估值建模、反向论证和完整报告生成 |
| 当前不提供 | 自动实时数据终端、券商连接、自动交易、收益承诺、统一 Agent 安装器 |

---

## v2.2 数据来源与准出体系

### 来源等级策略（Source Policy）

所有进入研究结论的数据必须携带 **Data Card**，并按来源可靠性分为五级：

| 等级 | 最大权限 | 可进入结论 | 典型来源 |
|------|---------|-----------|---------|
| **S** | `full` | ✅ 是 | SEC EDGAR / 港交所公告 / 公司经审计财报 |
| **A** | `full` | ✅ 是 | Bloomberg / FactSet / 官方统计 |
| **B** | `reference_only` | 仅参考 | 卖方研报 / 行业媒体 / 聚合器 |
| **C** | `reference_only` | 仅参考 | 未验证聚合器 / 社交媒体 |
| **D** | `blocked` | ❌ 不可 | 未知来源 / 匿名 / 不可追溯 |

每张 Data Card 必须包含以下必填元数据：

```text
basis             — 财务口径 (gaap_actual / non_gaap / management_guidance)
period            — 数据期间 (TTM / FY2024 / Q1 2025)
source_tier       — 来源等级 (S / A / B / C / D)
can_enter_conclusion — 请求权限 (full / reference_only / blocked)
freshness_status  — 时效性 (current / stale / unknown)
has_conflict      — 是否存在冲突数据 (true / false)
```

任何 `freshness_status` 不在 `{current, stale, unknown}` 的值将被拒绝。存在冲突数据（`has_conflict=true`）或过期数据（`stale`）不能进入正式结论。

**估值分母**（`valuation_denominator`）被列为关键字段，必须由 S/A 级 Data Card 以 `full` 权限提供。

### Data Integrity Hardlock

正式准出必须通过四层数据硬锁：

```text
No card, no conclusion.         → 无 Data Card，不可进入结论。
No basis, no formal valuation.  → 无财务口径，不可正式估值。
No bridge, no PE.               → 无股本桥接，不可使用 PE。
No industry hard fields, no FULL_PASS. → 行业硬字段缺失，不可通过。
```

### Gatekeeper 准出状态

| 状态 | 含义 | 可正式发布 | 可测试 |
|------|------|-----------|--------|
| `PASS_FORMAL` | 所有数据卡、来源策略、Hardlock 均通过 | ✅ | ✅ |
| `PASS_TEST_ONLY` | 合约完整性通过，但数据为合成/测试数据 | ❌ | ✅ |
| `FAIL_DATA_HARDLOCK` | 数据硬锁失败 | ❌ | ❌ |

合成数据（`data_provenance=SYNTHETIC_FIXTURE`）最多只能获得 `PASS_TEST_ONLY`，不可进入生产准出。

### 报告绑定与验证（Validator）

`scripts/validate_agent_report.py` 在 Gatekeeper 之前执行三项检查：

1. **绑定检查**：报告元数据（research_id、symbol、market、as_of_date、bundle_sha256）与 Research Bundle 是否一致
2. **Bundle Hash 验证**：Bundle 引用的所有外部文件（data_cards、industry_fields）参与递归哈希，任何内容变更都会改变哈希值
3. **路径安全**：拒绝绝对路径和父目录逃逸

```bash
python scripts/validate_agent_report.py \
  --report outputs/agent_demo/SAMPLE_MANAGED_CARE_agent_report_bound_zh.md \
  --bundle examples/full_chain_sample/research_bundle.json \
  --output validation_result.json
```

绑定失败时 Gatekeeper 不会被调用，防止数据错配的报告进入校核流程。

---

## 快速体验

```bash
git clone https://github.com/pencilyu1102-pixel/meridian-research-engine-v2.git
cd meridian-research-engine-v2
pip install -r requirements.txt

# 运行全部测试（127 passed）
python -m pytest -q

# 宏观六因子评分
python tools/macro_score.py --growth 1 --inflation 0 --liquidity 1 --credit 0 --earnings 1 --risk 0

# 点位精算引擎
python tools/price_level_engine.py --eps 10.00 --ticker SAMPLE --multiples 12,15,18,20

# Gatekeeper 准出检查（两条等价格式）
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
python tools/report_gatekeeper.py --file reports/SAMPLE_research_report_zh.md --language zh
```

> 以上是独立的计算和校核工具，不是完整 AI 研报生成器。完整投研报告需要 AI Agent 配合 SKILL.md、workflows 和 templates 完成。

```bash
# 离线全链路 Demo（合成数据 → 报告 → Hardlock → Gatekeeper）
python scripts/run_demo.py

# 报告绑定验证（Validator → Hardlock → Gatekeeper）
python scripts/validate_agent_report.py \
  --report outputs/agent_demo/SAMPLE_MANAGED_CARE_agent_report_bound_zh.md \
  --bundle examples/full_chain_sample/research_bundle.json \
  --output validation_result.json
```

完整安装、测试和工具说明见 [`docs/quickstart_usage.md`](docs/quickstart_usage.md)。

---

## 适合谁

适合：希望用 AI 完成有来源、有反方证据、有复盘条件的投研研究者和投资者。

不适合：寻找即时荐股、买卖信号或自动交易系统的用户。

---

## 项目边界

本项目**不**做以下事情：

- 不预测短期股价；
- 不输出买入 / 卖出信号；
- 不自动交易；
- 不承诺收益；
- 不替代使用者自己的投资判断；
- 不在公开仓库展示真实持仓、真实成本、真实价格区间或真实操作建议。

它关注的是研究流程本身：数据是否可靠、假设是否清楚、估值是否可解释、反方证据是否充分、结论是否具备复盘条件。

---

## 核心方法与九智能体体系

项目围绕全球股票通用买方研究框架，提供以下核心方法论文档：

| 模块 | 文档 | 用途 |
|---|---|---|
| 市场适配器 | [`docs/market_adapters.md`](docs/market_adapters.md) | 美/中/港/全球四套市场分析框架 |
| 行业适配器 | [`docs/industry_adapters.md`](docs/industry_adapters.md) | 8 种行业收入驱动公式 |
| 基本面驱动模型 | [`docs/fundamental_driver_model.md`](docs/fundamental_driver_model.md) | 收入/利润/现金流/ROIC 驱动树 |
| 竞争与份额模型 | [`docs/competition_share_model.md`](docs/competition_share_model.md) | TAM/SAM/SOM + 价值链 + 护城河 |
| 市场隐含预期 | [`docs/implied_expectation_model.md`](docs/implied_expectation_model.md) | 当前价格隐含了什么 |
| 证伪框架 | [`docs/falsification_framework.md`](docs/falsification_framework.md) | 阈值 + 数据来源 + 触发动作 |
| 数据质量检查 | [`docs/data_quality_checklist.md`](docs/data_quality_checklist.md) | 10 项强制数据校验 |

研究体系由 9 个 Agent 角色协同完成：宏观共识、资产轮动、行业位置、公司基本面、估值安全边际、持仓执行、数据审计、反向论证和主审整合。详见 [`agents/`](agents/) 目录。

核心理念：

```text
先看宏观周期，再看公司。
先看板块轮动，再看行业位置。
公司好，不等于价格好。
价格好，不等于适合当前账户。
数据可靠，不等于数据意义已经被正确解释。
所有核心结论必须可证伪——没有阈值和动作的风险提示，不得视为完整风险分析。
```

---

## v2.1.0-alpha：Data Integrity Hardlock

当前版本将准出机制从「报告结构准出」升级为「数据口径准出」。正式准出必须同时通过 **Data Integrity Hardlock**（四层：Data Card / Earnings Basis / Capital Structure Bridge / Industry Hard Fields）和 Gatekeeper 结构检查。

```text
No card, no conclusion.
No basis, no formal valuation.
No bridge, no PE.
No industry hard fields, no FULL_PASS.
```

---

## 当前版本与路线图

| 项目 | 内容 |
|---|---|
|| 当前版本 | **v2.2.0-beta** (feat/v2.2-full-chain-research-ux) |
|| 首发版本 | v2.0.0-beta |
|| 下一里程碑 | v2.3.0（验证实验室集成） |
|| 仓库 | pencilyu1102-pixel/meridian-research-engine-v2 |

| 版本 | 日期 | 主要变更 |
|---|---|---|
| **v2.2.0-beta** | 2026-07 | 来源政策 SABCD 统一准入、Validator 报告绑定与 Bundle Hash、PASS_TEST_ONLY 准出体系、估值分母关键字段、非法 freshness 拒绝 |
| **v2.1.0-alpha** | 2026-07 | Data Integrity Hardlock：四层数据硬锁 + 10 条准出降级规则，Data Card/Earnings Basis/Capital Bridge/Industry Hard Fields |
| **v2.0.1-beta** | 2026-07 | CI 完善、公开 SAMPLE 边界强化、Gatekeeper CLI 兼容性修复 |
| **v2.0.0-beta** | 2026-07 | 首发：市场/行业适配器、基本面驱动、竞争份额、隐含预期、证伪框架、Gatekeeper v2.1、25 章节模板、综合测试 |

详见 [CHANGELOG.md](CHANGELOG.md)。

---

## 项目来源

原始上游为 MIT License 开源项目 `xbtlin/ai-berkshire`。在该基础上，Ada Pan 与 topgunsyang-dotcom 围绕 AI 投研工作流、数据审计、宏观周期、板块轮动、反向论证、证伪框架与 Gatekeeper 准出机制进行了共创整理和扩展。

本项目不是 AI Berkshire 的官方版本，也不代表任何券商、投顾机构或金融机构。上游版权声明和 MIT License 条款已在 [`LICENSE`](LICENSE) 与 [`NOTICE`](NOTICE) 中保留。

---

## 最终提醒

经纬投研引擎的目的，不是让 AI 更会说服你。它的目的，是让 AI **更难**轻易说服你。

```text
看清大势；识别轮动；核验数据；理解变量；
识别风险；控制仓位；保留现金；等待真正值得承担风险的机会。
```

很多时候，最好的投资动作不是买，也不是卖，而是：**看懂之前，先别动。**

---

## 许可证

MIT License. See [`LICENSE`](LICENSE).

---

English version: [README_EN.md](README_EN.md)
