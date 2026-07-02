import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@postgres:5432/urlshortener",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    # Public base used when building the short URL returned to clients.
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")

    # Length of generated short codes (base62).
    CODE_LENGTH = int(os.environ.get("CODE_LENGTH", "6"))

    # Cache TTL (seconds) for code -> original_url lookups.
    CACHE_TTL = int(os.environ.get("CACHE_TTL", "3600"))

    # Rate limits (flask-limiter syntax). Redirects are left generous.
    SHORTEN_RATE_LIMIT = os.environ.get("SHORTEN_RATE_LIMIT", "10 per minute")
    DEFAULT_RATE_LIMIT = os.environ.get("DEFAULT_RATE_LIMIT", "200 per minute")
