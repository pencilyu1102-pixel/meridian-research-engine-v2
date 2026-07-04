# Report Export / 报告导出说明

Meridian Research Engine 2.0 uses Markdown as the canonical report source in the `v2.0.0-beta` initial release. Word and PDF are delivery formats.

Meridian Research Engine 2.0默认以 Markdown 作为标准报告源文件，Word / PDF 是交付层格式，而不是研究源文件。

## Language rule / 语言规则

Reports must be generated in one language at a time.

- Chinese request -> Chinese report source -> Chinese Word / PDF.
- English request -> English report source -> English Word / PDF.
- Explicit language request overrides auto-detection.
- Do not export bilingual-heading reports.

Use language-specific templates:

```text
templates/standard_research_report_zh.md
templates/standard_research_report_en.md
```

`templates/standard_research_report.md` is only a selector file and should not be filled as a final report.

See also:

```text
docs/language_policy.md
```

## Why Markdown first? / 为什么先用 Markdown？

Markdown is used as the source format because it is:

- easier to version-control in Git;
- easier to review in pull requests;
- easier to diff when assumptions or data change;
- easier for AI agents and scripts to fill consistently;
- safer for open-source examples because private account data can be kept out.

Word and PDF exports should be generated only after the report passes Gatekeeper v2.1.

## Chinese report workflow / 中文报告流程

```bash
mkdir -p reports
cp templates/standard_research_report_zh.md reports/SAMPLE_research_report_zh.md
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
pandoc reports/SAMPLE_research_report_zh.md -o reports/SAMPLE_research_report_zh.docx
```

Export PDF from Word / WPS, or use Pandoc if a PDF engine is available:

```bash
pandoc reports/SAMPLE_research_report_zh.md \
  --pdf-engine=xelatex \
  -o reports/SAMPLE_research_report_zh.pdf
```

Chinese PDF export may require local Chinese fonts and a LaTeX engine.

## English report workflow / 英文报告流程

```bash
mkdir -p reports
cp templates/standard_research_report_en.md reports/SAMPLE_research_report_en.md
python tools/report_gatekeeper.py reports/SAMPLE_research_report_en.md --language en
pandoc reports/SAMPLE_research_report_en.md -o reports/SAMPLE_research_report_en.docx
```

Export PDF from Word / WPS, or use Pandoc if a PDF engine is available:

```bash
pandoc reports/SAMPLE_research_report_en.md \
  --pdf-engine=xelatex \
  -o reports/SAMPLE_research_report_en.pdf
```

## Optional Word style reference / 可选 Word 样式

If you have a Word reference style file:

```bash
pandoc reports/SAMPLE_research_report_zh.md \
  --reference-doc templates/report_style_reference.docx \
  -o reports/SAMPLE_research_report_zh.docx
```

If `templates/report_style_reference.docx` does not exist, use the basic command first.

## Recommended output hierarchy / 推荐输出层级

```text
reports/
├── SAMPLE_research_report_zh.md      # Chinese source of truth
├── SAMPLE_research_report_zh.docx    # Chinese Word delivery version
├── SAMPLE_research_report_zh.pdf     # Chinese PDF delivery version
├── SAMPLE_research_report_en.md      # English source of truth
├── SAMPLE_research_report_en.docx    # English Word delivery version
└── SAMPLE_research_report_en.pdf     # English PDF delivery version
```

## Rules before export / 导出前规则

Before exporting to Word or PDF:

- select one report language;
- use the matching language template;
- run `python tools/report_gatekeeper.py <report.md> --language zh` or `--language en`;
- check data source, date, unit, currency, and confidence level;
- remove private account screenshots, real cost basis, and private transaction records from public examples;
- keep output clearly marked as research workflow material, not investment advice.

## Future work / 后续计划

A future version may add a dedicated export command, for example:

```bash
python tools/export_report.py reports/SAMPLE_research_report_zh.md --format docx
python tools/export_report.py reports/SAMPLE_research_report_en.md --format pdf
```

For now, Markdown is the standard source format and Pandoc / office software is the recommended export path.
