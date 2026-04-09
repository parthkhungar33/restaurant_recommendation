from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from src.phase_2_retrieval.main import app
from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_2_retrieval.service_retrieval import query_recommendations


def _seed_test_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
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
            INSERT INTO restaurants_clean
            (
              restaurant_id, name, cuisines_text, rating,
              avg_cost_for_two, locality, location_city, votes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("r1", "Cafe One", "Italian", 4.5, 900, "A", "Bangalore", 100),
                ("r1", "Cafe One", "Italian", 4.5, 900, "A", "Bangalore", 95),  # duplicate id
                (
                    "r2",
                    "Cafe One",
                    "Italian",
                    4.5,
                    900,
                    "A",
                    "Bangalore",
                    90,
                ),  # duplicate signature
                (
                    "r3",
                    "Cafe One",
                    "Italian",
                    4.4,
                    920,
                    "B",
                    "Bangalore",
                    88,
                ),  # same name, diff locality
                ("r4", "Cafe Two", "Chinese", 4.2, 1600, "C", "Bangalore", 70),  # over-budget case
            ],
        )
        conn.commit()


def test_max_budget_filter_behavior(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _seed_test_db(db_path)
    req = RecommendationQueryRequest(
        location="Bangalore",
        max_budget=1000,
        cuisine="Italian",
        min_rating=4.0,
        limit=1,
    )
    resp = query_recommendations(request=req, db_path=str(db_path))
    costs = [r.estimated_cost for r in resp.recommendations if r.estimated_cost is not None]
    assert costs
    assert all(c <= 1000 for c in costs)


def test_same_name_different_locality_not_deduped(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    _seed_test_db(db_path)
    req = RecommendationQueryRequest(location="Bangalore", cuisine="Italian", limit=10)
    resp = query_recommendations(request=req, db_path=str(db_path))
    names = [(r.restaurant_name, r.locality) for r in resp.recommendations]
    assert ("Cafe One", "A") in names
    assert ("Cafe One", "B") in names


def test_min_rating_above_five_rejected_by_api() -> None:
    client = TestClient(app)
    response = client.post(
        "/recommendations/query",
        json={
            "location": "Bangalore",
            "max_budget": 1200,
            "cuisine": "Italian",
            "min_rating": 5.5,
            "limit": 3,
        },
    )
    assert response.status_code == 422
