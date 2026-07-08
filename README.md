# Meridian Research Engine 2.0｜经纬投研引擎 2.0

Meridian Research Engine 2.0｜经纬投研引擎 2.0 是一个本地运行的 AI 投研审计与研究准出引擎，也是面向个人投资者和研究者的全球股票通用买方研究框架。

它不是 AI 荐股系统，不预测股价，不输出买卖信号，也不替代投资决策。

它解决的是另一个问题：

> 当 AI 给出一个看似完整的投资观点时，如何确认它的数据、假设、估值、反方证据、仓位约束和复盘条件是否真的成立？

项目以宏观周期、板块轮动、数据审计、基本面驱动、竞争份额、隐含预期反推、反向论证与 Gatekeeper 准出校验为核心，把一篇 AI 投研报告从"看起来有道理"推进到"可以被审计、可以被反驳、可以被复盘"。

---

## 这不是一个 AI 荐股系统

本项目不做以下事情：

- 不预测短期股价；
- 不输出买入 / 卖出信号；
- 不自动交易；
- 不承诺收益；
- 不替代使用者自己的投资判断；
- 不在公开仓库展示真实持仓、真实成本、真实价格区间或真实操作建议。

它关注的是研究流程本身：

```text
数据是否可靠？
假设是否清楚？
估值是否可解释？
反方证据是否充分？
账户动作是否被过早输出？
结论是否具备复盘条件？
```

---

## Demo：研究准出仪表盘

经纬投研引擎不会直接输出"买入 / 卖出 / 目标价"作为最终结论，而是先判断一份研究报告是否具备正式准出条件。

示例：

- [`reports/SAMPLE_research_dashboard_zh.md`](reports/SAMPLE_research_dashboard_zh.md)
- [`reports/SAMPLE_research_report_zh.md`](reports/SAMPLE_research_report_zh.md)

核心区别：

```text
普通 AI 股票分析：直接给结论。
经纬投研引擎：先检查结论是否有资格被交付。
```

---

## 版本信息

| 项目 | 内容 |
|---|---|
| 项目英文名 | Meridian Research Engine 2.0 |
| 中文名 | 经纬投研引擎 2.0 |
| 当前版本 | v2.1.0-alpha |
| 首发版本 | v2.0.0-beta |
| 仓库 | pencilyu1102-pixel/meridian-research-engine-v2 |

English version: [README_EN.md](README_EN.md)

---

## v2.1.0-alpha: Data Integrity Hardlock

`v2.1.0-alpha` 将经纬投研引擎从“报告结构准出”进一步升级为“数据口径准出”。

正式准出不再只依赖报告结构完整性，而必须同时通过 **Data Integrity Hardlock**。

四层 hardlock 为：

1. Data Card
2. Earnings Basis
3. Capital Structure Bridge
4. Industry Hard Fields

必须明确：

```text
Gatekeeper 的 FULL_PASS 只有在 Hardlock = PASS_FORMAL 时，才代表正式可准出。
```

这意味着系统不再只检查“报告像不像一份完整报告”，还要检查“进入结论层的数据字段是否具备正式准出资格”。

简化理解：

```text
No card, no conclusion.
No basis, no formal valuation.
No bridge, no PE.
No industry hard fields, no FULL_PASS.
```

本项目仍然不是投资建议工具，不是荐股系统，也不提供自动交易或买卖信号。

---

## 快速开始

完整本地运行、测试和核心工具命令见：

- [`docs/quickstart_usage.md`](docs/quickstart_usage.md)

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

## 核心模块文档

首发版本包含**全球股票通用买方研究框架**，并提供 7 个核心模块文档：

