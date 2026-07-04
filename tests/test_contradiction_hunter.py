from tools.contradiction_hunter import find_banned_phrases


def test_contradiction_hunter_counts_each_banned_phrase():
    text = (
        "长期看好，短期波动。"
        "一方面，公司基本盘稳定；另一方面，估值合理，但需关注风险。"
    )

    findings = find_banned_phrases(text)

    assert len(findings) == 4
    assert "一方面" in findings
    assert "另一方面" in findings
