# 标准投研报告模板 v2.0.0-beta

> 用途：结构化投研、数据审计、估值反推、组合执行与复盘。本文档仅作为研究流程模板，不构成投资建议。  
> 使用规则：正式报告必须保留所有二级标题。若某章节不适用，写明"不适用 + 原因"，不得删除章节。  
> Gatekeeper 模式：`formal` 用于正式准出；`core` 用于框架能力测试；`smoke` 用于快速检查。

---

# {{标的名称}} 投研报告

- 报告日期：{{YYYY-MM-DD}}
- 标的代码：{{TICKER}}
- 交易市场：{{US Equity / China A-Share / Hong Kong Equity / Global / Other}}
- 行业适配器：{{半导体硬件 / 软件SaaS云 / 互联网平台 / 消费零售 / 周期能源材料 / 金融 / 医药生物 / 公用事业REITs / 混合业务}}
- 研究人：{{NAME_OR_TEAM}}
- 数据截至：{{YYYY-MM-DD HH:MM TZ}}
- 报告状态：草稿 / 复核 / 定稿
- 报告语言：中文
- Gatekeeper 模式：formal / core / smoke

---

## 报告准出状态

| 检查项 | 状态 | 说明 |
|---|---|---|
| 数据来源已核验 | TODO | 公司公告、交易所、行情、第三方数据是否可复核 |
| 数据日期已核验 | TODO | 股价、市值、财报、共识预期的日期是否一致 |
| 币种和单位已核验 | TODO | 人民币/美元/港币；亿元/百万/十亿；普通股/ADS/H股 |
| 市场适配器已完成 | TODO | 已选择市场，并说明适用/不适用字段 |
| 行业适配器已完成 | TODO | 已选择行业模型，并说明主要收入公式 |
| 宏观部分已完成 | TODO | 宏观六因子与市场适配器是否一致 |
| 板块部分已完成 | TODO | 行业景气、拥挤度、资金面 |
| 基本面驱动模型已完成 | TODO | 收入、毛利率、费用率、现金流、ROIC/ROE |
| 竞争与份额模型已完成 | TODO | TAM/SAM/SOM、价值链、护城河、竞争对手 |
| 估值部分已完成 | TODO | 正常化基础、三情景、反向估值、隐含预期 |
| 市场隐含预期已完成 | TODO | 当前价格隐含的 CAGR、利润率、份额、倍数 |
| 真实持仓执行已完成 | TODO | 账户约束、仓位、保证金、单股上限 |
| 反向论证已完成 | TODO | Bear/Bull 两端均已列出 |
| 证伪框架已完成 | TODO | 阈值、数据来源、触发动作 |
| 复盘条件已完成 | TODO | 财报、估值、竞争、资金面、风险事件 |
| 语言一致性已检查 | TODO | 不得使用中英文混排标题 |

准出结论：

```text
TODO：可准出 / 条件准出 / 不可准出

硬锁规则：
- 缺少有效股价、市值、核心财务来源、营收或 EPS：不可准出。
- 币种、股本、估值口径冲突且未校正：不可准出。
- 缺少市场适配器、行业适配器、基本面驱动、竞争份额、隐含预期或证伪框架：最高只能条件准出。
```

---

## 一句话结论

```text
TODO：用一句话同时说明公司判断、估值判断、市场隐含预期、账户约束和复盘状态。
```

```text
公司判断：TODO
估值判断：TODO
市场预期判断：TODO
账户判断：TODO
复盘状态：TODO
```

---

## 决策权重表

| 模块 | 权重 | 当前判断 | 置信度 | 主要证据 |
|---|---:|---|---|---|
| 宏观周期 | TODO | TODO | TODO | TODO |
| 市场适配与资金结构 | TODO | TODO | TODO | TODO |
| 板块轮动 | TODO | TODO | TODO | TODO |
| 行业生命周期 | TODO | TODO | TODO | TODO |
| 公司质量 | TODO | TODO | TODO | TODO |
| 基本面驱动模型 | TODO | TODO | TODO | TODO |
| 竞争与份额模型 | TODO | TODO | TODO | TODO |
| 数据可靠性 | TODO | TODO | TODO | TODO |
| 估值与安全边际 | TODO | TODO | TODO | TODO |
| 真实持仓执行 | TODO | TODO | TODO | TODO |
| 反向论证与证伪 | TODO | TODO | TODO | TODO |

