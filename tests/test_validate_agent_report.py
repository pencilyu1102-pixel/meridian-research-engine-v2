"""Phase 3D.1 semantic closure tests — D-tier recordable, PASS_TEST_ONLY gatekeeper, boundary."""

import json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BOUND_REPORT = ROOT / "tests/fixtures/agent_demo/SAMPLE_MANAGED_CARE_agent_report_bound_zh.md"
UNBOUND_REPORT = ROOT / "tests/fixtures/agent_demo/SAMPLE_MANAGED_CARE_agent_report_zh.md"
BUNDLE_PATH = ROOT / "examples/full_chain_sample/research_bundle.json"
OUT_DIR = Path(tempfile.mkdtemp(prefix="mre_test_"))

def _base_card(**kw):
    return {"field_name":"eps","value":"1","source":"x","source_tier":"S",
            "timestamp":"t","period":"p","unit":"u","currency":"c",
            "accounting_basis":"gaap","can_enter_conclusion":"full","notes":"",
            "freshness_status":"current","has_conflict":False,
            "request_id":"SYNTHETIC::TEST::VAL::001","data_provenance":"SYNTHETIC_FIXTURE", **kw}

def _run(r, b, o):
    return subprocess.run([sys.executable,"scripts/validate_agent_report.py",
        "--report",str(r),"--bundle",str(b),"--output",str(o)],
        cwd=str(ROOT),capture_output=True,text=True,timeout=30)


# ═══ D-tier tests ═════════════════════════════════════════════════════

def test_d_tier_blocked_is_recordable_but_not_conclusion_eligible():
    from tools.data_card_registry import validate_data_card
    # Use a non-critical field so tier-permission alone is tested
    card = _base_card(field_name="gross_margin", source_tier="D", can_enter_conclusion="blocked")
    r = validate_data_card(card)
    assert r.status == "PASS_FORMAL"  # recordable — D+blocked is a valid record
    from tools.source_policy import check_source_admission
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion  # not conclusion-eligible
    assert sp.effective_permission == "blocked"

def test_d_tier_reference_only_is_rejected():
    from tools.data_card_registry import validate_data_card
    card = _base_card(source_tier="D", can_enter_conclusion="reference_only")
    r = validate_data_card(card)
    assert r.status == "FAIL_SOURCE_PERMISSION"

def test_d_tier_full_is_rejected():
    from tools.data_card_registry import validate_data_card
    card = _base_card(source_tier="D", can_enter_conclusion="full")
    r = validate_data_card(card)
    assert r.status == "FAIL_SOURCE_PERMISSION"

def test_core_field_with_only_d_blocked_card_fails_hardlock():
    """A critical field with only D/blocked card should not pass formal hardlock."""
    from tools.source_policy import check_source_admission
    card = _base_card(source_tier="D", can_enter_conclusion="blocked", field_name="current_price")
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion
    assert not sp.can_enter_primary_valuation
    assert "critical field 'current_price' requires full permission" in str(sp.violations)


# ═══ PASS_TEST_ONLY gatekeeper tests ═════════════════════════════════

def test_synthetic_hardlock_preserves_pass_test_only_at_gatekeeper():
    from tools.report_gatekeeper import check_report
    report = BOUND_REPORT.read_text()
    hl = {"status": "PASS_TEST_ONLY", "violations": ["synthetic fixture"]}
    r = check_report(report, mode="formal", language="zh", hardlock_verdict=hl)
    assert r["final_status"] == "PASS_TEST_ONLY"
    assert r["release_decision"] == "TEST_ONLY_NOT_RELEASABLE"
    assert r["can_be_used_as_formal_report"] is False
    assert r["can_be_used_as_framework_test"] is True

def test_pass_test_only_is_not_fail_data_hardlock():
    from tools.report_gatekeeper import check_report
    report = BOUND_REPORT.read_text()
    hl = {"status": "PASS_TEST_ONLY", "violations": []}
    r = check_report(report, mode="formal", language="zh", hardlock_verdict=hl)
    assert r["final_status"] != "FAIL_DATA_HARDLOCK"

def test_real_hardlock_failure_remains_fail_data_hardlock():
    from tools.report_gatekeeper import check_report
    report = BOUND_REPORT.read_text()
    hl = {"status": "FAIL_DATA_HARDLOCK", "violations": ["missing card"]}
    r = check_report(report, mode="formal", language="zh", hardlock_verdict=hl)
    assert r["final_status"] == "FAIL_DATA_HARDLOCK"
    assert r["release_decision"] == "不可准出"


