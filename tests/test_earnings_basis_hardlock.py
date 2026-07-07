import json
from pathlib import Path

from tools.earnings_basis_checker import (
    STATUS_FAIL_EARNINGS_BASIS,
    STATUS_PASS_FORMAL,
    check_earnings_basis,
)

FIXTURES = Path(__file__).parent / "fixtures" / "data_cards"


def _load_entry(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_gaap_actual_defaults_to_full_permission():
    result = check_earnings_basis(_load_entry("sample_gaap_actual.json"))

    assert result.status == STATUS_PASS_FORMAL
    assert result.permission == "full"


def test_management_guidance_defaults_to_reference_only():
    result = check_earnings_basis(_load_entry("sample_guidance_background.json"))

    assert result.status == STATUS_PASS_FORMAL
    assert result.permission == "reference_only"


def test_aggregator_field_requires_verification_for_core_valuation():
    result = check_earnings_basis(_load_entry("sample_aggregator_unverified.json"))

    assert result.status == STATUS_FAIL_EARNINGS_BASIS
    assert result.permission == "reference_only"
    assert result.violations == (
        "aggregator field must be source-verified before core valuation use",
    )


def test_guidance_eps_cannot_be_used_as_trailing_eps():
    result = check_earnings_basis(_load_entry("sample_guidance_as_trailing.json"))

    assert result.status == STATUS_FAIL_EARNINGS_BASIS
    assert result.violations == ("guidance EPS cannot be used as trailing EPS",)


def test_missing_basis_fails_hardlock():
    result = check_earnings_basis({"usage_context": "core_valuation"})

    assert result.status == STATUS_FAIL_EARNINGS_BASIS
    assert result.violations == ("earnings basis is required",)


def test_adjusted_eps_needs_gaap_anchor_for_conclusion_use():
    result = check_earnings_basis(_load_entry("sample_adjusted_without_gaap_anchor.json"))

    assert result.status == STATUS_FAIL_EARNINGS_BASIS
    assert result.permission == "reference_only"
    assert result.violations == (
        "adjusted EPS cannot enter conclusion without GAAP comparison",
    )
