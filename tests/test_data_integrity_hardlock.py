import json
from pathlib import Path

from tools.data_integrity_hardlock import (
    STATUS_FAIL_DATA_HARDLOCK,
    STATUS_FAIL_INDUSTRY_HARD_FIELDS,
    STATUS_PASS_FORMAL,
    aggregate_hardlock_verdicts,
)

FIXTURES = Path(__file__).parent / "fixtures" / "data_integrity"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_hardlock_aggregate_passes_when_all_modules_pass():
    result = aggregate_hardlock_verdicts(_load_fixture("sample_all_pass.json"))

    assert result.status == STATUS_PASS_FORMAL
    assert result.violations == ()
    assert result.details["module_statuses"]["industry_hard_fields"] == STATUS_PASS_FORMAL
    assert result.details["release_tier"] == "formal_releasable"


def test_hardlock_aggregate_propagates_single_failure_status():
    result = aggregate_hardlock_verdicts(_load_fixture("sample_single_failure.json"))

    assert result.status == "FAIL_EARNINGS_BASIS"
    assert result.violations == ("guidance EPS cannot be used as trailing EPS",)
    assert result.details["release_tier"] == "not_releasable"


def test_hardlock_aggregate_returns_fail_data_hardlock_for_multiple_failures():
    result = aggregate_hardlock_verdicts(_load_fixture("sample_multiple_failures.json"))

    assert result.status == STATUS_FAIL_DATA_HARDLOCK
    assert any("data_card: missing required field: source" == item for item in result.violations)
    assert any("earnings_basis: guidance EPS cannot be used as trailing EPS" == item for item in result.violations)
    assert any("capital_bridge: market cap closure exceeds tolerance" == item for item in result.violations)
    assert any("industry_hard_fields: missing required industry hard field: mcr_or_mlr" == item for item in result.violations)


def test_hardlock_aggregate_degrades_non_formal_module_statuses_to_fail_data_hardlock():
    result = aggregate_hardlock_verdicts(_load_fixture("sample_degraded_status.json"))

    assert result.status == STATUS_FAIL_DATA_HARDLOCK
    assert result.violations == (
        "earnings_basis: valuation input lacks metadata",
    )


def test_hardlock_aggregate_propagates_industry_hard_fields_as_single_failure():
    result = aggregate_hardlock_verdicts(_load_fixture("sample_industry_only_failure.json"))

    assert result.status == STATUS_FAIL_INDUSTRY_HARD_FIELDS
    assert result.violations == ("missing required industry hard field: share_count_bridge",)
    assert result.details["module_statuses"]["industry_hard_fields"] == STATUS_FAIL_INDUSTRY_HARD_FIELDS


def test_hardlock_aggregate_combines_industry_hard_fields_with_other_failures():
    result = aggregate_hardlock_verdicts(_load_fixture("sample_industry_plus_other_failure.json"))

    assert result.status == STATUS_FAIL_DATA_HARDLOCK
    assert any("earnings_basis: guidance EPS cannot be used as trailing EPS" == item for item in result.violations)
    assert any("industry_hard_fields: missing required industry hard field: mcr_or_mlr" == item for item in result.violations)
