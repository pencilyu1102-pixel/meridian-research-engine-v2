"""Meridian Gatekeeper v2.1 — three-mode, multi-gate report release check.
Three-mode, three-gate architecture with structured status output.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .contradiction_hunter import find_banned_phrases
except ImportError:
    from contradiction_hunter import find_banned_phrases

# ── Canonical section names (formal template standard) ─────────────────

CANONICAL_ZH: dict[str, str] = {
    "one_sentence": "## 一句话结论",
    "gatekeeper": "## 报告准出状态",
    "weight_table": "## 决策权重表",
    "adapter": "## 市场与行业适配器",
    "macro_score": "## 宏观六因子评分",
    "market_pricing": "## 市场定价与共识验证",
    "sector_rotation": "## 板块轮动与三道门",
    "data_reliability": "## 数据可信度总评",
    "data_cards": "## 关键数据卡片",
    "variable_ranking": "## 核心变量排序",
    "industry_position": "## 行业位置",
    "competition_model": "## 竞争与份额模型",
    "company_fundamentals": "## 公司基本盘",
    "driver_model": "## 基本面驱动模型",
    "valuation": "## 估值与安全边际",
    "implied_expectation": "## 市场隐含预期",
    "price_level": "## Price Level Engine",
    "portfolio_execution": "## 真实持仓执行",
    "bear_case": "## Bear Case",
    "falsification": "## 证伪框架",
    "four_layers": "## 四类判断",
    "action_plan": "## 最终操作方案",
    "max_risk": "## 最大风险",
    "review_triggers": "## 下次复盘条件",
    "appendix": "## 附录",
}

CANONICAL_EN: dict[str, str] = {
    "one_sentence": "## One-sentence conclusion",
    "gatekeeper": "## Report gatekeeper",
    "weight_table": "## Decision weight table",
    "adapter": "## Market and industry adapters",
    "data_reliability": "## Data reliability review",
    "data_cards": "## Key data cards",
    "variable_ranking": "## Core variable ranking",
    "macro_score": "## Macro six-factor score",
    "market_pricing": "## Market pricing and consensus validation",
    "sector_rotation": "## Sector rotation and three-gate check",
    "industry_position": "## Industry position",
    "company_fundamentals": "## Company fundamentals",
    "driver_model": "## Fundamental driver model",
    "competition_model": "## Competition and share model",
    "valuation": "## Valuation and margin of safety",
    "implied_expectation": "## Market implied expectations",
    "price_level": "## Price Level Engine",
    "portfolio_execution": "## Portfolio execution",
    "bear_case": "## Bear case",
    "falsification": "## Falsification framework",
    "four_layers": "## Four-layer judgment",
    "action_plan": "## Final action framework",
    "max_risk": "## Maximum risk",
    "review_triggers": "## Next review triggers",
    "appendix": "## Appendix",
}

# ── Core modules (for core/smoke mode) ─────────────────────────────────

CORE_MODULES_ZH = [
    "市场与行业适配器", "公司基本盘", "竞争与份额模型",
    "估值与安全边际", "市场隐含预期", "Bear Case",
    "证伪框架", "最终操作方案", "最大风险",
]

CORE_MODULES_EN = [
    "Industry adapter", "Company fundamentals",
    "Competition and share model", "Valuation and margin of safety",
    "Implied expectation", "Bear case",
    "Final action framework", "Maximum risk",
]

SMOKE_MODULES_ZH = [
    "行业适配器", "竞争与份额模型",
    "市场隐含预期",
]

SMOKE_MODULES_EN = [
    "Industry adapter", "Competition and share model",
    "Implied expectation",
]

# ── Section alias lookup (for mode=core/smoke recognition) ─────────────

SECTION_ALIASES_ZH: dict[str, list[str]] = {
    "市场与行业适配器": ["市场与行业适配器", "市场适配器", "行业适配器", "行业模型", "行业位置", "行业分析", "行业驱动模型"],
    "公司基本盘": ["公司基本盘", "Company fundamentals", "基本盘分析", "Business Fundamentals"],
    "基本面驱动模型": ["基本面驱动模型", "基本面驱动树", "收入驱动模型", "Fundamental Driver Model"],
    "竞争与份额模型": [
        "竞争与份额模型", "竞争份额模型", "竞争格局与份额模型",
        "Competition and Share Model", "Competition & Share Model",
        "Market Share and Competition", "竞争格局分析",
    ],
    "估值与安全边际": ["估值与安全边际", "Valuation and margin of safety", "Valuation Analysis", "估值分析"],
    "市场隐含预期": [
        "市场隐含预期", "隐含预期模型", "当前价格隐含预期",
        "Implied Expectation", "What the Price Implies",
    ],
    "Bear Case": ["Bear Case", "Bear case", "反向论证", "反方观点", "负面论证"],
    "证伪框架": ["证伪框架", "证伪指标", "可证伪条件", "证伪条件", "Falsification"],
    "最终操作方案": ["最终操作方案", "Final action framework", "Final Action Framework", "操作方案"],
    "最大风险": ["最大风险", "Maximum risk", "Maximum Risk", "风险分析"],
}

SECTION_ALIASES_EN: dict[str, list[str]] = {
    "Industry adapter": ["Industry adapter", "Industry Adapter", "Industry Model", "Industry Position", "Sector Adapter"],
    "Company fundamentals": ["Company fundamentals", "Company Fundamentals", "Business Fundamentals"],
    "Fundamental driver model": ["Fundamental driver model", "Fundamental Driver Model", "Business Driver Model"],
    "Competition and share model": [
        "Competition and share model", "Competition and Share Model",
        "Competition & Share Model", "Market Share and Competition",
    ],
    "Valuation and margin of safety": ["Valuation and margin of safety", "Valuation and Margin of Safety"],
    "Implied expectation": ["Implied expectation", "Implied Expectation", "What the Price Implies"],
    "Bear case": ["Bear case", "Bear Case", "Bear"],
    "Final action framework": ["Final action framework", "Final Action Framework"],
    "Maximum risk": ["Maximum risk", "Maximum Risk"],
}


def _normalize(s: str) -> str:
    """Normalize for fuzzy matching — safe for full text."""
    t = re.sub(r"\s+", " ", s).strip().lower()
    t = t.replace("&", "and")
    t = re.sub(r"^\d+[\.\s\)-]+", "", t)
    # Safe: only strip trailing parenthetical descriptions like "(US Equity)"
    t = re.sub(r"\s*\([^)]*\)", "", t)
    return t.strip()


def _match_section(canonical: str, text: str, aliases: dict[str, list[str]]) -> bool:
    """Check if a section (canonical name or any alias) appears in text."""
    norm_text = _normalize(text)

    # Direct canonical match
    if _normalize(canonical) in norm_text:
        return True

    # Alias match
    for alias in aliases.get(canonical, []):
        if _normalize(alias) in norm_text:
            return True

    return False


# ── Hardlock Gate ──────────────────────────────────────────────────────

def check_hardlock(text: str) -> dict[str, Any]:
    """Check data integrity. Returns {status, failure_type, details}."""
    failures: list[str] = []
    tl = text.lower()

    # 1. Stock price — must have ACTUAL price value, not just keyword in "no price" context
    has_actual_price = bool(re.search(r'[\$¥￥]\s*[\d,]+\.?\d*', text))
    has_price_in_figure = bool(bool(re.search(r'股价.*\d', text)) or bool(re.search(r'\d.*元', text)))
    price_labeled_missing = bool(re.search(
        r'(?:无[数据]?[：:]?\s*|缺失[：:]?\s*|缺少[：:]?\s*|暂无[：:]?\s*|没有[：:]?\s*|N/A\s*|n/a\s*|Not Available\s*|No data\s*).{0,20}(?:股价|stock price|closing price)',
        text, re.IGNORECASE
    ))
    if (not has_actual_price and not has_price_in_figure) or price_labeled_missing:
        failures.append("missing_price")

    # 2. Market cap — must have actual numerical value
    has_actual_mcap_num = bool(re.search(
        r'\d+[,.]?\d*\s*(?:万亿|亿|万|千亿|兆|[Tt][Rr]?[Nn]?|[Bb][Nn]?[Dd]?)$',
        text
    )) or bool(re.search(r'~\$[\d,.]+\s*[TtBb]', text))
    has_mcap_in_figure = bool(re.search(r'市值.*\d', text))
    mcap_labeled_missing = bool(re.search(
        r'(?:无[数据]?[：:]?\s*|缺失[：:]?\s*|缺少[：:]?\s*|暂无[：:]?\s*|N/A\s*|n/a\s*).{0,20}(?:市值|market cap)',
        text, re.IGNORECASE
    ))
    if (not has_actual_mcap_num and not has_mcap_in_figure) or mcap_labeled_missing:
        failures.append("missing_market_cap")

    # 3. Financial sources
    sources_lower = ["财报", "年报", "季报", "financial statement", "annual report", "10-k", "10-q", "ir", "sec", "microsoft ir", "sec edgar"]
    if not any(s in tl for s in sources_lower):
        failures.append("missing_financial_sources")

    # 4. Revenue or EPS
    has_rev = any(kw in tl for kw in ["营收", "收入", "revenue", "sales", "net income", "profit"])
    has_eps = any(kw in tl for kw in ["eps", "每股收益", "earnings per share", "earnings"])
    has_earnings_text = bool(re.search(r'\$\s*[\d,.]+\s*(?:B|M|b|m|per share|EPS|eps)', text))
    if not has_rev and not has_eps and not has_earnings_text:
        failures.append("missing_revenue_or_eps")

    passed = len(failures) == 0
    return {
        "status": "PASS" if passed else "FAIL",
        "failure_type": "_".join(failures) if failures else "",
        "details": failures,
    }


# ── Template Gate ──────────────────────────────────────────────────────

def check_template(text: str, lang: str) -> dict[str, Any]:
    """Check formal template section completeness."""
    canon = CANONICAL_ZH if lang == "zh" else CANONICAL_EN
    missing: list[str] = []
    for key, heading in canon.items():
        if heading not in text:
            # Also accept ### for subsections
            alt = heading.replace("## ", "### ")
            if alt not in text:
                missing.append(heading.replace("## ", ""))

    passed = len(missing) == 0
    return {
        "status": "PASS" if passed else "FAIL_TEMPLATE_COMPLIANCE",
        "missing_sections": missing,
        "details": f"{len(missing)} sections missing" if missing else "all sections present",
    }


# ── Core Quality Gate ─────────────────────────────────────────────────

def check_core_quality(text: str, lang: str, mode: str) -> dict[str, Any]:
    """Check core module presence and content depth."""
    # Select modules by mode
    if mode == "smoke":
        if lang == "zh":
            modules = SMOKE_MODULES_ZH
            aliases = SECTION_ALIASES_ZH
        else:
            modules = SMOKE_MODULES_EN
            aliases = SECTION_ALIASES_EN
    else:  # core or formal
        if lang == "zh":
            modules = CORE_MODULES_ZH
            aliases = SECTION_ALIASES_ZH
        else:
            modules = CORE_MODULES_EN
            aliases = SECTION_ALIASES_EN

    missing_modules: list[str] = []
    present_modules: list[str] = []

    for module in modules:
        if _match_section(module, text, aliases):
            present_modules.append(module)
        else:
            missing_modules.append(module)

    # Content depth: check key keywords per present module
    depth_checks: list[tuple[str, list[str]]] = []
    if lang == "zh":
        depth_checks = [
            ("竞争与份额模型", ["TAM", "SAM", "SOM", "竞争", "份额"]),
            ("市场隐含预期", ["隐含", "倍数", "差异"]),
            ("公司基本盘", ["收入", "毛利率", "增长"]),
            ("最大风险", ["风险", "概率", "影响"]),
            ("最终操作方案", ["条件", "动作"]),
        ]
    else:
        depth_checks = [
            ("Competition and share model", ["TAM", "SAM", "SOM"]),
            ("Implied expectation", ["implied", "CAGR", "multiple"]),
            ("Company fundamentals", ["revenue", "margin"]),
            ("Maximum risk", ["risk"]),
            ("Final action framework", ["action"]),
        ]

    shallow_modules: list[str] = []
    for module_name, keywords in depth_checks:
        if _match_section(module_name, text, aliases):
            found = sum(1 for kw in keywords if kw.lower() in text.lower())
            if found < min(2, len(keywords)):
                shallow_modules.append(module_name)

    if missing_modules:
        status = "FAIL_CONTENT_DEPTH"
    elif shallow_modules:
        status = "CONDITIONAL_PASS"
    else:
        status = "PASS"

    return {
        "status": status,
        "present_modules": present_modules,
        "missing_modules": missing_modules,
        "shallow_modules": shallow_modules,
        "details": f"{len(present_modules)}/{len(modules)} modules present"
        if not missing_modules
        else f"missing: {', '.join(missing_modules)}",
    }


# ── Main check ─────────────────────────────────────────────────────────

def check_report(
    text: str,
    mode: str = "formal",
    language: str = "auto",
    hardlock_verdict: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Multi-mode, multi-gate report check.

    Modes:
      formal - full template + core quality + hardlock
      core   - core quality + hardlock (no template check)
      smoke  - minimal core quality + hardlock
    """
    # Detect language
    if language == "auto":
        zh_count = sum(1 for h in CANONICAL_ZH.values() if h in text)
        en_count = sum(1 for h in CANONICAL_EN.values() if h in text)
        lang = "en" if en_count > zh_count else "zh"
    else:
        lang = language

    # Legacy text hardlock / structure sanity gate — always run
    legacy_hardlock = check_hardlock(text)

    # Template Gate — only in formal mode
    template: dict[str, Any] = {"status": "SKIPPED", "missing_sections": [], "details": "mode != formal"}
    if mode == "formal":
        template = check_template(text, lang)

    # Core Quality Gate — run in all modes
    core_quality = check_core_quality(text, lang, mode)

    # ── Determine final status ──
    legacy_hardlock_fail = legacy_hardlock["status"] == "FAIL"

    # When a formal structured hardlock passes, text heuristics become
    # warnings rather than blocking gates.  Rule-description text such as
    # "缺少有效股价则不可准出" must not override a PASS_FORMAL verdict.
    external_hardlock_is_formal = (
        hardlock_verdict is not None
        and str(hardlock_verdict.get("status", "")) == "PASS_FORMAL"
    )
    hardlock_fail = legacy_hardlock_fail and not external_hardlock_is_formal

    template_fail = template["status"] != "PASS"
    core_fail = core_quality["status"] in ("FAIL_CONTENT_DEPTH",)

    if hardlock_fail:
        structure_status = "FAIL_DATA_HARDLOCK"
        structure_release_grade = "不可准出"
    elif mode == "formal" and template_fail:
        structure_status = "CORE_PASS_TEMPLATE_FAIL"
        structure_release_grade = "条件准出"
    elif core_fail:
        structure_status = "FAIL_CONTENT_DEPTH"
        structure_release_grade = "条件准出"
    elif core_quality["status"] == "CONDITIONAL_PASS":
        structure_status = "CONDITIONAL_PASS"
        structure_release_grade = "条件准出"
    else:
        structure_status = "FULL_PASS"
        structure_release_grade = "结构通过"

    external_hardlock_status = "PASS_TEST_ONLY"
    external_hardlock_violations: list[str] = []
    if hardlock_verdict is not None:
        external_hardlock_status = str(hardlock_verdict.get("status", "FAIL_DATA_HARDLOCK"))
        external_hardlock_violations = [str(item) for item in hardlock_verdict.get("violations", [])]

    if structure_status != "FULL_PASS":
        final_status = structure_status
        release_decision = "不可准出" if structure_status == "FAIL_DATA_HARDLOCK" else "条件准出"
        failure_family = "FAIL_DATA_HARDLOCK" if structure_status == "FAIL_DATA_HARDLOCK" else "STRUCTURE_QUALITY"
    elif hardlock_verdict is None:
        final_status = "PASS_TEST_ONLY"
        release_decision = "不可准出"
        failure_family = "FAIL_DATA_HARDLOCK"
    elif external_hardlock_status == "PASS_TEST_ONLY":
        final_status = "PASS_TEST_ONLY"
        release_decision = "TEST_ONLY_NOT_RELEASABLE"
        failure_family = ""
    elif external_hardlock_status == "PASS_FORMAL":
        final_status = "FULL_PASS"
        release_decision = "可准出"
        failure_family = ""
    else:
        final_status = "FAIL_DATA_HARDLOCK"
        release_decision = "不可准出"
        failure_family = "FAIL_DATA_HARDLOCK"

    can_formal = final_status == "FULL_PASS"
    can_test = final_status in ("FULL_PASS", "PASS_TEST_ONLY", "CONDITIONAL_PASS", "CORE_PASS_TEMPLATE_FAIL")

    # Build required fixes
    fixes: list[str] = []
    warnings: list[str] = []

    if legacy_hardlock_fail and external_hardlock_is_formal:
        # Text heuristic flagged issues but structured hardlock passed —
        # likely rule-description text in the report body.  Downgrade to
        # warning rather than blocking.
        for detail in legacy_hardlock["details"]:
            warnings.append(f"文本启发式标记: {detail}（结构化Hardlock已通过，可能是规则说明文本触发的误报）")
    elif hardlock_fail:
        for detail in legacy_hardlock["details"]:
            if detail == "missing_price":
                fixes.append("补充最新股价")
            elif detail == "missing_market_cap":
                fixes.append("补充市值")
            elif detail == "missing_financial_sources":
                fixes.append("补充财务数据来源")
            elif detail == "missing_revenue_or_eps":
                fixes.append("补充营收或EPS")
    if template_fail and mode == "formal":
        fixes.append("使用正式模板重新生成报告，保留标准章节标题")
    if core_fail:
        fixes.append("补充缺失的核心模块：")
        fixes.extend(f"  - {m}" for m in core_quality.get("missing_modules", []))
    if hardlock_verdict is None and structure_status == "FULL_PASS":
        fixes.append("补充外部 Data Integrity Hardlock verdict 后再申请正式准出")
    elif hardlock_verdict is not None and external_hardlock_status != "PASS_FORMAL":
        fixes.extend(f"hardlock: {item}" for item in external_hardlock_violations)

    return {
        "final_status": final_status,
        "release_grade": release_decision,
        "release_decision": release_decision,
        "structure_status": structure_status,
        "hardlock_status": external_hardlock_status,
        "structure_release_grade": structure_release_grade,
        "failure_family": failure_family,
        "hardlock_gate": external_hardlock_status,
        "legacy_data_gate": legacy_hardlock["status"],
        "template_gate": template["status"],
        "core_quality_gate": core_quality["status"],
        "failure_type": legacy_hardlock["failure_type"] if hardlock_fail else ("template_compliance" if template_fail and mode == "formal" else "content_depth"),
        "can_be_used_as_formal_report": can_formal,
        "can_be_used_as_framework_test": can_test,
        "required_fixes": fixes,
        "warnings": warnings,
        "_language": lang,
        "_mode": mode,
    }


