"""
main.py — Havre FastAPI application entrypoint
"""

from contextlib import asynccontextmanager
import sys, asyncio

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .models import Listing, SearchProfile, Notification, Source  # ensure models are registered
from .routers import listings, profiles, sources, stats


# psycopg3 requires SelectorEventLoop on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# ── Startup / shutdown ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (dev only — use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed sources table if empty
    await _seed_sources()

    yield

    await engine.dispose()


async def _seed_sources():
    """Ensures known scrapers are registered in the sources table."""
    from .database import AsyncSessionLocal
    from sqlalchemy import select

    sources_data = [
        {"name": "centris", "display_name": "Centris.ca", "scrape_interval_minutes": 30},
        {"name": "duproprio", "display_name": "DuProprio", "scrape_interval_minutes": 45},
        {"name": "kijiji", "display_name": "Kijiji Immobilier", "scrape_interval_minutes": 60},
    ]

    async with AsyncSessionLocal() as db:
        for s in sources_data:
            result = await db.execute(select(Source).where(Source.name == s["name"]))
            if not result.scalar_one_or_none():
                db.add(Source(**s))
        await db.commit()


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Havre API",
    description="Unified real estate search platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API key auth ───────────────────────────────────────────────────────────────

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


# ── Routers ────────────────────────────────────────────────────────────────────

# Public health check — no auth needed
@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}


# Protected routes
app.include_router(listings.router, dependencies=[Depends(verify_api_key)])
app.include_router(profiles.router, dependencies=[Depends(verify_api_key)])
app.include_router(sources.router,  dependencies=[Depends(verify_api_key)])
app.include_router(stats.router,    dependencies=[Depends(verify_api_key)])