| 模块 | 文档 | 用途 |
|---|---|---|
| 市场适配器 | [`docs/market_adapters.md`](docs/market_adapters.md) | 美/中/港/全球市场分析重点，含币种、会计口径、政策、资金拥挤度 |
| 行业适配器 | [`docs/industry_adapters.md`](docs/industry_adapters.md) | 8 种行业收入驱动公式（半导体/软件/互联网/消费/周期/金融/医药/公用） |
| 基本面驱动模型 | [`docs/fundamental_driver_model.md`](docs/fundamental_driver_model.md) | 收入/利润/现金流/ROIC 四棵驱动树的构建和拆解方法 |
| 竞争与份额模型 | [`docs/competition_share_model.md`](docs/competition_share_model.md) | TAM/SAM/SOM、价值链、护城河、竞争对手反推 |
| 市场隐含预期模型 | [`docs/implied_expectation_model.md`](docs/implied_expectation_model.md) | 当前价格隐含了什么增长/利润率/倍数/份额 |
| 证伪框架 | [`docs/falsification_framework.md`](docs/falsification_framework.md) | 核心判断的可证伪条件和阈值设定原则 |
| 数据质量检查清单 | [`docs/data_quality_checklist.md`](docs/data_quality_checklist.md) | 10 项强制数据校验（口径、时间、币种、One-time 调整等） |

---

## 语言规则

报告必须根据使用者选择或输入语言生成单一语言版本，避免中英文标题混排。

- 中文请求：使用中文报告模板（25 个规范二级标题）；
- 英文请求：使用英文报告模板（25 个规范二级标题）；
- 用户明确指定语言时，以用户指定为准；
- 股票代码、命令、路径、模块名、公式、引用来源可保留原文；
- 标题、表头、解释段落、结论、复盘条件必须使用同一种语言。

语言策略详见：

- [`docs/language_policy.md`](docs/language_policy.md)

---

## 标准报告模板

不要直接填写 `templates/standard_research_report.md`，它只是语言选择入口。

根据报告语言选择模板：

- 中文报告：[`templates/standard_research_report_zh.md`](templates/standard_research_report_zh.md)（25 个规范二级标题）
- 英文报告：[`templates/standard_research_report_en.md`](templates/standard_research_report_en.md)（25 个规范二级标题）

标准报告必须区分四层判断：

```text
公司判断：这是不是一家好公司；
估值判断：现在这个价格贵不贵；
账户判断：结合真实仓位和成本，现在能不能动；
复盘/操作状态：当前是观察、复盘、等待、降风险，还是资料不足。
```

这四层不能混在一起。公司好，不等于价格好；价格好，也不等于适合当前账户。

**模板使用规则：**
- 正式报告必须保留所有 `##` 二级标题；
- 若某章节不适用，写明"不适用 + 原因"，不得删除章节；
- Gatekeeper 模式：`formal`（默认，正式准出）/ `core`（框架能力测试）/ `smoke`（快速检查）。

---

## Gatekeeper v2.1 — 报告准出校验

`tools/report_gatekeeper.py` 是Meridian Research Engine 2.0的**内容级准出校验系统**，在报告交付前自动检查章节存在性、语言合规性和内容深度。

Gatekeeper v2.1 是本项目区别于普通 AI 股票分析工具的核心模块：它不负责让结论更漂亮，而是负责阻止不合格的报告被交付。

### 三层架构

| 层级 | 检查内容 | 作用 |
|---|---|---|
| Layer 0 | 章节存在性（精确匹配 25 个规范标题） | 确保无遗漏章节 |
| Layer 1 | 语言合规性 + 空泛短语检测（双语标题、"待补充" 等） | 确保语言整洁 |
| Layer 2 | 内容深度（关键模块必备字段检查） | 确保非空壳报告 |
| Layer 3 | 10 条准出降级规则（最高锁至不可准出） | 确保数据完整 |

### 三种运行模式

| 模式 | 用途 | 检查范围 |
|---|---|---|
| `formal`（默认） | 正式准出 | 全部 25 章节精确匹配 + 内容深度 + 语言检查 + 10 条降级规则 |
| `core` | 框架能力测试 | 10 个核心模块模糊匹配 + 内容深度 |
| `smoke` | 快速烟雾测试 | 3 个最容易遗漏的模块（行业适配器、竞争份额、隐含预期） |

### 三档准出结论

