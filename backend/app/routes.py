from flask import Blueprint, current_app, jsonify, redirect, request

from . import cache
from .extensions import limiter
from .models import Click, Url, db
from .shortener import generate_unique_code
from .validators import normalize_and_validate

bp = Blueprint("main", __name__)


def _code_exists(code):
    return db.session.query(Url.id).filter_by(code=code).first() is not None


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.post("/api/shorten")
@limiter.limit(lambda: current_app.config["SHORTEN_RATE_LIMIT"])
def shorten():
    data = request.get_json(silent=True) or {}
    try:
        url = normalize_and_validate(data.get("url"))
    except ValueError as e:
        return jsonify(error=str(e)), 400

    code = generate_unique_code(
        _code_exists, length=current_app.config["CODE_LENGTH"]
    )
    entry = Url(code=code, original_url=url)
    db.session.add(entry)
    db.session.commit()

    cache.set_url(code, url)

    short_url = f"{current_app.config['BASE_URL'].rstrip('/')}/{code}"
    return (
        jsonify(code=code, short_url=short_url, original_url=url),
        201,
    )


@bp.get("/api/stats/<code>")
def stats(code):
    entry = Url.query.filter_by(code=code).first()
    if entry is None:
        return jsonify(error="Short code not found"), 404
    return jsonify(entry.to_stats())


@bp.get("/<code>")
def follow(code):
    # Fast path: Redis.
    original_url = cache.get_url(code)

    entry = None
    if original_url is None:
        entry = Url.query.filter_by(code=code).first()
        if entry is None:
            return jsonify(error="Short code not found"), 404
        original_url = entry.original_url
        cache.set_url(code, original_url)

    # Record the click. Use a targeted UPDATE so we don't need the row loaded.
    if entry is None:
        entry = Url.query.filter_by(code=code).first()
    if entry is not None:
        db.session.add(Click(url_id=entry.id))
        entry.click_count = Url.click_count + 1
        db.session.commit()

    return redirect(original_url, code=302)
