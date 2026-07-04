# Quick Start and Usage / 快速开始与使用说明

This guide explains how to install, test, and run Meridian Research Engine 2.0 (经纬投研引擎 2.0) locally as the `v2.0.0-beta` initial release.

This project is a research workflow and data-audit aid. It is not financial advice, does not execute trades, and does not provide guaranteed outcomes.

## 1. Requirements / 环境要求

Recommended environment:

```bash
python --version
# Python 3.11 or later is recommended

git --version
```

## 2. Clone the repository / 克隆仓库

```bash
git clone https://github.com/pencilyu1102-pixel/meridian-research-engine-v2.git
cd meridian-research-engine-v2
```

For a private repository, make sure your GitHub account has access before cloning.

## 3. Create a virtual environment / 创建虚拟环境

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use:

```powershell
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies / 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 5. Run tests / 运行测试

```bash
python -m pytest -q
```

A clean run should show all tests passing.

## 6. Run core tools / 运行核心工具

### 6.1 Macro six-factor scoring / 宏观六因子评分

```bash
python tools/macro_score.py --growth 1 --inflation 0 --liquidity 1 --credit 0 --earnings 1 --risk 0
```

### 6.2 Price Level Engine / 点位精算引擎

```bash
python tools/price_level_engine.py --eps 10.00 --ticker SAMPLE --multiples 12,15,18,20
```

### 6.3 Portfolio cost / 持仓管理成本

```bash
python tools/portfolio_cost.py examples/transactions_example.csv --ticker ABC
```

This calculates aggregate management cost for portfolio review. It is not tax-lot accounting and is not FIFO / LIFO reporting.

### 6.4 Valuation scenario / 三情景估值

```bash
python tools/valuation_scenario.py --eps 10.00 --bear 12 --base 15 --bull 18
```

### 6.5 Gatekeeper v2.1 / 报告准出检查

Chinese report:

```bash
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
```

English report:

```bash
python tools/report_gatekeeper.py reports/SAMPLE_research_report_en.md --language en
```

The gatekeeper checks required sections, banned vague phrases, and bilingual headings.

## 7. Language selection / 语言选择

The final report must use one language at a time.

```text
Chinese user request -> use templates/standard_research_report_zh.md
English user request -> use templates/standard_research_report_en.md
Explicit language request -> follow the explicit language
```

Do not fill `templates/standard_research_report.md` directly. It is only a selector file.

See also:

```text
docs/language_policy.md
```

## 8. Standard report workflow / 标准报告工作流

Chinese report example:

```bash
mkdir -p reports
cp templates/standard_research_report_zh.md reports/SAMPLE_research_report_zh.md
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
```

English report example:

```bash
mkdir -p reports
cp templates/standard_research_report_en.md reports/SAMPLE_research_report_en.md
python tools/report_gatekeeper.py reports/SAMPLE_research_report_en.md --language en
```

## 9. Word / PDF export / Word 与 PDF 导出

See:

```text
docs/report_export.md
```

Chinese Word export:

```bash
pandoc reports/SAMPLE_research_report_zh.md -o reports/SAMPLE_research_report_zh.docx
```

English Word export:

```bash
pandoc reports/SAMPLE_research_report_en.md -o reports/SAMPLE_research_report_en.docx
```

PDF can be exported from Word / WPS, or generated with Pandoc if a PDF engine is available.

## 10. Public-project rules / 公开项目规则

When publishing or sharing outputs from this repository:

- Use `SAMPLE`, `TICKER`, or generic examples instead of personal holdings.
- Do not include real account screenshots, real cost basis, or private transaction records.
- Do not present model output as financial advice.
- Keep upstream MIT attribution in `LICENSE` and `NOTICE`.
- Keep this project clearly separated from the upstream AI Berkshire project.
- Keep final reports in one selected language; do not publish bilingual-heading reports.
