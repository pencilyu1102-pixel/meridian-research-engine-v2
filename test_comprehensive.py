"""
Meridian Research Engine 2.0 8大能力完整测试套件
测试覆盖：功能正确性、边界条件、错误处理、CLI兼容性
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decimal import Decimal
import subprocess
import traceback

passed = 0
failed = 0
results = []

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        status = "✅ PASS"
    else:
        failed += 1
        status = "❌ FAIL"
    results.append((status, name, detail))
    print(f"  {status}: {name}" + (f" — {detail}" if detail else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ========== 1. 宏观周期 (Macro Cycle) ==========
section("能力1: 宏观周期 (Macro Cycle) - macro_score.py")

from tools.macro_score import calculate_macro_score, classify_macro_state, format_macro_score_table

# 1.1 标准计算
s = calculate_macro_score({"growth": "1", "inflation": "0", "liquidity": "1", "credit": "0", "earnings": "1", "risk": "0"})
test("六因子求和正确", s.total_score == Decimal("3"), f"total={s.total_score}")
test("归一化分数正确", s.normalized_score == Decimal("62.50"), f"normalized={s.normalized_score}")
test("状态判定正确", s.macro_state == "中性偏观察", f"state={s.macro_state}")

# 1.2 全部+2 => 宏观强顺风
s2 = calculate_macro_score({"growth": "2", "inflation": "2", "liquidity": "2", "credit": "2", "earnings": "2", "risk": "2"})
test("全部正向:总分12", s2.total_score == Decimal("12"))
test("全部正向:归一化100", s2.normalized_score == Decimal("100.00"))
test("全部正向:状态强顺风", s2.macro_state == "宏观强顺风")

# 1.3 全部-2 => 宏观强逆风
s3 = calculate_macro_score({"growth": "-2", "inflation": "-2", "liquidity": "-2", "credit": "-2", "earnings": "-2", "risk": "-2"})
test("全部负向:总分-12", s3.total_score == Decimal("-12"))
test("全部负向:归一化0", s3.normalized_score == Decimal("0.00"))
test("全部负向:状态强逆风", s3.macro_state == "宏观强逆风")

# 1.4 全部0
s4 = calculate_macro_score({"growth": "0", "inflation": "0", "liquidity": "0", "credit": "0", "earnings": "0", "risk": "0"})
test("全部中性:总分0", s4.total_score == Decimal("0"))
test("全部中性:归一化50", s4.normalized_score == Decimal("50.00"))
test("全部中性:中性偏观察", s4.macro_state == "中性偏观察")

# 1.5 边界值
test("classify 80 => 强顺风", classify_macro_state("80") == "宏观强顺风")
test("classify 65 => 偏顺风", classify_macro_state("65") == "宏观偏顺风")
test("classify 50 => 中性偏观察", classify_macro_state("50") == "中性偏观察")
test("classify 35 => 偏逆风", classify_macro_state("35") == "宏观偏逆风")
test("classify 34.99 => 强逆风", classify_macro_state("34.99") == "宏观强逆风")

# 1.6 超出范围拒绝
try:
    calculate_macro_score({"growth": "3", "inflation": "0", "liquidity": "0", "credit": "0", "earnings": "0", "risk": "0"})
    test("超范围因子拒绝", False, "应抛ValueError但未抛")
except ValueError:
    test("超范围因子拒绝", True, "正确抛出ValueError")

# 1.7 risk vs risk_appetite别名
s5 = calculate_macro_score({"growth": "1", "inflation": "1", "liquidity": "1", "credit": "1", "earnings": "1", "risk_appetite": "1"})
test("risk_appetite别名可用", s5.total_score == Decimal("6"), f"total={s5.total_score}")

# 1.8 Markdown输出
md = format_macro_score_table(s)
test("Markdown表包含总分", "Total score" in md)
test("Markdown表包含归一化分数", "Normalized score" in md)
test("Markdown表包含投资提示", "not financial advice" in md)

# ========== 2. 板块轮动与交叉验证 ==========
section("能力2: 板块轮动与交叉验证 (Sector Rotation) - cross_validate.py")

from tools.cross_validate import parse_source_value, cross_validate_values, render_validation

v1 = cross_validate_values([parse_source_value("Bloomberg=100.5"), parse_source_value("Reuters=100.52"), parse_source_value("Yahoo=100.48")])
test("一致数据无冲突", not v1["conflict"], f"spread={v1['spread']}")

v2 = cross_validate_values([parse_source_value("Bloomberg=100"), parse_source_value("Reuters=105")], "1")
test("不一致数据有冲突", v2["conflict"], f"spread={v2['spread']}")

v3 = cross_validate_values([parse_source_value("Bloomberg=100")], "0.01")
test("单一来源无冲突", not v3["conflict"])

try:
    cross_validate_values([])
    test("空列表拒绝", False, "应抛ValueError")
except ValueError:
    test("空列表拒绝", True, "正确抛出ValueError")

try:
    parse_source_value("invalid")
    test("格式错误拒绝", False, "应抛ValueError")
except ValueError:
    test("格式错误拒绝", True, "正确抛出ValueError")

md2 = render_validation(v1)
test("渲染含count字段", "count" in md2)
test("渲染含conflict字段", "conflict" in md2)

# ========== 3. 数据源可信度审计 ==========
section("能力3: 数据源可信度审计 (Data Source Audit) - source_audit.py")

from tools.source_audit import audit_source, render_source_audit

a1 = audit_source("Bloomberg", "S", "2026-07-01", "USD/share", "USD", "GAAP", "Q2 2026")
test("S级完整数据准入", a1.can_enter_conclusion, f"tier={a1.tier} issues={a1.issues}")

a2 = audit_source("Twitter", "D", "2026-07-01", "USD/share", "USD", "GAAP", "Q2 2026")
test("D级数据禁止准出", not a2.can_enter_conclusion)

a3 = audit_source("Unknown", "S", "", "USD", "USD", "GAAP", "Q2 2026")
test("缺失timestamp禁止准出", not a3.can_enter_conclusion)
test("缺失timestamp报issue", "missing timestamp" in a3.issues)

a4 = audit_source("Refinitiv", "A", "2026-07-01", "USD/share", "USD", "IFRS", "Q2 2026", has_conflict=True)
test("冲突数据禁止准出", not a4.can_enter_conclusion)
test("冲突数据报issue", "conflicting source data" in a4.issues)

a5 = audit_source("CSRC", "C", "2026-07-01", "CNY", "CNY", "CAS", "Q2 2026")
test("C级数据禁止准出", not a5.can_enter_conclusion)

a6 = audit_source("Bloomberg", "A", "2026-07-01", "USD/share", "USD", "GAAP", "Q2 2026")
test("A级完整数据准入", a6.can_enter_conclusion)

a7 = audit_source("Bloomberg", "B", "2026-07-01", "USD/share", "USD", "GAAP", "Q2 2026")
test("B级完整数据准入", a7.can_enter_conclusion)

md3 = render_source_audit(a1)
test("审计渲染含source", "source" in md3)
test("审计渲染含结论准入", "can_enter_conclusion" in md3)

# ========== 4. 数据意义卡片 ==========
section("能力4: 数据意义卡片 (Data Point Card) - data_point_card.py")

from tools.data_point_card import render_data_point_card, DataPointCard

card = DataPointCard(
    data_point="营收同比增长15%",
    source="Bloomberg",
    source_tier="S",
    timestamp="2026-07-01",
    unit="USD",
    currency="USD",
    accounting_basis="GAAP",
    period_basis="Q2 2026",
    can_enter_conclusion="Yes",
    meaning="表明核心业务仍在扩张，增速略超市场预期",
    invalidation_condition="若下季度增速跌破10%则需重新评估"
)
md4 = render_data_point_card(card)
test("卡片含数据点", "营收同比增长15%" in md4)
test("卡片含含义", "核心业务仍在扩张" in md4)
test("卡片含失效条件", "重新评估" in md4)
test("卡片含来源等级", "S" in md4)

# ========== 5. 点位精算引擎 ==========
section("能力5: 点位精算引擎 (Price Level Engine) - price_level_engine.py")

from tools.price_level_engine import build_valuation_anchor_table, render_price_level_report, parse_multiples

anchors = build_valuation_anchor_table("10.00", ["12", "14", "16", "18", "20"])
test("估值锚点个数正确", len(anchors) == 5, f"count={len(anchors)}")
test("EPS 10x 12倍 => $120", anchors[0].price == Decimal("120.00"))
test("EPS 10x 20倍 => $200", anchors[4].price == Decimal("200.00"))

report = render_price_level_report("MSFT", "12.50", ["20", "22", "24", "26", "28", "30"])
test("报告含ticker", "MSFT" in report)
test("报告含EPS", "12.50" in report)
test("报告含倍数表", "Multiple" in report)

# 默认倍数
defaults = parse_multiples()
test("默认12个倍数", len(defaults) == 12, f"count={len(defaults)}")
test("默认最低16x", defaults[0] == Decimal("16.0"))
test("默认最高23x", defaults[-1] == Decimal("23.0"))

# 自定义逗号分隔
custom = parse_multiples("10,15,20,25")
test("自定义解析正确", len(custom) == 4)
test("首个自定义值", custom[0] == Decimal("10"))
test("末个自定义值", custom[-1] == Decimal("25"))

# ========== 6. 真实持仓执行 ==========
section("能力6: 真实持仓执行 (Portfolio Execution) - portfolio_cost.py")

from tools.portfolio_cost import calculate_portfolio_cost, format_portfolio_cost_table, calculate_portfolio_cost_from_rows

csv_path = "examples/transactions_example.csv"
cost = calculate_portfolio_cost(csv_path, ticker="ABC")
test("剩余股数=11", cost.remaining_shares == Decimal("11"))
test("买入总额=1400", cost.gross_buy_amount == Decimal("1400"))
test("卖出总额=440", cost.gross_sell_amount == Decimal("440"))
test("总费用=3", cost.total_fees == Decimal("3"))
test("净投入=963", cost.net_invested_capital == Decimal("963"))
test("管理成本=87.55/股", cost.management_cost_per_share == Decimal("963") / Decimal("11"))

# 无ticker过滤 = 所有交易
cost_all = calculate_portfolio_cost(csv_path)
test("无过滤总买入=23", cost_all.total_bought_shares == Decimal("23"))
test("无过滤总剩余=19", cost_all.remaining_shares == Decimal("19"))

# Markdown输出
md6 = format_portfolio_cost_table(cost)
test("持仓表含剩余股数", "remaining_shares" in md6)
test("持仓表含管理成本", "management_cost_per_share" in md6)

# 全卖出 = 0剩余
rows_sold = [
    {"date": "2026-01-01", "ticker": "ABC", "action": "BUY", "shares": "10", "price": "100", "fee": "0"},
    {"date": "2026-02-01", "ticker": "ABC", "action": "SELL", "shares": "10", "price": "110", "fee": "0"},
]
cost_sold = calculate_portfolio_cost_from_rows(rows_sold, "ABC")
test("全卖出剩余=0", cost_sold.remaining_shares == Decimal("0"))
test("全卖出管理成本=None", cost_sold.management_cost_per_share is None)

# 不存在的ticker
try:
    calculate_portfolio_cost(csv_path, ticker="NONEXISTENT")
    test("不存在的ticker", False, "应抛ValueError")
except ValueError:
    test("不存在的ticker", True, "正确抛出ValueError")

# 非法action
try:
    rows_bad = [{"date": "2026-01-01", "ticker": "ABC", "action": "HOLD", "shares": "10", "price": "100", "fee": "0"}]
    calculate_portfolio_cost_from_rows(rows_bad, "ABC")
    test("非法action拒绝", False, "应抛ValueError")
except ValueError:
    test("非法action拒绝", True, "正确抛出ValueError")

# ========== 7. 反向论证 / Bear Case ==========
section("能力7: 反向论证 (Bear Case / Contradiction Hunter) - contradiction_hunter.py")

from tools.contradiction_hunter import find_banned_phrases, render_findings

text_bad = "长期看好，短期波动。一方面增长不错，另一方面也有风险。估值合理，但需关注风险。"
findings = find_banned_phrases(text_bad)
test("检出禁用词个数", len(findings) == 3, f"found={findings}")

# 逐个禁用词检查
test("检出'长期看好，短期波动'", "长期看好，短期波动" in findings)
test("检出'一方面'", "一方面" in findings)
test("检出'估值合理，但需关注风险'", "估值合理，但需关注风险" in findings)

# 无禁用词
text_clean = "当前宏观环境偏逆风，持仓已减至30%仓位。下一触发条件是CPI跌破3%。"
findings_clean = find_banned_phrases(text_clean)
test("干净文本无检出", len(findings_clean) == 0)

# 渲染
rendered = render_findings(findings)
test("渲染含发现项", "长期看好" in rendered)
rendered_clean = render_findings(findings_clean)
test("干净渲染提示无发现", "No banned vague phrases" in rendered_clean)

# ========== 8. 报告准出机制 ==========
section("能力8: 报告准出机制 (Report Gatekeeper) - report_gatekeeper.py")

from tools.report_gatekeeper import check_report_text, render_gatekeeper_result

# 完整报告
good_report = """
# 测试报告
一句话结论：当前观望
报告准出状态：待定
决策权重表：略
数据可信度总评：S级
关键数据卡片：略
核心变量排序：通胀>增长
宏观六因子评分：50
市场定价是否已经反映机构共识：部分反映
板块轮动判断：科技向金融切换
三道门检查：通过
行业位置：中游
公司基本盘：健康
估值与安全边际：有安全边际
Price Level Engine：略
真实持仓执行：已检查
Bear Case：已准备
四类判断：持有
最终操作方案：观望
最大风险：通胀超预期
下次复盘条件：CPI公布后
"""
gk = check_report_text(good_report)
test("完整报告通过准出", gk["passed"], f"missing={gk['missing_sections']}")
test("完整报告无缺失章节", len(gk["missing_sections"]) == 0)

# 不完整报告
bad_report = "这是一段简短的描述，没有章节标题。长期看好，短期波动。"
gk_bad = check_report_text(bad_report)
test("不完整报告未通过", not gk_bad["passed"])
test("不完整报告检出缺失章节", len(gk_bad["missing_sections"]) > 0, f"missing={len(gk_bad['missing_sections'])}")
test("不完整报告检出禁用词", len(gk_bad["banned_phrases"]) > 0)

# 渲染
rendered_gk = render_gatekeeper_result(gk)
test("准出渲染含PASS", "Pass: True" in rendered_gk)
rendered_gk_bad = render_gatekeeper_result(gk_bad)
test("不准出渲染含Missing", "Missing Sections" in rendered_gk_bad)

# ========== CLI执行测试 ==========
section("CLI兼容性测试 (8个CLI入口)")

rv = lambda cmd: subprocess.run([sys.executable] + cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))

r = rv(["tools/macro_score.py", "--growth", "1", "--inflation", "0", "--liquidity", "1", "--credit", "0", "--earnings", "1", "--risk", "0"])
test("macro_score CLI退出码0", r.returncode == 0)
test("macro_score CLI输出正常", "Total score" in r.stdout)

r3 = rv(["tools/portfolio_cost.py", "examples/transactions_example.csv", "--ticker", "ABC"])
test("portfolio_cost CLI退出码0", r3.returncode == 0)
test("portfolio_cost CLI含剩余股数", "remaining_shares" in r3.stdout)

r4 = rv(["tools/price_level_engine.py", "--eps", "10.00", "--ticker", "MSFT"])
test("price_level_engine CLI退出码0", r4.returncode == 0)
test("price_level_engine CLI含ticker", "MSFT" in r4.stdout)

r5 = rv(["tools/valuation_scenario.py", "--eps", "10.00", "--bear", "12", "--base", "14", "--bull", "16"])
test("valuation_scenario CLI退出码0", r5.returncode == 0)
test("valuation_scenario CLI含三场景", "Bear case" in r5.stdout)

r6 = rv(["tools/cross_validate.py", "--value", "Bloomberg=100.5", "--value", "Reuters=100.52"])
test("cross_validate CLI退出码0", r6.returncode == 0)
test("cross_validate CLI含conflict", "conflict" in r6.stdout)

r7 = rv(["tools/source_audit.py", "--source", "Bloomberg", "--tier", "S", "--timestamp", "2026-07-01", "--unit", "USD", "--currency", "USD", "--accounting-basis", "GAAP", "--period-basis", "Q2"])
test("source_audit CLI退出码0(准入)", r7.returncode == 0)
test("source_audit CLI含结论准入", "can_enter_conclusion" in r7.stdout)

# 不允许准出的CLI
r7b = rv(["tools/source_audit.py", "--source", "Twitter", "--tier", "D", "--timestamp", "2026-07-01", "--unit", "USD", "--currency", "USD", "--accounting-basis", "GAAP", "--period-basis", "Q2"])
test("source_audit CLI退出码1(拒绝)", r7b.returncode == 1)

r8 = rv(["tools/data_point_card.py", "--data-point", "营收增长15%", "--source", "Bloomberg", "--source-tier", "S", "--timestamp", "2026-07-01", "--meaning", "核心业务扩张", "--invalidation-condition", "跌破10%"])
test("data_point_card CLI退出码0", r8.returncode == 0)
test("data_point_card CLI含Data Point", "Data point" in r8.stdout)

# contradiction_hunter CLI
import tempfile
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write("长期看好，短期波动。")
    temp_path = f.name
r9 = rv(["tools/contradiction_hunter.py", temp_path])
test("contradiction_hunter CLI退出码0", r9.returncode == 0)
test("contradiction_hunter CLI检出禁用词", "长期看好" in r9.stdout)
os.unlink(temp_path)

# report_gatekeeper CLI
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(good_report)
    temp_path2 = f.name
r10 = rv(["tools/report_gatekeeper.py", temp_path2])
test("report_gatekeeper CLI退出码0(通过)", r10.returncode == 0)
test("report_gatekeeper CLI含PASS", "Pass: True" in r10.stdout)
os.unlink(temp_path2)

# 不通过的报告
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(bad_report)
    temp_path3 = f.name
r10b = rv(["tools/report_gatekeeper.py", temp_path3])
test("report_gatekeeper CLI退出码1(不通过)", r10b.returncode == 1)
os.unlink(temp_path3)

# ========== 财务计算 ==========
section("财务计算 (financial_rigor.py) - 跨能力支撑层")

from tools.financial_rigor import (
    calculate_market_cap, calculate_pe, calculate_fcf_yield,
    normalize_eps, calculate_price_from_multiple, format_decimal, quantize_money
)

test("市值=股价*股数", calculate_market_cap("100", "20") == Decimal("2000"))
test("PE=股价/EPS", calculate_pe("100", "5") == Decimal("20"))
test("FCF收益率=FCF/市值", calculate_fcf_yield("50", "1000") == Decimal("0.05"))
test("归一化EPS", normalize_eps("9.50", ["0.50"]) == Decimal("10.00"))
test("隐含股价", calculate_price_from_multiple("10.00", "12") == Decimal("120.00"))
test("金额量化", quantize_money("123.456") == Decimal("123.46"))

try:
    calculate_pe("100", "0")
    test("PE分母为0拒绝", False, "应抛ZeroDivisionError")
except ZeroDivisionError:
    test("PE分母为0拒绝", True, "正确抛出ZeroDivisionError")

try:
    calculate_price_from_multiple(10.00, "12")
    test("float输入拒绝", False, "应抛TypeError")
except TypeError:
    test("float输入拒绝", True, "正确抛出TypeError")

# ========== 三情景估值 ==========
section("三情景估值 (valuation_scenario.py)")

from tools.valuation_scenario import calculate_valuation_scenarios, format_scenario_table

scenario = calculate_valuation_scenarios("10.00", "12", "14", "16")
test("熊市估值120", scenario.bear_case_price == Decimal("120.00"))
test("基准估值140", scenario.base_case_price == Decimal("140.00"))
test("牛市估值160", scenario.bull_case_price == Decimal("160.00"))

md_scenario = format_scenario_table(scenario)
test("三情景渲染含全部3个场景", "Bear case price" in md_scenario)
test("三情景渲染含Base", "Base case price" in md_scenario)
test("三情景渲染含Bull", "Bull case price" in md_scenario)

# ========== 汇总 ==========
print(f"\n{'='*60}")
print(f"  测试汇总")
print(f"{'='*60}")
print(f"  通过: {passed}")
print(f"  失败: {failed}")
print(f"  总数: {passed + failed}")
print(f"  通过率: {passed/(passed+failed)*100:.1f}%")
print(f"{'='*60}")
