#!/usr/bin/env python3
"""
Meridian Research Engine 2.0 — Agent Report Validation Adapter

Validates an agent-generated report against a research bundle:
  1. Verifies report-bundle binding (research_id, symbol, market, hash, etc.)
  2. Builds Data Integrity Hardlock from bundle fixtures
  3. Runs Gatekeeper with structured hardlock verdict
  4. Outputs validated result with provenance metadata

Usage:
  python scripts/validate_agent_report.py \\
    --report outputs/agent_demo/REPORT.md \\
    --bundle examples/full_chain_sample/research_bundle.json \\
    --output outputs/agent_demo/VALIDATION.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Report metadata block (HTML comment, no YAML dependency) ───────────

_META_BLOCK_RE = re.compile(
    r'<!--\s*MRE_REPORT_META\s*\n(.*?)\n\s*-->', re.DOTALL
)

_META_KV_RE = re.compile(r'^(\w+)=(.*)$')


def parse_report_meta(text: str) -> dict[str, str]:
    """Parse MRE_REPORT_META comment block from a Markdown report.

    Returns a dict of key=value pairs.  Raises ValueError on missing block,
    duplicate keys, or malformed lines.
    """
    m = _META_BLOCK_RE.search(text)
    if not m:
        raise ValueError("report metadata block (MRE_REPORT_META) not found")
    seen: set[str] = set()
    meta: dict[str, str] = {}
    for line in m.group(1).strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        kv = _META_KV_RE.match(line)
        if not kv:
            raise ValueError(f"malformed metadata line: {line!r}")
        key, value = kv.group(1), kv.group(2).strip()
        if key in seen:
            raise ValueError(f"duplicate metadata key: {key}")
        seen.add(key)
        meta[key] = value
    return meta


def format_report_meta(meta: dict[str, str]) -> str:
    """Format a metadata dict as an MRE_REPORT_META comment block."""
    lines = ["<!-- MRE_REPORT_META"]
    for k, v in meta.items():
        lines.append(f"{k}={v}")
    lines.append("-->")
    return "\n".join(lines)


# ── Bundle hashing (transitive — covers referenced artifact files) ─────

_BUNDLE_HASH_KEY = "bundle_sha256"


def _file_sha256(path: Path) -> str:
    """SHA256 of a file's raw bytes (deterministic)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json_hash(obj: Any) -> str:
    """SHA256 of sorted-key, compact, UTF-8 JSON representation."""
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def compute_artifact_hashes(bundle: dict[str, Any]) -> dict[str, str]:
    """Compute SHA256 hashes of all referenced artifact files.

    Covers: data_cards, industry_hard_fields.
    """
    bundle_dir = Path(bundle.get("_bundle_dir", "."))
    hashes: dict[str, str] = {}

    # Data cards
    dc_path = bundle.get("data_cards", {}).get("path", "")
    if dc_path:
        resolved = _resolve_safe(dc_path, bundle_dir)
        hashes["data_cards"] = _file_sha256(resolved)

    # Industry hard fields
    ihf_path = bundle.get("industry_hard_fields", {}).get("path", "")
    if ihf_path:
        resolved = _resolve_safe(ihf_path, bundle_dir)
        hashes["industry_hard_fields"] = _file_sha256(resolved)

    return hashes


def compute_bundle_hash(bundle: dict[str, Any]) -> str:
    """Compute transitive canonical SHA256 of a bundle + all referenced artifacts.

    Excludes meta.bundle_sha256 and _bundle_dir (runtime-injected).
    Includes artifact SHA256 values so any referenced file change changes the bundle hash.
    Keys sorted, UTF-8, compact separators.
    """
    import copy
    clean = {k: copy.deepcopy(v) for k, v in bundle.items() if k != "_bundle_dir"}
    if "meta" in clean and isinstance(clean["meta"], dict):
        clean["meta"] = {k: v for k, v in clean["meta"].items() if k != _BUNDLE_HASH_KEY}

    # Inject artifact hashes so content changes cascade to bundle hash
    artifact_hashes = compute_artifact_hashes(bundle)
    clean["_artifact_hashes"] = artifact_hashes

    return _canonical_json_hash(clean)


# ── Path safety ────────────────────────────────────────────────────────

