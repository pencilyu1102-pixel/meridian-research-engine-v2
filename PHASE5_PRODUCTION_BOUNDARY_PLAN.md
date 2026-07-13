# PHASE5 — 生产边界与真实数据接入规划

> 状态：设计草案 | main: `08beb25` | 生产准出：**当前不具备**

---

## 当前不能生产准出 — 一页摘要

v2.2 的 Source Policy、Data Card、Hardlock、Gatekeeper 和 Validator 均已实现并通过 127 项测试，但它们运行在 **合成数据**（`SYNTHETIC_FIXTURE`）上，所有路径被 `PASS_TEST_ONLY` / `LOCKED` 截断。要从测试准出进入生产准出（`PASS_FORMAL`），至少需要：

1. **真实 S/A 级 Data Card** — 当前所有卡片均为合成 Fixture，`source_tier=S/D` 或标记 `SYNTHETIC_FIXTURE`；
2. **真实行情数据** — `current_price`、`market_cap`、`shares_outstanding` 等关键字段从未被真实数据填充；
3. **生产 Data Provenance** — 当前 `data_provenance=SYNTHETIC_FIXTURE`，在 Hardlock 层被强制降级为 `PASS_TEST_ONLY`；
4. **真实账户信息** — `account_action=LOCKED`，无持仓、成本、现金数据；
5. **独立数据接入层** — 当前无任何外部数据终端连接。

在以上条件满足前，MRE v2.2 的生产状态为 **LOCKED**。

---

## 1. 私有真实数据部署边界

### 隔离原则

```
公共仓库 (github.com/pencilyu1102-pixel/meridian-research-engine-v2)
├── 仅含合成数据、SAMPLE 标识、测试 Fixture
├── 不含 API key、凭证、真实公司名、真实行情
└── CI 运行合成 Fixture 测试

私有部署 (本地 / 私有仓库)
├── 真实 Data Card（S/A 级来源）
├── 数据接入配置（API key、凭证管理）
├── 真实行情与财务数据
├── 账户信息（持仓、成本、现金）
└── 生产报告输出
```

### 具体措施

| 边界项 | 公共仓库 | 私有部署 |
|--------|---------|---------|
| `data_provenance` | `SYNTHETIC_FIXTURE` | `REAL_PRODUCTION` |
| 来源等级 | 仅合成 SAMPLE | S/A 真实来源 |
| 公司标识 | `SAMPLE_MANAGED_CARE` 等 | 实际 ticker |
| 行情数据 | 虚构值 | 交易所/数据终端 |
| 凭证/密钥 | 禁止 | 通过环境变量/私有配置文件 |
| 账户信息 | 无 | 私有配置文件 |
| Git 跟踪 | `outputs/` 不纳入 | 私有仓库自行管理 |

### 文件隔离清单

以下文件/目录 **禁止** 进入公共仓库：
- 包含真实 ticker 或公司名的 Data Card
- 包含 API key 或凭证的任何文件
- `outputs/production/` 目录
- 真实行情 JSON
- 账户执行报告

---

## 2. S/A 级来源接入接口

### 数据提供者接口（规划）

```text
DataSource (抽象)
├── fetch_financials(ticker, period) → DataCard[]
├── fetch_price(ticker) → DataCard
├── fetch_shares(ticker) → DataCard
└── verify_freshness(card) → freshness_status

Concrete implementations (私有部署, 示例):
├── SECEdgarSource      → EDGAR 10-K/10-Q (S-tier)
├── ExchangePriceSource → 交易所行情 (A-tier)
├── TerminalSource      → 专业数据终端 (A-tier, 示例: Bloomberg/FactSet)
└── AggregatorSource    → 金融数据聚合器 (A-tier, 示例: Refinitiv)
```

### Data Card 生成规则

每个接入源在生成 Data Card 时必须：

1. 声明 `source_tier`（S 或 A）
2. 填入 `basis`（gaap_actual / non_gaap）
3. 填入 `period`、`timestamp`
4. 设置 `freshness_status=current`
5. 设置 `has_conflict` 基于交叉验证结果
6. 请求权限 `can_enter_conclusion=full`

### 凭证管理

```
凭证存储：
  环境变量：MRE_DATA_SOURCE_KEY, MRE_MARKET_DATA_KEY
  私有配置文件：~/.mre/credentials.yaml (gitignored)
  不在代码中硬编码
  不在公共仓库提交
```

---

## 3. 生产数据校验流程

### freshness 校验

| 状态 | 含义 | 数据年龄 | 准入 |
|------|------|---------|------|
| `current` | 最新可得数据 | < 1 季度 | full |
| `stale` | 过期但仍可用 | 1-2 季度 | reference_only |
| `unknown` | 无法确认时效 | 不可知 | blocked |

生产部署后需实现：
- 每个数据源的 `last_updated` 时间戳自动比对
- 季度报告发布后自动标记上一季度数据为 `stale`

### conflict 冲突检测

```
Card A (S-tier, gaap_actual):  EPS = $5.70
Card B (A-tier, aggregator):  EPS = $5.45
→ has_conflict = true
→ Card B 降级为 reference_only
→ 估值以 Card A 为准
```

需实现：
- 同字段、多来源的交叉验证
- 偏差超过阈值（如 5%）自动标记冲突
- 冲突卡片自动降级，不可进入正式结论

### critical fields 强制校验

生产环境中必须验证以下字段均由 S/A 级 `full` 权限 Data Card 提供：

