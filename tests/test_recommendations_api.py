from fastapi.testclient import TestClient

from src.phase_2_retrieval.main import app


def test_recommendations_query_success() -> None:
    client = TestClient(app)
    response = client.post(
        "/recommendations/query",
        json={
            "location": "Bangalore",
            "max_budget": 1200,
            "cuisine": "North Indian",
            "min_rating": 4.0,
            "limit": 3,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "applied_filters" in data
    assert isinstance(data["recommendations"], list)


def test_recommendations_query_validation() -> None:
    client = TestClient(app)
    response = client.post(
        "/recommendations/query",
        json={
            "location": " ",
            "limit": 0,
        },
    )

    assert response.status_code == 422
