import redis

_client = None
_ttl = 3600


def init_cache(app):
    global _client, _ttl
    _client = redis.Redis.from_url(
        app.config["REDIS_URL"], decode_responses=True, socket_connect_timeout=2
    )
    _ttl = app.config["CACHE_TTL"]


def _key(code):
    return f"url:{code}"


def get_url(code):
    """Return cached original_url for a code, or None. Never raises on Redis errors."""
    if _client is None:
        return None
    try:
        return _client.get(_key(code))
    except redis.RedisError:
        return None


def set_url(code, original_url):
    if _client is None:
        return
    try:
        _client.set(_key(code), original_url, ex=_ttl)
    except redis.RedisError:
        pass
