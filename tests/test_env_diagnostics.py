from src.phase_0_foundation.core_config import settings


def test_groq_api_key_presence_flag() -> None:
    # Never print or expose key value; only check presence.
    assert bool(settings.groq_api_key), "GROQ_API_KEY is missing or not loaded from .env"
