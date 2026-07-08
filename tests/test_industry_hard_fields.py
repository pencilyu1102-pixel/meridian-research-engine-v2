import json
from pathlib import Path

from tools.industry_hard_fields import (
    STATUS_FAIL_INDUSTRY_HARD_FIELDS,
    STATUS_PASS_FORMAL,
    check_industry_hard_fields,
    get_required_fields,
    load_industry_hard_fields,
)

FIXTURES = Path(__file__).parent / "fixtures" / "industry_hard_fields"


def _check_fixture(name: str):
    payload = load_industry_hard_fields(FIXTURES / name)
    return check_industry_hard_fields(payload)


def test_cn_semiconductor_growth_passes_when_all_required_fields_are_present():
    result = _check_fixture("sample_cn_growth_pass.json")

    assert get_required_fields("CN_SEMICONDUCTOR_GROWTH") == (
        "revenue_growth_driver",
        "gross_margin_trend",
        "r_and_d_intensity",
        "share_count_bridge",
        "valuation_anchor_type",
        "low_base_or_oneoff_flag",
    )
    assert result.status == STATUS_PASS_FORMAL
    assert result.missing_fields == ()
    assert result.field_count_required == 6
    assert result.field_count_present == 6
    assert result.violations == ()


def test_cn_semiconductor_growth_fails_when_share_bridge_is_missing():
    result = _check_fixture("sample_cn_growth_missing_share_bridge.json")

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.missing_fields == ("share_count_bridge",)
    assert "missing required industry hard field: share_count_bridge" in result.violations


def test_us_managed_care_passes_when_all_required_fields_are_present():
    result = _check_fixture("sample_us_health_pass.json")

    assert get_required_fields("US_MANAGED_CARE") == (
        "mcr_or_mlr",
        "utilization_trend",
        "medicare_advantage",
        "insurance_segment",
        "health_services_segment",
        "pharmacy_or_care_services",
        "doj_risk",
        "cms_risk",
        "ftc_risk",
        "oig_risk",
        "sec_risk",
    )
    assert result.status == STATUS_PASS_FORMAL
    assert result.field_count_required == 11
    assert result.field_count_present == 11
    assert result.missing_fields == ()


def test_us_managed_care_fails_when_mcr_or_mlr_is_missing():
    result = _check_fixture("sample_us_health_missing_mcr.json")

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.missing_fields == ("mcr_or_mlr",)
    assert "missing required industry hard field: mcr_or_mlr" in result.violations


def test_us_managed_care_fails_when_regulatory_risk_field_is_missing():
    result = _check_fixture("sample_us_health_missing_regulatory_risk.json")

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.missing_fields == ("cms_risk",)
    assert "missing required industry hard field: cms_risk" in result.violations


def test_us_managed_care_fails_when_insurance_segment_is_missing():
    payload = json.loads((FIXTURES / "sample_us_health_pass.json").read_text(encoding="utf-8"))
    payload["fields"]["insurance_segment"]["present"] = False
    payload["fields"]["insurance_segment"]["can_enter_conclusion"] = "blocked"
    result = check_industry_hard_fields(payload)

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.missing_fields == ("insurance_segment",)
    assert "missing required industry hard field: insurance_segment" in result.violations


def test_us_managed_care_fails_when_health_services_segment_is_missing():
    payload = json.loads((FIXTURES / "sample_us_health_pass.json").read_text(encoding="utf-8"))
    payload["fields"]["health_services_segment"]["present"] = False
    payload["fields"]["health_services_segment"]["can_enter_conclusion"] = "blocked"
    result = check_industry_hard_fields(payload)

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.missing_fields == ("health_services_segment",)
    assert "missing required industry hard field: health_services_segment" in result.violations


def test_us_managed_care_fails_when_pharmacy_or_care_services_is_missing():
    payload = json.loads((FIXTURES / "sample_us_health_pass.json").read_text(encoding="utf-8"))
    payload["fields"]["pharmacy_or_care_services"]["present"] = False
    payload["fields"]["pharmacy_or_care_services"]["can_enter_conclusion"] = "blocked"
    result = check_industry_hard_fields(payload)

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.missing_fields == ("pharmacy_or_care_services",)
    assert "missing required industry hard field: pharmacy_or_care_services" in result.violations


def test_legacy_unh_specific_fields_are_not_required_anymore():
    payload = json.loads((FIXTURES / "sample_us_health_pass.json").read_text(encoding="utf-8"))
    payload["fields"]["optum"] = {"present": False, "can_enter_conclusion": "blocked"}
    payload["fields"]["unitedhealthcare"] = {"present": False, "can_enter_conclusion": "blocked"}
    payload["fields"]["pbm"] = {"present": False, "can_enter_conclusion": "blocked"}
    result = check_industry_hard_fields(payload)

    assert result.status == STATUS_PASS_FORMAL
    assert result.missing_fields == ()


def test_reference_only_field_cannot_support_formal_conclusion():
    payload = json.loads((FIXTURES / "sample_us_health_pass.json").read_text(encoding="utf-8"))
    payload["fields"]["pharmacy_or_care_services"]["can_enter_conclusion"] = "reference_only"
    result = check_industry_hard_fields(payload)

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.missing_fields == ()
    assert (
        "industry hard field pharmacy_or_care_services cannot support formal conclusion: reference_only"
        in result.violations
    )


def test_unknown_industry_adapter_cannot_pass_formal():
    payload = {
        "ticker": "SAMPLE_UNKNOWN",
        "industry_adapter": "UNKNOWN_ADAPTER",
        "fields": {},
    }
    result = check_industry_hard_fields(payload)

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.industry_adapter == "UNKNOWN_ADAPTER"
    assert result.field_count_required == 0
    assert result.field_count_present == 0
    assert result.violations == ("unknown industry_adapter: UNKNOWN_ADAPTER",)