def render_result(r: dict[str, Any]) -> str:
    """Render gatekeeper result as YAML-like structured output."""
    lines = [
        "gatekeeper_result:",
        f"  final_status: {r['final_status']}",
        f"  release_grade: {r['release_grade']}",
        f"  release_decision: {r['release_decision']}",
        f"  structure_status: {r['structure_status']}",
        f"  hardlock_status: {r['hardlock_status']}",
        f"  failure_family: {r['failure_family']}",
        f"  hardlock_gate: {r['hardlock_gate']}",
        f"  legacy_data_gate: {r['legacy_data_gate']}",
        f"  template_gate: {r['template_gate']}",
        f"  core_quality_gate: {r['core_quality_gate']}",
        f"  failure_type: {r['failure_type']}",
        f"  can_be_used_as_formal_report: {str(r['can_be_used_as_formal_report']).lower()}",
        f"  can_be_used_as_framework_test: {str(r['can_be_used_as_framework_test']).lower()}",
        f"  required_fixes:",
    ]
    for fix in r.get("required_fixes", []):
        lines.append(f"    - {fix}")
    return "\n".join(lines)


# ── Backward-compatible wrappers (legacy test support) ─────────────────


def check_report_text(text: str, language: str = "zh") -> dict[str, Any]:
    """
    Backward-compatible wrapper for legacy comprehensive tests.

    Returns a dict with at least:
    - passed: bool
    - missing_sections: list
    - banned_phrases: list
    - raw_result: dict
    """
    result = check_report(text, mode="formal", language=language)
    banned = find_banned_phrases(text)
    return {
        "passed": result["can_be_used_as_formal_report"],
        "missing_sections": result.get("required_fixes", []),
        "banned_phrases": banned,
        "raw_result": result,
    }