综合等级：

```text
TODO：研究候选 / 持仓复核 / 等待 / 否决 / 数据不足
```

---

## 市场与行业适配器

### 市场适配器

| 字段 | 选择或判断 | 适用性 | 原因 |
|---|---|---|---|
| 所属市场 | TODO | applicable | US Equity / China A-Share / Hong Kong Equity / Global / Other |
| 主要币种 | TODO | applicable | 报告估值和财务口径使用的币种 |
| 会计口径 | TODO | applicable | GAAP / Non-GAAP / IFRS / 中国会计准则 |
| 利率和流动性 | TODO | applicable / not_applicable / uncertain | 对估值倍数和风险偏好的影响 |
| 政策和监管 | TODO | applicable / not_applicable / uncertain | 市场或行业特有监管 |
| 资金拥挤度 | TODO | applicable / not_applicable / uncertain | A股、港股、热门主题尤其需要 |
| 分红/回购 | TODO | applicable / not_applicable / uncertain | 美股、港股、成熟企业尤其需要 |
| 汇率因素 | TODO | applicable / not_applicable / uncertain | 跨国收入、ADR、港股、全球公司 |
| 特殊结构 | TODO | applicable / not_applicable / uncertain | ADS、A/H、双重上市、VIE、REITs 等 |

### 行业适配器

| 字段 | 内容 |
|---|---|
| 主行业适配器 | TODO |
| 副行业适配器 | TODO，如混合业务公司需填写 |
| 适配置信度 | 高 / 中 / 低 |
| 选择原因 | TODO |
| 主要收入公式 | TODO，例如：收入 = 出货量 × ASP × 产品结构 |
| 必填行业指标 | TODO |
| 不适用指标 | TODO，写明不适用原因 |

---

## 宏观六因子评分

| 因子 | 分数（-2 到 +2） | 证据 | 数据意义 |
|---|---:|---|---|
| 增长 | TODO | TODO | TODO |
| 通胀 | TODO | TODO | TODO |
| 流动性 | TODO | TODO | TODO |
| 信用 | TODO | TODO | TODO |
| 盈利 | TODO | TODO | TODO |
| 风险偏好 | TODO | TODO | TODO |

```text
原始分数：TODO
标准化分数：TODO
宏观状态：TODO
市场适配说明：TODO
```

---

## 市场定价与共识验证

| 问题 | 判断 | 证据 |
|---|---|---|
| 当前市场共识是什么？ | TODO | TODO |
| 共识是否已经被价格反映？ | TODO | TODO |
| 哪些因素尚未充分反映？ | TODO | TODO |
| 哪些因素可能被过度反映？ | TODO | TODO |
| 市场可能错在哪里？ | TODO | TODO |
| 什么数据会改变当前判断？ | TODO | TODO |

结论：

```text
TODO：尚未反映 / 部分反映 / 已充分反映 / 可能过度反映 / 不清楚
```

---

## 板块轮动与三道门

### 板块判断

| 板块或主题 | 当前状态 | 证据 | 风险 |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

### 三道门检查

| 门槛 | 结果 | 原因 |
|---|---|---|
| 第一门：宏观风向 | TODO | TODO |
| 第二门：行业景气 | TODO | TODO |
| 第三门：估值、拥挤度、竞争份额和增长质量 | TODO | TODO |

结论：

```text
TODO：通过 / 部分通过 / 不通过 / 仅观察
```

---

## 数据可信度总评

| 数据点 | 数值 | 来源 | 来源等级 | 日期 | 单位和币种 | 是否进入结论 |
|---|---:|---|---|---|---|---|
| 最新股价 | TODO | TODO | TODO | TODO | TODO | TODO |
| 市值 / 企业价值 | TODO | TODO | TODO | TODO | TODO | TODO |
| 股本 / ADS 比例 | TODO | TODO | TODO | TODO | TODO | TODO |
| 营收 | TODO | TODO | TODO | TODO | TODO | TODO |
| EPS / 净利润 / FCF | TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO | TODO |

冲突检查：

```text
时间一致性：TODO
币种一致性：TODO
单位一致性：TODO
会计口径一致性：TODO
周期口径一致性：TODO
股本口径一致性：TODO
估值口径一致性：TODO
一次性因素：TODO
实际值或预测值：TODO
同业对比口径：TODO
```

