from src.phase_5_evaluation.service_evaluation import (
    _percentile,
    _score_explanation_quality,
    _score_relevance,
)


def test_percentile_basic() -> None:
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert _percentile(values, 50) == 30.0
    assert _percentile(values, 95) >= 40.0


def test_relevance_score_bounds() -> None:
    query = {"cuisine": "Italian", "budget": "medium", "min_rating": 4.0}
    rec = {"cuisine": "Italian, Pizza", "estimated_cost": 900, "rating": 4.2}
    score = _score_relevance(query, rec)
    assert 0.0 <= score <= 5.0
    assert score >= 4.0


def test_explanation_quality_scoring() -> None:
    assert _score_explanation_quality("") == 0.0
    assert _score_explanation_quality("short explanation") == 2.0
    text = "This explanation has enough words to be considered decent quality."
    assert _score_explanation_quality(text) >= 3.0
