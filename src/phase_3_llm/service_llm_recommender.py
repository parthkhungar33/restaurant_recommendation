from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from src.phase_2_retrieval.model_recommendation import (
    RecommendationItem,
    RecommendationQueryRequest,
)
from src.phase_3_llm.model_llm_recommendation import LLMRankedItem, LLMRankedList

PROMPT_DIR = Path("src/phase_3_llm/prompts")
PREFERENCE_TAG_MAP = {
    "date": ["romantic", "ambience", "quiet"],
    "family-friendly": ["family-friendly", "spacious", "kid-friendly"],
    "quick service": ["quick-service", "fast-turnaround"],
    "casual": ["casual", "relaxed"],
    "fine dine": ["fine-dine", "premium"],
    "outdoor seating": ["outdoor", "open-air"],
    "veg friendly": ["vegetarian-options", "veg-friendly"],
    "group friendly": ["group-friendly", "large-seating"],
}

PREFERENCE_STYLE_GUIDE = {
    "date": "playful, charming, and lightly flirty; keep it classy and non-explicit.",
    "family-friendly": (
        "warm, reassuring, and family-centered; emphasize comfort and together time."
    ),
    "quick service": "crisp and practical; highlight speed and convenience.",
    "casual": "easygoing and friendly; keep language relaxed.",
    "fine dine": "polished and premium; spotlight ambience and quality.",
    "outdoor seating": "fresh and scenic; mention open-air vibe naturally.",
    "veg friendly": "supportive and helpful; call out vegetarian suitability clearly.",
    "group friendly": "social and upbeat; emphasize shared experience and spaciousness.",
}


class GroqChatClient:
    def __init__(self, *, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        model_candidates = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=30.0) as client:
            for model_name in model_candidates:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.2,
                }
                response = client.post(self.base_url, json=payload, headers=headers)
                if response.is_success:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]

                error_text = response.text.lower()
                if "decommissioned" in error_text or "model_decommissioned" in error_text:
                    continue

                response.raise_for_status()

        raise RuntimeError("No supported Groq model available for this request.")


def _load_system_prompt() -> str:
    return (PROMPT_DIR / "system_v1.txt").read_text(encoding="utf-8")


def _build_user_prompt(
    request: RecommendationQueryRequest, candidates: list[RecommendationItem]
) -> str:
    selected_preferences = request.additional_preferences or []
    normalized_tags: list[str] = []
    for pref in selected_preferences:
        normalized_tags.extend(PREFERENCE_TAG_MAP.get(pref, [pref]))
    # Keep tags unique while preserving order.
    normalized_tags = list(dict.fromkeys(normalized_tags))
    style_hints = [
        PREFERENCE_STYLE_GUIDE[pref]
        for pref in selected_preferences
        if pref in PREFERENCE_STYLE_GUIDE
    ]
    style_hints = list(dict.fromkeys(style_hints))
    explanation_style = (
        " ".join(style_hints)
        if style_hints
        else "friendly, confident, and conversational."
    )

    payload = {
        "user_preferences": {
            "location": request.location,
            "max_budget": request.max_budget,
            "cuisine": request.cuisine,
            "min_rating": request.min_rating,
            "additional_preferences": selected_preferences,
            "preference_tags": normalized_tags,
            "explanation_style": explanation_style,
        },
        "candidates": [
            {
                "restaurant_id": item.restaurant_id,
                "restaurant_name": item.restaurant_name,
                "cuisine": item.cuisine,
                "rating": item.rating,
                "estimated_cost": item.estimated_cost,
                "locality": item.locality,
            }
            for item in candidates
        ],
    }
    return (
        "Rank these restaurant candidates and explain why they fit.\n"
        "Apply the explanation_style guidance while staying grounded in candidate facts.\n"
        "Return strict JSON only.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    return json.loads(cleaned)


def _validate_ranked_list(
    payload: dict[str, Any], candidates: list[RecommendationItem]
) -> list[LLMRankedItem]:
    ranked = LLMRankedList.model_validate(payload)
    allowed = {c.restaurant_id for c in candidates}
    candidates_by_id = {c.restaurant_id: c for c in candidates}
    filtered: list[LLMRankedItem] = []
    seen: set[str] = set()
    seen_name_locality: set[str] = set()
    for item in ranked.recommendations:
        if item.restaurant_id not in allowed:
            continue
        if item.restaurant_id in seen:
            continue
        candidate = candidates_by_id.get(item.restaurant_id)
        locality = (candidate.locality if candidate else "") or ""
        name_key = " ".join(item.restaurant_name.strip().lower().split())
        locality_key = " ".join(locality.strip().lower().split())
        composite = f"{name_key}|{locality_key}"
        if composite in seen_name_locality:
            continue
        seen.add(item.restaurant_id)
        seen_name_locality.add(composite)
        filtered.append(item)
    if not filtered:
        raise ValueError("LLM output does not contain valid candidate ids.")
    return filtered


def _fallback_rank(candidates: list[RecommendationItem], limit: int) -> list[LLMRankedItem]:
    ranked: list[LLMRankedItem] = []
    for idx, item in enumerate(candidates[:limit], start=1):
        explanation = (
            "This place looks like a solid match for your location and preferences, with suitable "
            "cuisine, rating, and budget fit."
        )
        ranked.append(
            LLMRankedItem(
                restaurant_id=item.restaurant_id,
                restaurant_name=item.restaurant_name,
                ai_explanation=explanation,
                llm_rank=idx,
            )
        )
    return ranked


def rank_candidates_with_llm(
    *,
    request: RecommendationQueryRequest,
    candidates: list[RecommendationItem],
    client: GroqChatClient,
) -> list[LLMRankedItem]:
    system_prompt = _load_system_prompt()
    user_prompt = _build_user_prompt(request=request, candidates=candidates)

    for attempt in range(2):
        raw = client.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        try:
            parsed = _extract_json(raw)
            return _validate_ranked_list(parsed, candidates=candidates)
        except (json.JSONDecodeError, ValidationError, ValueError):
            if attempt == 1:
                break
            user_prompt = (
                user_prompt
                + "\n\nPrevious response failed schema validation. "
                + "Return strict JSON only with valid candidate ids."
            )

    return _fallback_rank(candidates=candidates, limit=len(candidates))