数据可信度结论：

```text
TODO：S / A / B / C / D，并说明原因
```

---

## 关键数据卡片

### 数据卡片一：{{DATA_POINT}}

| 字段 | 内容 |
|---|---|
| 数据事实 | TODO |
| 来源与等级 | TODO |
| 数据意义 | TODO |
| 驱动类型 | 行业 beta / 公司 alpha / 价格提升 / 份额提升 / 产品结构升级 / 一次性因素 / 会计因素 / 周期因素 |
| 边际变化 | TODO |
| 相对比较 | TODO |
| 可持续性 | 高 / 中 / 低 / 不确定 |
| 估值影响 | 提升 EPS / 提升估值倍数 / 降低风险溢价 / 一次性影响 / 压低估值 |
| 账户或复盘影响 | TODO |
| 失效条件 | TODO |

### 数据卡片二：{{DATA_POINT}}

| 字段 | 内容 |
|---|---|
| 数据事实 | TODO |
| 来源与等级 | TODO |
| 数据意义 | TODO |
| 驱动类型 | TODO |
| 边际变化 | TODO |
| 相对比较 | TODO |
| 可持续性 | TODO |
| 估值影响 | TODO |
| 账户或复盘影响 | TODO |
| 失效条件 | TODO |

---

## 核心变量排序

| 排名 | 变量 | 当前值 | 驱动层级 | 当前方向 | 领先性 | 重要性 | 跟踪频率 | 证伪阈值 | 数据来源 |
|---:|---|---:|---|---|---|---|---|---|---|
| 1 | TODO | TODO | 收入/毛利率/现金流/估值/份额/政策/资金面 | TODO | 领先/同步/滞后 | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 3 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

---

## 行业位置

```text
TODO：说明行业阶段、竞争格局、行业 beta、公司 alpha、利润池位置和行业生命周期。
```

| 项目 | 判断 | 证据 |
|---|---|---|
| 行业阶段 | 导入期 / 成长期 / 成熟期 / 衰退期 / 周期底部 / 周期顶部 | TODO |
| 行业 beta | 高 / 中 / 低 | TODO |
| 公司 alpha | 高 / 中 / 低 | TODO |
| 利润池位置 | 核心 / 中游 / 边缘 / 不确定 | TODO |
| 供需结构 | TODO | TODO |
| 价格趋势 | TODO | TODO |

---

## 竞争与份额模型

### 市场边界

| 层级 | 定义 | 数值或判断 | 来源 | 可信度 |
|---|---|---:|---|---|
| TAM 理论总市场 | TODO | TODO | TODO | TODO |
| SAM 可服务市场 | TODO | TODO | TODO | TODO |
| SOM 现实可获取市场 | TODO | TODO | TODO | TODO |

### 价值链和利润池

```text
上游供应商 → 公司 → 渠道/平台 → 客户 → 终端用户
TODO
```

| 问题 | 判断 | 证据 |
|---|---|---|
| 谁拿走最大利润？ | TODO | TODO |
| 谁掌握稀缺资源？ | TODO | TODO |
| 谁控制客户入口？ | TODO | TODO |
| 公司是否处于利润池核心？ | TODO | TODO |

### 护城河和竞争优势

| 优势类型 | 是否存在 | 量化证据 | 趋势 | 可持续性 |
|---|---|---|---|---|
| 成本优势 | TODO | TODO | 增强/持平/减弱 | TODO |
| 技术优势 | TODO | TODO | TODO | TODO |
| 网络效应 | TODO | TODO | TODO | TODO |
| 品牌优势 | TODO | TODO | TODO | TODO |
| 渠道优势 | TODO | TODO | TODO | TODO |
| 数据优势 | TODO | TODO | TODO | TODO |
| 监管牌照 | TODO | TODO | TODO | TODO |
| 生态锁定 | TODO | TODO | TODO | TODO |

### 竞争对手反推

| 竞争对手 | 优势 | 劣势 | 对公司威胁 | 监测指标 |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

### 份额变化模型

```text
公司收入 = 市场规模 × 行业渗透率 × 公司市场份额 × 价格/Take Rate × 产品结构
```