| 等级 | 含义 |
|---|---|
| **FULL_PASS / 可准出** | 核心数据、估值口径、驱动模型、竞争模型和证伪指标均完整 |
| **CORE_PASS_TEMPLATE_FAIL / 条件准出** | 核心内容通过，但章节标题不符合规范或存在数据缺口 |
| **HARD_LOCK_FAIL / 不可准出** | 缺少股价/市值/财务数据，无法形成可证伪判断 |

### 10 条准出降级规则

1. 无市场适配器 → 最高条件准出
2. 无行业适配器 → 最高条件准出
3. 无基本面驱动模型 → 最高条件准出
4. 无竞争与份额模型 → 最高条件准出
5. 无市场隐含预期 → 最高条件准出
6. **股价/市值/股本过期或缺失 → 不可准出**
7. **核心数据无来源 → 不可准出**
8. Bear/Base/Bull 无概率或触发条件 → 最高条件准出
9. 无证伪指标 → 最高条件准出
10. 风险缺少阈值和动作 → 最高条件准出

### 运行命令

```bash
# 正式准出（25 章节精确匹配 + 内容深度）
python tools/report_gatekeeper.py reports/REPORT.md --language zh

# 核心模块检查（10 个核心模块，别名模糊匹配）
python tools/report_gatekeeper.py reports/REPORT.md --language zh --mode core

# 快速烟雾测试（3 个最容易遗漏的模块）
python tools/report_gatekeeper.py reports/REPORT.md --language zh --mode smoke

# 英文报告
python tools/report_gatekeeper.py reports/REPORT.md --language en
```

### 已知陷阱

- **市值硬锁假阳性：** 报告中出现 `无` + `市值` 在 20 个字符内会触发 `missing_market_cap` 硬锁。请使用 `空仓` 而非 `无持仓` 规避（详见 SKILL.md）。

---

## 项目能力

| 能力 | 作用 |
|---|---|
| 宏观周期 | 六因子评分（-2~+2），判断宏观环境性质 |
| 板块轮动 | 三道门检查（宏观风向、行业景气、估值拥挤度） |
| 市场适配器 | 按市场选择分析重点（US/CN/HK/GL 四套框架） |
| 行业适配器 | 8 种行业收入驱动公式 + 必填指标 |
| 基本面驱动模型 | 收入/毛利率/费用率/现金流/ROIC 五棵驱动树 |
| 竞争与份额模型 | TAM/SAM/SOM + 价值链 + 护城河 + 竞争对手反推 |
| 市场隐含预期 | 反推当前价格隐含的 CAGR、利润率、份额、倍数 |
| 数据审计 | 审查来源、时间、口径、单位、币种和可靠性 |
| 数据意义解释 | 解释数据说明了什么，而不是只堆数字 |
| 三情景估值 | Bear/Base/Bull + 概率加权价值 |
| Price Level Engine | 多档位价格区间锚（估值锚/市场锚/账户约束/基本面触发） |
| 真实持仓执行 | 区分公司研究和账户动作，检查现金、仓位、成本和风险承受力 |
| 反向论证（Bear Case） | 主动寻找最强反方证据，防止结论过度乐观 |
| 证伪框架 | 核心判断设置阈值 + 数据来源 + 触发动作 |
| 报告准出机制（Gatekeeper v2.1） | 三层检查 + 三档准出，防止数据不全的报告被交付 |

---

## 为什么需要这个项目

直接问 AI：

```text
某家公司现在能不能买？
```

很容易得到这种回答：

```text
公司长期基本面较好，但短期存在不确定性，建议谨慎关注。
```

这类回答看似完整，但通常无法直接用于研究，因为它没有回答几个更关键的问题：

- 当前宏观环境是顺风还是逆风？
- 资金正在流向哪些板块？
- 机构共识是否已经被市场价格反映？
- 数据来源是否可靠？
- 数据到底意味着什么？
- 当前估值是否有安全边际？
- 使用者自己的账户是否允许继续操作？
- 什么情况下结论失效？
- 下一次复盘应该看哪些变量？

Meridian Research Engine 2.0试图解决的不是“AI 会不会分析”，而是：

```text
AI 的分析能不能更有纪律、更可审计、更接近真实投研流程。
```

---

## 标准分析顺序

