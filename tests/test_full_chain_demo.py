"""Test full-chain offline demo: reproducibility, boundary, correctness, non-impersonation."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = ROOT / "outputs" / "demo"
REPORT_PATH = OUTPUT_DIR / "SAMPLE_MANAGED_CARE_full_chain_report_zh.md"
RESULT_PATH = OUTPUT_DIR / "SAMPLE_MANAGED_CARE_full_chain_result.json"
HARDLOCK_PATH = OUTPUT_DIR / "SAMPLE_MANAGED_CARE_hardlock_verdict.json"


def _run_demo() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/run_demo.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ── Basic smoke tests ──────────────────────────────────────────────────

def test_demo_runs_and_exits_zero():
    """Demo must run to completion (exit 0 even if report is rejected)."""
    r = _run_demo()
    assert r.returncode == 0, f"Demo failed with exit {r.returncode}\n{r.stderr[:500]}"


def test_demo_produces_report():
    """Demo must produce a Markdown report with sufficient content."""
    _run_demo()
    text = REPORT_PATH.read_text(encoding="utf-8")
    assert len(text) > 3000, f"Report too short: {len(text)} chars"
    assert "SAMPLE_MANAGED_CARE" in text


def test_demo_produces_result_json():
    """Demo must produce a structured result JSON."""
    _run_demo()
    data = _read_json(RESULT_PATH)
    assert "gatekeeper_result" in data
    assert "hardlock_verdict" in data
    assert "demo_info" in data


# ── Boundary / provenance tests ────────────────────────────────────────

def test_demo_is_explicitly_synthetic():
    """Result JSON must declare SYNTHETIC_FIXTURE provenance."""
    _run_demo()
    data = _read_json(RESULT_PATH)
    assert data["demo_info"]["data_provenance"] == "SYNTHETIC_FIXTURE"


def test_demo_production_research_is_locked():
    """Demo must NOT claim production research eligibility."""
    _run_demo()
    data = _read_json(RESULT_PATH)
    assert data["demo_info"]["production_research_eligible"] is False
    assert data["demo_info"]["real_world_sources_verified"] is False
    assert data["demo_info"]["account_action"] == "LOCKED"


def test_demo_report_contains_demo_banner():
    """Report must contain the DEMO ONLY banner."""
    _run_demo()
    text = REPORT_PATH.read_text(encoding="utf-8")
    assert "DEMO ONLY" in text
    assert "仅供演示" in text


def test_demo_sources_do_not_impersonate_real_sources():
    """Fixture source names must contain SYNTHETIC or FIXTURE, not real company names."""
    _run_demo()

    # Check data cards
    cards_path = ROOT / "examples" / "full_chain_sample" / "synthetic_data_cards.json"
    cards = json.loads(cards_path.read_text(encoding="utf-8"))
    for card in cards:
        source = card.get("source", "")
        assert "SYNTHETIC" in source or "FIXTURE" in source, (
            f"Fixture source does not declare SYNTHETIC/FIXTURE: {source}"
        )
        # Must not look like a real URL
        assert "://" not in source, f"Fixture source looks like a URL: {source}"

    # Check industry fields
    ind_path = ROOT / "examples" / "full_chain_sample" / "synthetic_industry_fields.json"
    ind_data = json.loads(ind_path.read_text(encoding="utf-8"))
    for name, field in ind_data.get("fields", {}).items():
        notes = field.get("notes", "")
        assert "Synthetic" in notes or "SYNTHETIC" in notes, (
            f"Industry field '{name}' notes don't declare synthetic: {notes}"
        )

    # Check report text
    report_text = REPORT_PATH.read_text(encoding="utf-8")
    # Must use SYNTHETIC_FIXTURE_ prefixes in data source table
    assert "SYNTHETIC_FIXTURE_" in report_text


# ── Reproducibility tests ──────────────────────────────────────────────

def test_demo_report_is_reproducible():
    """Two consecutive runs must produce identical report content."""
    _run_demo()
    report1 = REPORT_PATH.read_text(encoding="utf-8")
    _run_demo()
    report2 = REPORT_PATH.read_text(encoding="utf-8")
    assert report1 == report2, "Report content not reproducible between runs"


def test_demo_json_outputs_are_reproducible():
    """Two consecutive runs must produce identical JSON results."""
    _run_demo()
    data1 = _read_json(RESULT_PATH)
    _run_demo()
    data2 = _read_json(RESULT_PATH)
    assert data1 == data2, "Result JSON not reproducible between runs"


def test_demo_hardlock_json_is_reproducible():
    """Two consecutive runs must produce identical Hardlock JSON."""
    _run_demo()
    hl1 = _read_json(HARDLOCK_PATH)
    _run_demo()
    hl2 = _read_json(HARDLOCK_PATH)
    assert hl1 == hl2, "Hardlock JSON not reproducible between runs"


# ── Expected result lock ───────────────────────────────────────────────

def test_demo_result_matches_expected():
    """Verify the demo result matches expected contract-completeness state.

    The synthetic fixtures are designed to satisfy all hardlock layers and
    template requirements. FULL_PASS means contract completeness, not that
    real-world data has been verified.

    If fixtures change intentionally, update EXPECTED_GATEKEEPER_STATUS.
    """
    EXPECTED_GATEKEEPER_STATUS = "PASS_TEST_ONLY"
    EXPECTED_HARDLOCK_STATUS = "PASS_TEST_ONLY"

    _run_demo()
    data = _read_json(RESULT_PATH)

    actual_gk = data["gatekeeper_result"]["final_status"]
    actual_hl = data["hardlock_verdict"]["status"]

    assert actual_gk == EXPECTED_GATEKEEPER_STATUS, (
        f"Gatekeeper status mismatch: expected {EXPECTED_GATEKEEPER_STATUS}, got {actual_gk}"
    )
    assert actual_hl == EXPECTED_HARDLOCK_STATUS, (
        f"Hardlock status mismatch: expected {EXPECTED_HARDLOCK_STATUS}, got {actual_hl}"
    )

    # Verify boundary interpretation is correct
    interpret = data["demo_info"]["engine_verdict_interpretation"]
    assert "contract completeness" in interpret.lower() or "contract" in interpret.lower(), (
        f"Verdict interpretation missing contract-completeness disclaimer: {interpret}"
    )


# ── Git / security hygiene ─────────────────────────────────────────────

def test_demo_output_not_tracked_by_git():
    """Demo output directory must not be tracked by git."""
    result = subprocess.run(
        ["git", "ls-files", "outputs/demo"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "", f"outputs/demo is tracked by git: {result.stdout}"


def test_demo_no_real_companies():
    """Demo output must not contain real company names or tickers (outside metadata block)."""
    text = REPORT_PATH.read_text(encoding="utf-8")
    # Strip metadata block to avoid false positive on MRE_REPORT_META
    import re
    clean = re.sub(r'<!--\s*MRE_REPORT_META.*?-->', '', text, flags=re.DOTALL)
    forbidden = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "META", "UNH", "NVDA", "TSLA",
        "寒武纪", "688256", "贵州茅台", "腾讯",
    ]
    for name in forbidden:
        assert name not in clean, f"Real company found in demo: {name}"
