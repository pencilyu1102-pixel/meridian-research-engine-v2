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

from tools.bundle_data_card_resolver import ensure_all_validated, generate_datasource_cards

DEFAULT_RAW = ROOT / "examples/full_chain_sample/synthetic_source_records.json"
DEFAULT_MANIFEST = ROOT / "examples/full_chain_sample/synthetic_fetch_manifest.json"
DEFAULT_CANONICAL = ROOT / "examples/full_chain_sample/synthetic_data_cards.json"


def load_inputs(raw_path: Path, manifest_path: Path, canonical_path: Path):
    records = json.loads(raw_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not isinstance(manifest, dict) or not isinstance(canonical, list):
        raise ValueError("raw records and canonical cards must be arrays; manifest must be an object")
    return records, manifest, canonical


def generate_cards(records: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any]):
    """Compatibility wrapper around the shared intake generator."""
    return generate_datasource_cards(records, manifest)


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
