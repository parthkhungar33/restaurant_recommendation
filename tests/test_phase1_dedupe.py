from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.phase_1_ingestion.data_ingestion import (
    dedupe_restaurants_by_business_key,
    dedupe_restaurants_table_in_sqlite,
    persist_to_sqlite,
)
from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_2_retrieval.service_retrieval import query_recommendations


def test_dedupe_restaurants_by_business_key_keeps_most_complete_row() -> None:
    df = pd.DataFrame(
        [
            {
                "restaurant_id": "r1",
                "name": "Sparse",
                "location_city": "Bangalore",
                "locality": None,
                "cuisines": "[]",
                "cuisines_text": "Italian",
                "avg_cost_for_two": None,
                "budget_band": "unknown",
                "rating": None,
                "votes": None,
                "service_tags": "[]",
                "source_dataset": "test",
                "ingest_version": "v1",
                "ingested_at": "2020-01-01T00:00:00+00:00",
            },
            {
                "restaurant_id": "r2",
                "name": "Rich",
                "location_city": "Bangalore",
                "locality": "Indiranagar",
                "cuisines": "[]",
                "cuisines_text": "Italian, Pizza",
                "avg_cost_for_two": 1200.0,
                "budget_band": "medium",
                "rating": 4.5,
                "votes": 200,
                "service_tags": "[]",
                "source_dataset": "test",
                "ingest_version": "v1",
                "ingested_at": "2021-01-01T00:00:00+00:00",
            },
        ]
    )
    out = dedupe_restaurants_by_business_key(df)
    assert len(out) == 2
    out2 = dedupe_restaurants_by_business_key(
        pd.DataFrame(
            [
                df.iloc[0].to_dict(),
                {**df.iloc[1].to_dict(), "name": "Sparse", "locality": None},
            ]
        )
    )
    assert len(out2) == 1
    assert out2.iloc[0]["restaurant_id"] == "r2"
    assert out2.iloc[0]["rating"] == 4.5


def test_persist_to_sqlite_creates_unique_index_on_business_key(tmp_path: Path) -> None:
    df = pd.DataFrame(
        [
            {
                "restaurant_id": "a",
                "name": "One",
                "location_city": "Bangalore",
                "locality": None,
                "cuisines": "[]",
                "cuisines_text": "",
                "avg_cost_for_two": None,
                "budget_band": "unknown",
                "rating": None,
                "votes": None,
                "service_tags": "[]",
                "source_dataset": "test",
                "ingest_version": "v1",
                "ingested_at": "2020-01-01T00:00:00+00:00",
            },
        ]
    )
    db_path = tmp_path / "t.db"
    persist_to_sqlite(df, db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' "
            "AND name='ux_restaurants_name_city_locality'"
        ).fetchone()
        assert row is not None
        assert "UNIQUE" in (row[0] or "").upper()


def test_dedupe_sqlite_in_place(tmp_path: Path) -> None:
    db_path = tmp_path / "d.db"
    df = pd.DataFrame(
        [
            {
                "restaurant_id": "x1",
                "name": "Weak",
                "location_city": "Bangalore",
                "locality": "Koramangala",
                "cuisines": "[]",
                "cuisines_text": "",
                "avg_cost_for_two": None,
                "budget_band": "unknown",
                "rating": None,
                "votes": None,
                "service_tags": "[]",
                "source_dataset": "test",
                "ingest_version": "v1",
                "ingested_at": "2020-01-01T00:00:00+00:00",
            },
            {
                "restaurant_id": "x2",
                "name": "Weak",
                "location_city": "Bangalore",
                "locality": "Koramangala",
                "cuisines": "[]",
                "cuisines_text": "Chinese",
                "avg_cost_for_two": 800.0,
                "budget_band": "low",
                "rating": 4.2,
                "votes": 50,
                "service_tags": "[]",
                "source_dataset": "test",
                "ingest_version": "v1",
                "ingested_at": "2021-01-01T00:00:00+00:00",
            },
        ]
    )
    with sqlite3.connect(db_path) as conn:
        df.to_sql("restaurants_clean", conn, if_exists="replace", index=False)
        conn.commit()

    stats = dedupe_restaurants_table_in_sqlite(db_path)
    assert stats["rows_before"] == 2
    assert stats["rows_after"] == 1
    assert stats["rows_removed"] == 1

    with sqlite3.connect(db_path) as conn:
        n = conn.execute("SELECT COUNT(*) FROM restaurants_clean").fetchone()[0]
        assert n == 1
        rid = conn.execute("SELECT restaurant_id FROM restaurants_clean").fetchone()[0]
        assert rid == "x2"


def test_query_recommendations_no_duplicate_ids_in_results(tmp_path: Path) -> None:
    db_path = tmp_path / "q.db"
    df = pd.DataFrame(
        [
            {
                "restaurant_id": "1",
                "name": "A",
                "location_city": "Bangalore",
                "locality": "L1",
                "cuisines": "[]",
                "cuisines_text": "Italian",
                "avg_cost_for_two": 1000.0,
                "budget_band": "medium",
                "rating": 4.5,
                "votes": 10,
                "service_tags": "[]",
                "source_dataset": "test",
                "ingest_version": "v1",
                "ingested_at": "2020-01-01T00:00:00+00:00",
            },
            {
                "restaurant_id": "2",
                "name": "B",
                "location_city": "Bangalore",
                "locality": "L2",
                "cuisines": "[]",
                "cuisines_text": "Italian",
                "avg_cost_for_two": 1100.0,
                "budget_band": "medium",
                "rating": 4.6,
                "votes": 20,
                "service_tags": "[]",
                "source_dataset": "test",
                "ingest_version": "v1",
                "ingested_at": "2020-01-01T00:00:00+00:00",
            },
        ]
    )
    persist_to_sqlite(df, db_path)
    resp = query_recommendations(
        request=RecommendationQueryRequest(
            location="Bangalore",
            cuisine="Italian",
            limit=10,
        ),
        db_path=str(db_path),
    )
    ids = [r.restaurant_id for r in resp.recommendations]
    assert len(ids) == len(set(ids))
