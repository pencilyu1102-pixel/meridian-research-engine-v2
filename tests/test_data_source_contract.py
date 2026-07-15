"""Phase 6.1 DataSource contract tests.

Validates the DataSource abstraction, FetchRequest/FetchFailure types,
SyntheticDataSource behaviour, and integration with existing Registry + Source Policy.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.data_card_registry import validate_data_card
from tools.data_source import (
    DataSource,
    FetchFailure,
    FetchFailureReason,
    FetchRequest,
    build_data_card,
)
from tools.source_policy import PROVENANCE_SYNTHETIC
from tools.synthetic_data_source import SyntheticDataSource

FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "data_sources" / "synthetic_source_records.json"
)


# ── Shared helpers ──────────────────────────────────────────────────────

def _make_ds(*, default_tier: str = "S") -> SyntheticDataSource:
    """Return a SyntheticDataSource loaded from the standard fixture."""
    return SyntheticDataSource(fixture_path=FIXTURE_PATH, default_tier=default_tier)


# ══════════════════════════════════════════════════════════════════════════
# A. FetchRequest
# ══════════════════════════════════════════════════════════════════════════

class TestFetchRequest:
    def test_accepts_valid_input(self):
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r1")
        assert req.symbol == "SAMPLE_CO"
        assert req.field == "current_price"
        assert req.request_id == "r1"
        assert req.as_of is None
        assert req.period is None
        assert req.context == {}

    def test_accepts_with_optional_fields(self):
        req = FetchRequest(
            symbol="SAMPLE_CO",
            field="eps_ttm",
            request_id="r2",
            as_of="2026-06-30",
            period="2026-Q2",
            context={"region": "US"},
        )
        assert req.as_of == "2026-06-30"
        assert req.period == "2026-Q2"
        assert req.context == {"region": "US"}

    def test_rejects_empty_symbol(self):
        with pytest.raises(ValueError, match="symbol must be non-empty"):
            FetchRequest(symbol="", field="price", request_id="r1")

    def test_rejects_whitespace_symbol(self):
        with pytest.raises(ValueError, match="symbol must be non-empty"):
            FetchRequest(symbol="   ", field="price", request_id="r1")

    def test_rejects_empty_field(self):
        with pytest.raises(ValueError, match="field must be non-empty"):
            FetchRequest(symbol="SAMPLE_CO", field="", request_id="r1")

    def test_rejects_whitespace_field(self):
        with pytest.raises(ValueError, match="field must be non-empty"):
            FetchRequest(symbol="SAMPLE_CO", field="  ", request_id="r1")

    def test_rejects_empty_request_id(self):
        with pytest.raises(ValueError, match="request_id must be non-empty"):
            FetchRequest(symbol="SAMPLE_CO", field="price", request_id="")

    def test_rejects_whitespace_request_id(self):
        with pytest.raises(ValueError, match="request_id must be non-empty"):
            FetchRequest(symbol="SAMPLE_CO", field="price", request_id="   ")

    def test_fields_cannot_be_reassigned(self):
        """FetchRequest is a frozen dataclass: fields cannot be reassigned."""
        req = FetchRequest(symbol="SAMPLE_CO", field="price", request_id="r1")
        with pytest.raises(Exception):
            req.symbol = "OTHER"  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════
# B. DataSource
# ══════════════════════════════════════════════════════════════════════════

class TestDataSource:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            DataSource(  # type: ignore[abstract]
                source_name="test", default_tier="S", data_provenance=PROVENANCE_SYNTHETIC
            )

    def test_invalid_default_tier_is_rejected(self):
        class BadSource(DataSource):
            def fetch(self, request):
                return {}

        with pytest.raises(ValueError, match="default_tier must be one of"):
            BadSource(source_name="test", default_tier="X", data_provenance=PROVENANCE_SYNTHETIC)

    def test_empty_source_name_is_rejected(self):
        class BadSource(DataSource):
            def fetch(self, request):
                return {}

        with pytest.raises(ValueError, match="source_name must be non-empty"):
            BadSource(source_name="", default_tier="S", data_provenance=PROVENANCE_SYNTHETIC)

    def test_empty_data_provenance_is_rejected(self):
        class BadSource(DataSource):
            def fetch(self, request):
                return {}

        with pytest.raises(ValueError, match="data_provenance must be non-empty"):
            BadSource(source_name="test", default_tier="S", data_provenance="")


# ══════════════════════════════════════════════════════════════════════════
# C. SyntheticDataSource — success paths
# ══════════════════════════════════════════════════════════════════════════

class TestSyntheticDataSourceSuccess:
    def test_returns_data_card(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r1")
        card = ds.fetch(req)
        assert isinstance(card, dict)
        assert card["field_name"] == "current_price"
        assert card["value"] == 100.0

    def test_returned_card_matches_requested_field(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r2")
        card = ds.fetch(req)
        assert card["field_name"] == "current_price"

    def test_returned_card_contains_request_id(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="my-trace-id")
        card = ds.fetch(req)
        assert card["request_id"] == "my-trace-id"

    def test_returned_card_contains_synthetic_provenance(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r3")
        card = ds.fetch(req)
        assert card["data_provenance"] == PROVENANCE_SYNTHETIC

    def test_synthetic_source_name_is_present(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r4")
        card = ds.fetch(req)
        assert card["source"] == "SyntheticDataSource"

    def test_period_match_returns_exact_record(self):
        """When request.period is specified, the exact period record is returned."""
        ds = _make_ds()
        req = FetchRequest(
            symbol="SAMPLE_CO", field="market_cap", request_id="r5", period="2025-12-31"
        )
        card = ds.fetch(req)
        assert card["field_name"] == "market_cap"
        assert card["period"] == "2025-12-31"

    def test_single_candidate_without_period_succeeds(self):
        """When only one record exists for symbol+field, no period needed."""
        # SAMPLE_BANK/eps_ttm has exactly one record in the fixture
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_BANK", field="eps_ttm", request_id="r6")
        card = ds.fetch(req)
        assert card["field_name"] == "eps_ttm"

    def test_timestamp_is_explicit_from_fixture(self):
        """Data Card timestamp MUST come from the fixture, not runtime."""
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r7")
        card = ds.fetch(req)
        assert card["timestamp"] == "2026-07-15T00:00:00Z"

    def test_freshness_status_is_explicit_from_fixture(self):
        """Data Card freshness_status MUST come from the fixture, not a default."""
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r8")
        card = ds.fetch(req)
        assert card["freshness_status"] == "current"


# ══════════════════════════════════════════════════════════════════════════
# D. Fix 1: tier isolation — source_tier only from DataSource instance
# ══════════════════════════════════════════════════════════════════════════

class TestTierIsolation:
    def test_s_tier_instance_outputs_s_tier(self):
        ds = _make_ds(default_tier="S")
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r1")
        card = ds.fetch(req)
        assert card["source_tier"] == "S"
        assert card["can_enter_conclusion"] == "full"

    def test_b_tier_instance_outputs_b_tier_capped(self):
        ds = _make_ds(default_tier="B")
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r2")
        card = ds.fetch(req)
        assert card["source_tier"] == "B"
        assert card["can_enter_conclusion"] == "reference_only"

    def test_d_tier_instance_outputs_d_tier_blocked(self):
        ds = _make_ds(default_tier="D")
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r3")
        card = ds.fetch(req)
        assert card["source_tier"] == "D"
        assert card["can_enter_conclusion"] == "blocked"

    def test_fixture_cannot_override_instance_tier(self):
        """Even if a fixture record had a source_tier field, it is ignored."""
        records = [{
            "symbol": "SAMPLE_CO", "field": "test_field", "value": 99,
            "period": "2026-Q2", "unit": "", "currency": "",
            "accounting_basis": "", "requested_permission": "full",
            "freshness_status": "current", "has_conflict": False,
            "notes": "", "timestamp": "2026-07-15T00:00:00Z",
            "source_tier": "S",  # <— this should be ignored
        }]
        ds = SyntheticDataSource(records=records, default_tier="B")
        req = FetchRequest(symbol="SAMPLE_CO", field="test_field", request_id="r4")
        card = ds.fetch(req)
        assert card["source_tier"] == "B"


# ══════════════════════════════════════════════════════════════════════════
# E. Fix 2: ambiguous period detection
# ══════════════════════════════════════════════════════════════════════════

class TestAmbiguousPeriod:
    def test_multiple_candidates_without_period_fails(self):
        """When multiple records share symbol+field, request without period fails."""
        records = [
            {"symbol": "CO", "field": "price", "value": 10, "period": "2026-Q1",
             "freshness_status": "current", "timestamp": "2026-04-01T00:00:00Z",
             "unit": "", "currency": "", "accounting_basis": "",
             "requested_permission": "full", "has_conflict": False, "notes": ""},
            {"symbol": "CO", "field": "price", "value": 20, "period": "2026-Q2",
             "freshness_status": "current", "timestamp": "2026-07-01T00:00:00Z",
             "unit": "", "currency": "", "accounting_basis": "",
             "requested_permission": "full", "has_conflict": False, "notes": ""},
        ]
        ds = SyntheticDataSource(records=records, default_tier="S")
        req = FetchRequest(symbol="CO", field="price", request_id="r1")
        result = ds.fetch(req)
        assert isinstance(result, FetchFailure)
        assert result.reason == FetchFailureReason.PARSE_ERROR
        assert "ambiguous" in result.detail.lower()
        assert "period is required" in result.detail.lower()
        assert result.retry_allowed is False

    def test_single_candidate_without_period_succeeds(self):
        """Single record for symbol+field, no period — should succeed."""
        records = [{
            "symbol": "CO", "field": "price", "value": 10, "period": "2026-Q1",
            "freshness_status": "current", "timestamp": "2026-04-01T00:00:00Z",
            "unit": "", "currency": "", "accounting_basis": "",
            "requested_permission": "full", "has_conflict": False, "notes": "",
        }]
        ds = SyntheticDataSource(records=records, default_tier="S")
        req = FetchRequest(symbol="CO", field="price", request_id="r2")
        card = ds.fetch(req)
        assert isinstance(card, dict)
        assert card["value"] == 10

    def test_exact_period_match_works_with_multiple_candidates(self):
        """With period specified, exact match succeeds even with multiple candidates."""
        records = [
            {"symbol": "CO", "field": "price", "value": 10, "period": "2026-Q1",
             "freshness_status": "current", "timestamp": "2026-04-01T00:00:00Z",
             "unit": "", "currency": "", "accounting_basis": "",
             "requested_permission": "full", "has_conflict": False, "notes": ""},
            {"symbol": "CO", "field": "price", "value": 20, "period": "2026-Q2",
             "freshness_status": "current", "timestamp": "2026-07-01T00:00:00Z",
             "unit": "", "currency": "", "accounting_basis": "",
             "requested_permission": "full", "has_conflict": False, "notes": ""},
        ]
        ds = SyntheticDataSource(records=records, default_tier="S")
        req = FetchRequest(symbol="CO", field="price", period="2026-Q2", request_id="r3")
        card = ds.fetch(req)
        assert card["value"] == 20

    def test_fixture_order_does_not_affect_ambiguity(self):
        """Reversing fixture order does not change ambiguous result."""
        records = [
            {"symbol": "CO", "field": "price", "value": 20, "period": "2026-Q2",
             "freshness_status": "current", "timestamp": "2026-07-01T00:00:00Z",
             "unit": "", "currency": "", "accounting_basis": "",
             "requested_permission": "full", "has_conflict": False, "notes": ""},
            {"symbol": "CO", "field": "price", "value": 10, "period": "2026-Q1",
             "freshness_status": "current", "timestamp": "2026-04-01T00:00:00Z",
             "unit": "", "currency": "", "accounting_basis": "",
             "requested_permission": "full", "has_conflict": False, "notes": ""},
        ]
        ds = SyntheticDataSource(records=records, default_tier="S")
        req = FetchRequest(symbol="CO", field="price", request_id="r4")
        result = ds.fetch(req)
        assert isinstance(result, FetchFailure)
        assert result.reason == FetchFailureReason.PARSE_ERROR


# ══════════════════════════════════════════════════════════════════════════
# F. Fix 3: timestamp and freshness must be explicit
# ══════════════════════════════════════════════════════════════════════════

class TestExplicitTimestampAndFreshness:
    def test_missing_timestamp_returns_parse_error(self):
        records = [{
            "symbol": "CO", "field": "price", "value": 10, "period": "2026-Q1",
            "freshness_status": "current",
            # "timestamp" intentionally missing
            "unit": "", "currency": "", "accounting_basis": "",
            "requested_permission": "full", "has_conflict": False, "notes": "",
        }]
        ds = SyntheticDataSource(records=records, default_tier="S")
        req = FetchRequest(symbol="CO", field="price", request_id="r1")
        result = ds.fetch(req)
        assert isinstance(result, FetchFailure)
        assert result.reason == FetchFailureReason.PARSE_ERROR
        assert "timestamp" in result.detail

    def test_missing_freshness_status_returns_parse_error(self):
        records = [{
            "symbol": "CO", "field": "price", "value": 10, "period": "2026-Q1",
            "timestamp": "2026-04-01T00:00:00Z",
            # "freshness_status" intentionally missing
            "unit": "", "currency": "", "accounting_basis": "",
            "requested_permission": "full", "has_conflict": False, "notes": "",
        }]
        ds = SyntheticDataSource(records=records, default_tier="S")
        req = FetchRequest(symbol="CO", field="price", request_id="r2")
        result = ds.fetch(req)
        assert isinstance(result, FetchFailure)
        assert result.reason == FetchFailureReason.PARSE_ERROR
        assert "freshness_status" in result.detail

    def test_no_default_for_freshness_in_build_data_card(self):
        """build_data_card requires freshness_status explicitly — no default."""
        req = FetchRequest(symbol="CO", field="price", request_id="r3")
        with pytest.raises(TypeError):
            build_data_card(  # type: ignore[call-arg]
                request=req, value=42, source_name="test", source_tier="S",
                timestamp="2026-07-15T00:00:00Z", period="2026-Q2",
                data_provenance=PROVENANCE_SYNTHETIC,
                # freshness_status intentionally missing
            )


# ══════════════════════════════════════════════════════════════════════════
# G. Permission integration with source_policy
# ══════════════════════════════════════════════════════════════════════════

class TestPermissionCapping:
    def test_b_tier_full_is_capped_to_reference_only(self):
        ds = _make_ds(default_tier="B")
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r1")
        card = ds.fetch(req)
        assert card["source_tier"] == "B"
        assert card["can_enter_conclusion"] == "reference_only"

    def test_d_tier_is_blocked(self):
        ds = _make_ds(default_tier="D")
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r2")
        card = ds.fetch(req)
        assert card["source_tier"] == "D"
        assert card["can_enter_conclusion"] == "blocked"

    def test_generated_card_passes_registry_validation(self):
        ds = _make_ds(default_tier="S")
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r3")
        card = ds.fetch(req)
        result = validate_data_card(card)
        assert result.status == "PASS_FORMAL"

    def test_generated_card_uses_existing_source_policy(self):
        """build_data_card must delegate permission capping to source_policy."""
        from tools.source_policy import effective_permission

        req = FetchRequest(symbol="SAMPLE_CO", field="eps", request_id="r4")
        card = build_data_card(
            request=req,
            value=5.25,
            source_name="test",
            source_tier="B",
            timestamp="2026-07-15T00:00:00Z",
            period="2026-Q2",
            freshness_status="current",
            requested_permission="full",
            data_provenance=PROVENANCE_SYNTHETIC,
        )
        expected = effective_permission("B", "full")
        assert card["can_enter_conclusion"] == expected
        assert card["can_enter_conclusion"] == "reference_only"


# ══════════════════════════════════════════════════════════════════════════
# H. freshness / conflict
# ══════════════════════════════════════════════════════════════════════════

class TestFreshnessAndConflict:
    def test_stale_full_card_cannot_enter_formal_conclusion(self):
        ds = _make_ds(default_tier="S")
        req = FetchRequest(symbol="SAMPLE_CO", field="market_cap", request_id="r1")
        card = ds.fetch(req)
        assert card["freshness_status"] == "stale"
        result = validate_data_card(card)
        assert not result.is_valid
        assert any("stale" in v.lower() for v in result.violations)

    def test_unknown_freshness_cannot_enter_formal_conclusion(self):
        ds = _make_ds(default_tier="S")
        req = FetchRequest(symbol="SAMPLE_CO", field="shares_outstanding", request_id="r2")
        card = ds.fetch(req)
        assert card["freshness_status"] == "unknown"
        result = validate_data_card(card)
        assert not result.is_valid
        assert any("unknown freshness" in v.lower() for v in result.violations)

    def test_conflicting_card_cannot_enter_formal_conclusion(self):
        ds = _make_ds(default_tier="S")
        req = FetchRequest(symbol="SAMPLE_BANK", field="current_price", request_id="r3")
        card = ds.fetch(req)
        assert card["has_conflict"] is True
        result = validate_data_card(card)
        assert not result.is_valid
        assert any("conflict" in v.lower() for v in result.violations)

    def test_current_no_conflict_can_enter_conclusion(self):
        ds = _make_ds(default_tier="S")
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r4")
        card = ds.fetch(req)
        assert card["freshness_status"] == "current"
        assert card["has_conflict"] is False
        result = validate_data_card(card)
        assert result.is_valid


# ══════════════════════════════════════════════════════════════════════════
# I. Failure paths
# ══════════════════════════════════════════════════════════════════════════

class TestFailurePaths:
    def test_missing_field_returns_fetch_failure(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="nonexistent_field", request_id="r1")
        result = ds.fetch(req)
        assert isinstance(result, FetchFailure)
        assert result.status == "FETCH_FAILED"
        assert result.reason == FetchFailureReason.FIELD_MISSING

    def test_missing_symbol_returns_fetch_failure(self):
        ds = _make_ds()
        req = FetchRequest(symbol="UNKNOWN_CO", field="current_price", request_id="r2")
        result = ds.fetch(req)
        assert isinstance(result, FetchFailure)
        assert result.reason == FetchFailureReason.FIELD_MISSING

    def test_failure_preserves_request_id(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="nonexistent", request_id="trace-abc")
        result = ds.fetch(req)
        assert result.request_id == "trace-abc"

    def test_synthetic_failure_is_not_retryable(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="nonexistent", request_id="r4")
        result = ds.fetch(req)
        assert result.retry_allowed is False

    def test_parse_error_on_bad_fixture_path(self):
        with pytest.raises(ValueError, match="does not exist"):
            SyntheticDataSource(fixture_path="tests/fixtures/nonexistent.json")

    def test_constructor_requires_records_or_fixture(self):
        with pytest.raises(ValueError, match="requires either records= or fixture_path="):
            SyntheticDataSource()


# ══════════════════════════════════════════════════════════════════════════
# J. Data Card completeness
# ══════════════════════════════════════════════════════════════════════════

class TestDataCardCompleteness:
    def test_card_has_all_required_fields(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r1")
        card = ds.fetch(req)
        required = {
            "field_name", "value", "source", "source_tier", "timestamp",
            "period", "unit", "currency", "accounting_basis",
            "can_enter_conclusion", "notes", "freshness_status", "has_conflict",
        }
        for field in required:
            assert field in card, f"Missing required field: {field}"

    def test_card_has_request_id(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="my-req")
        card = ds.fetch(req)
        assert card["request_id"] == "my-req"

    def test_card_has_data_provenance(self):
        ds = _make_ds()
        req = FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="r2")
        card = ds.fetch(req)
        assert card["data_provenance"] == PROVENANCE_SYNTHETIC

    def test_build_data_card_includes_request_id_and_provenance(self):
        req = FetchRequest(symbol="SAMPLE_CO", field="test_field", request_id="build-1")
        card = build_data_card(
            request=req,
            value=42,
            source_name="test",
            source_tier="S",
            timestamp="2026-01-01T00:00:00Z",
            period="2026-Q1",
            freshness_status="current",
            data_provenance=PROVENANCE_SYNTHETIC,
        )
        assert card["request_id"] == "build-1"
        assert card["data_provenance"] == PROVENANCE_SYNTHETIC