| 变量 | 当前判断 | 未来 3-5 年假设 | 证据 | 证伪条件 |
|---|---|---|---|---|
| 市场规模 | TODO | TODO | TODO | TODO |
| 渗透率 | TODO | TODO | TODO | TODO |
| 公司份额 | TODO | TODO | TODO | TODO |
| 价格 / Take Rate | TODO | TODO | TODO | TODO |
| 产品结构 | TODO | TODO | TODO | TODO |

---

## 公司基本盘

| 维度 | 判断 | 证据 |
|---|---|---|
| 收入质量 | TODO | TODO |
| 利润质量 | TODO | TODO |
| 现金流质量 | TODO | TODO |
| 资产负债质量 | TODO | TODO |
| 资本配置 | TODO | TODO |
| 管理层执行 | TODO | TODO |

公司基本盘结论：

```text
TODO
```

---

## 基本面驱动模型

### 收入驱动树

```text
收入增长 = 行业增长贡献 + 渗透率提升贡献 + 份额提升贡献 + 价格提升贡献 + 产品结构升级贡献 + 并购贡献 + 一次性因素
```

| 增长来源 | 贡献判断 | 证据 | 可持续性 | 风险 |
|---|---|---|---|---|
| 行业增长 | 高/中/低 | TODO | TODO | TODO |
| 渗透率提升 | 高/中/低 | TODO | TODO | TODO |
| 份额提升 | 高/中/低 | TODO | TODO | TODO |
| 价格提升 | 高/中/低 | TODO | TODO | TODO |
| 产品结构升级 | 高/中/低 | TODO | TODO | TODO |
| 并购贡献 | 有/无 | TODO | TODO | TODO |
| 一次性因素 | 有/无 | TODO | 不可持续 | TODO |

### 毛利率、费用率与利润驱动

| 项目 | 当前值 | 趋势 | 驱动因素 | 判断 |
|---|---:|---|---|---|
| 毛利率 | TODO | TODO | TODO | TODO |
| 销售费用率 | TODO | TODO | TODO | TODO |
| 研发费用率 | TODO | TODO | TODO | TODO |
| 管理费用率 | TODO | TODO | TODO | TODO |
| 营业利润率 | TODO | TODO | TODO | TODO |
| 净利率 | TODO | TODO | TODO | TODO |

### 现金流驱动树

| 项目 | 当前值 | 同比/环比 | 对现金流影响 | 判断 |
|---|---:|---:|---|---|
| OCF 经营现金流 | TODO | TODO | TODO | TODO |
| CapEx 资本开支 | TODO | TODO | TODO | TODO |
| 应收变化 | TODO | TODO | TODO | TODO |
| 存货变化 | TODO | TODO | TODO | TODO |
| 预付款变化 | TODO | TODO | TODO | TODO |
| FCF 自由现金流 | TODO | TODO | TODO | TODO |
| FCF Margin | TODO | TODO | TODO | TODO |
| FCF 转化率 | TODO | TODO | TODO | TODO |

### ROIC / ROE 驱动

| 指标 | 当前值 | 计算口径 | 判断 |
|---|---:|---|---|
| ROIC | TODO | NOPAT / Average Invested Capital | TODO |
| ROE | TODO | Net Income / Average Equity | TODO |
| ROIC vs WACC | TODO | TODO | TODO |
| ROE 杜邦拆解 | TODO | 净利率 × 周转率 × 杠杆 | TODO |

---

## 估值与安全边际

### 正常化基础

```text
正常化 EPS / FCF 口径：TODO
调整项：TODO
为什么这样调整：TODO
```

### 三情景估值

| 情景 | 核心假设 | 概率 | 倍数或收益率 | 隐含价值 | 触发条件 |
|---|---|---:|---:|---:|---|
| 悲观 | TODO | TODO | TODO | TODO | TODO |
| 基准 | TODO | TODO | TODO | TODO | TODO |
| 乐观 | TODO | TODO | TODO | TODO | TODO |

概率加权价值：

```text
TODO：Bear × 概率 + Base × 概率 + Bull × 概率
```

---

## 市场隐含预期

| 当前价格隐含假设 | 市场隐含值 | 本报告判断 | 差异 | 证据 |
|---|---:|---:|---|---|
| 未来收入 CAGR | TODO | TODO | TODO | TODO |
| 长期毛利率 | TODO | TODO | TODO | TODO |
| 长期净利率 / FCF Margin | TODO | TODO | TODO | TODO |
| 市场份额 | TODO | TODO | TODO | TODO |
| 估值倍数 | TODO | TODO | TODO | TODO |
| ROIC / ROE | TODO | TODO | TODO | TODO |

