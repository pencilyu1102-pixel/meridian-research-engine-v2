# 全链路离线 Demo 示例

本目录包含离线全链路演示的虚构输入数据。所有数据均为合成 Fixture，不包含真实公司、真实价格或真实投资建议。

## 文件说明

- `synthetic_data_cards.json` — 虚构数据卡片（8 个关键字段）
- `synthetic_industry_fields.json` — 虚构行业硬字段（US_MANAGED_CARE，11 个必填字段）
- `README.md` — 本文件

## 运行 Demo

```bash
cd meridian-research-engine-v2
python scripts/run_demo.py
```

Demo 无需 API Key，无需联网，结果可重复。

## 输出

- `outputs/demo/SAMPLE_full_chain_report_zh.md` — 虚构研究报告
- `outputs/demo/SAMPLE_full_chain_result.json` — 校核结果

## 研究标识

研究对象为虚构标识 **SAMPLE_MANAGED_CARE**，不代表任何真实公司。
