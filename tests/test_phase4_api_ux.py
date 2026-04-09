from fastapi.testclient import TestClient

from src.phase_2_retrieval.main import app
from src.phase_3_llm.model_llm_recommendation import LLMRankedItem


def test_metadata_locations_returns_values() -> None:
    client = TestClient(app)
    response = client.get("/metadata/locations")
    assert response.status_code == 200
    data = response.json()
    assert "locations" in data
    assert isinstance(data["locations"], list)
    assert "top_cuisines" in data
    assert "top_experiences" in data
    assert isinstance(data["top_cuisines"], list)
    assert isinstance(data["top_experiences"], list)
    if data["top_cuisines"]:
        assert {"value", "label", "count"}.issubset(data["top_cuisines"][0].keys())


def test_recommendations_response_schema_with_mocked_llm(monkeypatch) -> None:
    from src.phase_0_foundation.core_config import settings
    from src.phase_4_api_ux import service_api_ux

    monkeypatch.setattr(settings, "groq_api_key", "dummy-key")

    def _fake_rank_candidates_with_llm(*, request, candidates, client):  # type: ignore[no-untyped-def]
        _ = request
        _ = client
        return [
            LLMRankedItem(
                restaurant_id=candidates[0].restaurant_id,
                restaurant_name=candidates[0].restaurant_name,
                ai_explanation="Mocked explanation.",
                llm_rank=1,
            ),
            LLMRankedItem(
                restaurant_id=candidates[0].restaurant_id,
                restaurant_name=candidates[0].restaurant_name,
                ai_explanation="Duplicate mocked explanation.",
                llm_rank=2,
            ),
        ]

    monkeypatch.setattr(service_api_ux, "rank_candidates_with_llm", _fake_rank_candidates_with_llm)

    client = TestClient(app)
    response = client.post(
        "/recommendations",
        json={"location": "Bangalore", "max_budget": 1200, "cuisine": "Italian", "limit": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "applied_filters" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) == 1
    row = data["recommendations"][0]
    expected_keys = {
        "restaurant_id",
        "restaurant_name",
        "cuisine",
        "rating",
        "estimated_cost",
        "ai_explanation",
    }
    assert set(row.keys()) == expected_keys
    assert "fit_score" not in row
