import sqlite3

from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_2_retrieval.service_retrieval import query_recommendations


def _make_test_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE restaurants_clean (
                restaurant_id TEXT,
                name TEXT,
                cuisines_text TEXT,
                rating REAL,
                avg_cost_for_two REAL,
                locality TEXT,
                location_city TEXT,
                votes INTEGER
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO restaurants_clean (
                restaurant_id, name, cuisines_text, rating,
                avg_cost_for_two, locality, location_city, votes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("r1", "Alpha", "Italian", 4.6, 1500, "Indiranagar", "Bangalore", 100),
                ("r2", "Beta", "Italian", 4.4, 1400, "Indiranagar", "Bangalore", 95),
                ("r3", "Gamma", "Italian", 4.1, 1300, "Indiranagar", "Bangalore", 90),
            ],
        )
        conn.commit()


def test_min_rating_not_relaxed_when_partial_results_exist(tmp_path) -> None:
    db_path = str(tmp_path / "restaurants.db")
    _make_test_db(db_path)

    response = query_recommendations(
        request=RecommendationQueryRequest(
            location="Bangalore",
            cuisine="Italian",
            min_rating=4.5,
            limit=5,
        ),
        db_path=db_path,
    )

    assert response.applied_filters.min_rating == 4.5
    assert "min_rating" not in response.applied_filters.relaxed_constraints
    assert response.recommendations
    assert all((row.rating or 0) >= 4.5 for row in response.recommendations)