结论：

```text
TODO：当前股价已经定价了什么？本报告是否同意？市场错在哪里？
```

---

## Price Level Engine

| 价格区间 | 估值锚 | 市场锚 | 账户约束 | 基本面触发条件 | 解释 |
|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO | TODO |

核心规则：

```text
价格只是条件，不是信号。
```

---

## 真实持仓执行

在使用任何账户级动作语言之前，必须完成本节。

| 项目 | 数值 | 说明 |
|---|---:|---|
| 当前股数 | TODO | TODO |
| 原始成本 | TODO | TODO |
| 账户成本 | TODO | TODO |
| 管理成本 | TODO | TODO |
| 已实现盈亏 | TODO | TODO |
| 当前权重 | TODO | TODO |
| 现金水平 | TODO | TODO |
| 是否使用保证金 | TODO | TODO |
| 单股权重上限 | TODO | TODO |

持仓执行结论：

```text
TODO：允许账户动作 / 不允许账户动作 / 需要更多数据 / 仅复盘
```

---

## Bear Case

最强反方观点：

```text
TODO
```

| 反方因素 | 概率 | 影响 | 证据 | 跟踪触发条件 |
|---|---:|---:|---|---|
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

什么会证明正面判断错误？

```text
TODO
```

什么会证明反方判断错误？

```text
TODO
```

---

## 证伪框架

| 核心判断 | 证伪指标 | 阈值 | 数据来源 | 触发动作 |
|---|---|---:|---|---|
| TODO | TODO | TODO | TODO | 下修模型 / 降级评级 / 减仓复核 / 退出研究 |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

原则：

```text
所有核心结论必须可证伪。没有阈值和动作的风险提示，不得视为完整风险分析。
```

---

## 四类判断

```text
公司判断：TODO
估值判断：TODO
账户判断：TODO
复盘判断：TODO
```

四层判断不得混在一起。

---

## 最终操作方案

仅使用条件化表达，不输出机械买卖指令。

| 纪律类型 | 条件 | 状态 | 动作 | 原因 |
|---|---|---|---|---|
| 估值纪律 | TODO | TODO | TODO | TODO |
| 基本面纪律 | TODO | TODO | TODO | TODO |
| 竞争纪律 | TODO | TODO | TODO | TODO |
| 资金面纪律 | TODO | TODO | TODO | TODO |

最终框架：

```text
TODO：持仓复核 / 等待 / 复盘区 / 研究候选 / 降低风险 / 数据不足
```

---

## 最大风险

| 风险类型 | 风险描述 | 概率 | 潜在影响 | 领先指标 | 应对动作 |
|---|---|---:|---|---|---|
| 基本面风险 | TODO | TODO | TODO | TODO | TODO |
| 估值风险 | TODO | TODO | TODO | TODO | TODO |
| 竞争风险 | TODO | TODO | TODO | TODO | TODO |
| 财务质量风险 | TODO | TODO | TODO | TODO | TODO |
| 流动性风险 | TODO | TODO | TODO | TODO | TODO |
| 政策/监管风险 | TODO | TODO | TODO | TODO | TODO |
| 黑天鹅风险 | TODO | TODO | TODO | TODO | TODO |

最大单一风险：

```text
TODO：指出一个最可能改变整套判断的核心风险。
```

---

## 下次复盘条件

| 触发项 | 阈值或事件 | 复盘类型 | 需要更新的模型 | 为什么重要 |
|---|---|---|---|---|
| TODO | TODO | 财报/估值/竞争/资金面/风险事件 | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

下次复盘时间：

```text
TODO
```

---

## 附录

### 来源列表

| 来源 | 链接或引用 | 等级 | 用途 |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

### 计算说明

```text
TODO：列明 EPS、FCF、ROIC、ROE、EV、股本、币种、反向 DCF、概率加权估值的计算口径。
```

### 不适用字段说明

| 字段 | 不适用原因 |
|---|---|
| TODO | TODO |

### 开源与免责声明

```text
本报告格式属于 Meridian Research Engine 2.0 / Meridian Research Engine 2.0。
本项目是基于 MIT License 的 AI Berkshire 二次开发项目。
本报告仅为研究流程输出，不构成投资建议。
```