def _resolve_safe(path_str: str, relative_to: Path) -> Path:
    """Resolve a relative path safely — rejects absolute paths and escapes."""
    p = Path(path_str)
    if p.is_absolute():
        raise ValueError(f"artifact path must be relative, got absolute: {path_str}")
    resolved = (relative_to / p).resolve()
    # Prevent directory traversal escapes
    try:
        resolved.relative_to(relative_to.resolve())
    except ValueError:
        raise ValueError(
            f"artifact path escapes bundle directory: {path_str} → {resolved}"
        )
    if not resolved.exists():
        raise FileNotFoundError(f"artifact file not found: {resolved}")
    return resolved


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    """Load and validate a research bundle JSON file."""
    bp = Path(bundle_path).resolve()
    bundle = json.loads(bp.read_text(encoding="utf-8"))
    bundle["_bundle_dir"] = str(bp.parent)
    return bundle


# ── Binding check ──────────────────────────────────────────────────────

# Fields that must match between report metadata and bundle metadata.
_BINDING_FIELDS = [
    "research_id",
    "symbol",
    "market",
    "industry_adapter",
    "as_of_date",
    "data_provenance",
]

# Fields that must be present in both but have different sources:
# bundle_sha256 is computed from the bundle, not read from report meta as-is.


def check_binding(report_meta: dict[str, str], bundle: dict[str, Any]) -> list[str]:
    """Verify report meta matches bundle meta. Returns list of violations (empty = ok).

    Checks:
      - All _BINDING_FIELDS match between report meta and bundle.meta
      - report_meta.bundle_sha256 == computed bundle hash
    """
    violations: list[str] = []
    bundle_meta = bundle.get("meta", {})

    for field in _BINDING_FIELDS:
        rv = report_meta.get(field)
        bv = bundle_meta.get(field)
        if rv is None:
            violations.append(f"report metadata missing field: {field}")
        elif str(bv) != str(rv):
            violations.append(
                f"{field} mismatch: report={rv!r}, bundle={bv!r}"
            )

    # Hash check
    expected_hash = compute_bundle_hash(bundle)
    report_hash = report_meta.get(_BUNDLE_HASH_KEY)
    if report_hash is None:
        violations.append(f"report metadata missing field: {_BUNDLE_HASH_KEY}")
    elif report_hash != expected_hash:
        violations.append(
            f"bundle_sha256 mismatch: report={report_hash[:16]}..., computed={expected_hash[:16]}..."
        )

    return violations


# ── Hardlock builder (shared with run_demo.py) ─────────────────────────

