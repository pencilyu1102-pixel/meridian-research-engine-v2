# PHASE6 — DataSource 接口设计

> 状态：设计草案 | main: `85fb04d` | 实现：**尚未开始**

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
[UNKNOWN] DataSource 抽象基类         — 尚未实现，本文档为接口规范
[UNKNOWN] SyntheticDataSource         — 尚未实现，可作为 Phase 6 最小可行的公共仓库交付物
[UNKNOWN] 任一真实数据源适配器         — 无 SEC/Bloomberg/交易所适配器
[UNKNOWN] 凭证管理与加密存储           — 仅设计约束，无实现
[UNKNOWN] 重试与指数退避               — 仅设计策略，无实现
[UNKNOWN] 多源交叉验证引擎             — 冲突检测逻辑在 source_policy 中已有 has_conflict 字段，但无触发来源
[UNKNOWN] 自动时效窗口计算             — freshness_status 由 DataSource 实现自行判断，无统一窗口逻辑
[UNKNOWN] 全链路追踪                   — request_id 链路设计中，但无 tracing 基础设施
```

---

## 当前状态

```
main HEAD:      85fb04d
Tests:          127 passed
Demo:           PASS_TEST_ONLY / TEST_ONLY_NOT_RELEASABLE / LOCKED
Validator:      PASS_TEST_ONLY / LOCKED
Production:     NOT ELIGIBLE
```

生产代码不变。Tag/release 未创建。等待人工批准 Phase 6 设计后进入实现。
