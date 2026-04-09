from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from src.phase_2_retrieval.model_recommendation import (
    AppliedFilters,
    RecommendationItem,
    RecommendationQueryRequest,
    RecommendationQueryResponse,
)


def _normalize_cuisines(cuisine: str | list[str] | None) -> list[str]:
    if cuisine is None:
        return []
    parts = [cuisine] if isinstance(cuisine, str) else cuisine
    normalized: list[str] = []
    seen: set[str] = set()
    for value in parts:
        item = " ".join(value.strip().split()).title()
        if not item:
            continue
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(item)
    return normalized


_RELAXED_FRIENDLY_LABELS: dict[str, str] = {
    "min_rating": "rating",
    "max_budget": "budget",
    "cuisine": "cuisine",
}


def _friendly_relaxation_note(relaxed_keys: list[str]) -> str:
    """Copy for when we widen filters so results are not empty or too sparse."""
    if not relaxed_keys:
        return ""
    labels = [
        _RELAXED_FRIENDLY_LABELS.get(key, key.replace("_", " "))
        for key in relaxed_keys
    ]
    if len(labels) == 1:
        return (
            f"We nudged your {labels[0]} preference a bit so we could line up "
            "great options for you."
        )
    if len(labels) == 2:
        return (
            f"We nudged your {labels[0]} and {labels[1]} preferences a bit "
            "so we could line up more places you will enjoy."
        )
    return (
        "We nudged your "
        + ", ".join(labels[:-1])
        + f", and {labels[-1]} preferences a bit so we could line up "
        "more places you will enjoy."
    )


@dataclass
class FilterState:
    location: str
    max_budget: float | None
    cuisines: list[str]
    min_rating: float | None
    relaxed_constraints: list[str] = field(default_factory=list)


def _build_query(state: FilterState, limit: int) -> tuple[str, list[object]]:
    conditions = ["location_city = ?"]
    params: list[object] = [state.location]

    if state.max_budget is not None:
        conditions.append("avg_cost_for_two <= ?")
        params.append(state.max_budget)
    if state.min_rating is not None:
        conditions.append("rating >= ?")
        params.append(state.min_rating)
    for cuisine in state.cuisines:
        conditions.append("LOWER(cuisines_text) LIKE ?")
        params.append(f"%{cuisine.lower()}%")

    where_clause = " AND ".join(conditions)
    sql = (
        "SELECT restaurant_id, name, cuisines_text, rating, avg_cost_for_two, locality "
        "FROM restaurants_clean "
        f"WHERE {where_clause} "
        "ORDER BY rating DESC, votes DESC, avg_cost_for_two ASC "
        "LIMIT ?"
    )
    params.append(limit)
    return sql, params


def _fetch_candidates(
    conn: sqlite3.Connection, state: FilterState, limit: int
) -> list[sqlite3.Row]:
    sql, params = _build_query(state, limit=limit)
    return conn.execute(sql, params).fetchall()


def _format_item(row: sqlite3.Row, reason_tags: list[str]) -> RecommendationItem:
    return RecommendationItem(
        restaurant_id=row["restaurant_id"],
        restaurant_name=row["name"],
        cuisine=row["cuisines_text"] or "",
        rating=row["rating"],
        estimated_cost=row["avg_cost_for_two"],
        locality=row["locality"],
        reason_tags=reason_tags,
    )


def query_recommendations(
    request: RecommendationQueryRequest, db_path: str
) -> RecommendationQueryResponse:
    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(
            "Database not found. Run `python scripts/ingest_restaurants.py` first."
        )

    cuisines = _normalize_cuisines(request.cuisine)
    state = FilterState(
        location=request.location,
        max_budget=request.max_budget,
        cuisines=cuisines,
        min_rating=request.min_rating,
    )

    notes: list[str] = []
    with sqlite3.connect(db_file) as conn:
        conn.row_factory = sqlite3.Row
        rows = _fetch_candidates(conn, state, limit=max(request.limit * 4, 20))

        # Keep rating strict when we still have some matches; only relax when
        # the rating gate yields zero candidates.
        if len(rows) == 0 and state.min_rating is not None:
            state.min_rating = None
            state.relaxed_constraints.append("min_rating")
            rows = _fetch_candidates(conn, state, limit=max(request.limit * 4, 20))

        if len(rows) < request.limit and state.cuisines:
            state.cuisines = []
            state.relaxed_constraints.append("cuisine")
            rows = _fetch_candidates(conn, state, limit=max(request.limit * 4, 20))

        if len(rows) < request.limit and state.max_budget is not None:
            state.max_budget = None
            state.relaxed_constraints.append("max_budget")
            rows = _fetch_candidates(conn, state, limit=max(request.limit * 4, 20))

        if not rows:
            return RecommendationQueryResponse(
                applied_filters=AppliedFilters(
                    location=request.location,
                    max_budget=request.max_budget,
                    cuisines=cuisines,
                    min_rating=request.min_rating,
                    relaxed_constraints=state.relaxed_constraints,
                ),
                total_candidates=0,
                recommendations=[],
                notes=["No restaurants found for this location and preference set."],
            )

        if state.relaxed_constraints:
            notes.append(_friendly_relaxation_note(state.relaxed_constraints))

        reason_tags = ["location_match"]
        if request.max_budget and "max_budget" not in state.relaxed_constraints:
            reason_tags.append("max_budget_match")
        if cuisines and "cuisine" not in state.relaxed_constraints:
            reason_tags.append("cuisine_match")
        if request.min_rating is not None and "min_rating" not in state.relaxed_constraints:
            reason_tags.append("rating_match")

        recommendations = [_format_item(row, reason_tags) for row in rows[: request.limit]]

    return RecommendationQueryResponse(
        applied_filters=AppliedFilters(
            location=request.location,
            max_budget=request.max_budget,
            cuisines=cuisines,
            min_rating=request.min_rating,
            relaxed_constraints=state.relaxed_constraints,
        ),
        total_candidates=len(rows),
        recommendations=recommendations,
        notes=notes,
    )
