"""End-to-end API tests for the URL shortener backend."""


def _shorten(client, url):
    return client.post("/api/shorten", json={"url": url})


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_shorten_returns_code(client):
    resp = _shorten(client, "https://example.com/some/long/path")
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["original_url"] == "https://example.com/some/long/path"
    assert data["code"]
    assert data["short_url"].endswith("/" + data["code"])


def test_shorten_adds_scheme_when_missing(client):
    resp = _shorten(client, "example.com")
    assert resp.status_code == 201
    assert resp.get_json()["original_url"] == "https://example.com"


def test_shorten_rejects_invalid_url(client):
    resp = _shorten(client, "not a url")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_shorten_rejects_missing_url(client):
    resp = client.post("/api/shorten", json={})
    assert resp.status_code == 400


def test_redirect_follows_to_original(client):
    code = _shorten(client, "https://example.com").get_json()["code"]
    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://example.com"


def test_clicks_are_tracked(client):
    code = _shorten(client, "https://example.com").get_json()["code"]
    client.get(f"/{code}")
    client.get(f"/{code}")

    stats = client.get(f"/api/stats/{code}").get_json()
    assert stats["click_count"] == 2
    assert len(stats["recent_clicks"]) == 2


def test_stats_shape(client):
    code = _shorten(client, "https://example.com").get_json()["code"]
    stats = client.get(f"/api/stats/{code}").get_json()
    for key in ("code", "original_url", "created_at", "click_count", "recent_clicks"):
        assert key in stats


def test_unknown_code_returns_404(client):
    assert client.get("/doesnotexist").status_code == 404
    assert client.get("/api/stats/doesnotexist").status_code == 404


def test_rate_limit_enforced(make_app):
    app = make_app(RATELIMIT_ENABLED=True, SHORTEN_RATE_LIMIT="3 per minute")
    client = app.test_client()
    statuses = [_shorten(client, "https://example.com").status_code for _ in range(5)]
    assert statuses.count(201) == 3
    assert 429 in statuses
