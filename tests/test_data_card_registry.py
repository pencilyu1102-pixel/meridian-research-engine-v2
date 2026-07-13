import json
from pathlib import Path

from tools.data_card_registry import (
    STATUS_FAIL_DATA_CARD_MISSING,
    STATUS_FAIL_SOURCE_PERMISSION,
    STATUS_PASS_FORMAL,
    DataCardRegistry,
    validate_data_card,
)

FIXTURES = Path(__file__).parent / "fixtures" / "data_cards"


def _load_single_card(name: str) -> dict:
    cards = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return cards[0]


def test_complete_data_card_passes_validation():
    card = _load_single_card("sample_cn_growth_full.json")
    result = validate_data_card(card)

    assert result.status == STATUS_PASS_FORMAL
    assert result.violations == ()


def test_missing_required_fields_fail_validation():
    cases = [
        "sample_missing_source.json",
        "sample_missing_timestamp.json",
        "sample_missing_period.json",
        "sample_missing_unit.json",
        "sample_missing_currency.json",
    ]

    for case in cases:
        result = validate_data_card(_load_single_card(case))
        assert result.status == STATUS_FAIL_DATA_CARD_MISSING
        assert result.violations


def test_unknown_source_tier_fails_permission_check():
    result = validate_data_card(_load_single_card("sample_unknown_source_tier.json"))

    assert result.status == STATUS_FAIL_SOURCE_PERMISSION
    assert result.violations == ("unknown source_tier: Z",)


def test_blocked_card_cannot_enter_conclusion():
    registry = DataCardRegistry.from_json_file(FIXTURES / "sample_blocked_card.json")

    validation = registry.validate("sample_background_metric")
    permission = registry.conclusion_permission("sample_background_metric")

    assert validation.status == STATUS_PASS_FORMAL
    assert permission.can_enter_conclusion is False
    assert permission.can_enter_primary_valuation is False
    assert permission.reason == "blocked"


def test_reference_only_cards_cannot_enter_primary_valuation():
    registry = DataCardRegistry(
        [
            {
                "field_name": "sample_reference_metric",
                "value": 10,
                "source": "Synthetic sample",
                "source_tier": "B",
                "timestamp": "2026-07-07T00:00:00Z",
                "period": "FY2025",
                "unit": "ratio",
                "currency": "N/A",
                "accounting_basis": "reference_metric",
                "can_enter_conclusion": "reference_only",
                "notes": "reference only",
                "freshness_status": "current",
                "has_conflict": False,
            }
        ]
    )

    permission = registry.conclusion_permission("sample_reference_metric")

    assert permission.can_enter_conclusion is False
    assert permission.can_enter_primary_valuation is False
    assert permission.reason == "reference_only"
