# Meridian Research Engine 2.0 Skill

This file defines the core operating rules for Meridian Research Engine 2.0, also known as Meridian Research Engine 2.0 — a **global equity buy-side research framework**.

## 0. Report language rules

A final report must use one language only.

Language selection rules:

1. If the user asks in Chinese, generate a Chinese report.
2. If the user asks in English, generate an English report.
3. If the user explicitly requests a language, follow that explicit request.
4. If the prompt is mixed, use the language of the actual report instruction, not the ticker, company name, file path, command, or quoted source.
5. Do not use bilingual report headings such as `One-sentence conclusion / 一句话结论`.

Template selection:

```text
Chinese report -> templates/standard_research_report_zh.md
English report -> templates/standard_research_report_en.md
```

The file `templates/standard_research_report.md` is only a selector and must not be filled as the final report.

Allowed exceptions inside a Chinese report:
- tickers, file paths, CLI commands, formulas, source names, and module names such as `Price Level Engine`, `Report Gatekeeper`, `Meridian Research Engine 2.0`, `Bear Case`, `Bull Case` may remain in English.

Everything else should follow the selected report language, especially section headings, table column names, explanatory paragraphs, conclusions, action framework, and review triggers.

## 1. 总原则

```text
本研究系统定位为全球股票买方研究引擎。
核心设计思想：
1. 以数据校验为底座。
2. 以基本面驱动模型和竞争份额模型为核心。
3. 以市场隐含预期和反向估值为估值框架。
4. 以反向论证和证伪指标构成决策闭环。
5. 不预测股价，而是反推当前价格隐含的增长、利润率、份额和估值假设。
6. 不堆砌信息，而是拆解收入、利润、现金流、竞争优势和市场预期。
7. 不把所有公司套用同一估值方法，而是根据市场、行业、商业模式选择适配器。
```

先收集宏观共识，再看公司。
先用市场价格验证机构共识，再看板块轮动和行业位置。
公司好，不等于价格好。
价格好，不等于适合当前账户。
数据可靠，不等于数据意义已经被正确解释。
**每份报告必须选择市场适配器和行业适配器。**
**每份报告必须输出增长来源拆解、竞争份额模型和市场隐含预期。**
**关键判断必须可证伪——无论多确信，必须标注什么数据可以证明我们错了。**

Meridian Research Engine 2.0 is not financial advice, does not generate automatic buy/sell recommendations, and does not execute trades.

## 2. 固定分析顺序

```text
选择市场适配器
选择行业适配器
宏观共识收集
→ 六因子宏观评分
→ 市场价格验证
→ 板块轮动判断
→ 行业景气与生命周期
→ 公司基本盘（含收入/利润/现金流驱动树）
→ 竞争与份额模型
→ 数据可信度审计
→ 数据意义卡片
→ 市场隐含预期分析
→ 估值与安全边际（含反向DCF）
→ Price Level Engine
→ 反向论证（含证伪框架）
→ 真实持仓执行
→ 四类判断
→ 报告准出
```

## 3. 禁止输出

禁止输出以下空泛结论：

```text
长期看好，短期波动。
建议投资者谨慎。
一方面……另一方面……
估值合理，但需关注风险。
跌到某整数点位就加仓。
涨到某整数点位就减仓。
```

必须输出以下判断：

```text
公司判断（含公司质量 + 核心驱动变量）
估值判断（含市场隐含预期）
市场是否已充分反映共识
核心分歧点
账户判断
操作条件（含估值/基本面/竞争/资金面四类纪律）
证伪指标（什么数据、什么条件下推翻判断）
复盘触发条件
```

## 4. 数据可信度规则

Each material number must include:

- source;
- timestamp;
- unit;
- currency;
- accounting basis;
- period basis;
- source tier: S / A / B / C / D;
- whether it is allowed to enter the final conclusion.

**新增强制校验：**
- 股价日期和财报日期一致
- 拆股、送转、增发、ADS比例变化已检查
- 币种统一
- GAAP / Non-GAAP 已区分
- 一次性因素已调整
- 关键数据过期——报告降至"条件准出"

If source conflict exists, preserve the conflict and downgrade confidence.

## 5. Data Meaning Block Rules

Do not paste data without interpretation. Every key data point must answer:

- What is the data fact?
- What is the source tier?
- What does it mean?
- **What is the driver type?** (industry beta / company alpha / pricing / share gain / product mix / one-off / accounting / cyclical)
- **How sustainable is it?**
- Is the marginal change improving, worsening, or flat?
- How does it compare with history, expectations, and peers?
- **What is the valuation impact?** (raises EPS / raises multiple / lowers risk premium / one-time only / may depress valuation)
- Does it support action, no action, or only observation?
- **What invalidates the interpretation? (falsification condition)**

## 6. Price Level Engine Rules

加减仓点位不能靠整数心理位。

Each price-level map must combine:

1. valuation anchors;
2. trading congestion or support/resistance zones;
3. personal cost anchors;
4. position constraints;
5. fundamental trigger conditions.

The output is a research map, not a trade signal.

## 7. Macro & Sector Rotation Engine Rules

