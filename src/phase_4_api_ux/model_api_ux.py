from __future__ import annotations

from pydantic import BaseModel, Field

from src.phase_2_retrieval.model_recommendation import AppliedFilters


class UXRecommendationItem(BaseModel):
    restaurant_id: str
    restaurant_name: str
    cuisine: str
    rating: float | None = None
    estimated_cost: float | None = None
    ai_explanation: str


class UXRecommendationResponse(BaseModel):
    request_id: str
    applied_filters: AppliedFilters
    recommendations: list[UXRecommendationItem]
    notes: list[str] = Field(default_factory=list)


class LocationsResponse(BaseModel):
    locations: list[str]
    top_cuisines: list[dict[str, int | str]] = Field(default_factory=list)
    top_experiences: list[dict[str, int | str]] = Field(default_factory=list)
