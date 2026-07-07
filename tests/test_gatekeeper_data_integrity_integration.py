from tools.report_gatekeeper import CANONICAL_ZH, check_report


def _build_full_report_text() -> str:
    section_bodies = {
        "one_sentence": "结论：样例公司股价 $123.45，市值 1000亿，EPS 1.23，来源为财报 / 10-K / SEC。",
        "gatekeeper": "结构完整性自检。",
        "weight_table": "权重示意。",
        "adapter": "行业适配说明。",
        "macro_score": "宏观因子概览。",
        "market_pricing": "市场定价与共识对照。",
        "sector_rotation": "板块轮动观察。",
        "data_reliability": "数据可信度评估。",
        "data_cards": "关键数据卡片摘要。",
        "variable_ranking": "变量排序。",
        "industry_position": "行业位置。",
        "competition_model": "TAM SAM SOM 竞争 份额 均已覆盖。",
        "company_fundamentals": "收入 毛利率 增长 财报 10-K SEC 均已覆盖。",
        "driver_model": "基本面驱动拆解。",
        "valuation": "估值与安全边际分析。",
        "implied_expectation": "隐含 倍数 差异 已分析。",
        "price_level": "Price level reference only.",
        "portfolio_execution": "执行说明。",
        "bear_case": "Bear Case 完整。",
        "falsification": "证伪条件。",
        "four_layers": "四层判断。",
        "action_plan": "条件 动作 已定义。",
        "max_risk": "风险 概率 影响 已定义。",
        "review_triggers": "复盘条件。",
        "appendix": "附录。",
    }
    return "\n\n".join(
        f"{heading}\n{section_bodies[key]}" for key, heading in CANONICAL_ZH.items()
    )


def test_gatekeeper_allows_formal_release_only_when_structure_and_hardlock_both_pass():
    report = _build_full_report_text()
    result = check_report(report, hardlock_verdict={"status": "PASS_FORMAL", "violations": []})

    assert result["structure_status"] == "FULL_PASS"
    assert result["hardlock_status"] == "PASS_FORMAL"
    assert result["final_status"] == "FULL_PASS"
    assert result["release_decision"] == "可准出"
    assert result["can_be_used_as_formal_report"] is True


def test_gatekeeper_blocks_release_when_capital_bridge_hardlock_fails():
    report = _build_full_report_text()
    result = check_report(report, hardlock_verdict={"status": "FAIL_CAPITAL_BRIDGE", "violations": ["share bridge missing"]})

    assert result["structure_status"] == "FULL_PASS"
    assert result["hardlock_status"] == "FAIL_CAPITAL_BRIDGE"
    assert result["final_status"] == "FAIL_DATA_HARDLOCK"
    assert result["release_decision"] == "不可准出"
    assert result["failure_family"] == "FAIL_DATA_HARDLOCK"


def test_gatekeeper_blocks_release_when_earnings_basis_hardlock_fails():
    report = _build_full_report_text()
    result = check_report(report, hardlock_verdict={"status": "FAIL_EARNINGS_BASIS", "violations": ["guidance used as trailing EPS"]})

    assert result["structure_status"] == "FULL_PASS"
    assert result["hardlock_status"] == "FAIL_EARNINGS_BASIS"
    assert result["final_status"] == "FAIL_DATA_HARDLOCK"
    assert result["release_decision"] == "不可准出"


def test_gatekeeper_without_hardlock_verdict_cannot_formally_release_even_when_structure_passes():
    report = _build_full_report_text()
    result = check_report(report)

    assert result["structure_status"] == "FULL_PASS"
    assert result["hardlock_status"] == "PASS_TEST_ONLY"
    assert result["final_status"] == "PASS_TEST_ONLY"
    assert result["release_decision"] == "不可准出"
    assert result["can_be_used_as_formal_report"] is False
    assert result["can_be_used_as_framework_test"] is True