# ═══ Freshness / conflict / denominator tests ═════════════════════════

def test_missing_freshness_metadata_fails():
    from tools.data_card_registry import validate_data_card
    card = _base_card()
    del card["freshness_status"]
    r = validate_data_card(card)
    assert r.status == "FAIL_DATA_CARD_MISSING"

def test_missing_conflict_metadata_fails():
    from tools.data_card_registry import validate_data_card
    card = _base_card()
    del card["has_conflict"]
    r = validate_data_card(card)
    assert r.status == "FAIL_DATA_CARD_MISSING"

def test_unknown_freshness_cannot_receive_full_permission():
    from tools.source_policy import check_source_admission
    card = _base_card(freshness_status="unknown", can_enter_conclusion="full")
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion

def test_valuation_denominator_requires_full_eligible_card():
    from tools.source_policy import check_source_admission
    # shares_outstanding is a critical field → must have full permission
    card = _base_card(field_name="shares_outstanding", source_tier="B", can_enter_conclusion="reference_only")
    sp = check_source_admission(card)
    assert not sp.can_enter_primary_valuation
    assert "critical field" in str(sp.violations)


# ═══ Full validator integration ═════════════════════════════════════

def test_validator_produces_pass_test_only():
    r = _run(BOUND_REPORT, BUNDLE_PATH, OUT_DIR / "_v.json")
    assert r.returncode == 0
    d = json.loads((OUT_DIR / "_v.json").read_text())
    assert d["hardlock_verdict"]["status"] == "PASS_TEST_ONLY"
    assert d["gatekeeper_result"]["final_status"] == "PASS_TEST_ONLY"
    assert d["gatekeeper_result"]["release_decision"] == "TEST_ONLY_NOT_RELEASABLE"
    assert d["production_research_eligible"] is False


# ═══ Phase 3C: binding tests (recovered) ══════════════════════════════

import re, shutil, tempfile

def _mismatch(field, bad):
    text = BOUND_REPORT.read_text()
    new = re.sub(rf'^{field}=.*$', f'{field}={bad}', text, flags=re.MULTILINE)
    out = OUT_DIR / f"_bm_{field}.md"
    out.write_text(new)
    return out

def test_matching_report_and_bundle_pass_binding():
    r = _run(BOUND_REPORT, BUNDLE_PATH, OUT_DIR / "_b_ok.json")
    assert r.returncode == 0
    d = json.loads((OUT_DIR / "_b_ok.json").read_text())
    assert d["binding_status"] == "PASS"

def test_report_bundle_research_id_mismatch_fails():
    r = _run(_mismatch("research_id","WRONG"), BUNDLE_PATH, OUT_DIR / "_b_rid.json")
    assert r.returncode != 0
    d = json.loads((OUT_DIR / "_b_rid.json").read_text())
    assert d["binding_status"] == "REPORT_BUNDLE_MISMATCH"

def test_report_bundle_symbol_mismatch_fails():
    r = _run(_mismatch("symbol","WRONG"), BUNDLE_PATH, OUT_DIR / "_b_sym.json")
    assert r.returncode != 0

def test_report_bundle_market_mismatch_fails():
    r = _run(_mismatch("market","WRONG"), BUNDLE_PATH, OUT_DIR / "_b_mkt.json")
    assert r.returncode != 0

def test_report_bundle_industry_adapter_mismatch_fails():
    r = _run(_mismatch("industry_adapter","WRONG"), BUNDLE_PATH, OUT_DIR / "_b_ind.json")
    assert r.returncode != 0

def test_report_bundle_as_of_date_mismatch_fails():
    r = _run(_mismatch("as_of_date","2000-01-01"), BUNDLE_PATH, OUT_DIR / "_b_dt.json")
    assert r.returncode != 0

def test_report_bundle_hash_mismatch_fails():
    r = _run(_mismatch("bundle_sha256","0"*64), BUNDLE_PATH, OUT_DIR / "_b_h.json")
    assert r.returncode != 0
    d = json.loads((OUT_DIR / "_b_h.json").read_text())
    assert d["gatekeeper_result"] is None

def test_report_bundle_data_provenance_mismatch_fails():
    r = _run(_mismatch("data_provenance","REAL"), BUNDLE_PATH, OUT_DIR / "_b_dp.json")
    assert r.returncode != 0

