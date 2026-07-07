import json
from pathlib import Path

from tools.capital_structure_bridge import (
    STATUS_FAIL_CAPITAL_BRIDGE,
    STATUS_PASS_FORMAL,
    validate_capital_structure_bridge,
)

FIXTURES = Path(__file__).parent / "fixtures" / "capital_bridge"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_a_share_core_metrics_without_bridge_fail():
    result = validate_capital_structure_bridge(_load_fixture("sample_a_share_missing_bridge.json"))

    assert result.status == STATUS_FAIL_CAPITAL_BRIDGE
    assert result.violations == (
        "A-share report includes price/market cap/EPS/PE/shares without capital bridge",
    )


def test_a_share_bridge_passes_when_corporate_actions_are_bridged():
    result = validate_capital_structure_bridge(_load_fixture("sample_a_share_bridge_pass.json"))

    assert result.status == STATUS_PASS_FORMAL
    assert result.violations == ()


def test_us_market_cap_closure_passes_within_tolerance():
    result = validate_capital_structure_bridge(_load_fixture("sample_us_market_cap_closure_pass.json"))

    assert result.status == STATUS_PASS_FORMAL
    assert "market_cap_gap_pct" in result.details


def test_us_pe_mismatch_without_denominator_explanation_fails():
    result = validate_capital_structure_bridge(_load_fixture("sample_us_pe_mismatch_fail.json"))

    assert result.status == STATUS_FAIL_CAPITAL_BRIDGE
    assert result.violations == (
        "PE denominator mismatch exceeds tolerance without denominator explanation",
    )


def test_us_share_basis_needs_usage_explanation():
    result = validate_capital_structure_bridge(_load_fixture("sample_us_share_basis_missing_explanation.json"))

    assert result.status == STATUS_FAIL_CAPITAL_BRIDGE
    assert result.violations == (
        "current shares and weighted diluted shares both present without basis usage explanation",
    )


def test_us_denominator_explanation_can_clear_mismatch_when_otherwise_explained():
    result = validate_capital_structure_bridge(_load_fixture("sample_us_explained_denominator_pass.json"))

    assert result.status == STATUS_PASS_FORMAL
    assert result.violations == ()
