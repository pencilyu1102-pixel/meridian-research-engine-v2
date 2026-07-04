#!/usr/bin/env python3
"""
Meridian Research Engine 2.0 — Preflight Release Check
Run before every public release to verify the repository is safe to publish.

Usage:
    python scripts/preflight_release_check.py

Exit 0 = READY_FOR_HUMAN_REVIEW
Exit 1 = NOT_READY (blocking issues found)
"""

import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))

ERRORS: list[str] = []
WARNINGS: list[str] = []


def _run(cmd: list[str], label: str) -> str:
    """Run a command, return stdout. Raise SystemExit on failure."""
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        msg = (completed.stderr or completed.stdout or "unknown error").strip()
        raise SystemExit(f"Command failed: {label}\n{msg}")
    return (completed.stdout or "").strip()


def check(msg: str, ok: bool, severity: str = "error") -> None:
    """Record a check result."""
    if ok:
        print(f"  [PASS] {msg}")
    elif severity == "error":
        print(f"  [FAIL] {msg}")
        ERRORS.append(msg)
    else:
        print(f"  [WARN] {msg}")
        WARNINGS.append(msg)


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ═══════════════════════════════════════════════════════════
# 1. Forbidden paths
# ═══════════════════════════════════════════════════════════
section("1. Forbidden paths")

FORBIDDEN_PATHS = [
    "reports/archive_nonpublic",
    "reports/private",
    "data/private",
    "exports/private",
]

for fp in FORBIDDEN_PATHS:
    exists = (ROOT / fp).exists()
    check(f"Path absent: {fp}/", not exists)

# ═══════════════════════════════════════════════════════════
# 2. Sensitive keyword scan
# ═══════════════════════════════════════════════════════════
section("2. Sensitive keyword scan")

SENSITIVE_PATTERNS = [
    r"API.?KEY\s*=.",
    r"api.?key\s*=.",
    r"token\s*=.",
    r"password\s*=.",
    r"secret\s*=.",
    r"sk-[A-Za-z0-9]{20,}",
    r"ghp_[A-Za-z0-9]{36}",
    r"gho_[A-Za-z0-9]{36}",
    r"寒武纪",
    r"688256",
    r"META",
    r"MSFT",
    r"AMZN",
    r"UNH",
    r"IBKR",
    r"Interactive Brokers",
    r"真实持仓",
    r"真实成本",
    r"交易记录",
    r"目标价",
    r"account id",
    r"账户号",
    r"券商",
]

# Build grep command
grep_cmd = [
    "grep", "-RIn", 
    "-e", "API.?KEY.*=.",
    "-e", "api.?key.*=.",
    "-e", "token.*=.",
    "-e", "password.*=.",
    "-e", "secret.*=.",
    "-e", "sk-[A-Za-z0-9]",
    "-e", "ghp_",
    "-e", "gho_",
    "-e", "寒武纪",
    "-e", "688256",
    "-e", "META",
    "-e", "MSFT",
    "-e", "AMZN",
    "-e", "UNH",
    "-e", "IBKR",
    "-e", "Interactive Brokers",
    "-e", "真实持仓",
    "-e", "真实成本",
    "-e", "交易记录",
    "-e", "目标价",
    "-e", "account id",
    "-e", "账户号",
    "-e", "券商",
    "--exclude-dir=.git",
    "--exclude-dir=.venv",
    "--exclude-dir=__pycache__",
    "--exclude-dir=scripts",
    ".",
]

result = subprocess.run(grep_cmd, capture_output=True, text=True)
if result.returncode == 0 and result.stdout.strip():
    # Parse hits, exclude known false positives (disclaimers, template section names)
    hits = [line.strip() for line in result.stdout.split("\n") if line.strip()]
    # Allow these patterns in specific contexts:
    SAFE_CONTEXTS = [
        "真实持仓执行",           # Template/module heading
        "不展示真实个人持仓",      # Disclaimer language
        "不展示真实持仓",         # Disclaimer language
        "公开仓库不会展示真实",     # README privacy disclaimer
        "不得输出真实个人持仓",     # Workflow rule
        "不涉及真实持仓",         # Test disclaimer
        "不涉及真实交易记录",      # Test disclaimer  
        "真实持仓、持仓数量",      # Privacy boundary doc
        "真实持仓，需要结合账户",   # Audience description
        "判断真实持仓",           # Agent description table
        "Real holdings",          # Privacy boundary doc (English)
        "Real cost basis",        # Privacy boundary doc (English)
        "Real transaction records", # Privacy boundary doc (English)
        "不构成投资建议",          # Disclaimer
        "券商研报",               # Data tier label
        "交易记录示例",           # Example file label
        "验证CSV交易记录处理",     # Test description
        "不构成任何投资建议",      # Disclaimer
        "合规说明、免责声明",      # Compliance context
        ".env.example",           # Placeholder
        "!.env.example",          # .gitignore
        "Broker account IDs",     # Privacy boundary doc
        "券商账户号",             # Privacy boundary doc
        "不与任何券商",           # Disclaimer
        "也不是任何券商",         # Legal notice
        "grep -RniE",            # Privacy boundary doc examples
        "api_key|apikey|secret|token|password|bearer", # Privacy boundary doc examples
        "risk-appetite",          # CLI parameter name
        "证券\", \"银行\", \"保险\", \"金融\", \"券商\", \"投资\"", # Industry classifier keywords
    ]
    
    real_hits = []
    for h in hits:
        # Also skip files that are entirely compliance/disclaimer docs
        if any(skip in h for skip in [
            "docs/privacy_boundary.md",
            "docs/disclaimer.md", 
            "docs/legal_compliance.md",
            "NOTICE:",
        ]):
            if any(ctx in h for ctx in ["目标价", "券商", "真实", "交易记录", "成本"]):
                continue  # These are compliance docs, their matches are expected
        
        is_safe = any(safe_marker in h for safe_marker in SAFE_CONTEXTS)
        if not is_safe:
            real_hits.append(h)
    
    if real_hits:
        for h in real_hits:
            print(f"  [HIT] {h[:120]}")
        check("No sensitive keywords found (excluding disclaimers)", False)
    else:
        check("No sensitive keywords found (all matches are disclaimers)", True)
