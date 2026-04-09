from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.phase_0_foundation.core_config import settings
from src.phase_2_retrieval.main import app
from src.phase_3_llm.service_llm_recommender import GroqChatClient


def _require_live_env() -> None:
    if os.getenv("RUN_LIVE_GROQ_TESTS", "").strip().lower() not in {"1", "true", "yes"}:
        pytest.skip("RUN_LIVE_GROQ_TESTS is not enabled; skipping live integration tests.")
    if not settings.groq_api_key:
        pytest.skip("GROQ_API_KEY not set; skipping live integration test.")
    if not Path(settings.db_path).exists():
        pytest.skip(f"DB not found at {settings.db_path}; run ingestion first.")


def test_live_groq_connectivity_returns_text() -> None:
    _require_live_env()
    client = GroqChatClient(
        api_key=settings.groq_api_key or "",
        base_url=settings.groq_base_url,
    )
    output = client.complete(
        system_prompt="You are a concise assistant.",
        user_prompt='Reply with exactly: {"ok": true}',
    )
    assert isinstance(output, str)
    assert output.strip() != ""


def test_live_recommendations_endpoint_llm_flow() -> None:
    _require_live_env()
    api = TestClient(app)
    response = api.post(
        "/recommendations",
        json={
            "location": "Bangalore",
            "max_budget": 1200,
            "cuisine": "North Indian",
            "min_rating": 4.0,
            "limit": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    first = data["recommendations"][0]
    assert "ai_explanation" in first
    assert first["ai_explanation"]
