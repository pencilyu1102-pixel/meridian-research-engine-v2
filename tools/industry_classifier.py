"""Industry adapter classifier for Meridian Research Engine 2.0.
Classifies companies into the appropriate industry adapter based on
business description, sector, and revenue breakdown.
"""

from __future__ import annotations

import argparse
import re
from typing import Any

# ── Keyword patterns for each adapter ─────────────────────────────────

ADAPTER_SIGNATURES: list[tuple[str, str, list[str], list[str], list[str]]] = [
    (
        "半导体·硬件·制造",
        "Semiconductor/Hardware/Manufacturing",
        [
            "semiconductor", "chip", "processor", "gpu", "asic", "fpga",
            "硬件", "芯片", "半导体", "制造", "foundry", "晶圆",
            "wafer", "设备", "设备制造", "electronics manufacturing",
            "pcb", "电路板", "封装", "assembly", "test",
        ],
        [
            "shipment", "unit", "ASP", "yield", "capacity", "fab",
            "产能", "良率", "出货量", "制程", "工艺",
        ],
        [
            "same-store sales", "SSSG", "NIM", "deposit", "贷款",
        ],
    ),
    (
        "软件·SaaS·云服务",
        "Software/SaaS/Cloud",
        [
            "software", "saas", "cloud", "subscription", "ARR", "MRR",
            "软件", "云", "订阅", "平台即服务", "paas", "iaas",
            "erp", "crm", "database", "devops", "api",
        ],
        [
            "ARR", "RPO", "NRR", "churn", "ARPU", "CAC", "LTV",
            "Rule of 40", "FCF margin", "gross margin", "retention",
        ],
        [
            "NIM", "NPL", "不良率", "same-store", "commodity price",
        ],
    ),
    (
        "互联网平台·广告·电商",
        "Internet Platform/Ad/E-commerce",
        [
            "internet", "platform", "advertising", "e-commerce", "ecommerce",
            "social media", "search", "marketplace", "user generated",
            "互联网", "平台", "广告", "电商", "社交", "搜索",
            "短视频", "直播", "feed", "recommendation",
        ],
        [
            "DAU", "MAU", "GMV", "take rate", "ARPU", "CPM", "CPC",
            "用户", "月活", "日活", "变现率", "佣金",
        ],
        [
            "NIM", "deposit", "yield", "产能", "inventory turnover",
        ],
    ),
    (
        "消费·零售·奢侈品",
        "Consumer/Retail/Luxury",
        [
            "retail", "consumer", "luxury", "brand", "apparel", "beverage",
            "food", "restaurant", "store", "fashion",
            "消费", "零售", "品牌", "白酒", "饮料", "食品",
            "服装", "门店", "加盟", "快消", "FMCG",
        ],
        [
            "SSSG", "same-store", "comparable store", "store count",
            "同店", "门店数", "客流", "客单价", "复购率",
        ],
        [
            "fab", "wafer", "yield", "ARR", "NIM", "不良率",
        ],
    ),
    (
        "周期·能源·原材料",
        "Cyclicals/Energy/Commodities",
        [
            "oil", "gas", "energy", "coal", "mining", "commodity",
            "chemical", "steel", "aluminum", "copper", "lithium",
            "石油", "煤炭", "能源", "矿产", "化工", "钢铁",
            "有色金属", "锂", "航运", "shipping",
        ],
        [
            "commodity price", "cost curve", "production volume",
            "unit cost", "inventory cycle", "产能", "产量", "成本曲线",
        ],
        [
            "ARR", "DAU", "SSSG", "NIM",
        ],
    ),
    (
        "银行·保险·金融",
        "Banks/Insurance/Financials",
        [
            "bank", "insurance", "broker", "financial", "asset management",
            "证券", "银行", "保险", "金融", "券商", "投资",
            "wealth management", "lending", "deposit",
        ],
        [
            "NIM", "净息差", "NPL", "不良率", "拨备", "credit cost",
            "ROE", "capital adequacy", "偿付能力", "AUM",
        ],
        [
            "SSSG", "fab", "chip", "ARR", "churn",
        ],
    ),
    (
        "医药·生物科技",
        "Pharma/Biotech",
        [
            "pharma", "biotech", "drug", "therapeutic", "vaccine",
            "clinical", "oncology", "antibody",
            "医药", "制药", "生物", "临床", "创新药", "CXO",
            "CRO", "CDMO", "医疗器械",
        ],
        [
            "pipeline", "clinical trial", "patent", "rNPV",
            "管线", "临床试验", "专利", "适应症", "TAM",
        ],
        [
            "NIM", "fab", "yield", "commodity price",
        ],
    ),
    (
        "公用事业·REITs·基础设施",
        "Utilities/REITs/Infrastructure",
        [
            "utility", "power", "electric", "water", "gas utility",
            "REIT", "real estate investment trust", "infrastructure",
            "toll road", "pipeline",
            "公用事业", "电力", "水务", "燃气", "公路", "REITs",
            "基础设施", "光伏运营",
        ],
        [
            "NOI", "FFO", "cap rate", "occupancy", "rental",
            "出租率", "租金", "分红率", "regulatory",
        ],
        [
            "fab", "chip", "DAU", "SSSG", "pipeline",
        ],
    ),
]