def build_hardlock_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Build a Data Integrity Hardlock verdict from a research bundle.

    Synthetic data is capped at PASS_TEST_ONLY — never formally releasable.
    All data is expected to be synthetic fixture — no real market data.
    """
    from tools.data_card_registry import DataCardRegistry
    from tools.earnings_basis_checker import check_earnings_basis
    from tools.industry_hard_fields import check_industry_hard_fields, load_industry_hard_fields
    from tools.capital_structure_bridge import validate_capital_structure_bridge
    from tools.data_integrity_hardlock import aggregate_hardlock_verdicts
    from tools.source_policy import PROVENANCE_SYNTHETIC

    bundle_dir = Path(bundle["_bundle_dir"])
    provenance = bundle.get("meta", {}).get("data_provenance", "")

    cards_path = _resolve_safe(bundle["data_cards"]["path"], bundle_dir)
    cards_json = json.loads(cards_path.read_text(encoding="utf-8"))
    if not isinstance(cards_json, list):
        raise TypeError("data_cards must be a JSON array")
    registry = DataCardRegistry(cards_json)
    eps_v = registry.validate("eps_ttm", data_provenance=provenance)
    price_v = registry.validate("current_price", data_provenance=provenance)

    dc_status = "PASS_FORMAL"
    dc_violations: list[str] = []
    for v in [eps_v, price_v]:
        if v.status != "PASS_FORMAL":
            dc_status = v.status
            dc_violations.extend(v.violations)

    earn_cfg = bundle["earnings_basis"]
    earn_result = check_earnings_basis({
        "basis": earn_cfg["basis"],
        "usage_context": earn_cfg.get("usage_context", "trailing_eps"),
        "explicit_approval": earn_cfg.get("explicit_approval", False),
        "verified": earn_cfg.get("verified", False),
        "has_gaap_anchor": earn_cfg.get("has_gaap_anchor", False),
    })

    ind_path = _resolve_safe(bundle["industry_hard_fields"]["path"], bundle_dir)
    ind_payload = load_industry_hard_fields(ind_path)
    ind_result = check_industry_hard_fields(ind_payload)

    bridge_cfg = bundle["capital_structure_bridge"]
    bridge_result = validate_capital_structure_bridge(bridge_cfg)

    verdicts = {
        "data_card": {"status": dc_status, "violations": dc_violations},
        "earnings_basis": {"status": earn_result.status, "violations": list(earn_result.violations)},
        "industry_hard_fields": ind_result.to_verdict(),
        "capital_structure_bridge": {"status": bridge_result.status, "violations": list(bridge_result.violations)},
    }

    aggregated = aggregate_hardlock_verdicts(verdicts)

    # Synthetic data boundary: never PASS_FORMAL, cap at PASS_TEST_ONLY
    status = aggregated.status
    violations = list(aggregated.violations)
    is_synthetic = provenance.upper() == PROVENANCE_SYNTHETIC.upper()
    if is_synthetic and status == "PASS_FORMAL":
        status = "PASS_TEST_ONLY"
        violations.append("synthetic fixture data — not formally releasable (PASS_TEST_ONLY)")

    return {
        "status": status,
        "violations": violations,
        "details": aggregated.details,
        "module_verdicts": {
            k: {"status": v["status"], "violations": v["violations"]} for k, v in verdicts.items()
        },
    }


# ── Main validation ────────────────────────────────────────────────────

def validate_report(
    report_path: str | Path,
    bundle_path: str | Path,
) -> dict[str, Any]:
    """Full validation: binding → hardlock → gatekeeper → result."""
    rp = Path(report_path).resolve()
    bp = Path(bundle_path).resolve()

    report_text = rp.read_text(encoding="utf-8")
    bundle = load_bundle(bp)

    # ── Binding check ──
    report_meta = parse_report_meta(report_text)
    binding_violations = check_binding(report_meta, bundle)
    computed_hash = compute_bundle_hash(bundle)

    if binding_violations:
        return {
            "report_path": str(rp),
            "bundle_path": str(bp),
            "binding_status": "REPORT_BUNDLE_MISMATCH",
            "binding_violations": binding_violations,
            "data_provenance": bundle.get("meta", {}).get("data_provenance", "UNKNOWN"),
            "production_research_eligible": False,
            "account_action": "LOCKED",
            "bundle_sha256": computed_hash,
            "report_bundle_sha256": report_meta.get(_BUNDLE_HASH_KEY),
            "hardlock_verdict": None,
            "gatekeeper_result": None,
            "warnings": [],
            "error": "Binding check failed — report does not match bundle. Hardlock and Gatekeeper not executed.",
        }

    # ── Hardlock ──
    hardlock = build_hardlock_from_bundle(bundle)

    # ── Gatekeeper ──
    from tools.report_gatekeeper import check_report
    gk_result = check_report(report_text, mode="formal", language="zh", hardlock_verdict=hardlock)

    is_synthetic = bundle.get("meta", {}).get("data_provenance", "") == "SYNTHETIC_FIXTURE"

    return {
        "report_path": str(rp),
        "bundle_path": str(bp),
        "binding_status": "PASS",
        "binding_violations": [],
        "data_provenance": bundle.get("meta", {}).get("data_provenance", "UNKNOWN"),
        "hardlock_verdict": hardlock,
        "gatekeeper_result": gk_result,
        "production_research_eligible": False if is_synthetic else None,
        "account_action": "LOCKED" if is_synthetic else "UNKNOWN",
        "bundle_sha256": computed_hash,
        "report_sha256": _file_sha256(rp),
        "report_bundle_sha256": report_meta.get(_BUNDLE_HASH_KEY),
        "artifact_hashes": compute_artifact_hashes(bundle),
        "warnings": gk_result.get("warnings", []),
    }


# ── CLI ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Meridian Research Engine 2.0 — Agent Report Validation Adapter"
    )
    parser.add_argument("--report", required=True, help="Path to agent-generated Markdown report")
    parser.add_argument("--bundle", required=True, help="Path to research bundle JSON")
    parser.add_argument("--output", required=True, help="Path for validation result JSON output")
    args = parser.parse_args()

    print(f"Report: {args.report}")
    print(f"Bundle: {args.bundle}")

    result = validate_report(args.report, args.bundle)

    bs = result["binding_status"]
    print(f"Binding: {bs}")
    if bs != "PASS":
        for v in result.get("binding_violations", []):
            print(f"  VIOLATION: {v}")
        print("  → Hardlock and Gatekeeper NOT executed.")
    else:
        h = result["hardlock_verdict"]
        g = result["gatekeeper_result"]
        print(f"Hardlock: {h['status']}")
        print(f"Gatekeeper: {g['final_status']}")
        print(f"Release: {g['release_decision']}")
        if result["warnings"]:
            print(f"Warnings: {result['warnings']}")

    print(f"Production eligible: {result['production_research_eligible']}")
    print(f"Bundle SHA256: {result['bundle_sha256'][:16]}...")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}")

    sys.exit(0 if bs == "PASS" else 1)


if __name__ == "__main__":
    main()
