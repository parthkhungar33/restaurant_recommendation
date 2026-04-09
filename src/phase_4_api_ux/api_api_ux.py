from fastapi import APIRouter, HTTPException, status

from src.phase_0_foundation.core_config import settings
from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_4_api_ux.model_api_ux import LocationsResponse, UXRecommendationResponse
from src.phase_4_api_ux.service_api_ux import (
    build_recommendation_response,
    get_locations,
    get_top_cuisines,
    get_top_experiences,
)

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=UXRecommendationResponse)
def recommendations(payload: RecommendationQueryRequest) -> UXRecommendationResponse:
    try:
        return build_recommendation_response(payload=payload)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/metadata/locations", response_model=LocationsResponse)
def metadata_locations() -> LocationsResponse:
    return LocationsResponse(
        locations=get_locations(settings.db_path),
        top_cuisines=get_top_cuisines(),
        top_experiences=get_top_experiences(),
    )