```text
市场适配器选择（US/CN/HK/GL）
→ 行业适配器选择（8 种行业模型）
→ 宏观共识收集 + 六因子宏观评分
→ 市场定价与共识验证
→ 板块轮动 + 三道门判断
→ 行业位置
→ 公司基本盘（6 维）
→ 数据可信度审计（10 项强制校验）
→ 关键数据卡片 + 核心变量排序
→ 基本面驱动模型（收入→毛利率→费用→现金流→ROIC）
→ 竞争与份额模型（TAM/SAM/SOM→护城河→竞争对手反推）
→ 估值与安全边际（三情景 + 概率加权）
→ 市场隐含预期反推
→ Price Level Engine
→ 真实持仓执行
→ Bear Case / 反向论证
→ 证伪框架（阈值 + 触发动作）
→ 四层判断（公司/估值/账户/复盘）
→ 最终操作方案（四类纪律）
→ 最大风险 + 下次复盘条件
→ Gatekeeper v2.1 准出校验
```

这个流程的目标是：**防止 AI 直接跳到结论。**

正式报告不能只说：

```text
长期看好，短期波动。
估值合理，建议关注。
跌到某个整数点位可以买。
涨到某个整数点位可以卖。
```

而必须说明：

- 为什么这样判断；
- 哪些数据支持；
- 哪些数据反对；
- 当前价格对应什么估值逻辑；
- 当前账户是否允许操作；
- 什么条件下结论失效；
- 下一次复盘看什么。

---

## 工作流入口

| 入口 | 用途 |
|---|---|
| `/macro-sector-rotation` | 宏观与板块轮动分析 |
| `/stock-research` | 单公司完整研究 |
| `/earnings-review` | 财报精读与业绩归因 |
| `/news-pulse` | 股价异动归因 |
| `/portfolio-review` | 持仓复盘与账户执行检查 |
| `/qdii-review` | QDII / ETF 分析 |
| `/industry-funnel` | 行业漏斗筛选 |
| `/buy-checklist` | 买入前检查 |
| `/sell-checklist` | 卖出前检查 |
| `/data-audit` | 数据可信度专项审计 |

示例：

```text
按Meridian Research Engine 2.0跑 /macro-sector-rotation 美股。
输出宏观六因子评分、机构共识与分歧、市场是否已经反映机构共识、顺风板块、承压板块和下阶段观察指标。
```

```text
按Meridian Research Engine 2.0跑 /stock-research TICKER，并使用中文标准报告模板输出。
```

---

## 核心理念

```text
先看宏观周期，再看公司。
先看板块轮动，再看行业位置。
公司好，不等于价格好。
价格好，不等于适合当前账户。
数据可靠，不等于数据意义已经被正确解释。
研究结论，不等于操作指令。
价格点位，不是买卖信号，而是复盘条件。
所有核心结论必须可证伪 —— 没有阈值和动作的风险提示，不得视为完整风险分析。
```

一个完整判断至少要拆成四层：

```text
公司判断：这是不是一家好公司？
估值判断：现在这个价格贵不贵？
账户判断：结合真实仓位和成本，现在能不能动？
交易判断：具体是买、卖、持有，还是等待？
```

这四层不能混在一起。

---

## 宏观与板块轮动引擎

宏观与板块轮动引擎用于把宏观环境翻译成可审计的行业和板块研究判断。

它不直接预测经济，而是综合三类信号：

1. 官方与准官方宏观数据；
2. 主流资管和投行观点；
3. 市场价格与高频指标。

系统围绕六个宏观因子进行分析：

| 因子 | 关注问题 |
|---|---|
| 增长 | 经济是在加速、放缓还是分化？ |
| 通胀 | 通胀是在上行、下行还是保持粘性？ |
| 流动性 | 央行环境是宽松、中性还是收紧？ |
| 信用 | 企业和居民融资是在扩张还是收缩？ |
| 盈利 | 企业盈利预期是在上修还是下修？ |
| 风险偏好 | 市场愿意冒险还是避险？ |

宏观判断不会直接导出买卖结论。一个板块必须通过三道门：

```text
第一门：宏观风向是否支持？
第二门：行业景气是否验证？
第三门：估值与交易拥挤度是否合理？
```