def test_missing_report_metadata_fails():
    text = BOUND_REPORT.read_text()
    clean = re.sub(r'<!--\s*MRE_REPORT_META.*?-->', '', text, flags=re.DOTALL)
    rp = OUT_DIR / "_b_nometa.md"
    rp.write_text(clean)
    r = _run(rp, BUNDLE_PATH, OUT_DIR / "_b_nometa.json")
    assert r.returncode != 0

def test_duplicate_report_metadata_fails():
    text = BOUND_REPORT.read_text()
    dup = text.replace("symbol=SAMPLE_MANAGED_CARE", "symbol=SAMPLE_MANAGED_CARE\nsymbol=DUP")
    rp = OUT_DIR / "_b_dup.md"
    rp.write_text(dup)
    r = _run(rp, BUNDLE_PATH, OUT_DIR / "_b_dup.json")
    assert r.returncode != 0

def test_failed_binding_does_not_call_formal_gatekeeper():
    r = _run(_mismatch("research_id","BAD"), BUNDLE_PATH, OUT_DIR / "_b_nogk.json")
    d = json.loads((OUT_DIR / "_b_nogk.json").read_text())
    assert d["gatekeeper_result"] is None
    assert d["hardlock_verdict"] is None

def test_validation_output_contains_report_and_bundle_hashes():
    r = _run(BOUND_REPORT, BUNDLE_PATH, OUT_DIR / "_b_hashes.json")
    d = json.loads((OUT_DIR / "_b_hashes.json").read_text())
    assert len(d["bundle_sha256"]) == 64
    assert len(d["report_sha256"]) == 64
    assert "artifact_hashes" in d


# ═══ Phase 3C.1: transitive hash tests (recovered) ════════════════════

def _copy_bundle_to_tmp():
    tmp = Path(tempfile.mkdtemp())
    for f in ["research_bundle.json","synthetic_data_cards.json","synthetic_industry_fields.json"]:
        shutil.copy(ROOT/"examples/full_chain_sample"/f, tmp/f)
    return tmp

