import pandas as pd

from src.phase_1_ingestion.data_ingestion import (
    BudgetThresholds,
    build_quality_report,
    normalize_restaurants,
)


def test_normalize_restaurants_maps_core_fields() -> None:
    raw = pd.DataFrame(
        [
            {
                "Restaurant Name": "Cafe 123",
                "City": "bangalore",
                "Cuisines": "Italian, Chinese",
                "Average Cost for two": "1200",
                "Aggregate Rating": "4.3",
                "Votes": "150",
            }
        ]
    )

    normalized = normalize_restaurants(
        raw_df=raw,
        ingest_version="test-v1",
        thresholds=BudgetThresholds(low_max=500, medium_max=1200),
    )

    assert len(normalized) == 1
    row = normalized.iloc[0]
    assert row["name"] == "Cafe 123"
    assert row["location_city"] == "Bangalore"
    assert row["cuisines_text"] == "Italian, Chinese"
    assert row["budget_band"] == "medium"
    assert row["rating"] == 4.3
    assert row["votes"] == 150


def test_build_quality_report_has_completeness() -> None:
    df = pd.DataFrame(
        [
            {"restaurant_id": "1", "name": "A", "location_city": "Delhi", "budget_band": "low"},
            {"restaurant_id": "2", "name": "B", "location_city": "Mumbai", "budget_band": "high"},
        ]
    )
    report = build_quality_report(df)
    assert report["total_rows"] == 2
    assert report["required_field_completeness_pct"] == 100.0
