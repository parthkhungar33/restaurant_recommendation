from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

from src.phase_0_foundation.core_config import settings
from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_2_retrieval.service_retrieval import query_recommendations
from src.phase_3_llm.service_llm_recommender import GroqChatClient, rank_candidates_with_llm
from src.phase_4_api_ux.model_api_ux import UXRecommendationItem, UXRecommendationResponse

TOP_CUISINES: list[dict[str, int | str]] = [
    {"value": "North Indian", "label": "North Indian", "count": 5005},
    {"value": "Chinese", "label": "Chinese", "count": 3573},
    {"value": "South Indian", "label": "South Indian", "count": 2334},
    {"value": "Fast Food", "label": "Fast Food", "count": 2053},
    {"value": "Biryani", "label": "Biryani", "count": 1716},
    {"value": "Desserts", "label": "Desserts", "count": 1240},
    {"value": "Beverages", "label": "Beverages", "count": 1131},
    {"value": "Continental", "label": "Continental", "count": 978},
]

TOP_EXPERIENCES: list[dict[str, int | str]] = [
    {"value": "quick-service", "label": "Quick Service", "count": 2121},
    {"value": "casual", "label": "Casual", "count": 1116},
    {"value": "nightlife", "label": "Nightlife", "count": 367},
    {"value": "family-friendly", "label": "Family-Friendly", "count": 83},
]


def _signature(
    name: str, locality: str | None, cuisine: str, rating: float | None, cost: float | None
) -> str:
    locality_key = (locality or "").strip().lower()
    return f"{name.strip().lower()}|{locality_key}|{cuisine.strip().lower()}|{rating}|{cost}"


def build_recommendation_response(payload: RecommendationQueryRequest) -> UXRecommendationResponse:
    expanded_payload = payload.model_copy(update={"limit": max(payload.limit * 4, 20)})
    base_response = query_recommendations(request=expanded_payload, db_path=settings.db_path)
    request_id = str(uuid4())

    if not base_response.recommendations:
        return UXRecommendationResponse(
            request_id=request_id,
            applied_filters=base_response.applied_filters,
            recommendations=[],
            notes=base_response.notes,
        )

    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in .env")

    client = GroqChatClient(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
    )
    ranked = rank_candidates_with_llm(
        request=payload,
        candidates=base_response.recommendations,
        client=client,
    )
    ranked = sorted(ranked, key=lambda item: item.llm_rank)

    base_by_id = {item.restaurant_id: item for item in base_response.recommendations}
    recommendations: list[UXRecommendationItem] = []
    seen_ids: set[str] = set()
    seen_signatures: set[str] = set()
    for ranked_item in ranked:
        base = base_by_id.get(ranked_item.restaurant_id)
        if not base:
            continue
        if ranked_item.restaurant_id in seen_ids:
            continue
        signature = _signature(
            ranked_item.restaurant_name,
            base.locality,
            base.cuisine or "",
            base.rating,
            base.estimated_cost,
        )
        if signature in seen_signatures:
            continue
        seen_ids.add(ranked_item.restaurant_id)
        seen_signatures.add(signature)
        recommendations.append(
            UXRecommendationItem(
                restaurant_id=ranked_item.restaurant_id,
                restaurant_name=ranked_item.restaurant_name,
                cuisine=base.cuisine,
                rating=base.rating,
                estimated_cost=base.estimated_cost,
                ai_explanation=ranked_item.ai_explanation,
            )
        )
        if len(recommendations) >= payload.limit:
            break

    return UXRecommendationResponse(
        request_id=request_id,
        applied_filters=base_response.applied_filters,
        recommendations=recommendations,
        notes=base_response.notes,
    )


def get_locations(db_path: str) -> list[str]:
    db_file = Path(db_path)
    if not db_file.exists():
        return []
    with sqlite3.connect(db_file) as conn:
        rows = conn.execute(
            "SELECT DISTINCT location_city FROM restaurants_clean "
            "WHERE location_city IS NOT NULL AND TRIM(location_city) != '' "
            "ORDER BY location_city ASC"
        ).fetchall()
    return [str(row[0]) for row in rows]


def get_top_cuisines() -> list[dict[str, int | str]]:
    return [dict(item) for item in TOP_CUISINES]


def get_top_experiences() -> list[dict[str, int | str]]:
    return [dict(item) for item in TOP_EXPERIENCES]
