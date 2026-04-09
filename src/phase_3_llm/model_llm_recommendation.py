from __future__ import annotations

from pydantic import BaseModel, Field

from src.phase_2_retrieval.model_recommendation import AppliedFilters


class LLMRankedItem(BaseModel):
    restaurant_id: str = Field(min_length=1)
    restaurant_name: str = Field(min_length=1)
    ai_explanation: str = Field(min_length=1)
    llm_rank: int = Field(ge=1)


class LLMRankedList(BaseModel):
    recommendations: list[LLMRankedItem]


class LLMRecommendationResponse(BaseModel):
    applied_filters: AppliedFilters
    total_candidates: int
    recommendations: list[LLMRankedItem]
    notes: list[str] = Field(default_factory=list)