def test_data_cards_content_change_changes_bundle_hash():
    from scripts.validate_agent_report import compute_bundle_hash, load_bundle
    tmp = _copy_bundle_to_tmp()
    h1 = compute_bundle_hash(load_bundle(tmp/"research_bundle.json"))
    cards = json.loads((tmp/"synthetic_data_cards.json").read_text())
    cards[0]["value"] = "999.99"
    (tmp/"synthetic_data_cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2))
    h2 = compute_bundle_hash(load_bundle(tmp/"research_bundle.json"))
    assert h1 != h2

def test_industry_fields_content_change_changes_bundle_hash():
    from scripts.validate_agent_report import compute_bundle_hash, load_bundle
    tmp = _copy_bundle_to_tmp()
    h1 = compute_bundle_hash(load_bundle(tmp/"research_bundle.json"))
    ind = json.loads((tmp/"synthetic_industry_fields.json").read_text())
    ind["fields"]["mcr_or_mlr"]["notes"] = "CHANGED"
    (tmp/"synthetic_industry_fields.json").write_text(json.dumps(ind, ensure_ascii=False, indent=2))
    h2 = compute_bundle_hash(load_bundle(tmp/"research_bundle.json"))
    assert h1 != h2

def test_unchanged_bundle_is_hash_stable():
    from scripts.validate_agent_report import compute_bundle_hash, load_bundle
    h1 = compute_bundle_hash(load_bundle(BUNDLE_PATH))
    h2 = compute_bundle_hash(load_bundle(BUNDLE_PATH))
    assert h1 == h2

def test_absolute_artifact_path_is_rejected():
    from scripts.validate_agent_report import compute_bundle_hash
    import pytest
    b = json.loads(BUNDLE_PATH.read_text())
    b["data_cards"]["path"] = "/etc/passwd"
    b["_bundle_dir"] = str(BUNDLE_PATH.parent)
    with pytest.raises(ValueError, match="absolute"):
        compute_bundle_hash(b)

def test_parent_path_escape_is_rejected():
    from scripts.validate_agent_report import compute_bundle_hash
    import pytest
    b = json.loads(BUNDLE_PATH.read_text())
    b["data_cards"]["path"] = "../../../etc/passwd"
    b["_bundle_dir"] = str(BUNDLE_PATH.parent)
    with pytest.raises(ValueError, match="escapes"):
        compute_bundle_hash(b)

def test_missing_artifact_file_fails():
    from scripts.validate_agent_report import compute_bundle_hash
    import pytest
    b = json.loads(BUNDLE_PATH.read_text())
    b["data_cards"]["path"] = "nonexistent.json"
    b["_bundle_dir"] = str(BUNDLE_PATH.parent)
    with pytest.raises(FileNotFoundError):
        compute_bundle_hash(b)


# ═══ Phase 3D: source policy + adapter tests (recovered) ══════════════

def test_s_tier_full_current_no_conflict_passes():
    from tools.source_policy import check_source_admission
    sp = check_source_admission(_base_card(source_tier="S"))
    assert sp.can_enter_conclusion

def test_a_tier_full_current_no_conflict_passes():
    from tools.source_policy import check_source_admission
    sp = check_source_admission(_base_card(source_tier="A"))
    assert sp.can_enter_conclusion

def test_b_tier_full_is_rejected():
    from tools.source_policy import check_source_admission
    sp = check_source_admission(_base_card(source_tier="B", can_enter_conclusion="full"))
    assert not sp.can_enter_conclusion

def test_b_tier_reference_only_is_allowed():
    from tools.source_policy import check_source_admission
    sp = check_source_admission(_base_card(source_tier="B", can_enter_conclusion="reference_only"))
    assert sp.effective_permission == "reference_only"

def test_c_tier_full_is_rejected():
    from tools.source_policy import check_source_admission
    sp = check_source_admission(_base_card(source_tier="C", can_enter_conclusion="full"))
    assert not sp.can_enter_conclusion

def test_stale_high_tier_cannot_enter_formal():
    from tools.source_policy import check_source_admission
    sp = check_source_admission(_base_card(source_tier="A", freshness_status="stale"))
    assert not sp.can_enter_conclusion

def test_conflicting_high_tier_cannot_enter_formal():
    from tools.source_policy import check_source_admission
    sp = check_source_admission(_base_card(source_tier="A", has_conflict=True))
    assert not sp.can_enter_conclusion

def test_data_card_schema_accepts_s_tier():
    from tools.data_card_registry import validate_data_card
    r = validate_data_card(_base_card(source_tier="S"))
    assert r.status == "PASS_FORMAL"

def test_source_audit_and_data_card_use_same_policy():
    from tools.source_policy import ALLOWED_SOURCE_TIERS as P
    from tools.data_card_registry import ALLOWED_SOURCE_TIERS as D
    from tools.tool_metadata_guard import ALLOWED_SOURCE_TIERS as T
    from tools.source_audit import ALLOWED_SOURCE_TIERS as S
    assert P == D == T == S

def test_synthetic_bundle_returns_pass_test_only():
    from scripts.validate_agent_report import load_bundle, build_hardlock_from_bundle
    hl = build_hardlock_from_bundle(load_bundle(BUNDLE_PATH))
    assert hl["status"] == "PASS_TEST_ONLY"

def test_synthetic_bundle_is_never_formal_releasable():
    from scripts.validate_agent_report import load_bundle, build_hardlock_from_bundle
    hl = build_hardlock_from_bundle(load_bundle(BUNDLE_PATH))
    assert hl["status"] != "PASS_FORMAL"

def test_synthetic_production_locked():
    r = _run(BOUND_REPORT, BUNDLE_PATH, OUT_DIR / "_b_lock.json")
    d = json.loads((OUT_DIR / "_b_lock.json").read_text())
    assert d["production_research_eligible"] is False
    assert d["account_action"] == "LOCKED"

def test_revenue_consistency():
    cards = json.loads((ROOT/"examples/full_chain_sample/synthetic_data_cards.json").read_text())
    t, s = None, {}
    for c in cards:
        if c["field_name"]=="revenue_ttm": t=int(c["value"])
        elif c["field_name"] in ("revenue_insurance","revenue_health_services","revenue_pharmacy"):
            s[c["field_name"]]=int(c["value"])
    assert t and sum(s.values())==t

def test_macro_synthetic():
    b = json.loads(BUNDLE_PATH.read_text())
    assert b["macro_factors"]["data_provenance"]=="SYNTHETIC_FIXTURE"
    for _,f in b["macro_factors"]["factors"].items(): assert "SYNTHETIC" in f["source"]


# ═══ Phase 3D behavior: real-missing still blocked (recovered) ═══════

def test_real_missing_price_still_fails_gatekeeper():
    """Unbound report with rule text + no hardlock → still fails legacy check."""
    from tools.report_gatekeeper import check_report
    old_report = UNBOUND_REPORT.read_text()
    r = check_report(old_report, mode="formal", language="zh", hardlock_verdict=None)
    assert r["final_status"] == "FAIL_DATA_HARDLOCK"

def test_structured_hardlock_fail_still_blocks():
    from tools.report_gatekeeper import check_report
    report = BOUND_REPORT.read_text()
    hl = {"status": "FAIL_DATA_HARDLOCK", "violations": ["missing"]}
    r = check_report(report, mode="formal", language="zh", hardlock_verdict=hl)
    assert r["final_status"] == "FAIL_DATA_HARDLOCK"


# ═══ Phase 3D.3: permission violation — non-critical fields (5 tests) ═══

def test_noncritical_b_full_returns_fail_source_permission():
    """B-tier requesting full on a non-critical field → FAIL_SOURCE_PERMISSION."""
    from tools.source_policy import check_source_admission
    card = _base_card(field_name="gross_margin", source_tier="B", can_enter_conclusion="full")
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion
    assert "B-tier cannot request full" in " ".join(sp.violations)

def test_noncritical_c_full_returns_fail_source_permission():
    """C-tier requesting full on a non-critical field → FAIL_SOURCE_PERMISSION."""
    from tools.source_policy import check_source_admission
    card = _base_card(field_name="gross_margin", source_tier="C", can_enter_conclusion="full")
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion
    assert "C-tier cannot request full" in " ".join(sp.violations)

def test_noncritical_d_full_returns_fail_source_permission():
    """D-tier requesting full on a non-critical field → FAIL_SOURCE_PERMISSION."""
    from tools.source_policy import check_source_admission
    card = _base_card(field_name="gross_margin", source_tier="D", can_enter_conclusion="full")
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion
    assert "D-tier cannot enter conclusion" in " ".join(sp.violations)

def test_noncritical_d_reference_only_returns_fail_source_permission():
    """D-tier requesting reference_only on a non-critical field → FAIL_SOURCE_PERMISSION."""
    from tools.source_policy import check_source_admission
    card = _base_card(field_name="gross_margin", source_tier="D", can_enter_conclusion="reference_only")
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion
    assert "D-tier cannot enter conclusion" in " ".join(sp.violations)

def test_noncritical_d_blocked_is_recordable():
    """D-tier blocked on non-critical field → recordable, but not conclusion-eligible."""
    from tools.source_policy import check_source_admission
    card = _base_card(field_name="gross_margin", source_tier="D", can_enter_conclusion="blocked")
    sp = check_source_admission(card)
    assert "D-tier cannot enter conclusion" not in " ".join(sp.violations)
    assert not sp.can_enter_conclusion
    assert sp.effective_permission == "blocked"


# ═══ Phase 3D.3: metadata guard required fields (2 tests) ═══

def test_metadata_missing_freshness_cannot_pass_formal():
    """Missing freshness_status in metadata → cannot PASS_FORMAL."""
    from tools.tool_metadata_guard import evaluate_tool_metadata
    meta = {"basis": "gaap", "period": "FY2025", "source_tier": "S", "can_enter_conclusion": "full"}
    v = evaluate_tool_metadata(meta)
    assert v.status != "PASS_FORMAL"

def test_metadata_missing_conflict_cannot_pass_formal():
    """Missing has_conflict in metadata → cannot PASS_FORMAL."""
    from tools.tool_metadata_guard import evaluate_tool_metadata
    meta = {"basis": "gaap", "period": "FY2025", "source_tier": "S", "can_enter_conclusion": "full",
            "freshness_status": "current"}
    v = evaluate_tool_metadata(meta)
    assert v.status != "PASS_FORMAL"


# ═══ Phase 3D.4: final contract cleanup (3 tests) ═══

def test_invalid_freshness_status_cannot_enter_formal():
    """freshness_status='invalid' must be rejected — only current/stale/unknown allowed."""
    from tools.source_policy import check_source_admission
    card = _base_card(source_tier="S", freshness_status="invalid")
    sp = check_source_admission(card)
    assert not sp.can_enter_conclusion

def test_valuation_denominator_field_requires_full_permission():
    """valuation_denominator as a critical field requires full permission from S/A-tier card."""
    from tools.source_policy import check_source_admission
    # Non-critical field with B-tier → should be allowed as reference_only
    # But valuation_denominator is a critical field → must have full permission
    card = _base_card(field_name="valuation_denominator", source_tier="B", can_enter_conclusion="reference_only")
    sp = check_source_admission(card)
    assert not sp.can_enter_primary_valuation
    assert "critical field" in " ".join(sp.violations) or "valuation_denominator" in " ".join(sp.violations)
