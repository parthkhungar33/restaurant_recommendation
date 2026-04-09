from __future__ import annotations

from pydantic import BaseModel, Field


class RestaurantCanonical(BaseModel):
    restaurant_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    location_city: str = Field(min_length=1)
    locality: str | None = None
    cuisines: list[str] = Field(default_factory=list)
    cuisines_text: str = ""
    avg_cost_for_two: float | None = None
    budget_band: str = "unknown"
    rating: float | None = None
    votes: int | None = None
    service_tags: list[str] = Field(default_factory=list)
    source_dataset: str = "ManikaSaini/zomato-restaurant-recommendation"
    ingest_version: str = ""
    ingested_at: str = ""