else:
    check("No sensitive keywords found", True)

# ═══════════════════════════════════════════════════════════
# 3. README: no specific company paths
# ═══════════════════════════════════════════════════════════
section("3. README: no specific company paths")

readme = (ROOT / "README.md").read_text()
readme_en = (ROOT / "README_EN.md").read_text()

has_688256 = "688256" in readme or "688256" in readme_en
has_cold_stone = "寒武纪" in readme or "寒武纪" in readme_en
has_archive = "archive_nonpublic" in readme or "archive_nonpublic" in readme_en

check("README contains no 688256", not has_688256)
check("README contains no 寒武纪 reference", not has_cold_stone)
check("README contains no archive_nonpublic reference", not has_archive)

# ═══════════════════════════════════════════════════════════
# 4. Run pytest
# ═══════════════════════════════════════════════════════════
section("4. pytest")

try:
    output = _run([sys.executable, "-m", "pytest", "-q"], "pytest")
    print(f"  {output}")
    check("pytest passed", True)
except SystemExit as e:
    check(f"pytest failed: {e}", False)
    ERRORS.append("pytest FAILED")

# ═══════════════════════════════════════════════════════════
# 5. Run test_comprehensive.py
# ═══════════════════════════════════════════════════════════
section("5. test_comprehensive.py")

try:
    output = _run([sys.executable, "test_comprehensive.py"], "test_comprehensive")
    # Parse output for pass/fail counts
    if "通过率: 100.0%" in output or "通过率: 100%" in output:
        print(f"  {output.split(chr(10))[-5:]}")
        check("test_comprehensive.py 100% pass", True)
    else:
        # Check for pass count
        for line in output.split("\n"):
            if "失败: 0" in line or "failed: 0" in line.lower():
                check("test_comprehensive.py passed (0 failures)", True)
                break
        else:
            check("test_comprehensive.py may have failures", False, "warn")
except SystemExit as e:
    check(f"test_comprehensive.py failed: {e}", False)
    ERRORS.append("test_comprehensive FAILED")

# ═══════════════════════════════════════════════════════════
# 6. Gatekeeper CLI
# ═══════════════════════════════════════════════════════════
section("6. Gatekeeper CLI")

SAMPLE_ZH = "reports/SAMPLE_research_report_zh.md"

try:
    output = _run(
        [sys.executable, "tools/report_gatekeeper.py", SAMPLE_ZH, "--language", "zh", "--mode", "formal"],
        "gatekeeper (positional)"
    )
    has_hardlock = "hardlock_gate:" in output
    has_template = "template_gate:" in output
    check("Gatekeeper positional arg: output contains hardlock_gate", has_hardlock)
    check("Gatekeeper positional arg: output contains template_gate", has_template)
except SystemExit as e:
    check(f"Gatekeeper positional arg failed: {e}", False)
    ERRORS.append("Gatekeeper CLI FAILED")

try:
    output2 = _run(
        [sys.executable, "tools/report_gatekeeper.py", "--file", SAMPLE_ZH, "--language", "zh", "--mode", "formal"],
        "gatekeeper (--file)"
    )
    has_hardlock2 = "hardlock_gate:" in output2
    check("Gatekeeper --file: output contains hardlock_gate", has_hardlock2)
except SystemExit as e:
    check(f"Gatekeeper --file failed: {e}", False)
    ERRORS.append("Gatekeeper --file CLI FAILED")

# ═══════════════════════════════════════════════════════════
# 7. Required files present
# ═══════════════════════════════════════════════════════════
section("7. Required files")

REQUIRED_FILES = [
    "README.md",
    "README_EN.md",
    "LICENSE",
    "NOTICE",
    "PRIVACY.md",
    "DISCLAIMER.md",
    ".env.example",
    ".gitignore",
    "docs/disclaimer.md",
    "docs/privacy_boundary.md",
    "docs/legal_compliance.md",
    ".github/workflows/tests.yml",
]

for rf in REQUIRED_FILES:
    exists = (ROOT / rf).exists()
    check(f"File present: {rf}", exists)

# ═══════════════════════════════════════════════════════════
# 8. Summary
# ═══════════════════════════════════════════════════════════
section("SUMMARY")

print(f"\n  Errors:   {len(ERRORS)}")
print(f"  Warnings: {len(WARNINGS)}")

if ERRORS:
    print("\n  BLOCKING ISSUES:")
    for e in ERRORS:
        print(f"    - {e}")

if WARNINGS:
    print("\n  Warnings:")
    for w in WARNINGS:
        print(f"    - {w}")

if ERRORS:
    print("\n  => NOT_READY")
    sys.exit(1)
else:
    print("\n  => READY_FOR_HUMAN_REVIEW")
    sys.exit(0)