```
current_price, market_cap, eps_ttm, eps, revenue_ttm,
shares_outstanding, current_shares, valuation_denominator
```

任一关键字段无 `full` 权限 → Hardlock `FAIL_DATA_HARDLOCK`

---

## 4. 从 PASS_TEST_ONLY 到 PASS_FORMAL 的必要条件

当前 `build_hardlock_from_bundle()` 中，`data_provenance=SYNTHETIC_FIXTURE` 触发强制降级：

```python
if data_provenance == PROVENANCE_SYNTHETIC:
    violations.append("synthetic fixture data — not formally releasable")
    status = STATUS_PASS_TEST_ONLY
```

生产准出需要 **同时满足**：

| 条件 | 检查位置 | 当前状态 |
|------|---------|---------|
| `data_provenance != SYNTHETIC_FIXTURE` | Hardlock | ❌ 当前为 SYNTHETIC_FIXTURE |
| 所有关键字段有 S/A full 卡 | Source Policy | ❌ 当前无真实卡 |
| 所有卡片 `freshness_status=current` | Source Policy | ❌ 待实现 |
| 无冲突数据进入结论 | Source Policy | ❌ 待实现交叉验证 |
| `has_conflict=false` 对结论卡 | Source Policy | ❌ 待实现 |
| 行业硬字段完整 | Industry Hard Fields | ❌ 当前为合成 |
| 股本桥接通过 | Capital Bridge | ❌ 当前为合成 |
| 账户信息真实且完整 | 账户层 | ❌ 待实现 |
| 报告绑定通过 | Validator | ✅ 已实现 |
| Gatekeeper 结构检查通过 | Gatekeeper | ✅ 已实现 |

---

## 5. 准出策略

### 三态模型

```
PASS_FORMAL     ← 全部条件满足，可交付正式投研结论
PASS_TEST_ONLY  ← 合约完整性通过，数据不可生产（当前状态）
FAIL_DATA_HARDLOCK ← 数据硬锁失败，不可交付
```

### 失败回退

| 场景 | 触发条件 | 回退动作 |
|------|---------|---------|
| 数据源不可用 | API 超时/凭证失效 | 降级到 `stale` 缓存，标注 `freshness=stale` |
| 关键字段缺失 | 数据终端无返回 | `FAIL_DATA_HARDLOCK`，报告不可准出 |
| 冲突数据 | 多源偏差 > 5% | 标记冲突，低优先源降级 |
| 时效过期 | 数据年龄 > 2 季度 | 降级为 `stale`，报告仅参考 |

---

## 6. CI 契约测试与合成边界

### 应持续执行的测试

| 测试类别 | 内容 | 触发 |
|---------|------|------|
| 合成 Fixture 全量 | 127 tests | 每次 push |
| 合成边界检查 | 扫描无真实 ticker/公司名 | 每次 push |
| PASS_TEST_ONLY 永不为 PASS_FORMAL | 合成数据不可生产准出 | 每次 push |
| Source Policy 权限矩阵 | SABCD + freshness/conflict | 每次 push |
| Validator 绑定 | 127 tests 中的 binding 子集 | 每次 push |
| 路径安全 | 绝对路径/父目录逃逸拒绝 | 每次 push |

### CI 禁止项

- 任何真实行情请求
- 依赖外部 API 的测试
- 包含真实 ticker 或公司名的 Fixture

---

## 7. 尚未具备的能力

```
[UNKNOWN] 实时数据终端集成      — 未选择具体数据源，无 API 适配器实现
[UNKNOWN] 凭证管理与加密存储     — 未实现，仅规划了环境变量方案
[UNKNOWN] 多源交叉验证引擎       — 冲突检测逻辑已就绪，无真实数据源触发
[UNKNOWN] 生产报告输出管道       — Demo 仅输出合成报告，无生产格式定义
[UNKNOWN] 真实账户持仓执行       — 账户模型需要真实持仓/成本/现金输入
[UNKNOWN] 自动复盘调度           — Phase 4 文档提到复盘闭环，无实现代码
[UNKNOWN] 产品化部署与运维       — 无 Dockerfile、健康检查、日志聚合
```

---

## 实现优先级

| 优先级 | 项目 | 阻塞项 | 预计阶段 |
|--------|------|--------|---------|
| P0 | 真实 Data Card 接入（至少 1 个 S-tier 源） | 数据源选择 | Phase 6 |
| P0 | 生产 `data_provenance` 模式 | 真实数据卡存在 | Phase 6 |
| P1 | 真实行情数据接入 | API 凭证 | Phase 6 |
| P1 | 冲突交叉验证 | 至少 2 个独立数据源 | Phase 7 |
| P1 | 账户信息接入 | 私有配置文件 | Phase 7 |
| P2 | CI 集成真实数据测试 | 私有 CI 环境 | Phase 7 |
| P2 | 自动复盘调度 | 全部前置条件 | Phase 8 |
| P3 | 产品化部署 | Docker/监控 | Phase 8+ |

---

## 当前状态

```
main HEAD:      08beb25
Tests:          127 passed
Demo:           PASS_TEST_ONLY / TEST_ONLY_NOT_RELEASABLE / LOCKED
Validator:      PASS_TEST_ONLY / LOCKED
Synthetic data: PASS (0 real company references)
Production:     NOT ELIGIBLE
```

生产代码不变。Tag/release 未创建。等待人工批准 Phase 5 设计后进入实现阶段。