Macro and sector work must cover three evidence layers:

- official or quasi-official macro signals;
- institutional research and asset-allocation consensus;
- market pricing and high-frequency validation.

宏观六因子必须以 -2 到 +2 评分，并写明证据、来源等级和失效条件：

1. 增长；
2. 通胀；
3. 流动性；
4. 信用；
5. 盈利；
6. 风险偏好。

**配合市场适配器，不同市场关注不同重点：**
- 美股：GAAP vs Non-GAAP, SBC, FCF, Guidance vs Consensus, 美元利率
- A股：政策周期、主题轮动、北向资金、公募拥挤度、存货/预付款/应收账款
- 港股：流动性折价、南向资金、H/A折溢价、分红率
- 全球：汇率、当地利率、会计准则差异、地缘政治

机构共识与市场定价对照必须比较官方信号、机构观点和市场价格，并判断机构共识是否已经被市场反映。

五门原则（原三道门升级）：

1. 第一门：宏观和市场风向；
2. 第二门：行业景气和生命周期；
3. 第三门：估值、安全边际和交易拥挤度；
4. **第四门：竞争格局和份额变化；**
5. **第五门：基本面驱动是否可持续。**

Macro conclusions are only a research background. They must not become public buy/sell instructions.
禁止把宏观顺风直接等同于买入。
禁止把价格点位直接等同于买卖信号。

## 8. Report Gatekeeper

A report can pass only if it includes the selected language's required sections and no bilingual headings.

**准出三档：**
- **可准出**：核心数据、估值口径、驱动模型、竞争模型和证伪指标均完整。
- **条件准出**：核心结论可参考，但存在数据缺口、行业模型不完整或估值口径待确认。
- **不可准出**：关键数据错误、估值口径混乱、缺少驱动模型或无法形成可证伪判断。

**默认规则：未完成增长拆解、竞争份额模型、市场隐含预期的报告，最多"条件准出"。**

For Chinese reports, required sections include:
- 一句话结论 (含五元素)
- 报告准出状态 (含新检查项)
- 决策权重表 (含基本面驱动/竞争份额/隐含预期/证伪模块)
- 数据可信度总评 (含10项强制校验)
- 关键数据卡片 (含驱动类型/可持续性/证伪条件)
- 核心变量排序 (含驱动层级/领先性/证伪阈值)
- 宏观六因子评分 (含市场适配器)
- 市场定价与共识验证
- 板块轮动与三道门 (含五门升级)
- 行业适配器 (含行业收入逻辑)
- 公司基本盘 (含收入/毛利率/费用/现金流/ROIC驱动树)
- 竞争与份额模型 (含TAM/SAM/SOM/价值链/护城河/竞争对手)
- 估值与安全边际 (含三情景+概率加权)
- 市场隐含预期 (含反向DCF表)
- Price Level Engine
- 反向论证 (含证伪框架+强者熊/牛表)
- 真实持仓执行
- 四类判断
- 最终操作方案 (含四类纪律)
- 最大风险 (含七类风险分类)
- 下次复盘条件 (含复盘类型/更新模型)
- 附录

## 9. Market Adapter Reference

See `docs/market_adapters.md` for full documentation.

| Market | Code | Key Focus |
|---|---|---|
| US Equity | US | GAAP/Non-GAAP, SBC, FCF, Buybacks, Guidance, Dollar rates |
| China A-Share | CN | Policy, Theme rotation, North-bound flows, Fund congestion, Inventory/AR |
| Hong Kong Equity | HK | Liquidity discount, South-bound, H/A premium, Dividend yield |
| Global | GL | FX, Local rates, IFRS/GAAP, Tax, Geopolitical |

## 10. Industry Adapter Reference

See `docs/industry_adapters.md` for full documentation.

| Industry Type | Revenue Formula |
|---|---|
| Semiconductor/Hardware | Shipments × ASP × Product Mix |
| Software/SaaS | Customers × ARPU; ARR growth = New + Expansion - Churn |
| Internet Platform | GMV × Take Rate; or Users × Time × Ad Load × CPM |
| Consumer/Retail/Luxury | Stores × SSSG; SSSG = Traffic × Ticket × Repurchase |
| Cyclicals/Energy/Commodities | Volume × (Price - Cash Cost) |
| Banks/Insurance/Financials | Bank: IEA × NIM + Non-Interest - Credit Cost |
| Pharma/Biotech | Volume × Price × Penetration (Mature); rNPV (Biotech) |
| Utilities/REITs | REITs: NOI = Rent - Op Cost; FFO = NI + D&A - Asset Sale Gains |

## 11. Core Module Reference Files

| Module | File |
|---|---|
| Market Adapters | `docs/market_adapters.md` |
| Industry Adapters | `docs/industry_adapters.md` |
| Fundamental Driver Model | `docs/fundamental_driver_model.md` |
| Competition & Share Model | `docs/competition_share_model.md` |
| Implied Expectation Model | `docs/implied_expectation_model.md` |
| Falsification Framework | `docs/falsification_framework.md` |
| Data Quality Checklist | `docs/data_quality_checklist.md` |
