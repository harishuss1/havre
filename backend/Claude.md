# Havre — Project Context for Claude Code

> This file gives Claude Code full context on the Havre project.
> Read this before touching any code.

---

## What is Havre?

Havre (French for "haven") is a **personal real estate aggregator** for the Canadian market.
It scrapes listing data from multiple property websites (Centris, DuProprio, Kijiji Immobilier, etc.),
deduplicates them, stores them in a single database, and sends email/SMS notifications
whenever a new listing matches the user's saved search criteria.

**The core problem it solves:** buyers currently tab between 5–6 sites daily.
Havre collapses that into one dashboard that updates automatically every 30 minutes.

**This is a personal-use tool.** It is not a commercial product.
Scraping is against the ToS of most real estate platforms — keep it private.

---

## Monorepo Structure

```
havre/
├── .env.example              # all required env vars with placeholders
├── .gitignore
├── docker-compose.yml        # local dev: api + worker + postgres + redis
├── README.md
├── CLAUDE.md                 # ← you are here
│
├── backend/                  # Python — FastAPI + Celery
│   ├── requirements.txt
│   ├── Procfile              # Railway: web, worker, beat
│   └── app/
│       ├── main.py           # FastAPI entrypoint
│       ├── config.py         # settings, env vars, source registry
│       ├── database.py       # SQLAlchemy engine + session
│       │
│       ├── models/           # SQLAlchemy ORM models
│       │   ├── listing.py
│       │   ├── search_profile.py
│       │   ├── notification.py
│       │   └── source.py
│       │
│       ├── routers/          # FastAPI route handlers
│       │   ├── listings.py
│       │   ├── profiles.py
│       │   ├── sources.py
│       │   ├── notifications.py
│       │   └── stats.py
│       │
│       ├── scrapers/         # ← plugin system (see below)
│       │   ├── __init__.py   # SOURCE_REGISTRY + get_scraper()
│       │   ├── base.py       # BaseScraper, SearchCriteria, RawListing
│       │   ├── normaliser.py
│       │   ├── deduplicator.py
│       │   └── centris/
│       │       ├── __init__.py
│       │       ├── scraper.py    # Playwright scraper (DONE)
│       │       ├── selectors.py  # CSS selectors (DONE)
│       │       └── parser.py     # field extraction (DONE)
│       │
│       ├── tasks/            # Celery jobs
│       │   ├── celery_app.py
│       │   ├── scrape_tasks.py
│       │   ├── notify_tasks.py
│       │   └── beat_schedule.py
│       │
│       ├── notifications/
│       │   ├── email.py      # Resend API wrapper
│       │   ├── matcher.py    # listing vs profile matching logic
│       │   └── templates/    # HTML email templates
│       │
│       ├── migrations/       # Alembic
│       │   ├── env.py
│       │   └── versions/
│       │
│       └── tests/
│
└── frontend/                 # Next.js (React) — NOT YET BUILT
    ├── package.json
    ├── next.config.js
    ├── .env.local
    ├── app/                  # Next.js App Router
    │   ├── page.tsx          # / dashboard
    │   ├── listings/
    │   │   ├── page.tsx      # listing grid + filters
    │   │   └── [id]/page.tsx # listing detail
    │   ├── profiles/page.tsx
    │   ├── sources/page.tsx
    │   └── notifications/page.tsx
    ├── components/
    ├── lib/                  # API client, hooks, utils
    └── types/                # TypeScript types matching API schema
```

---

## Tech Stack

| Layer          | Technology              | Notes                                   |
| -------------- | ----------------------- | --------------------------------------- |
| Scraping       | Python + Playwright     | Headless Chromium for JS-rendered sites |
| Task queue     | Celery + Redis          | Background scrape jobs, cron scheduling |
| Backend API    | FastAPI (Python)        | REST API, async-native                  |
| Database       | PostgreSQL              | Primary store                           |
| DB driver      | psycopg[binary] 3.2.10+ | psycopg3 — NOT psycopg2                 |
| Cache/broker   | Redis                   | Celery broker + API cache               |
| Email alerts   | Resend                  | Transactional email                     |
| SMS alerts     | Twilio                  | Optional, Phase 7                       |
| Frontend       | Next.js 14 (React)      | App Router, TypeScript                  |
| Deployment     | Railway.app             | All services in one place               |
| Python version | **3.12**                | 3.14 breaks compiled packages           |

---

## What's Built (Phase 1 — Scraping Engine)

### `backend/app/scrapers/base.py`

- `SearchCriteria` dataclass — user's filter params (price, beds, cities, types)
- `RawListing` dataclass — shared schema all scrapers output
- `BaseScraper` abstract class — every scraper implements `fetch_listings()` + `normalise()`
- `BaseScraper.run()` — convenience method that chains both

### `backend/app/scrapers/deduplicator.py`

- `compute_hash(listing)` — MD5 of address + city + price + bedrooms + size_sqft
- `deduplicate(listings)` — removes within-batch dupes; cross-session dedup happens at DB save layer

### `backend/app/scrapers/centris/selectors.py`

- All CSS selectors, XPath, and API URLs for Centris.ca
- Centris category codes (house=1, condo=2, duplex=3, land=5)
- Property type string → enum map (French + English)
- **Only edit this file when Centris changes their site layout**

### `backend/app/scrapers/centris/parser.py`

