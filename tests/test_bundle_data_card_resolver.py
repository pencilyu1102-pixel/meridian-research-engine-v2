"""Phase 6.5B shared Bundle Data Card resolver contract tests."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from tools.bundle_data_card_resolver import (
    ensure_all_validated,
    generate_datasource_cards,
    resolve_bundle_data_cards,
    resolve_safe_artifact_path,
)
from tools.data_source import FetchFailure, FetchFailureReason
from tools.data_source_runner import DataSourceBatchResult, DataSourceRunResult, DataSourceRunStatus

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT / "examples" / "full_chain_sample"
BUNDLE_PATH = SAMPLE_DIR / "research_bundle.json"
EXPECTED_LEGACY_HASH = "4b427323a2bb5ec4445a86b761e0ca5b27bedf9fee6440252523c0125357ee8a"


def _bundle() -> dict:
    bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    bundle["_bundle_dir"] = str(SAMPLE_DIR)
    return bundle


def _intake_bundle(tmp_path: Path) -> dict:
    for name in (
        "research_bundle.json",
        "synthetic_source_records.json",
        "synthetic_fetch_manifest.json",
        "synthetic_data_cards.json",
        "synthetic_industry_fields.json",
    ):
        shutil.copy(SAMPLE_DIR / name, tmp_path / name)
    bundle = json.loads((tmp_path / "research_bundle.json").read_text(encoding="utf-8"))
    bundle["data_cards"] = {
        "mode": "datasource_intake",
        "records_path": "synthetic_source_records.json",
        "manifest_path": "synthetic_fetch_manifest.json",
        "expected_count": 11,
    }
    bundle["_bundle_dir"] = str(tmp_path)
    return bundle


def test_implicit_legacy_resolves_cards():
    resolved = resolve_bundle_data_cards(_bundle())
    assert resolved.mode == "legacy_static"
    assert resolved.generated_count == 11
    assert len(resolved.cards) == 11
    assert list(resolved.batch_statuses) == []
    assert resolved.artifact_hashes["data_cards"]


def test_explicit_legacy_resolves_cards():
    bundle = _bundle()
    bundle["data_cards"] = {"mode": "legacy_static", "path": "synthetic_data_cards.json"}
    resolved = resolve_bundle_data_cards(bundle)
    assert resolved.mode == "legacy_static"
    assert list(resolved.cards) == json.loads((SAMPLE_DIR / "synthetic_data_cards.json").read_text())


def test_legacy_hash_is_unchanged():
    from scripts.validate_agent_report import compute_bundle_hash, load_bundle
    assert compute_bundle_hash(load_bundle(BUNDLE_PATH)) == EXPECTED_LEGACY_HASH


def test_absolute_path_is_rejected():
    with pytest.raises(ValueError, match="absolute"):
        resolve_safe_artifact_path("/etc/passwd", SAMPLE_DIR)


def test_traversal_path_is_rejected():
    with pytest.raises(ValueError, match="escapes"):
        resolve_safe_artifact_path("../../../etc/passwd", SAMPLE_DIR)


def test_missing_path_is_rejected():
    with pytest.raises(FileNotFoundError):
        resolve_safe_artifact_path("missing.json", SAMPLE_DIR)


def test_path_and_intake_fields_conflict():
    bundle = _bundle()
    bundle["data_cards"] = {
        "mode": "datasource_intake",
        "path": "synthetic_data_cards.json",
        "records_path": "synthetic_source_records.json",
        "manifest_path": "synthetic_fetch_manifest.json",
        "expected_count": 11,
    }
    with pytest.raises(ValueError, match="path"):
        resolve_bundle_data_cards(bundle)


def test_unknown_mode_is_rejected():
    bundle = _bundle()
    bundle["data_cards"] = {"mode": "future_mode", "path": "synthetic_data_cards.json"}
    with pytest.raises(ValueError, match="unknown"):
        resolve_bundle_data_cards(bundle)


def test_intake_generates_eleven_cards_in_manifest_order(tmp_path: Path):
    resolved = resolve_bundle_data_cards(_intake_bundle(tmp_path))
    manifest = json.loads((tmp_path / "synthetic_fetch_manifest.json").read_text())
    assert resolved.mode == "datasource_intake"
    assert resolved.generated_count == 11
    assert [card["request_id"] for card in resolved.cards] == [r["request_id"] for r in manifest["requests"]]
    assert [status["status"] for status in resolved.batch_statuses] == ["CARD_VALIDATED"] * 3


def test_intake_preserves_b_tier_reference_only(tmp_path: Path):
    resolved = resolve_bundle_data_cards(_intake_bundle(tmp_path))
    analyst_cards = [c for c in resolved.cards if c["source"] == "SYNTHETIC_FIXTURE_ANALYST"]
    assert analyst_cards
    assert all(c["can_enter_conclusion"] == "reference_only" for c in analyst_cards)


def test_expected_count_mismatch_fails(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    bundle["data_cards"]["expected_count"] = 10
    with pytest.raises(ValueError, match="expected_count"):
        resolve_bundle_data_cards(bundle)


def test_provenance_mismatch_fails(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    bundle["meta"]["data_provenance"] = "REAL"
    with pytest.raises(ValueError, match="provenance"):
        resolve_bundle_data_cards(bundle)


def test_manifest_and_raw_symbol_cannot_override_bundle_symbol(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    records_path = tmp_path / "synthetic_source_records.json"
    manifest_path = tmp_path / "synthetic_fetch_manifest.json"
    records = json.loads(records_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    manifest["symbol"] = "OTHER_SYMBOL"
    for record in records:
        record["symbol"] = "OTHER_SYMBOL"
    records_path.write_text(json.dumps(records), encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="Bundle and manifest symbol mismatch"):
        resolve_bundle_data_cards(bundle)


def test_mapping_fetch_failure_details_are_not_dropped():
    result = DataSourceRunResult(
        status=DataSourceRunStatus.FETCH_FAILED,
        request_id="req-1",
        symbol="SAMPLE",
        field="revenue",
        failure=FetchFailure(
            reason=FetchFailureReason.FIELD_MISSING,
            detail="fixture omitted revenue",
            request_id="req-1",
            retry_allowed=True,
        ),
    )

    with pytest.raises(RuntimeError) as exc_info:
        ensure_all_validated([result.to_dict()])
    message = str(exc_info.value)
    assert "failure.reason=FIELD_MISSING" in message
    assert "failure.detail=fixture omitted revenue" in message
    assert "failure.retry_allowed=True" in message


def test_generate_datasource_cards_annotation_uses_batch_result():
    assert generate_datasource_cards.__annotations__["return"] == (
        "tuple[list[dict[str, Any]], list[DataSourceBatchResult]]"
    )


def test_missing_records_path_fails(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    del bundle["data_cards"]["records_path"]
    with pytest.raises(ValueError, match="records_path"):
        resolve_bundle_data_cards(bundle)


def test_missing_manifest_file_fails(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    (tmp_path / "synthetic_fetch_manifest.json").unlink()
    with pytest.raises(FileNotFoundError):
        resolve_bundle_data_cards(bundle)


def test_forbidden_raw_field_fails(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    records = json.loads((tmp_path / "synthetic_source_records.json").read_text())
    records[0]["source_tier"] = "S"
    (tmp_path / "synthetic_source_records.json").write_text(json.dumps(records))
    with pytest.raises(ValueError, match="forbidden"):
        resolve_bundle_data_cards(bundle)


def test_non_validated_result_fails_without_static_fallback(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    records = json.loads((tmp_path / "synthetic_source_records.json").read_text())
    records[0]["field"] = "missing_field"
    (tmp_path / "synthetic_source_records.json").write_text(json.dumps(records))
    with pytest.raises(RuntimeError, match="CARD_VALIDATED"):
        resolve_bundle_data_cards(bundle)


def test_generated_hash_is_deterministic(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    first = resolve_bundle_data_cards(bundle)
    second = resolve_bundle_data_cards(bundle)
    assert first.generated_cards_sha256 == second.generated_cards_sha256
    assert first.artifact_hashes == second.artifact_hashes


def test_raw_hash_detects_change(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    first = resolve_bundle_data_cards(bundle).artifact_hashes["data_card_records"]
    records = json.loads((tmp_path / "synthetic_source_records.json").read_text())
    records[0]["value"] = "changed"
    (tmp_path / "synthetic_source_records.json").write_text(json.dumps(records))
    second = resolve_bundle_data_cards(bundle).artifact_hashes["data_card_records"]
    assert first != second


def test_manifest_raw_hash_changes_on_reformat_but_generated_hash_does_not(tmp_path: Path):
    bundle = _intake_bundle(tmp_path)
    from scripts.validate_agent_report import compute_artifact_hashes, compute_bundle_hash

    first = resolve_bundle_data_cards(bundle)
    first_bundle_hash = compute_bundle_hash(bundle)
    payload = json.loads((tmp_path / "synthetic_fetch_manifest.json").read_text())
    (tmp_path / "synthetic_fetch_manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )
    second = resolve_bundle_data_cards(bundle)
    second_bundle_hash = compute_bundle_hash(bundle)

    assert first.artifact_hashes["data_card_manifest"] != second.artifact_hashes["data_card_manifest"]
    assert first.artifact_hashes["generated_data_cards"] == second.artifact_hashes["generated_data_cards"]
    assert first_bundle_hash != second_bundle_hash
    assert set(compute_artifact_hashes(bundle)) == {
        "data_card_records",
        "data_card_manifest",
        "generated_data_cards",
        "industry_hard_fields",
    }


def test_current_hardlock_resolves_through_legacy(tmp_path: Path):
    from scripts.validate_agent_report import build_hardlock_from_bundle
    result = build_hardlock_from_bundle(_bundle())
    assert result["status"] == "PASS_TEST_ONLY"


def test_intake_artifact_keys_are_explicit(tmp_path: Path):
    resolved = resolve_bundle_data_cards(_intake_bundle(tmp_path))
    assert set(resolved.artifact_hashes) == {
        "data_card_records",
        "data_card_manifest",
        "generated_data_cards",
    }
    assert resolved.generated_cards_sha256 == resolved.artifact_hashes["generated_data_cards"]