只有三道门都通过，才会进入重点研究或配置候选。

---

## 九智能体投研体系

| 智能体 | 职责 |
|---|---|
| 宏观共识智能体（Macro Consensus Agent） | 收集官方、机构、市场价格三类宏观信号，识别共识、分歧和观点滞后 |
| 资产轮动智能体（Asset Rotation Agent） | 判断资金流向、板块轮动、交易拥挤度和市场是否已经反映机构共识 |
| 行业位置智能体（Industry Position Agent） | 判断行业阶段、竞争格局、公司 alpha 与行业 beta |
| 公司基本盘智能体（Company Fundamental Agent） | 判断收入质量、利润质量、现金流质量和资本配置质量 |
| 估值与安全边际智能体（Valuation & Margin Agent） | 判断估值水平、安全边际和三情景估值 |
| 持仓执行智能体（Portfolio Execution Agent） | 判断真实持仓、成本、现金、保证金、底仓和交易仓 |
| 数据审计智能体（Data Auditor Agent） | 审计数据来源、口径、时间、币种、单位和可靠性 |
| 反向论证智能体（Bear Case Agent） | 主动寻找最强反方证据，攻击当前结论 |
| 主审整合智能体（Team Lead Agent） | 综合冲突、分配权重、形成最终决策备忘录 |

每个智能体不只是给结论，还必须回答：

```text
关键数据是什么？
这个数据说明了什么？
它比上一期变好还是变差？
它和历史、预期、同行相比如何？
它对估值有什么影响？
它对持仓和操作有什么影响？
什么变化会推翻当前判断？
```

---

## 数据可信度工程

每一个关键数据都需要判断：

- 来源等级；
- 数据时间；
- 币种；
- 单位；
- 财务口径；
- 是否为一次性因素；
- 是否为预测值；
- 是否与其他来源冲突；
- 是否可以进入最终结论。

| 等级 | 来源类型 | 使用方式 |
|---|---|---|
| S 级 | 公司公告、财报、10-K、10-Q、8-K、官方宏观数据 | 核心事实依据 |
| A 级 | 交易所行情、权威数据库、基金官方数据 | 行情、估值和宏观验证 |
| B 级 | 主流财经媒体 | 事件背景和市场反应 |
| C 级 | 券商研报、咨询报告、第三方估算 | 行业空间、市占率和预测数据 |
| D 级 | 社媒、论坛、社区讨论 | 情绪和线索，不能直接作为事实依据 |

如果数据冲突，优先排查：

```text
时间是否一致？
币种是否一致？
单位是否一致？
GAAP / Non-GAAP 是否一致？
TTM / 单季 / 全年是否一致？
是否包含一次性收益或费用？
是否是预测值而非实际值？
是否存在数据滞后？
```

禁止简单平均两个冲突数据。

---

## 数据意义解释

本项目强调：禁止裸数据。

错误写法：

```text
某公司收入增长，利润率提升，资本开支上升。
```

正确写法：

```text
收入增长说明核心业务仍有增长，但资本开支上升意味着市场关注点可能从收入增速转向自由现金流转化质量。因此，这组数据可能支持继续研究或持有，但不一定支持立即加仓。
```

每个关键数据都要回答：

```text
数据事实：这个数据是多少？
数据来源：来自哪里，来源等级是什么？
数据意义：它说明了什么？
边际变化：相比上一期变好还是变差？
相对比较：和历史、预期、同行相比如何？
估值影响：提高还是压低估值容忍度？
操作影响：支持买入、持有、减仓，还是只观察？
失效条件：什么变化会推翻当前解释？
```

---

## 估值与安全边际

估值判断必须说明当前价值区间是如何推导出来的，而不是只写“估值合理”。

至少需要回答：

```text
使用的是 PE、Forward PE、FCF Yield、EV/EBITDA，还是其他估值锚？
正常化 EPS / FCF 如何得到？
当前估值处在历史、同行和自身增长质量的什么位置？
悲观、基准、乐观三情景分别依赖哪些变量？
哪些变量会让估值区间上移或下移？
```

