#!/usr/bin/env python3
"""
Meridian Research Engine 2.0 — Offline Full-Chain Demo

Demonstrates: synthetic research input → structured report → Hardlock + Gatekeeper → release status.

No API key, no network. Results are deterministic and reproducible.

IMPORTANT: FULL_PASS validates contract completeness only. It does not verify
real-world data or constitute any research conclusion or investment advice.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))
sys.path.insert(0, str(ROOT))

# Import shared hardlock builder — same path as validate_agent_report.py
from scripts.validate_agent_report import build_hardlock_from_bundle, load_bundle, compute_bundle_hash

SAMPLE_DIR = ROOT / "examples" / "full_chain_sample"
OUTPUT_DIR = ROOT / "outputs" / "demo"
BUNDLE_PATH = SAMPLE_DIR / "research_bundle.json"
TODAY = date.today().isoformat()

# ── Synthetic identifiers ─────────────────────────────────────────────
TICKER = "SAMPLE_MANAGED_CARE"
COMPANY_NAME = "SAMPLE Managed Care Co."
MARKET = "US Equity"
INDUSTRY_ADAPTER = "US_MANAGED_CARE"


def generate_report() -> str:
    """Load report fixture and substitute placeholders."""
    fixture_path = SAMPLE_DIR / "report_fixture_zh.md"
    template = fixture_path.read_text(encoding="utf-8")
    bundle = load_bundle(BUNDLE_PATH)
    bundle_hash = compute_bundle_hash(bundle)
    return template.format(
        today=TODAY,
        ticker=TICKER,
        company_name=COMPANY_NAME,
        market=MARKET,
        industry_adapter=INDUSTRY_ADAPTER,
        bundle_sha256=bundle_hash,
    )


def run_demo():
    """Main demo runner: build hardlock → generate report → run gatekeeper → save results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  Meridian Research Engine 2.0 — 离线全链路 Demo")
    print("=" * 60)
    print()

    # 1. Build hardlock verdict from shared bundle
    print("[1/4] 构建 Data Integrity Hardlock 裁决...")
    try:
        bundle = load_bundle(BUNDLE_PATH)
        hardlock_verdict = build_hardlock_from_bundle(bundle)
        print(f"  Hardlock 状态: {hardlock_verdict['status']}")
        for k, v in hardlock_verdict["module_verdicts"].items():
            print(f"    {k}: {v['status']}")
        if hardlock_verdict["violations"]:
            print(f"  违规项: {hardlock_verdict['violations']}")
    except Exception as e:
        print(f"  FAIL: Hardlock 构建失败: {e}")
        sys.exit(1)

    # 2. Generate report
    print("[2/4] 生成虚构投研报告...")
    try:
        report_md = generate_report()
        report_path = OUTPUT_DIR / f"{TICKER}_full_chain_report_zh.md"
        report_path.write_text(report_md, encoding="utf-8")
        print(f"  报告已保存: {report_path}")
    except Exception as e:
        print(f"  FAIL: 报告生成失败: {e}")
        sys.exit(1)

    # 3. Gatekeeper check
    print("[3/4] 运行 Gatekeeper 校核...")
    try:
        hardlock_path = OUTPUT_DIR / f"{TICKER}_hardlock_verdict.json"
        hardlock_path.write_text(
            json.dumps(hardlock_verdict, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        from tools.report_gatekeeper import check_report
        result = check_report(
            report_md, mode="formal", language="zh", hardlock_verdict=hardlock_verdict
        )

        print(f"  Gatekeeper 最终状态: {result['final_status']}")
        print(f"  准出决定: {result['release_decision']}")
        print(f"  结构状态: {result['structure_status']}")
        print(f"  Hardlock 外部状态: {result['hardlock_status']}")
        print(f"  模板门: {result['template_gate']}")
        print(f"  核心质量门: {result['core_quality_gate']}")
        print(f"  数据门: {result['legacy_data_gate']}")
        if result.get("warnings"):
            print(f"  警告: {result['warnings']}")
        if result.get("required_fixes"):
            print(f"  需要修复: {result['required_fixes']}")
    except Exception as e:
        print(f"  FAIL: Gatekeeper 运行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 4. Save result with boundary metadata
    print("[4/4] 保存完整结果...")
    demo_result = {
        "demo_info": {
            "ticker": TICKER,
            "company_name": COMPANY_NAME,
            "market": MARKET,
            "industry_adapter": INDUSTRY_ADAPTER,
            "date": TODAY,
            "data_provenance": "SYNTHETIC_FIXTURE",
            "real_world_sources_verified": False,
            "production_research_eligible": False,
            "account_action": "LOCKED",
            "engine_verdict_interpretation": "FULL_PASS validates contract completeness only",
            "disclaimer": (
                "This demo uses synthetic fixture data only. No real companies, prices, "
                "or investment advice. FULL_PASS does not constitute a research conclusion."
            ),
        },
        "hardlock_verdict": hardlock_verdict,
        "gatekeeper_result": result,
        "output_files": {
            "report_markdown": str(report_path),
            "hardlock_verdict_json": str(hardlock_path),
        },
    }
    result_path = OUTPUT_DIR / f"{TICKER}_full_chain_result.json"
    result_path.write_text(
        json.dumps(demo_result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  结果已保存: {result_path}")

    print()
    print("=" * 60)
    print(f"  Demo 完成")
    print(f"  标的: {TICKER}")
    print(f"  Hardlock: {hardlock_verdict['status']}")
    print(f"  Gatekeeper: {result['final_status']}")
    print(f"  准出决定: {result['release_decision']}")
    print(f"  FULL_PASS 仅验证契约完整性")
    print(f"  报告: {report_path}")
    print(f"  结果: {result_path}")
    print("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    run_demo()
