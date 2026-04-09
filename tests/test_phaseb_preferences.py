from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_3_llm.service_llm_recommender import _build_user_prompt


def test_additional_preferences_accepts_list_and_dedups() -> None:
    req = RecommendationQueryRequest(
        location="Bangalore",
        additional_preferences=["Date", "date", "quick service"],
        limit=3,
    )
    assert req.additional_preferences == ["date", "quick service"]


def test_prompt_contains_normalized_preference_tags() -> None:
    req = RecommendationQueryRequest(
        location="Bangalore",
        additional_preferences=["date", "group friendly"],
        limit=2,
    )
    prompt = _build_user_prompt(request=req, candidates=[])
    assert '"preference_tags"' in prompt
    assert "romantic" in prompt
    assert "group-friendly" in prompt
