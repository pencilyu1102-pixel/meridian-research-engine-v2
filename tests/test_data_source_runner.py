"""Phase 6.3 DataSource Runner contract tests.

Validates single-request and batch execution through the Runner,
covering all four status outcomes, contract binding checks,
and batch aggregation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.data_source import FetchFailure, FetchFailureReason, FetchRequest
from tools.data_source_runner import (
    DataSourceBatchResult,
    DataSourceRunResult,
    DataSourceRunStatus,
    run_batch,
    run_fetch,
)
from tools.source_policy import PROVENANCE_SYNTHETIC
from tools.synthetic_data_source import SyntheticDataSource

FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "data_sources" / "synthetic_source_records.json"
)


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_ds(default_tier: str = "S") -> SyntheticDataSource:
    return SyntheticDataSource(fixture_path=FIXTURE_PATH, default_tier=default_tier)


def _make_request(symbol: str = "SAMPLE_CO", field: str = "current_price", request_id: str = "r1") -> FetchRequest:
    return FetchRequest(symbol=symbol, field=field, request_id=request_id)


class FakeFailSource:
    """A minimal DataSource-like that always returns a FetchFailure."""

    source_name = "FakeFailSource"
    default_tier = "S"
    data_provenance = PROVENANCE_SYNTHETIC

    def fetch(self, request: FetchRequest) -> FetchFailure:
        return FetchFailure(
            status="FETCH_FAILED",
            reason=FetchFailureReason.NETWORK_ERROR,
            detail="simulated failure",
            request_id=request.request_id,
            timestamp="2026-07-16T00:00:00Z",
            retry_allowed=True,
        )


class FakeMismatchSource:
    """Returns a FetchFailure with a mismatched request_id to test contract checks."""

    source_name = "FakeMismatchSource"
    default_tier = "S"
    data_provenance = PROVENANCE_SYNTHETIC

    def fetch(self, request: FetchRequest) -> FetchFailure:
        return FetchFailure(
            status="FETCH_FAILED",
            reason=FetchFailureReason.NETWORK_ERROR,
            detail="mismatched",
            request_id="WRONG_ID",
            timestamp="2026-07-16T00:00:00Z",
            retry_allowed=False,
        )


class FakeCardSource:
    """Returns a pre-configured card dict."""

    source_name = "FakeCardSource"
    default_tier = "S"
    data_provenance = PROVENANCE_SYNTHETIC

    def __init__(self, card: dict[str, Any], calls: list[int] | None = None) -> None:
        self._card = card
        self._calls: list[int] = calls if calls is not None else []

    def fetch(self, request: FetchRequest) -> dict[str, Any]:
        self._calls.append(1)
        return dict(self._card)


class FakeBadTypeSource:
    """Returns a non-dict, non-FetchFailure value."""

    source_name = "FakeBadTypeSource"
    default_tier = "S"
    data_provenance = PROVENANCE_SYNTHETIC

    def fetch(self, request: FetchRequest) -> Any:
        return "not_a_valid_response"


def _valid_card(**overrides: Any) -> dict[str, Any]:
    card = {
        "field_name": "current_price",
        "value": 100.0,
        "source": "test",
        "source_tier": "S",
        "timestamp": "2026-07-15T00:00:00Z",
        "period": "2026-Q2",
        "unit": "USD",
        "currency": "USD",
        "accounting_basis": "market_price",
        "can_enter_conclusion": "full",
        "notes": "",
        "freshness_status": "current",
        "has_conflict": False,
        "request_id": "r1",
        "data_provenance": PROVENANCE_SYNTHETIC,
    }
    card.update(overrides)
    return card


# ══════════════════════════════════════════════════════════════════════════
# A. Single request — success paths
# ══════════════════════════════════════════════════════════════════════════


class TestRunFetchSuccess:
    def test_s_tier_card_validated(self):
        """S-tier current card → CARD_VALIDATED with full permission."""
        ds = _make_ds(default_tier="S")
        req = _make_request()
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CARD_VALIDATED
        assert result.can_enter_conclusion is True
        assert result.effective_permission == "full"
        assert result.card is not None
        assert result.card["field_name"] == "current_price"

    def test_b_tier_reference_only_card_validated(self):
        """B-tier card → CARD_VALIDATED but effective_permission=reference_only."""
        # Use a non-critical field so B-tier + reference_only passes admission
        card = _valid_card(
            field_name="gross_margin",
            source_tier="B",
            can_enter_conclusion="reference_only",
        )
        ds = FakeCardSource(card)
        req = _make_request(field="gross_margin")
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CARD_VALIDATED
        assert result.can_enter_conclusion is False
        assert result.effective_permission == "reference_only"

    def test_to_dict_is_json_serializable(self):
        """DataSourceRunResult.to_dict() can be serialized with json.dumps."""
        ds = _make_ds(default_tier="S")
        req = _make_request()
        result = run_fetch(ds, req)
        d = result.to_dict()
        s = json.dumps(d)
        assert isinstance(s, str)
        assert '"CARD_VALIDATED"' in s


# ══════════════════════════════════════════════════════════════════════════
# B. Single request — FetchFailure paths
# ══════════════════════════════════════════════════════════════════════════


class TestRunFetchFailure:
    def test_fetch_failure_with_matching_request_id(self):
        """Matching request_id → FETCH_FAILED."""
        ds = FakeFailSource()
        req = _make_request(request_id="r1")
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.FETCH_FAILED
        assert result.failure is not None
        assert result.failure.request_id == "r1"
        assert len(result.violations) == 0

    def test_fetch_failure_with_mismatched_request_id(self):
        """Mismatched FetchFailure request_id → CONTRACT_FAILED."""
        ds = FakeMismatchSource()
        req = _make_request(request_id="r1")
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CONTRACT_FAILED
        assert result.failure is not None
        assert result.failure.request_id == "WRONG_ID"
        assert any("request_id mismatch" in v for v in result.violations)
        # The original FetchFailure must not be modified
        assert result.failure.request_id == "WRONG_ID"


# ══════════════════════════════════════════════════════════════════════════
# C. Single request — contract failure (binding checks)
# ══════════════════════════════════════════════════════════════════════════


class TestRunFetchContractFailure:
    def test_card_request_id_mismatch(self):
        card = _valid_card(request_id="BAD")
        ds = FakeCardSource(card)
        req = _make_request(request_id="r1")
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CONTRACT_FAILED
        assert any("request_id mismatch" in v for v in result.violations)

    def test_card_field_name_mismatch(self):
        card = _valid_card(field_name="wrong_field")
        ds = FakeCardSource(card)
        req = _make_request(field="current_price")
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CONTRACT_FAILED
        assert any("field_name mismatch" in v for v in result.violations)

    def test_card_provenance_mismatch(self):
        card = _valid_card(data_provenance="REAL_VENDOR")
        ds = FakeCardSource(card)
        req = _make_request()
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CONTRACT_FAILED
        assert any("provenance mismatch" in v for v in result.violations)

    def test_multiple_binding_failures_returned_at_once(self):
        """All binding failures must be in violations, not just the first."""
        card = _valid_card(request_id="BAD", field_name="WRONG", data_provenance="REAL")
        ds = FakeCardSource(card)
        req = _make_request(request_id="r1", field="current_price")
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CONTRACT_FAILED
        assert len(result.violations) == 3
        assert sum("request_id" in v for v in result.violations) == 1
        assert sum("field_name" in v for v in result.violations) == 1
        assert sum("provenance" in v for v in result.violations) == 1

    def test_illegal_response_type(self):
        ds = FakeBadTypeSource()
        req = _make_request()
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.CONTRACT_FAILED
        assert any("Unsupported response type" in v for v in result.violations)


# ══════════════════════════════════════════════════════════════════════════
# D. Single request — validation failure
# ══════════════════════════════════════════════════════════════════════════


class TestRunFetchValidationFailure:
    def test_missing_required_field(self):
        card = _valid_card()
        del card["freshness_status"]
        ds = FakeCardSource(card)
        req = _make_request()
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.VALIDATION_FAILED
        assert result.validation_status is not None
        assert "MISSING" in result.validation_status

    def test_stale_card_fails_validation(self):
        card = _valid_card(freshness_status="stale")
        ds = FakeCardSource(card)
        req = _make_request()
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.VALIDATION_FAILED

    def test_conflict_card_fails_validation(self):
        card = _valid_card(has_conflict=True)
        ds = FakeCardSource(card)
        req = _make_request()
        result = run_fetch(ds, req)
        assert result.status == DataSourceRunStatus.VALIDATION_FAILED

    def test_validation_fail_has_no_permission_info(self):
        card = _valid_card()
        del card["freshness_status"]
        ds = FakeCardSource(card)
        req = _make_request()
        result = run_fetch(ds, req)
        assert result.effective_permission is None
        assert result.can_enter_conclusion is False
        assert result.can_enter_primary_valuation is False


# ══════════════════════════════════════════════════════════════════════════
# E. Single request — data integrity
# ══════════════════════════════════════════════════════════════════════════


class TestRunFetchIntegrity:
    def test_calls_fetch_exactly_once(self):
        calls: list[int] = []
        card = _valid_card()
        ds = FakeCardSource(card, calls=calls)
        req = _make_request()
        run_fetch(ds, req)
        assert len(calls) == 1
        # Second call should not increase
        run_fetch(ds, req)
        assert len(calls) == 2

    def test_card_not_modified_by_runner(self):
        card = _valid_card()
        ds = FakeCardSource(card)
        req = _make_request()
        result = run_fetch(ds, req)
        # The original card dict in the fake source should be unchanged
        assert card["request_id"] == "r1"
        assert card["data_provenance"] == PROVENANCE_SYNTHETIC
        assert card["field_name"] == "current_price"


# ══════════════════════════════════════════════════════════════════════════
# F. Batch
# ══════════════════════════════════════════════════════════════════════════


class TestRunBatch:
    def test_preserves_input_order(self):
        ds = _make_ds(default_tier="S")
        reqs = [
            FetchRequest(symbol="SAMPLE_CO", field="market_cap", request_id="b1"),
            FetchRequest(symbol="SAMPLE_CO", field="current_price", request_id="b2"),
        ]
        batch = run_batch(ds, reqs)
        assert [r.field for r in batch.results] == ["market_cap", "current_price"]

    def test_empty_batch_returns_zero_total(self):
        ds = _make_ds()
        batch = run_batch(ds, [])
        assert batch.total == 0
        assert batch.validated_count == 0

    def test_duplicate_request_id_raises_value_error(self):
        ds = _make_ds()
        reqs = [
            _make_request(request_id="dup"),
            _make_request(request_id="dup"),
        ]
        with pytest.raises(ValueError, match="Duplicate request_id"):
            run_batch(ds, reqs)

    def test_duplicate_fail_fast_calls_fetch_zero_times(self):
        """Duplicate check must fail before any fetch() calls."""
        calls: list[int] = []
        card = _valid_card()
        ds = FakeCardSource(card, calls=calls)
        reqs = [
            FetchRequest(symbol="X", field="price", request_id="dup"),
            FetchRequest(symbol="X", field="price", request_id="dup"),
        ]
        with pytest.raises(ValueError):
            run_batch(ds, reqs)
        assert len(calls) == 0

    def test_mixed_status_correctly_summarized(self):
        """Batch with one result of each of the four statuses."""
        # CARD_VALIDATED
        card_ok = _valid_card(request_id="r_ok")
        ds_ok = FakeCardSource(card_ok)
        r_ok = run_fetch(ds_ok, _make_request(request_id="r_ok"))

        # FETCH_FAILED
        ds_fail = FakeFailSource()
        r_fail = run_fetch(ds_fail, _make_request(request_id="r_fail"))

        # CONTRACT_FAILED (request_id mismatch)
        card_mismatch = _valid_card(request_id="BAD")
        ds_contract = FakeCardSource(card_mismatch)
        r_contract = run_fetch(ds_contract, _make_request(request_id="r_contract"))

        # VALIDATION_FAILED (missing required field)
        card_invalid = _valid_card(request_id="r_invalid")
        del card_invalid["freshness_status"]
        ds_invalid = FakeCardSource(card_invalid)
        r_invalid = run_fetch(ds_invalid, _make_request(request_id="r_invalid"))

        batch = DataSourceBatchResult.from_results([r_ok, r_fail, r_contract, r_invalid])
        assert batch.total == 4
        assert batch.validated_count == 1
        assert batch.fetch_failed_count == 1
        assert batch.contract_failed_count == 1
        assert batch.validation_failed_count == 1

    def test_counts_cannot_be_faked(self):
        """Caller cannot inject count fields — they are always derived from results."""
        with pytest.raises(TypeError):
            DataSourceBatchResult(results=(), total=100)  # type: ignore[call-arg]

    def test_empty_batch_from_results(self):
        """from_results with empty list yields all-zero counts."""
        batch = DataSourceBatchResult.from_results([])
        assert batch.total == 0
        assert batch.validated_count == 0
        assert batch.fetch_failed_count == 0
        assert batch.contract_failed_count == 0
        assert batch.validation_failed_count == 0

    def test_batch_to_dict_serializable(self):
        ds = _make_ds(default_tier="S")
        reqs = [
            _make_request(request_id="s1"),
            _make_request(request_id="s2"),
        ]
        batch = run_batch(ds, reqs)
        d = batch.to_dict()
        s = json.dumps(d)
        assert isinstance(s, str)
        assert '"validated_count": 2' in s
