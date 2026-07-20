"""Shared Bundle → Data Card resolution for legacy and datasource intake modes."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from tools.data_source import FetchRequest
from tools.data_source_runner import DataSourceBatchResult, DataSourceRunStatus, run_batch
from tools.synthetic_data_source import SyntheticDataSource


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


@dataclass(frozen=True)
class ResolvedDataCards:
    """Cards resolved from one Bundle input contract."""

    cards: tuple[dict[str, Any], ...]
    mode: str
    artifact_hashes: dict[str, str]
    generated_cards_sha256: str | None
    batch_statuses: tuple[dict[str, Any], ...]

    @property
    def generated_count(self) -> int:
        return len(self.cards)


def _canonical_json_hash(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _raw_file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_safe_artifact_path(path_str: str, bundle_dir: str | Path) -> Path:
    """Resolve a Bundle-relative artifact path without allowing escapes."""
    path = Path(path_str)
    if path.is_absolute():
        raise ValueError(f"artifact path must be relative, got absolute: {path_str}")
    base = Path(bundle_dir).resolve()
    resolved = (base / path).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ValueError(
            f"artifact path escapes bundle directory: {path_str} → {resolved}"
        ) from exc
    if not resolved.exists():
        raise FileNotFoundError(f"artifact file not found: {resolved}")
    return resolved


def _bundle_dir(bundle: Mapping[str, Any]) -> Path:
    value = bundle.get("_bundle_dir")
    if not value:
        raise ValueError("bundle is missing runtime _bundle_dir")
    return Path(value)


def _data_cards_config(bundle: Mapping[str, Any]) -> tuple[str, Mapping[str, Any]]:
    config = bundle.get("data_cards")
    if not isinstance(config, Mapping):
        raise ValueError("bundle data_cards must be an object")
    mode = config.get("mode")
    if mode is None:
        mode = "legacy_static"
    if mode not in {"legacy_static", "datasource_intake"}:
        raise ValueError(f"unknown data_cards mode: {mode!r}")
    if mode == "legacy_static":
        if any(key in config for key in ("records_path", "manifest_path", "expected_count")):
            raise ValueError("legacy_static cannot contain datasource_intake fields")
        if not isinstance(config.get("path"), str) or not config["path"]:
            raise ValueError("legacy_static requires data_cards.path")
    else:
        required = ("records_path", "manifest_path", "expected_count")
        missing = [key for key in required if key not in config]
        if missing:
            raise ValueError(f"datasource_intake missing required field: {missing[0]}")
        if "path" in config:
            raise ValueError("datasource_intake cannot contain legacy data_cards.path")
        if not isinstance(config["expected_count"], int) or isinstance(config["expected_count"], bool):
            raise ValueError("datasource_intake expected_count must be an integer")
        if config["expected_count"] < 0:
            raise ValueError("datasource_intake expected_count must be non-negative")
    return mode, config


def _load_json_array(path: Path, label: str) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{label} must be a JSON array of objects")
    return value


def _validate_intake_inputs(
    records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> None:
    meta = bundle.get("meta")
    if not isinstance(meta, Mapping):
        raise ValueError("bundle meta must be an object")
    bundle_symbol = meta.get("symbol")
    if not isinstance(bundle_symbol, str) or not bundle_symbol:
        raise ValueError("bundle meta.symbol must be non-empty")
    manifest_symbol = manifest.get("symbol")
    if not isinstance(manifest_symbol, str) or not manifest_symbol:
        raise ValueError("manifest symbol must be non-empty")
    if manifest_symbol != bundle_symbol:
        raise ValueError("Bundle and manifest symbol mismatch")
    if not isinstance(manifest.get("sources"), Mapping):
        raise ValueError("manifest sources must be an object")
    requests = manifest.get("requests")
    if not isinstance(requests, list):
        raise ValueError("manifest requests must be an array")
    if manifest.get("data_provenance") != "SYNTHETIC_FIXTURE":
        raise ValueError("manifest provenance must be SYNTHETIC_FIXTURE")
    bundle_provenance = bundle.get("meta", {}).get("data_provenance")
    if bundle_provenance != manifest.get("data_provenance"):
        raise ValueError("Bundle and manifest provenance mismatch")
    if len(records) != len(requests):
        raise ValueError(f"raw/request count mismatch: {len(records)} != {len(requests)}")
    for record in records:
        forbidden = sorted(FORBIDDEN_RAW_FIELDS.intersection(record))
        if forbidden:
            raise ValueError(f"forbidden raw record field: {forbidden[0]}")
    request_ids: list[str] = []
    fields: list[str] = []
    for request in requests:
        if not isinstance(request, Mapping):
            raise ValueError("manifest requests must contain objects")
        forbidden = sorted(FORBIDDEN_REQUEST_FIELDS.intersection(request))
        if forbidden:
            raise ValueError(f"forbidden request field: {forbidden[0]}")
        request_ids.append(str(request.get("request_id", "")))
        fields.append(str(request.get("field", "")))
        if request.get("source_group") not in manifest["sources"]:
            raise ValueError("manifest request references unknown source_group")
    if not all(request_ids) or len(request_ids) != len(set(request_ids)):
        raise ValueError("manifest request_ids must be unique and non-empty")
    if not all(fields) or len(fields) != len(set(fields)):
        raise ValueError("manifest request fields must be unique and non-empty")
    for record in records:
        if record.get("source_group") not in manifest["sources"]:
            raise ValueError(f"raw record references unknown source_group: {record.get('source_group')}")
        if record.get("symbol") != manifest_symbol:
            raise ValueError("raw record symbol differs from manifest symbol")


def _make_request(manifest: Mapping[str, Any], item: Mapping[str, Any]) -> FetchRequest:
    return FetchRequest(
        symbol=str(manifest["symbol"]),
        field=str(item["field"]),
        period=item.get("period"),
        request_id=str(item["request_id"]),
    )


def ensure_all_validated(
    results: Sequence[Any],
    *,
    source_group_by_request: Mapping[str, str] | None = None,
) -> None:
    """Fail closed with structured Runner failure details."""
    for result in results:
        if isinstance(result, Mapping):
            status = result.get("status", "")
            request_id = str(result.get("request_id", ""))
            field = str(result.get("field", ""))
            violations = result.get("violations", [])
            failure = result.get("failure")
        else:
            status = result.status.value if hasattr(result.status, "value") else result.status
            request_id = result.request_id
            field = result.field
            violations = result.violations
            failure = result.failure
        if status != DataSourceRunStatus.CARD_VALIDATED.value:
            details = f"runner_status={status} expected=CARD_VALIDATED violations={list(violations)}"
            if failure is not None:
                if isinstance(failure, Mapping):
                    reason = failure.get("reason")
                    detail = failure.get("detail", "")
                    retry_allowed = failure.get("retry_allowed", "")
                else:
                    reason = getattr(failure, "reason", None)
                    detail = getattr(failure, "detail", "")
                    retry_allowed = getattr(failure, "retry_allowed", "")
                reason = reason.value if hasattr(reason, "value") else reason
                details += (
                    f" failure.reason={reason}"
                    f" failure.detail={detail}"
                    f" failure.retry_allowed={retry_allowed}"
                )
            raise RuntimeError(
                f"source_group={(source_group_by_request or {}).get(request_id, 'unknown')} "
                f"request_id={request_id} field={field} {details}"
            )


def generate_datasource_cards(
    records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
    *,
    bundle: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[DataSourceBatchResult]]:
    """Generate cards through one SyntheticDataSource per manifest source group."""
    if bundle is None:
        bundle = {
            "meta": {
                "data_provenance": manifest.get("data_provenance"),
                "symbol": manifest.get("symbol"),
            }
        }
    _validate_intake_inputs(records, manifest, bundle)
    by_group: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        by_group.setdefault(str(record["source_group"]), []).append(record)
    requests_by_group: dict[str, list[FetchRequest]] = {}
    for item in manifest["requests"]:
        requests_by_group.setdefault(str(item["source_group"]), []).append(_make_request(manifest, item))

    cards_by_id: dict[str, dict[str, Any]] = {}
    results = []
    batches = []
    source_group_by_request = {
        str(item["request_id"]): str(item["source_group"])
        for item in manifest["requests"]
    }
    for group, definition in manifest["sources"].items():
        if not isinstance(definition, Mapping):
            raise ValueError(f"manifest source definition must be an object: {group}")
        source = SyntheticDataSource(
            records=by_group.get(group, []),
            default_tier=str(definition["source_tier"]),
            source_name=str(definition["source_name"]),
        )
        batch = run_batch(source, requests_by_group.get(group, []))
        batches.append(batch)
        results.extend(batch.results)
        for result in batch.results:
            cards_by_id[result.request_id] = result.card or {}

    ensure_all_validated(results, source_group_by_request=source_group_by_request)
    cards = [cards_by_id[str(item["request_id"])] for item in manifest["requests"]]
    return cards, batches


def _resolve_legacy(bundle: Mapping[str, Any], config: Mapping[str, Any]) -> ResolvedDataCards:
    path = resolve_safe_artifact_path(str(config["path"]), _bundle_dir(bundle))
    cards = _load_json_array(path, "data_cards")
    card_hash = _raw_file_sha256(path)
    return ResolvedDataCards(
        cards=tuple(cards),
        mode="legacy_static",
        artifact_hashes={"data_cards": card_hash},
        generated_cards_sha256=None,
        batch_statuses=(),
    )


def _resolve_intake(bundle: Mapping[str, Any], config: Mapping[str, Any]) -> ResolvedDataCards:
    base = _bundle_dir(bundle)
    records_path = resolve_safe_artifact_path(str(config["records_path"]), base)
    manifest_path = resolve_safe_artifact_path(str(config["manifest_path"]), base)
    records = _load_json_array(records_path, "raw records")
    manifest_value = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest_value, dict):
        raise ValueError("manifest must be a JSON object")
    cards, batches = generate_datasource_cards(records, manifest_value, bundle=bundle)
    expected = int(config["expected_count"])
    if len(cards) != expected:
        raise ValueError(f"expected_count mismatch: expected {expected}, generated {len(cards)}")
    batch_statuses = []
    for group, batch in zip(manifest_value["sources"], batches):
        statuses = [result.status.value for result in batch.results]
        batch_statuses.append({
            "source_group": group,
            "status": "CARD_VALIDATED" if statuses and all(status == "CARD_VALIDATED" for status in statuses) else (statuses[0] if statuses else "EMPTY"),
            "statuses": statuses,
            "total": batch.total,
            "validated_count": batch.validated_count,
        })
    generated_hash = _canonical_json_hash(cards)
    return ResolvedDataCards(
        cards=tuple(cards),
        mode="datasource_intake",
        artifact_hashes={
            "data_card_records": _raw_file_sha256(records_path),
            "data_card_manifest": _raw_file_sha256(manifest_path),
            "generated_data_cards": generated_hash,
        },
        generated_cards_sha256=generated_hash,
        batch_statuses=tuple(batch_statuses),
    )


def resolve_bundle_data_cards(bundle: Mapping[str, Any]) -> ResolvedDataCards:
    """Resolve cards from the Bundle's explicitly selected data_cards mode."""
    mode, config = _data_cards_config(bundle)
    if mode == "legacy_static":
        return _resolve_legacy(bundle, config)
    return _resolve_intake(bundle, config)
