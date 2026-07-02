import pytest

from app import create_app
from app.config import Config
from app.models import db


class BaseTestConfig(Config):
    """Self-contained config: SQLite file DB, no external Postgres/Redis.

    The Redis cache client is created lazily and its errors are swallowed,
    so pointing it at an unused localhost address is harmless in tests.
    Rate limiting is disabled by default and turned on only where tested.
    """

    TESTING = True
    REDIS_URL = "redis://localhost:6379/0"
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_ENABLED = False
    BASE_URL = "http://testhost"


def _make_app(tmp_path, **overrides):
    db_file = tmp_path / "test.db"

    class Cfg(BaseTestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file}"

    for key, value in overrides.items():
        setattr(Cfg, key, value)

    return create_app(Cfg)


@pytest.fixture
def app(tmp_path):
    application = _make_app(tmp_path)
    yield application
    with application.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_app(tmp_path):
    """Factory for tests that need custom config (e.g. rate limiting on)."""
    created = []

    def _factory(**overrides):
        application = _make_app(tmp_path, **overrides)
        created.append(application)
        return application

    yield _factory

    for application in created:
        with application.app_context():
            db.drop_all()
