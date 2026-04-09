from fastapi import APIRouter, HTTPException, status

from src.phase_0_foundation.core_config import settings
from src.phase_2_retrieval.model_recommendation import (
    RecommendationQueryRequest,
    RecommendationQueryResponse,
)
from src.phase_2_retrieval.service_retrieval import query_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/query", response_model=RecommendationQueryResponse)
def recommendations_query(payload: RecommendationQueryRequest) -> RecommendationQueryResponse:
    try:
        return query_recommendations(request=payload, db_path=settings.db_path)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
