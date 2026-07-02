# URL Shortener

A bit.ly-style URL shortener: paste a long URL, get a short code, and track click analytics. Flask + Postgres + Redis backend, React (Vite) frontend, all wired together with Docker Compose.

## Stack

- **Backend:** Flask, SQLAlchemy, Postgres (persistence), Redis (redirect cache + rate limiting), gunicorn.
- **Frontend:** React + Vite, built to static files and served by nginx. nginx also reverse-proxies API and redirect routes to the backend, so everything runs behind one origin.
- **Short codes:** random base62 (6 chars by default), with collision retry.

## Run it

```bash
cp .env.example .env      # optional; sensible defaults are built in
docker-compose up --build
```

Then open http://localhost:8080.

That single command starts four containers: `postgres`, `redis`, `api` (Flask), and `frontend` (nginx). The database schema is created automatically on first boot.

## How it fits together

```
browser ──▶ nginx (:8080) ──┬─ /            → React SPA (static files)
                            ├─ /api/*        → Flask (:5000)
                            └─ /<code>       → Flask redirect (302)
Flask ──▶ Postgres   (URL mappings + click rows)
      └─▶ Redis       (code → URL cache, rate-limit counters)
```

## API

| Method | Path                | Description                                        |
| ------ | ------------------- | -------------------------------------------------- |
| POST   | `/api/shorten`      | Body `{ "url": "..." }` → `{ code, short_url, original_url }`. Rate-limited. |
| GET    | `/<code>`           | 302 redirect to the original URL; records a click. |
| GET    | `/api/stats/<code>` | `{ code, original_url, created_at, click_count, recent_clicks[] }`. |
| GET    | `/health`           | Health check.                                      |

### Example

```bash
curl -X POST http://localhost:8080/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/some/really/long/path"}'
# → {"code":"aZ3k9Q","short_url":"http://localhost:8080/aZ3k9Q","original_url":"..."}

curl -i http://localhost:8080/aZ3k9Q          # 302 redirect
curl http://localhost:8080/api/stats/aZ3k9Q   # click stats
```

## Design notes

- **Redirects hit Redis first**, falling back to Postgres and repopulating the cache. Redis errors degrade gracefully — the app still works from Postgres if the cache is down.
- **Rate limiting** uses `flask-limiter` with Redis storage. The shorten endpoint is capped (default 10/min per IP); other routes get a generous default. Tune via `SHORTEN_RATE_LIMIT` / `DEFAULT_RATE_LIMIT`.
- **Validation** requires an `http`/`https` URL with a real-looking domain; a missing scheme defaults to `https`.
- **Click analytics** store one timestamped row per click plus a denormalized `click_count` on the URL for fast reads.

## Configuration

All settings have defaults; override via `.env` (see `.env.example`). Key ones: `APP_PORT`, `BASE_URL`, Postgres credentials, `SECRET_KEY`, `CODE_LENGTH`, `SHORTEN_RATE_LIMIT`.

> **Note:** `BASE_URL` must match how you reach the app in the browser, since it's used to build the returned short links.

## Local development (without Docker)

Backend:

```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/urlshortener
export REDIS_URL=redis://localhost:6379/0
python wsgi.py
```

Frontend (proxies `/api` to `localhost:5000` via Vite):

```bash
cd frontend
npm install
npm run dev
```

## Project layout

```
url-shortener/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── wsgi.py
│   └── app/
│       ├── __init__.py     # app factory + extension wiring
│       ├── config.py
│       ├── models.py       # Url, Click
│       ├── routes.py       # shorten / redirect / stats
│       ├── shortener.py    # random base62 + collision retry
│       ├── cache.py        # Redis helpers
│       └── validators.py
└── frontend/
    ├── Dockerfile          # Vite build → nginx
    ├── nginx.conf
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/{main.jsx, App.jsx, api.js, styles.css}
```
