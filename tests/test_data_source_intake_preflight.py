"""Phase 6.4B Runner-backed offline intake parity preflight tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.data_source import FetchRequest
from tools.data_source_runner import DataSourceRunStatus, run_batch
from tools.synthetic_data_source import SyntheticDataSource

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT / "examples" / "full_chain_sample"
RAW_PATH = SAMPLE_DIR / "synthetic_source_records.json"
MANIFEST_PATH = SAMPLE_DIR / "synthetic_fetch_manifest.json"
CANONICAL_PATH = SAMPLE_DIR / "synthetic_data_cards.json"
SCRIPT = ROOT / "scripts" / "preflight_data_source_intake.py"
FORBIDDEN_RAW_FIELDS = {
    "source",
    "source_name",
    "source_tier",
    "request_id",
    "data_provenance",
    "can_enter_conclusion",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest() -> dict:
    return _load(MANIFEST_PATH)


def test_default_source_name_remains_backward_compatible():
    source = SyntheticDataSource(records=[
        {
            "symbol": "SAMPLE_CO",
            "field": "current_price",
            "value": 1,
            "period": "p",
            "timestamp": "t",
            "freshness_status": "current",
        }
    ])
    assert source.source_name == "SyntheticDataSource"


def test_custom_source_name_is_written_to_card():
    source = SyntheticDataSource(
        records=[
            {
                "symbol": "SAMPLE_CO",
                "field": "current_price",
                "value": 1,
                "period": "p",
                "timestamp": "t",
                "freshness_status": "current",
            }
        ],
        source_name="SYNTHETIC_FIXTURE_EXCHANGE",
    )
    card = source.fetch(FetchRequest(symbol="SAMPLE_CO", field="current_price", period="p", request_id="r1"))
    assert card["source"] == "SYNTHETIC_FIXTURE_EXCHANGE"


def test_blank_source_name_is_rejected():
    with pytest.raises(ValueError, match="source_name"):
        SyntheticDataSource(records=[], source_name=" ")


def test_full_chain_raw_records_have_expected_shape_and_groups():
    records = _load(RAW_PATH)
    assert len(records) == 11
    assert {r["source_group"] for r in records} == {"exchange", "company", "analyst"}
    assert {group: sum(r["source_group"] == group for r in records) for group in ("exchange", "company", "analyst")} == {
        "exchange": 2,
        "company": 7,
        "analyst": 2,
    }
    assert all(FORBIDDEN_RAW_FIELDS.isdisjoint(record) for record in records)


def test_manifest_has_eleven_unique_requests_and_valid_source_groups():
    manifest = _manifest()
    requests = manifest["requests"]
    assert len(requests) == 11
    assert len({r["request_id"] for r in requests}) == 11
    assert {r["source_group"] for r in requests} == set(manifest["sources"])
    assert manifest["data_provenance"] == "SYNTHETIC_FIXTURE"
    assert all("symbol" not in r and "source_name" not in r and "source_tier" not in r for r in requests)


def test_manifest_order_matches_canonical_order():
    manifest = _manifest()
    canonical = _load(CANONICAL_PATH)
    assert [r["field"] for r in manifest["requests"]] == [c["field_name"] for c in canonical]
    assert [r["request_id"] for r in manifest["requests"]] == [c["request_id"] for c in canonical]


def test_three_source_definitions_have_expected_names_and_tiers():
    sources = _manifest()["sources"]
    assert sources == {
        "exchange": {"source_name": "SYNTHETIC_FIXTURE_EXCHANGE", "source_tier": "A"},
        "company": {"source_name": "SYNTHETIC_FIXTURE_COMPANY", "source_tier": "A"},
        "analyst": {"source_name": "SYNTHETIC_FIXTURE_ANALYST", "source_tier": "B"},
    }


def test_runner_generates_eleven_cards_in_manifest_order():
    from scripts.preflight_data_source_intake import generate_cards, load_inputs

    records, manifest, canonical = load_inputs(RAW_PATH, MANIFEST_PATH, CANONICAL_PATH)
    generated, batches = generate_cards(records, manifest)
    assert len(generated) == len(canonical) == 11
    assert [card["request_id"] for card in generated] == [card["request_id"] for card in canonical]
    assert all(result.status == DataSourceRunStatus.CARD_VALIDATED for batch in batches for result in batch.results)


def test_analyst_cards_are_reference_only():
    from scripts.preflight_data_source_intake import generate_cards, load_inputs

    records, manifest, _ = load_inputs(RAW_PATH, MANIFEST_PATH, CANONICAL_PATH)
    generated, _ = generate_cards(records, manifest)
    analyst = [card for card in generated if card["source"] == "SYNTHETIC_FIXTURE_ANALYST"]
    assert len(analyst) == 2
    assert all(card["can_enter_conclusion"] == "reference_only" for card in analyst)


def test_run_batch_is_called_once_per_source_group():
    from scripts.preflight_data_source_intake import generate_cards, load_inputs

    records, manifest, _ = load_inputs(RAW_PATH, MANIFEST_PATH, CANONICAL_PATH)
    generated, batches = generate_cards(records, manifest)
    assert len(batches) == 3
    assert [batch.total for batch in batches] == [2, 7, 2]
    assert len(generated) == 11


def test_parity_passes_exactly():
    from scripts.preflight_data_source_intake import compare_cards, generate_cards, load_inputs

    records, manifest, canonical = load_inputs(RAW_PATH, MANIFEST_PATH, CANONICAL_PATH)
    generated, _ = generate_cards(records, manifest)
    report = compare_cards(generated, canonical, manifest)
    assert report["parity"] is True
    assert report["field_mismatches"] == []
    assert report["missing_request_ids"] == []
    assert report["extra_request_ids"] == []


def test_parity_reports_value_and_type_difference():
    from scripts.preflight_data_source_intake import compare_cards

    canonical = [{"request_id": "r1", "value": "1"}]
    generated = [{"request_id": "r1", "value": 1}]
    report = compare_cards(generated, canonical, {"requests": [{"request_id": "r1"}]})
    assert report["parity"] is False
    assert {m["field"] for m in report["field_mismatches"]} == {"value"}
    assert report["field_mismatches"][0]["expected_type"] == "str"
    assert report["field_mismatches"][0]["actual_type"] == "int"


def test_parity_reports_missing_and_extra_cards():
    from scripts.preflight_data_source_intake import compare_cards

    canonical = [{"request_id": "r1"}, {"request_id": "r2"}]
    generated = [{"request_id": "r1"}, {"request_id": "r3"}]
    report = compare_cards(generated, canonical, {"requests": [{"request_id": "r1"}, {"request_id": "r2"}]})
    assert report["parity"] is False
    assert report["missing_request_ids"] == ["r2"]
    assert report["extra_request_ids"] == ["r3"]


def test_non_validated_runner_result_fails_preflight():
    from scripts.preflight_data_source_intake import ensure_all_validated

    with pytest.raises(RuntimeError, match="FETCH_FAILED"):
        ensure_all_validated([
            {
                "source_group": "exchange",
                "request_id": "r1",
                "field": "current_price",
                "status": "FETCH_FAILED",
                "violations": ["missing"],
            }
        ])


def test_cli_default_run_passes_without_writing_files(tmp_path):
    before = hashlib.sha256(CANONICAL_PATH.read_bytes()).hexdigest()
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True)
    after = hashlib.sha256(CANONICAL_PATH.read_bytes()).hexdigest()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PREFLIGHT_PASS" in result.stdout
    assert '"generated_cards": 11' in result.stdout
    assert before == after


def test_cli_output_contains_locked_boundary():
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, capture_output=True, text=True)
    assert '"production_research_eligible": false' in result.stdout
    assert '"account_action": "LOCKED"' in result.stdout
    assert '"demo_input_changed": false' in result.stdout
    assert '"bundle_hash_changed": false' in result.stdout


def test_generated_cards_have_exact_canonical_key_sets():
    from scripts.preflight_data_source_intake import generate_cards, load_inputs

    records, manifest, canonical = load_inputs(RAW_PATH, MANIFEST_PATH, CANONICAL_PATH)
    generated, _ = generate_cards(records, manifest)
    assert [set(card) for card in generated] == [set(card) for card in canonical]


def test_manifest_requests_use_one_symbol_and_unique_fields():
    manifest = _manifest()
    assert all(request["request_id"].startswith("SYNTHETIC::FULL_CHAIN::") for request in manifest["requests"])
    assert len({request["field"] for request in manifest["requests"]}) == 11
    assert manifest["symbol"] == "SAMPLE_MANAGED_CARE"
