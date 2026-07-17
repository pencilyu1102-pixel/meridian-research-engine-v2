# PHASE6 — DataSource 接口设计

> 状态：**Phase 6.1 已实现，Phase 6.2 已实现，Phase 6.3 已实现** | main: `a95d0f6` | Phase 6.3 head: `d18f0e9` Draft PR: [#14](https://github.com/pencilyu1102-pixel/meridian-research-engine-v2/pull/14) CI: ✅

---

## 设计目标

定义一套最小的 DataSource 抽象接口，规范外部数据如何进入 MRE v2.2 的 Data Card → Source Policy → Hardlock → Gatekeeper 管线。本设计不包含任何真实供应商适配器实现。

---

## 1. 架构位置

```
┌─────────────────────────────────────────────────┐
│  DataSource (抽象接口)                            │
│  fetch() → 标准化 Data Card 或 FetchFailure       │
└──────────────┬──────────────────────────────────┘
               │ 输出: DataCard dict
               ▼
┌─────────────────────────────────────────────────┐
│  Data Card Registry (data_card_registry.py)      │
│  validate_data_card() → CardValidationResult     │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  Source Policy (source_policy.py)                │
│  check_source_admission() → SourcePermission     │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  Hardlock → Gatekeeper → 准出状态                 │
└─────────────────────────────────────────────────┘
```

**DataSource 只负责获取和标准化，不参与准出判断。**

---

## 2. fetch() 接口

### 输入：FetchRequest

```text
FetchRequest:
  symbol:       str        # 标的标识 (ticker 或内部 ID)
  field:        str        # 请求字段名 (eps_ttm / current_price / revenue_ttm / …)
  as_of:        str | None # 截止日期 (ISO 8601)，None 表示最新
  period:       str | None # 数据期间 (TTM / FY2024 / Q1 2025)
  request_id:   str        # 请求追踪 ID，用于审计日志
  context:      dict       # 额外上下文 (市场、货币、数据源偏好)
```

### 输出：Union[DataCard, FetchFailure]

成功时返回符合 `schemas/data_card.schema.json` 的 DataCard dict。

```text
DataCard (必填字段，映射到现有 schema):
  field_name:           str    # 与 FetchRequest.field 一致
  value:                Any    # 数值或结构化值
  source:               str    # 数据源标识 + 原始响应摘要
  source_tier:          "S"|"A"|"B"|"C"|"D"
  timestamp:            str    # 抓取时间 (ISO 8601)
  period:               str    # 数据期间
  unit:                 str    # 单位 (shares / USD / CNY / ratio / …)
  currency:             str    # 货币 (USD / CNY / HKD / …)
  accounting_basis:     str    # 财务口径 (gaap_actual / non_gaap / …)
  can_enter_conclusion: "full"|"reference_only"|"blocked"
  notes:                str    # 原始响应摘要 + 抓取元数据
  freshness_status:     "current"|"stale"|"unknown"
  has_conflict:         bool
  data_provenance:      str    # 来源溯源标识
```

失败时返回 FetchFailure：

```text
FetchFailure:
  status:         "FETCH_FAILED"
  reason:         "NETWORK_ERROR"|"FIELD_MISSING"|"PARSE_ERROR"|"AUTH_ERROR"|"TIMEOUT"
  detail:         str       # 人类可读的错误描述
  request_id:     str       # 对应 FetchRequest.request_id
  timestamp:      str       # 失败时间 (ISO 8601)
  retry_allowed:  bool      # 是否可重试
```

---

## 3. 来源等级规则

| 规则 | 说明 |
|------|------|
| 来源等级由 DataSource 实现自行声明 | 每个适配器在构造时声明其 `default_tier`（S/A/B/C/D） |
| 等级不能由供应商名称直接决定 | "Bloomberg" 这个名字不能自动获得 A-tier；适配器必须显式声明 |
| `full/reference_only/blocked` 由 `source_policy` 决定 | DataSource 只产出卡片，`check_source_admission()` 统一判断准入 |
| DataSource 可建议权限 | `can_enter_conclusion` 字段携带建议值，但最终由 Source Policy 裁定 |
| 降级优先 | 当不确定来源可靠性时，DataSource 应选择更严格的 tier |

---

## 4. freshness 处理

| 数据源状态 | freshness_status | 触发条件 |
|-----------|-----------------|---------|
| 实时/最新可得 | `current` | 抓取时间与报告期在允许窗口内（默认 1 季度） |
| 过期但仍可用 | `stale` | 抓取时间超出窗口，但数据本身可信 |
| 无法确认 | `unknown` | 数据源不提供时间戳、或抓取失败后使用缓存 |

```text
[INFERENCE] 时效窗口（1 季度）是设计假设；实际阈值可能因数据源类型而异。
[UNKNOWN] 自动时效标记逻辑尚未实现。
```

---

## 5. conflict 处理

DataSource 本身不判断冲突——它只产出单张卡片。冲突检测由调用方完成：

```text
1. 对同一 field_name，从多个 DataSource 获取卡片
2. 比较 values → 偏差超过阈值 → 标记 has_conflict=true
3. 低优先源降级 → can_enter_conclusion=reference_only
4. 高优先源保持 full
```

```text
[INFERENCE] 偏差阈值（如 5%）是设计假设。
[UNKNOWN] 多源交叉验证引擎尚未实现。
```

---

## 6. 失败回退策略

| 失败类型 | `retry_allowed` | 回退动作 |
|---------|----------------|---------|
| `NETWORK_ERROR` | true | 重试 3 次（指数退避），仍失败则返回 FetchFailure |
| `TIMEOUT` | true | 同上 |
| `FIELD_MISSING` | false | 返回 FetchFailure，标注缺失字段 |
| `PARSE_ERROR` | false | 返回 FetchFailure，保留原始响应片段用于调试 |
| `AUTH_ERROR` | true | 重试 1 次（刷新凭证），仍失败则返回 FetchFailure |

```text
[INFERENCE] 重试策略是设计假设。
[UNKNOWN] 凭证刷新机制尚未实现。
```

---

## 7. 可追溯性

每个 DataCard 和 FetchFailure 必须携带：

| 字段 | 来源 | 用途 |
|------|------|------|
| `source` | DataSource 实现 | 标识哪个适配器 + 原始响应的摘要指纹 |
| `timestamp` | 抓取时刻 | 审计时间线 |
| `request_id` | FetchRequest | 关联请求与响应，支持全链路追踪 |
| `notes` | DataSource 实现 | 原始响应摘要（截断），保留关键字段供事后查验 |
| `data_provenance` | 系统注入 | 标识数据归属（SYNTHETIC_FIXTURE / 生产标识） |

---

## 8. 与现有模块的契约边界

| 模块 | 职责 | DataSource 是否调用 |
|------|------|-------------------|
| `data_card_registry.py` | 结构校验（schema + 必填字段） | ✅ 调用方在 fetch() 返回后调用 |
| `source_policy.py` | 来源准入（tier → permission） | ✅ 调用方在 Registry 通过后调用 |
| `tool_metadata_guard.py` | 元数据必填字段检查 | ✅ 调用方决定是否调用 |
| `data_integrity_hardlock.py` | 四层硬锁聚合 | ❌ DataSource 不感知 |
| `report_gatekeeper.py` | 报告准出 | ❌ DataSource 不感知 |
| `validate_agent_report.py` | 报告绑定 + Bundle Hash | ❌ DataSource 不感知 |

DataSource 的上游是外部世界，下游是 Data Card Registry。它不知道 Hardlock 或 Gatekeeper 的存在。

---

## 9. 部署边界

```
公共仓库:
  - 此设计文档 (PHASE6_DATASOURCE_INTERFACE_DESIGN.md)
  - DataSource 抽象基类 (待实现)
  - SyntheticDataSource (仅返回合成 Fixture)
  - 不包含任何真实数据源适配器

私有部署:
  - 真实 DataSource 适配器 (SECEdgarSource, ExchangePriceSource, …)
  - 凭证配置文件 (~/.mre/credentials.yaml)
  - 真实行情与财务数据
```

---

## 10. 尚未具备

```text
[UNKNOWN] DataSource 抽象基类         — ✅ Phase 6.1 已实现 (tools/data_source.py)
[UNKNOWN] SyntheticDataSource         — ✅ Phase 6.1 已实现 (tools/synthetic_data_source.py)
[UNKNOWN] 任一真实数据源适配器         — 无 SEC/Bloomberg/交易所适配器
[UNKNOWN] 凭证管理与加密存储           — 仅设计约束，无实现
[UNKNOWN] 重试与指数退避               — 仅设计策略，无实现
[UNKNOWN] 多源交叉验证引擎             — 冲突检测逻辑在 source_policy 中已有 has_conflict 字段，但无触发来源
[UNKNOWN] 自动时效窗口计算             — freshness_status 由 DataSource 实现自行判断，无统一窗口逻辑
[UNKNOWN] 全链路追踪                   — request_id 链路设计中，但无 tracing 基础设施
[COMPLETED] request_id / data_provenance 全局 schema 化 — ✅ Phase 6.2 已完成：Schema required + Registry 强制非空 + Bundle provenance 一致性校验
```

---

## 当前状态

```
main HEAD:      a95d0f6
Phase 6.1 分支: feat/phase6.1-datasource-mvp (merged via PR #12)
Phase 6.2 分支: feat/phase6.2-traceability-migration (merged via PR #13)
Phase 6.3 分支: feat/phase6.3-datasource-runner (committed through d18f0e9, Draft PR #14, CI success)
Tests:          210 passed (186 baseline + 24 runner), 0 skipped, 0 xfailed, 0 deselected
Demo:           PASS_TEST_ONLY / TEST_ONLY_NOT_RELEASABLE / LOCKED
Validator:      Binding PASS / Hardlock PASS_TEST_ONLY / Production False / LOCKED
Production:     NOT ELIGIBLE
```

---

## Phase 6.1 实现摘要

> 完成日期: 2026-07-15

### 新增文件

| 文件 | 说明 |
|------|------|
| `tools/data_source.py` | FetchRequest / FetchFailure / DataSource 抽象类 / build_data_card() |
| `tools/synthetic_data_source.py` | SyntheticDataSource — fixture 驱动的测试适配器 |
| `tests/test_data_source_contract.py` | 38 项契约测试 |
| `tests/fixtures/data_sources/synthetic_source_records.json` | 7 条覆盖 S/B/C/D/Tier/Stale/Conflict 的合成记录 |

### 实现边界

- ✅ DataSource 复用 source_policy.effective_permission()，不复制权限规则
- ✅ SyntheticDataSource 固定 PROVENANCE_SYNTHETIC
- ✅ B-tier 请求 full → 自动截断为 reference_only
- ✅ D-tier 请求任何权限 → 自动截断为 blocked
- ✅ stale / unknown freshness / has_conflict → 无法进入正式结论
- ❌ 未修改 Hardlock / Gatekeeper / Bundle / Validator / 全局 Schema
- ❌ 无网络请求、无 API Key、无凭证、无真实数据
- ❌ 无 retry、cache、production 模式、自动 freshness

### 未实现能力

- 真实数据源适配器（Bloomberg / FactSet / SEC / 交易所）
- 多源交叉验证、自动时效窗口、重试与退避
- 全链路 tracing 基础设施

### Phase 6.2 实施摘要

> 完成日期: 2026-07-16
> 状态: merged via PR #13

**变更:**
- `schemas/data_card.schema.json` — required + properties 加入 request_id / data_provenance
- `tools/data_card_registry.py` — REQUIRED_FIELDS 追加两个字段，非空校验，provenance 一致性校验（外部参数不覆盖）
- 9 个 JSON Data Card fixture（19 张卡片）补齐 request_id + data_provenance
- `tests/test_validate_agent_report.py` `_base_card()` 补齐两个字段
- `tests/test_data_card_registry.py` 内联卡片迁移 + 8 个新增契约测试
- Bundle Hash 重算 + bound report 同步
- `synthetic_source_records.json` 故意不迁移（DataSource 原始记录，由实例注入）

**未修改:**
- Hardlock / Gatekeeper / Validator / CI / README
- tools/data_source.py / tools/synthetic_data_source.py / tools/source_policy.py

### 仍不具备生产资格

本阶段交付物为接口桩与契约测试。SyntheticDataSource 仅用于验证接口设计。**不构成生产数据入口。**

生产代码不变。Merged via PR #13. Tag/release not created.

### Phase 6.3 实施摘要

> 开始日期: 2026-07-16
> 状态: committed through `d18f0e9`, Draft PR [#14](https://github.com/pencilyu1102-pixel/meridian-research-engine-v2/pull/14), CI success

**变更:**
- `tools/data_source_runner.py` — `DataSourceRunResult` / `DataSourceBatchResult` / `run_fetch()` / `run_batch()`。批量计数由 `__post_init__` 自动从 `results` 派生，调用者不可注入。
- `tests/test_data_source_runner.py` — 24 项契约测试覆盖四类状态、绑定检查、批量聚合、计数防注入

**Runner 职责:**
- 统一 `DataSource.fetch()` → `validate_data_card()` → `check_source_admission()` 管线
- 请求—响应绑定校验（request_id / field_name / data_provenance）
- 四类状态：`CARD_VALIDATED` / `FETCH_FAILED` / `CONTRACT_FAILED` / `VALIDATION_FAILED`
- 批量执行保持输入顺序，fail-fast 重复 request_id

**边界:**
- 不负责生产准出（production_research_eligible / account_action / report_release）
- 不复制 Registry / Source Policy 规则
- 不修改 DataSource 返回的 Card
- External provenance 只校验不覆盖
- 不引入网络、retry、cache、真实数据源
- 未接入 Demo / Validator