估值结论只能说明安全边际和容忍度，不能直接替代账户动作。

---

## 点位精算引擎（Price Level Engine）

点位精算引擎不输出机械买卖信号，例如：

```text
跌到某个整数点位就买。
涨到某个整数点位就卖。
```

它用于帮助使用者把价格区间拆成五个维度：

```text
1. 估值锚：当前价格对应多少倍正常化 EPS / FCF；
2. 市场锚：是否接近成交密集区、支撑位或阻力位；
3. 个人成本锚：是否接近自己的成本、管理成本或交易仓成本；
4. 仓位约束：当前仓位、现金、保证金是否允许操作；
5. 基本面触发：核心经营数据是否支持该价格区间有效。
```

因此，同一个价格，对不同投资者可能意味着完全不同的动作：

```text
A 用户没有持仓、现金充足，可能只是进入观察范围；
B 用户已经重仓、现金不足，可能只能等待；
C 用户成本很低、仓位过高，可能不该增加风险；
D 用户使用保证金，则可能需要优先降风险。
```

核心规则：

```text
价格只是必要条件，不是充分条件。
```

---

## 真实持仓执行

即使一家公司很好，也必须进一步回答：

```text
我当前持仓多少？
账户成本是多少？
管理成本是多少？
是否已有底仓？
是否是交易仓？
现金比例多少？
是否使用保证金？
继续下跌是否还能承受？
操作后仓位是否过重？
```

管理成本公式：

```text
管理成本 = 当前剩余持仓投入成本 - 已实现收益
单股管理成本 = 管理成本 / 当前剩余股数
```

`tools/portfolio_cost.py` 计算的是组合管理意义上的 aggregate management cost，不是税务 lot 成本，也不是 FIFO / LIFO 报税成本。

---

## Bear Case 与 Report Gatekeeper

反向论证不是装饰项，而是必须主动攻击主结论：

```text
如果看多，最强看空证据是什么？
如果谨慎，最强看多证据是什么？
如果继续持有，是否只是懒惰决策？
哪些数据变化会推翻当前结论？
```

报告准出机制用于确认报告是否具备正式输出条件。它至少检查：

- 必要章节是否齐全；
- 数据是否有来源、日期、口径、单位和币种；
- 是否存在空泛结论；
- 是否混淆公司判断、估值判断、账户判断和交易判断；
- 是否在缺少账户信息时输出账户级动作；
- 是否保留了失效条件和复盘触发条件。

---

## 报告准出检查

中文报告：

```bash
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
```

英文报告：

```bash
python tools/report_gatekeeper.py reports/SAMPLE_research_report_en.md --language en
```

准出检查会覆盖：25 个规范章节存在性、空泛表达、双语标题混排、关键字段缺失。

---

## 项目目录

