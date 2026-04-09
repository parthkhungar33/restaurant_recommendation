from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RecommendationQueryRequest(BaseModel):
    location: str = Field(min_length=1)
    max_budget: float | None = Field(default=None, gt=0)
    cuisine: str | list[str] | None = None
    min_rating: float | None = Field(default=None, ge=0.0, le=5.0)
    additional_preferences: list[str] | None = None
    limit: int = Field(default=5, ge=1, le=20)

    @field_validator("location")
    @classmethod
    def normalize_location(cls, value: str) -> str:
        normalized = " ".join(value.strip().split()).title()
        if not normalized:
            raise ValueError("location must not be empty")
        return normalized

    @field_validator("additional_preferences", mode="before")
    @classmethod
    def normalize_preferences(
        cls, value: str | list[str] | None
    ) -> list[str] | None:
        if value is None:
            return None
        raw_items = [value] if isinstance(value, str) else value
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in raw_items:
            text = " ".join(str(item).strip().split()).lower()
            if not text:
                continue
            if text in seen:
                continue
            seen.add(text)
            cleaned.append(text)
        return cleaned or None


class AppliedFilters(BaseModel):
    location: str
    max_budget: float | None = None
    cuisines: list[str] = Field(default_factory=list)
    min_rating: float | None = None
    relaxed_constraints: list[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    restaurant_id: str
    restaurant_name: str
    cuisine: str
    rating: float | None = None
    estimated_cost: float | None = None
    locality: str | None = None
    reason_tags: list[str] = Field(default_factory=list)


class RecommendationQueryResponse(BaseModel):
    applied_filters: AppliedFilters
    total_candidates: int
    recommendations: list[RecommendationItem]
    notes: list[str] = Field(default_factory=list)
