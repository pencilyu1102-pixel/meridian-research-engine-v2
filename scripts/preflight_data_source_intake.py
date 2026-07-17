#!/usr/bin/env python3
"""Runner-backed, read-only parity preflight for the Full-chain synthetic intake."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.data_source import FetchRequest
from tools.data_source_runner import DataSourceRunStatus, run_batch
from tools.synthetic_data_source import SyntheticDataSource

DEFAULT_RAW = ROOT / "examples/full_chain_sample/synthetic_source_records.json"
DEFAULT_MANIFEST = ROOT / "examples/full_chain_sample/synthetic_fetch_manifest.json"
DEFAULT_CANONICAL = ROOT / "examples/full_chain_sample/synthetic_data_cards.json"
FORBIDDEN_RAW_FIELDS = {
    "source",
    "source_name",
    "source_tier",
    "request_id",
    "data_provenance",
    "can_enter_conclusion",
}
FORBIDDEN_REQUEST_FIELDS = {
    "symbol",
    "source_name",
    "source_tier",
    "data_provenance",
}


def load_inputs(raw_path: Path, manifest_path: Path, canonical_path: Path):
    records = json.loads(raw_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not isinstance(manifest, dict) or not isinstance(canonical, list):
        raise ValueError("raw records and canonical cards must be arrays; manifest must be an object")
    return records, manifest, canonical


def _validate_manifest(records: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]) -> None:
    requests = manifest["requests"]
    if len(records) != len(requests):
        raise ValueError(f"raw/request count mismatch: {len(records)} != {len(requests)}")
    for record in records:
        forbidden = sorted(FORBIDDEN_RAW_FIELDS.intersection(record))
        if forbidden:
            raise ValueError(f"forbidden raw record field: {forbidden[0]}")
    for request in requests:
        forbidden = sorted(FORBIDDEN_REQUEST_FIELDS.intersection(request))
        if forbidden:
            raise ValueError(f"forbidden request field: {forbidden[0]}")
    ids = [request["request_id"] for request in requests]
    if len(ids) != len(set(ids)):
        raise ValueError("manifest request_ids must be unique")
    fields = [request["field"] for request in requests]
    if len(fields) != len(set(fields)):
        raise ValueError("manifest request fields must be unique")
    groups = set(manifest["sources"])
    if any(request["source_group"] not in groups for request in requests):
        raise ValueError("manifest request references unknown source_group")
    if manifest["data_provenance"] != "SYNTHETIC_FIXTURE":
        raise ValueError("preflight only accepts SYNTHETIC_FIXTURE provenance")
    for record in records:
        if record["source_group"] not in groups:
            raise ValueError(f"raw record references unknown source_group: {record['source_group']}")
        if record["symbol"] != manifest["symbol"]:
            raise ValueError("raw record symbol differs from manifest symbol")


def _make_request(manifest: Mapping[str, Any], item: Mapping[str, Any]) -> FetchRequest:
    return FetchRequest(
        symbol=manifest["symbol"],
        field=item["field"],
        period=item["period"],
        request_id=item["request_id"],
    )


def generate_cards(records: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]):
    """Run one batch per source group and restore manifest order."""
    _validate_manifest(records, manifest)
    by_group: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        by_group.setdefault(record["source_group"], []).append(record)
    requests_by_group: dict[str, list[FetchRequest]] = {}
    for item in manifest["requests"]:
        requests_by_group.setdefault(item["source_group"], []).append(_make_request(manifest, item))

    results_by_id: dict[str, Any] = {}
    source_group_by_request = {
        item["request_id"]: item["source_group"] for item in manifest["requests"]
    }
    batches = []
    for group, definition in manifest["sources"].items():
        source = SyntheticDataSource(
            records=by_group.get(group, []),
            default_tier=definition["source_tier"],
            source_name=definition["source_name"],
        )
        batch = run_batch(source, requests_by_group.get(group, []))
        batches.append(batch)
        for result in batch.results:
            results_by_id[result.request_id] = result
    ensure_all_validated(
        list(results_by_id.values()),
        source_group_by_request=source_group_by_request,
    )
    return [results_by_id[item["request_id"]].card for item in manifest["requests"]], batches


def ensure_all_validated(
    results: Sequence[Any],
    *,
    source_group_by_request: Mapping[str, str] | None = None,
) -> None:
    for result in results:
        if isinstance(result, Mapping):
            status = result.get("status", "")
            request_id = result.get("request_id", "")
            field = result.get("field", "")
            violations = result.get("violations", [])
            failure = result.get("failure")
        else:
            status = result.status.value if hasattr(result.status, "value") else result.status
            request_id = result.request_id
            field = result.field
            violations = result.violations
            failure = result.failure
        if status != DataSourceRunStatus.CARD_VALIDATED.value:
            details = (
                f"runner_status={status} "
                f"violations={list(violations)}"
            )
            if failure is not None:
                reason = getattr(failure, "reason", None)
                reason = reason.value if hasattr(reason, "value") else reason
                details += (
                    f" failure.reason={reason}"
                    f" failure.detail={getattr(failure, 'detail', '')}"
                    f" failure.retry_allowed={getattr(failure, 'retry_allowed', '')}"
                )
            raise RuntimeError(
                f"source_group={(source_group_by_request or {}).get(request_id, 'unknown')} "
                f"request_id={request_id} field={field} {details}"
            )


def compare_cards(generated: Sequence[Mapping[str, Any]], canonical: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]) -> dict[str, Any]:
    generated_ids = [card.get("request_id") for card in generated]
    canonical_ids = [card.get("request_id") for card in canonical]
    request_ids = [item["request_id"] for item in manifest["requests"]]
    field_mismatches: list[dict[str, Any]] = []
    missing_keys: list[dict[str, Any]] = []
    extra_keys: list[dict[str, Any]] = []
    for request_id in sorted(set(generated_ids) & set(canonical_ids)):
        actual = next(card for card in generated if card.get("request_id") == request_id)
        expected = next(card for card in canonical if card.get("request_id") == request_id)
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            missing_keys.append({"request_id": request_id, "keys": missing})
        if extra:
            extra_keys.append({"request_id": request_id, "keys": extra})
        for field in sorted(set(actual) & set(expected)):
            if actual[field] != expected[field] or type(actual[field]) is not type(expected[field]):
                field_mismatches.append({
                    "request_id": request_id,
                    "field": field,
                    "expected": expected[field],
                    "actual": actual[field],
                    "expected_type": type(expected[field]).__name__,
                    "actual_type": type(actual[field]).__name__,
                })
    order_mismatches = [
        {"position": index, "expected": expected, "actual": actual}
        for index, (expected, actual) in enumerate(zip(request_ids, generated_ids))
        if expected != actual
    ]
    return {
        "parity": (
            len(generated) == len(canonical) == len(request_ids)
            and generated_ids == canonical_ids == request_ids
            and not missing_keys
            and not extra_keys
            and not field_mismatches
        ),
        "missing_request_ids": [request_id for request_id in canonical_ids if request_id not in generated_ids],
        "extra_request_ids": [request_id for request_id in generated_ids if request_id not in canonical_ids],
        "order_mismatches": order_mismatches,
        "missing_keys": missing_keys,
        "extra_keys": extra_keys,
        "field_mismatches": field_mismatches,
    }


def run_preflight(raw_path: Path, manifest_path: Path, canonical_path: Path) -> dict[str, Any]:
    records, manifest, canonical = load_inputs(raw_path, manifest_path, canonical_path)
    generated, batches = generate_cards(records, manifest)
    parity = compare_cards(generated, canonical, manifest)
    if not parity["parity"]:
        raise RuntimeError(json.dumps({"status": "PREFLIGHT_FAIL", **parity}, ensure_ascii=False))
    return {
        "status": "PREFLIGHT_PASS",
        "generated_cards": len(generated),
        "canonical_cards": len(canonical),
        "parity": True,
        "data_provenance": manifest["data_provenance"],
        "production_research_eligible": False,
        "account_action": "LOCKED",
        "demo_input_changed": False,
        "bundle_hash_changed": False,
        "batch_totals": [batch.total for batch in batches],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    args = parser.parse_args()
    try:
        print(json.dumps(run_preflight(args.raw, args.manifest, args.canonical), indent=2, ensure_ascii=False))
    except Exception as exc:
        try:
            failure = json.loads(str(exc))
            if not isinstance(failure, dict) or failure.get("status") != "PREFLIGHT_FAIL":
                raise ValueError
        except (TypeError, ValueError, json.JSONDecodeError):
            failure = {"status": "PREFLIGHT_FAIL", "error": str(exc)}
        print(json.dumps(failure, indent=2, ensure_ascii=False))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