```text
meridian-research-engine-v2/
├── README.md                  # 本文件（中文）
├── README_EN.md               # 英文说明
├── CHANGELOG.md               # 版本更新日志
├── SKILL.md                   # Agent 技能文件
├── LICENSE                    # MIT License
├── NOTICE                     # 原项目版权声明
├── requirements.txt           # Python 依赖
├── test_comprehensive.py      # 综合测试脚本
│
├── agents/                    # 研究代理定义
│   ├── macro_consensus_agent.md           # 宏观共识
│   ├── macro_liquidity_agent.md           # 宏观流动性
│   ├── asset_rotation_agent.md            # 资产/板块轮动
│   ├── industry_position_agent.md         # 行业位置
│   ├── company_fundamental_agent.md       # 公司基本面
│   ├── data_auditor_agent.md              # 数据审计
│   ├── valuation_margin_agent.md          # 估值安全边际
│   ├── portfolio_execution_agent.md       # 持仓执行
│   ├── bear_case_agent.md                 # 反向论证
│   └── team_lead_agent.md                 # 主审整合
│
├── workflows/                 # 工作流模板
│   ├── stock_research.md           # 个股研究
│   ├── macro_sector_rotation.md    # 宏观板块轮动
│   ├── macro_rotation.md           # 宏观轮动摘要
│   ├── news_pulse.md               # 股价异动归因
│   ├── earnings_review.md          # 财报精读
│   ├── portfolio_review.md         # 持仓复盘
│   ├── industry_funnel.md          # 行业漏斗筛选
│   ├── buy_checklist.md            # 买入检查清单
│   ├── sell_checklist.md           # 卖出检查清单
│   └── qdii_review.md              # QDII 溢价检查
│
├── templates/                 # 报告模板
│   ├── standard_research_report.md         # 模板入口
│   ├── standard_research_report_zh.md      # 中文报告模板（v2.0.0-beta，25 规范章节）
│   ├── standard_research_report_en.md      # 英文报告模板（v2.0.0-beta，25 规范章节）
│   ├── expanded_research_report.md         # 扩展报告模板
│   ├── data_point_card_template.md         # 数据卡片
│   ├── data_meaning_block_template.md      # 数据意义块
│   ├── core_variable_ranking_template.md   # 核心变量排序
│   ├── decision_weight_table_template.md   # 决策权重表
│   ├── macro_six_factor_score_template.md  # 宏观六因子评分
│   ├── macro_view_card_template.md         # 宏观观点卡片
│   ├── market_pricing_assessment_template.md # 市场定价评估
│   ├── sector_rotation_template.md         # 板块轮动
│   ├── bear_case_template.md               # 反向论证
│   ├── four_layer_judgment_template.md     # 四类判断
│   ├── price_level_engine_template.md      # 点位精算
│   ├── portfolio_cost_template.md          # 持仓成本
│   └── report_gatekeeper_checklist.md      # 准出检查清单
│
├── tools/                    # 核心工具
│   ├── macro_score.py              # 宏观六因子评分
│   ├── price_level_engine.py       # 点位精算引擎
│   ├── portfolio_cost.py           # 持仓成本计算
│   ├── valuation_scenario.py       # 三情景估值
│   ├── report_gatekeeper.py        # 报告准出校验（v2.0）
│   ├── reverse_dcf.py              # 反向 DCF
│   ├── cash_flow_driver.py         # 现金流驱动拆解
│   ├── data_point_card.py          # 数据卡片生成
│   ├── industry_classifier.py      # 行业分类器
│   ├── source_audit.py             # 来源审计
│   ├── financial_rigor.py          # 财务严谨性检查
│   ├── contradiction_hunter.py     # 矛盾识别
│   ├── cross_validate.py           # 交叉验证
│   └── roic_roe_calculator.py      # ROIC/ROE 计算
│
├── examples/                  # 示例数据
│   ├── transactions_example.csv     # 交易记录示例
│   ├── holdings_example.csv         # 持仓示例
│   ├── request_examples.md          # 请求示例
│   ├── generic_research_example.md  # 通用研究示例
│   └── generic_price_level_example.md # 价格区间示例
│
├── tests/                     # 单元测试
│   ├── test_macro_score.py
│   ├── test_price_level_engine.py
│   ├── test_valuation_scenario.py
│   ├── test_portfolio_cost.py
│   ├── test_financial_rigor.py
│   ├── test_contradiction_hunter.py
│   └── test_cross_validate.py
│
├── reports/                   # 报告输出示例
│   └── SAMPLE_research_report_zh.md
│
└── docs/                      # 文档
    ├── quickstart_usage.md             # 快速开始
    ├── market_adapters.md              # 市场适配器 
    ├── industry_adapters.md            # 行业适配器 
    ├── fundamental_driver_model.md     # 基本面驱动模型 
    ├── competition_share_model.md      # 竞争与份额模型 
    ├── implied_expectation_model.md    # 隐含预期模型 
    ├── falsification_framework.md      # 证伪框架 
    ├── data_quality_checklist.md       # 数据质量检查清单 
    ├── language_policy.md              # 语言策略
    ├── report_export.md                # 报告导出
    ├── macro_sector_rotation.md        # 宏观板块轮动说明
    ├── data_reliability.md             # 数据可靠性
    ├── architecture.md                 # 架构说明
    ├── methodology.md                  # 方法论
    ├── legal_compliance.md             # 合规说明
    └── price_level_engine.md           # 点位精算说明
```

