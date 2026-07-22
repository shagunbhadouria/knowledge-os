"""Pydantic Settings singleton for validated runtime configuration.

Rule R-36: the application must fail fast on startup with a clear error
message if any required environment variable is missing or malformed.
All other modules import `settings` from here — never read os.environ
directly (Rule R-19).
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration, sourced from environment variables.

    Every field below is required per Blueprint 7.1 unless a default is
    given. Pydantic Settings raises a ValidationError automatically on
    import if a required variable is missing — this IS the fail-fast
    behaviour Rule R-36 requires. No manual "if not X: raise" checks
    are needed for presence; add custom validators only for format
    checks beyond presence.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Databases
    mongodb_uri: str = Field(alias="MONGODB_URI")
    neo4j_uri: str = Field(alias="NEO4J_URI")
    neo4j_username: str = Field(alias="NEO4J_USERNAME")
    neo4j_password: str = Field(alias="NEO4J_PASSWORD")
    redis_url: str = Field(alias="REDIS_URL")

    # LLM providers
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    groq_model_fast: str = Field(alias="GROQ_MODEL_FAST")
    groq_model_smart: str = Field(alias="GROQ_MODEL_SMART")
    ollama_base_url: str = Field(alias="OLLAMA_BASE_URL")

    # Auth
    google_client_id: str = Field(alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(alias="GOOGLE_CLIENT_SECRET")
    jwt_private_key: str = Field(alias="JWT_PRIVATE_KEY")
    jwt_public_key: str = Field(alias="JWT_PUBLIC_KEY")

    # Webhook validation
    github_webhook_secret: str = Field(alias="GITHUB_WEBHOOK_SECRET")
    slack_signing_secret: str = Field(alias="SLACK_SIGNING_SECRET")

    # Graph / intelligence tuning
    entity_merge_threshold: float = Field(alias="ENTITY_MERGE_THRESHOLD")
    graph_expansion_hops: int = Field(alias="GRAPH_EXPANSION_HOPS")
    ktd_inactivity_days: int = Field(alias="KTD_INACTIVITY_DAYS")

    # Runtime
    frontend_url: str = Field(alias="FRONTEND_URL")
    log_level: str = Field(alias="LOG_LEVEL")
    port: int = Field(alias="PORT")
    node_env: str = Field(alias="NODE_ENV")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide Settings singleton.

    lru_cache ensures env vars are read and validated exactly once per
    process, on first access — not at module import time (Rule: no
    module-level side effects / no DB or env calls at import time).
    """

    return Settings()
