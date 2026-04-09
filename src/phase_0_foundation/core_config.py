from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "restaurant_recommender"
    app_env: str = "dev"
    app_debug: bool = True
    app_version: str = "0.1.0"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    db_path: str = "src/phase_1_ingestion/data/restaurants.db"
    groq_api_key: str | None = None
    groq_base_url: str = "https://api.groq.com/openai/v1/chat/completions"
    # Extra browser origins for CORS (comma-separated). Dev localhosts always allowed in code.
    cors_extra_origins: str = ""
    # E.g. https://.*\.vercel\.app for preview deploys without listing each URL.
    cors_origin_regex: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