---

## 适合谁

适合：

- 想用 AI 辅助投研，但不想被漂亮废话带偏的人；
- 需要宏观、板块、公司和账户统一分析框架的人；
- 需要数据审计、反向论证和复盘纪律的人；
- 有真实持仓，需要结合账户执行的人；
- 想建立长期投资研究流程的人。

不适合：

- 想要自动荐股的人；
- 想要短线交易信号的人；
- 想要"今天买什么、明天涨多少"的人；
- 不愿意做数据核验和复盘的人。

---

## 路线图

**已完成：**
- [x] 增加标准报告模板（中/英文分离，25 规范章节）
- [x] 增加语言识别与中英文模板分离
- [x] 增加 Word / PDF 报告导出说明
- [x] 增加英文 README
- [x] 增加快速开始与使用说明
- [x] 增加自动测试工作流（GitHub Actions）
- [x] 恢复并固定工作流入口说明
- [x] 增加全球框架：市场适配器 / 行业适配器（4 市场 + 8 行业）
- [x] 增加基本面驱动模型（收入/毛利率/费用/现金流/ROIC 五棵驱动树）
- [x] 增加竞争与份额模型（TAM/SAM/SOM + 价值链 + 护城河 + 竞争反推）
- [x] 增加市场隐含预期反推模型
- [x] 增加证伪框架（阈值 + 数据来源 + 触发动作）
- [x] 增加数据质量检查清单（10 项强制校验）
- [x] 增加 Gatekeeper v2.1 准出校验（三层 + 三档 + 三模式 + 10 条降级规则）
- [x] 增加综合测试套件（test_comprehensive.py）

**待完成：**
- [ ] 完善数据源登记系统
- [ ] 增加自动数据卡片生成器（Data Point Card）
- [ ] 增加数据交叉验证工具
- [ ] 增加宏观观点卡片生成器
- [ ] 增加市场是否已反映机构共识的辅助判断模块
- [ ] 增加 QDII 溢价和限购状态检查
- [ ] 增加组合集中度风险报告
- [ ] 增加自动化 Word / PDF 导出命令

---

## 版本信息

当前公开版本：**v2.0.0-beta**（Meridian Research Engine 2.0 首发版本）

| 版本 | 日期 | 主要变更 |
|---|---|---|
| **v2.0.0-beta** | 2026-07-04 | **Meridian Research Engine 2.0 首发版本**：市场/行业适配器、基本面驱动模型、竞争份额模型、隐含预期反推、证伪框架、数据质量清单、Gatekeeper v2.1（三层/三档/三模式）、25 规范章节模板、综合测试套件 |

详见 [CHANGELOG.md](CHANGELOG.md)。

---

## 项目来源 / Credits

Meridian Research Engine 2.0｜经纬投研引擎 2.0 的原始上游项目为 MIT License 开源项目 `xbtlin/ai-berkshire`。

在该上游项目基础上，Ada Pan 与 topgunsyang-dotcom 围绕 AI 投研工作流、数据审计、宏观周期、板块轮动、反向论证、证伪框架与 Gatekeeper 准出机制进行了共创整理、重构和扩展，并形成当前的 Meridian Research Engine 2.0 首发版本。

本项目不是 AI Berkshire 的官方版本，也不代表 xbtlin 或上游项目维护者立场；同时也不是任何券商、投顾机构、交易所、数据服务商或金融机构的官方项目。

原始上游版权声明和 MIT License 授权条款已在 `LICENSE` 与 `NOTICE` 中保留。

---

## 最终提醒

Meridian Research Engine 2.0的目的，不是让 AI 更会说服你。

它的目的，是让 AI **更难**轻易说服你。

真正成熟的投研系统，不是每次都给一个激动人心的结论，而是帮助你：

```text
看清大势；
识别轮动；
核验数据；
理解变量；
识别风险；
控制仓位；
保留现金；
等待真正值得承担风险的机会。
```

很多时候，最好的投资动作不是买，也不是卖，而是：

```text
看懂之前，先别动。
```

---

## 许可证

MIT License. See [`LICENSE`](LICENSE).