def classify(
    company: str = "",
    description: str = "",
    sector: str = "",
    primary_revenue_segment: str = "",
) -> dict[str, Any]:
    """Classify company into primary and secondary industry adapters."""
    combined = f"{company} {description} {sector} {primary_revenue_segment}".lower()

    scores: list[tuple[str, str, int, list[str], list[str]]] = []
    for (
        cn_name,
        en_name,
        keywords,
        relevant_metrics,
        not_applicable,
    ) in ADAPTER_SIGNATURES:
        score = 0
        matched = []
        for kw in keywords:
            found = len(re.findall(re.escape(kw), combined))
            if found:
                score += found * 3
                matched.append(kw)
        for kw in relevant_metrics:
            if kw.lower() in combined:
                score += 2

        # Penalty for mismatched terms
        for kw in not_applicable:
            if kw.lower() in combined:
                score -= 5

        if score > 0:
            scores.append((cn_name, en_name, score, matched, relevant_metrics))

    scores.sort(key=lambda x: x[2], reverse=True)

    if not scores:
        return {
            "primary_industry_adapter": "未确定",
            "secondary_industry_adapter": "未确定",
            "confidence": "low",
            "reason": "无法根据提供的信息确定行业适配器。请提供更详细的业务描述、行业分类或营收构成。",
            "required_metrics": [],
            "not_applicable_metrics": [],
        }

    primary = scores[0]
    secondary = scores[1] if len(scores) > 1 else None

    # Confidence based on score difference
    if primary[2] >= 10 and (not secondary or primary[2] - secondary[2] >= 5):
        confidence = "high"
    elif primary[2] >= 5:
        confidence = "medium"
    else:
        confidence = "low"

    reason_parts = []
    if primary[3]:
        reason_parts.append(
            f"匹配关键词：{', '.join(primary[3][:5])}"
        )
    reason_parts.append(f"得分：{primary[2]}")

    # Determine metrics
    _, _, _, relevant, _ = ADAPTER_SIGNATURES[
        next(i for i, (cn, en, *_) in enumerate(ADAPTER_SIGNATURES) if cn == primary[0])
    ]
    _, _, _, _, na_metrics = ADAPTER_SIGNATURES[
        next(i for i, (cn, en, *_) in enumerate(ADAPTER_SIGNATURES) if cn == primary[0])
    ]

    result: dict[str, Any] = {
        "primary_industry_adapter": primary[0] + " / " + primary[1],
        "secondary_industry_adapter": (
            secondary[0] + " / " + secondary[1] if secondary else "None"
        ),
        "confidence": confidence,
        "reason": "；".join(reason_parts),
        "required_metrics": relevant[:8],
        "not_applicable_metrics": na_metrics[:5],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Industry Adapter Classifier for Meridian Research Engine 2.0"
    )
    parser.add_argument("--company", default="", help="Company name")
    parser.add_argument(
        "--description", default="", help="Business description"
    )
    parser.add_argument("--sector", default="", help="Sector classification")
    parser.add_argument(
        "--primary-revenue-segment",
        default="",
        help="Primary revenue driver (e.g. cloud, advertising, hardware)",
    )
    args = parser.parse_args()

    result = classify(
        company=args.company,
        description=args.description,
        sector=args.sector,
        primary_revenue_segment=args.primary_revenue_segment,
    )

    lines = [
        "# Industry Adapter Classification Result",
        "",
        f"Primary: {result['primary_industry_adapter']}",
        f"Secondary: {result['secondary_industry_adapter']}",
        f"Confidence: {result['confidence']}",
        f"Reason: {result['reason']}",
    ]
    if result["required_metrics"]:
        lines.extend(["", "Required metrics:"])
        lines.extend(f"- {m}" for m in result["required_metrics"])
    if result["not_applicable_metrics"]:
        lines.extend(["", "Not applicable metrics:"])
        lines.extend(f"- {m}" for m in result["not_applicable_metrics"])

    print("\n".join(lines))


if __name__ == "__main__":
    main()
