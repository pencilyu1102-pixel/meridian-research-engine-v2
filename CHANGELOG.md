# Changelog

## v2.0-beta — Meridian Research Engine 2.0 initial private release（2026-07-04）

### Project initialization
- New private repository: `pencilyu1102-pixel/meridian-research-engine-v2`
- Full rename: Meridian Research Engine 2.0 / 经纬投研引擎 2.0
- Gatekeeper upgraded to **v2.1** with dual CLI interface (positional + --file)
- Canonical section count unified: **25** for both Chinese and English reports
- Added backward-compatible wrappers for legacy tests

### Compliance & privacy
- Added `docs/privacy_boundary.md` — mandatory privacy boundary policy
- Added `docs/disclaimer.md` — full legal disclaimer
- Added root `PRIVACY.md` and `DISCLAIMER.md` summaries
- Updated `.gitignore` with private directory exclusions

### Documentation
- Updated all project name references across the entire repository
- Fixed quickstart instructions with correct clone URL and gatekeeper commands
- Added intermediate working base attribution in NOTICE

---

## v1.0-beta — Argus Research Engine 首发版本（2026-07-03）

### 架构升级
- 从单只股票报告生成器升级为**全球股票通用买方研究框架**
- 新增 **市场适配器**（US/CN/HK/GL，4 套分析框架）
- 新增 **行业适配器**（半导体/软件/互联网/消费/周期/金融/医药/公用，8 种行业模型）

### 核心模块
- 新增 **基本面驱动模型**：收入/毛利率/费用/现金流/ROIC 五棵驱动树
- 新增 **竞争与份额模型**：TAM/SAM/SOM + 价值链 + 护城河 + 竞争对手反推
- 新增 **市场隐含预期模型**：反推当前价格隐含的 CAGR、利润率、份额、倍数
- 新增 **证伪框架**：阈值 + 数据来源 + 触发动作
- 新增 **数据质量检查清单**：10 项强制数据校验

### Gatekeeper v2.0
- 三层检查架构：章节存在性 → 语言合规性 → 内容深度
- 三档准出结论：FULL_PASS / CORE_PASS_TEMPLATE_FAIL / HARD_LOCK_FAIL
- 三种运行模式：formal（正式）/ core（框架测试）/ smoke（烟雾测试）
- 10 条准出降级规则（6 条→条件准出，2 条→不可准出）
- 25 个规范二级标题精确匹配
- 别名映射容差（core/smoke 模式）
- 硬锁检查逻辑（股价/市值/财务来源缺失）

### 报告模板（v1.1）
- 中文模板：24 个规范二级标题，含新增模块
- 英文模板：25 个规范二级标题（含 Appendix）
- 新增模板：决策权重表、市场定价评估、四类判断、宏观六因子评分等

### 新增文档
- 7 个核心模块文档（docs/）：market_adapters, industry_adapters, fundamental_driver_model, competition_share_model, implied_expectation_model, falsification_framework, data_quality_checklist
- reference 文件：gatekeeper_section_headers.md, global_upgrade_session_20260702.md

### 测试验证
- 新增 test_comprehensive.py 综合测试脚本
- 3 个门控测试报告：Microsoft（美股/SaaS）、CATL（A股/制造）、Tencent（港股/互联网）
- 1 个失败案例测试：确认缺数据时正确输出"条件准出"
- 2 个实测报告：寒武纪（A股/AI芯片）、Microsoft（美股/云计算）
- Gatekeeper 全部通过（FULL_PASS）

## v1.1-pricelevel

- Initial open-source project structure.
- Added nine-agent research architecture.
- Added Data Meaning Block and report gatekeeper templates.
- Added Price Level Engine methodology and CLI.
- Added Decimal-based financial calculation tools.
- Added portfolio cost and valuation scenario tools.
- Added examples and pytest coverage.
