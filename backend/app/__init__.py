from flask import Flask
from sqlalchemy.exc import IntegrityError

from . import cache
from .config import Config
from .extensions import limiter
from .models import db


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    cache.init_cache(app)

    # Configure flask-limiter via app config so init_app picks it up.
    app.config.setdefault("RATELIMIT_STORAGE_URI", app.config["REDIS_URL"])
    app.config.setdefault("RATELIMIT_DEFAULT", app.config["DEFAULT_RATE_LIMIT"])
    limiter.init_app(app)

    from .routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        try:
            db.create_all()
        except IntegrityError:
            # Another worker created the schema concurrently; safe to ignore.
            db.session.rollback()

    return app
