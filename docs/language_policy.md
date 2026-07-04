# Report Language Policy / 报告语言策略

Meridian Research Engine 2.0 `v2.0.0-beta` must generate reports in one language at a time. The final report must not mix Chinese and English section headings.

Meridian Research Engine 2.0的正式报告必须根据使用者语言生成单一语言版本，不允许出现中英文标题混排。

## 1. Language detection / 语言识别

Use the user's request language as the default report language.

- If the request is primarily Chinese, use Chinese.
- If the request is primarily English, use English.
- If the user explicitly specifies a language, that explicit choice overrides auto-detection.
- If the request is mixed, use the language of the actual report instruction, not the ticker name, company name, file path, command name, or quoted source text.

Examples:

```text
按Meridian Research Engine 2.0完整分析 SAMPLE
=> Chinese report

Run a complete Meridian Research Engine 2.0 report on SAMPLE
=> English report

请用英文输出 SAMPLE 完整报告
=> English report

Please generate the report in Chinese
=> Chinese report
```

## 2. Template selection / 模板选择

Do not fill `templates/standard_research_report.md` directly. It is a selector file.

Use one of the language-specific templates:

```text
templates/standard_research_report_zh.md  # Chinese report
templates/standard_research_report_en.md  # English report
```

Recommended file naming:

```text
reports/TICKER_research_report_zh.md
reports/TICKER_research_report_en.md
```

Word and PDF exports should preserve the same language:

```text
reports/TICKER_research_report_zh.docx
reports/TICKER_research_report_zh.pdf
reports/TICKER_research_report_en.docx
reports/TICKER_research_report_en.pdf
```

## 3. No mixed headings / 禁止标题混排

A final report must not use bilingual headings such as:

```text
## One-sentence conclusion / 一句话结论
## Report Gatekeeper / 报告准出状态
## Valuation and margin of safety / 估值与安全边际
```

Use Chinese headings in Chinese reports:

```text
## 一句话结论
## 报告准出状态
## 估值与安全边际
```

Use English headings in English reports:

```text
## One-sentence conclusion
## Report gatekeeper
## Valuation and margin of safety
```

## 4. Allowed exceptions / 允许保留的英文内容

The following may remain in English even inside a Chinese report:

- stock tickers, file names, command names, paths, and code;
- product/module names such as `Price Level Engine`, `Report Gatekeeper`, `GitHub Actions`;
- original source names, company names, and cited titles;
- formulas and CLI examples.

The following should be translated according to the report language:

- section headings;
- table column names;
- explanation paragraphs;
- gatekeeper conclusions;
- final action framework;
- review triggers.

## 5. Gatekeeper rule / 准出规则

Before a report is considered ready:

1. Select report language.
2. Use the matching language template.
3. Do not use bilingual section headings.
4. Run the report gatekeeper with the selected language.

Examples:

```bash
python tools/report_gatekeeper.py reports/SAMPLE_research_report_zh.md --language zh
python tools/report_gatekeeper.py reports/SAMPLE_research_report_en.md --language en
```

`--language auto` is allowed, but explicit language is preferred in automated workflows.
