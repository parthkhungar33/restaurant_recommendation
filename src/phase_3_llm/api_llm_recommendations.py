from fastapi import APIRouter, HTTPException, status

from src.phase_0_foundation.core_config import settings
from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_2_retrieval.service_retrieval import query_recommendations
from src.phase_3_llm.model_llm_recommendation import LLMRecommendationResponse
from src.phase_3_llm.service_llm_recommender import GroqChatClient, rank_candidates_with_llm

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=LLMRecommendationResponse)
def recommendations_llm(payload: RecommendationQueryRequest) -> LLMRecommendationResponse:
    if not settings.groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY is not configured in .env",
        )

    expanded_payload = payload.model_copy(update={"limit": max(payload.limit * 4, 20)})
    base_response = query_recommendations(request=expanded_payload, db_path=settings.db_path)
    if not base_response.recommendations:
        return LLMRecommendationResponse(
            applied_filters=base_response.applied_filters,
            total_candidates=base_response.total_candidates,
            recommendations=[],
            notes=base_response.notes,
        )

    client = GroqChatClient(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
    )
    ranked = rank_candidates_with_llm(
        request=payload,
        candidates=base_response.recommendations,
        client=client,
    )

    ordered = sorted(ranked, key=lambda item: item.llm_rank)

    return LLMRecommendationResponse(
        applied_filters=base_response.applied_filters,
        total_candidates=base_response.total_candidates,
        recommendations=ordered[: payload.limit],
        notes=base_response.notes,
    )