- `parse_price()` — "$1 250 000" → 1250000
- `parse_bedrooms()` — "3 + 1" → 3, "Studio" → 0
- `parse_area()` — handles both pi² (sqft) and m² (converts to sqft)
- `parse_city()` — strips borough names in parentheses
- `parse_postal_code()` — regex extracts Canadian postal code from address string
- `parse_property_type()` — maps French/English labels → enum

### `backend/app/scrapers/centris/scraper.py`

- `CentrisScraper(headless, max_pages)` — main scraper class
- Rotates user agents, sets fr-CA locale, randomises delays (2–5s)
- POSTs filters to Centris internal JSON API (`/property/UpdateQuery`)
- Paginates via "Next" button clicks
- Scrolls page to trigger lazy-loaded cards
- `normalise()` maps raw dicts → `RawListing` using parser helpers

### `backend/app/scrapers/__init__.py`

- `SOURCE_REGISTRY` dict — maps source name → scraper class
- `get_scraper(name)` — instantiates the right scraper by name
- **To add a new source:** add the folder, implement `BaseScraper`, register here

---

## What's Next (Phase 2)

Build the FastAPI backend + PostgreSQL schema:

### Database models to create (`backend/app/models/`)

**`listings` table:**

- id (UUID PK), source, external_id, title, address, city, region, postal_code
- price (int CAD), bedrooms, bathrooms, size_sqft
- property_type (enum: house/condo/duplex/land/other)
- listing_url, images (JSONB), description
- content_hash (MD5, used for dedup), first_seen_at, last_seen_at

**`search_profiles` table:**

- id (UUID PK), name, min_price, max_price, min_bedrooms
- cities (JSONB array), property_types (JSONB array), sources (JSONB array)
- is_active (bool), created_at

**`notifications` table:**

- id (UUID PK), listing_id (FK), profile_id (FK)
- channel (enum: email/sms), sent_at, status (enum: sent/failed)

**`sources` table:**

- id (UUID PK), name (unique), display_name, is_enabled
- scrape_interval_minutes (default 30), last_scraped_at, total_listings_found

### API endpoints to create (`backend/app/routers/`)

- `GET /listings` — paginated, filterable
- `GET /listings/{id}`
- `GET /sources` + `POST /sources/{name}/trigger`
- `GET/POST/PUT/DELETE /profiles`
- `GET /notifications`
- `GET /stats`

### DB connection string format (psycopg3):

```
postgresql+psycopg://user:password@host:5432/dbname
```

Note: `+psycopg` not `+psycopg2` — this is psycopg3.

---

## Scraper Plugin Contract

To add a new source (e.g. DuProprio), create `backend/app/scrapers/duproprio/` with:

```python
# scraper.py
from ..base import BaseScraper, SearchCriteria, RawListing

class DuProprioScraper(BaseScraper):
    source_name = "duproprio"

    async def fetch_listings(self, criteria: SearchCriteria) -> list[dict]:
        # Playwright logic here
        ...

    def normalise(self, raw: list[dict]) -> list[RawListing]:
        # Map site fields → RawListing
        ...
```

Then in `backend/app/scrapers/__init__.py`:

```python
from .duproprio import DuProprioScraper
SOURCE_REGISTRY["duproprio"] = DuProprioScraper
```

That's it. Nothing else changes.

---

## Environment Variables

```bash
# backend/.env (copy from .env.example, never commit)
DATABASE_URL=postgresql+psycopg://havre:password@localhost:5432/havre
REDIS_URL=redis://localhost:6379/0
RESEND_API_KEY=re_xxxxxxxxxxxx
NOTIFICATION_EMAIL=you@example.com
API_KEY=your-static-secret-key

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running Locally

```bash
# 1. Start PostgreSQL + Redis
docker-compose up -d

# 2. Backend
cd backend
source venv/Scripts/activate   # Windows Git Bash
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
playwright install chromium

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Start Celery beat scheduler (separate terminal)
celery -A app.tasks.celery_app beat --loglevel=info

# 3. Frontend (once built)
cd frontend
npm install
npm run dev
```

---

## Key Decisions & Rationale

- **Python 3.12 not 3.14** — 3.14 breaks lxml, greenlet, pydantic-core (no pre-built wheels yet)
- **psycopg3 not psycopg2** — async-native, Python 3.12 wheels available, actively maintained
- **Playwright not requests/BS4** — Centris is JS-rendered; static scrapers won't see listings
- **Selectors in separate file** — when sites redesign, only one file needs updating
- **Celery Beat for scheduling** — scrapes run on a cron schedule independent of web requests
- **Content hash dedup** — hashes address+city+price+beds, not URL, so cross-source dupes are caught
- **Railway for deployment** — handles Postgres, Redis, multiple service processes with minimal config

---

## Development Phases

| Phase | Status     | Description                                                  |
| ----- | ---------- | ------------------------------------------------------------ |
| 1     | ✅ Done    | Scraping engine — BaseScraper, deduplicator, Centris scraper |
| 2     | 🔨 Next    | FastAPI backend + PostgreSQL schema + Alembic migrations     |
| 3     | ⬜ Pending | DuProprio + Kijiji scrapers                                  |
| 4     | ⬜ Pending | Next.js frontend — listing grid, detail page, filters        |
| 5     | ⬜ Pending | Search profiles UI, notification history, source management  |
| 6     | ⬜ Pending | Deploy to Railway                                            |
| 7     | ⬜ Pending | Polish — map view, photo gallery, SMS via Twilio             |