def render_gatekeeper_result(result: dict[str, Any]) -> str:
    """
    Backward-compatible renderer.

    If result has raw_result, render both legacy summary and structured result.
    The output includes "Pass: True" or "Pass: False" for old tests.
    It includes "Missing Sections" for failed tests.
    """
    passed = result.get("passed", False)
    lines = [f"Pass: {passed}"]
    lines.append("Missing Sections:")
    for item in result.get("missing_sections", []):
        lines.append(f"- {item}")
    if "raw_result" in result:
        lines.append("")
        lines.append(render_result(result["raw_result"]))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Meridian Gatekeeper v2.1 — three-mode, multi-gate report release check"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to Markdown report (positional)",
    )
    parser.add_argument("--file", default=None, help="Path to Markdown report (--file flag)")
    parser.add_argument(
        "--mode",
        choices=("formal", "core", "smoke"),
        default="formal",
        help="Gatekeeper mode (formal=full, core=framework test, smoke=quick)",
    )
    parser.add_argument(
        "--language",
        choices=("auto", "zh", "en"),
        default="auto",
    )
    parser.add_argument("--hardlock-file", default=None, help="Path to JSON hardlock verdict")
    args = parser.parse_args()

    file_path = args.file or args.path
    if file_path is None:
        parser.error("report path is required (positional or --file)")
    text = Path(file_path).read_text(encoding="utf-8")
    hardlock_verdict = None
    if args.hardlock_file:
        hardlock_verdict = json.loads(Path(args.hardlock_file).read_text(encoding="utf-8"))
    result = check_report(text, mode=args.mode, language=args.language, hardlock_verdict=hardlock_verdict)
    print(render_result(result))


if __name__ == "__main__":
    main()
