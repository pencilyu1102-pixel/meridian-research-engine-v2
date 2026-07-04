from decimal import Decimal

import pytest

from tools.macro_score import calculate_macro_score, classify_macro_state


def test_macro_score_calculates_total_and_state():
    score = calculate_macro_score(
        {
            "growth": "1",
            "inflation": "0",
            "liquidity": "1",
            "credit": "0",
            "earnings": "1",
            "risk": "0",
        }
    )

    assert score.total_score == Decimal("3")
    assert score.normalized_score == Decimal("62.50")
    assert score.macro_state == "中性偏观察"


def test_macro_score_all_positive_factors_are_100():
    score = calculate_macro_score(
        {
            "growth": "2",
            "inflation": "2",
            "liquidity": "2",
            "credit": "2",
            "earnings": "2",
            "risk": "2",
        }
    )

    assert score.total_score == Decimal("12")
    assert score.normalized_score == Decimal("100.00")
    assert score.macro_state == "宏观强顺风"


def test_macro_score_all_negative_factors_are_zero():
    score = calculate_macro_score(
        {
            "growth": "-2",
            "inflation": "-2",
            "liquidity": "-2",
            "credit": "-2",
            "earnings": "-2",
            "risk": "-2",
        }
    )

    assert score.total_score == Decimal("-12")
    assert score.normalized_score == Decimal("0.00")
    assert score.macro_state == "宏观强逆风"


def test_macro_score_neutral_factors_are_50():
    score = calculate_macro_score(
        {
            "growth": "0",
            "inflation": "0",
            "liquidity": "0",
            "credit": "0",
            "earnings": "0",
            "risk": "0",
        }
    )

    assert score.total_score == Decimal("0")
    assert score.normalized_score == Decimal("50.00")
    assert score.macro_state == "中性偏观察"


def test_macro_score_classification_thresholds():
    assert classify_macro_state("80") == "宏观强顺风"
    assert classify_macro_state("65") == "宏观偏顺风"
    assert classify_macro_state("50") == "中性偏观察"
    assert classify_macro_state("35") == "宏观偏逆风"
    assert classify_macro_state("34.99") == "宏观强逆风"


def test_macro_score_rejects_out_of_range_factor():
    with pytest.raises(ValueError):
        calculate_macro_score(
            {
                "growth": "3",
                "inflation": "0",
                "liquidity": "0",
                "credit": "0",
                "earnings": "0",
                "risk": "0",
            }
        )
