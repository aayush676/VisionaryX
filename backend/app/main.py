import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings
from app.core.database import close_database_connection, ensure_indexes
from app.core.limiter import limiter
from app.routers import (
    analytics,
    auth,
    chatbot,
    digital_twin,
    goals,
    habits,
    journals,
    memory,
    notifications,
    simulations,
    users,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Index creation must never block or fail startup: if Mongo is slow or
    # briefly unreachable, the process should still bind its port and serve
    # /health so the platform sees a live service and the failure surfaces as
    # a request-time error instead of an unreachable, silently hanging app.
    try:
        await asyncio.wait_for(ensure_indexes(), timeout=15)
    except Exception as exc:
        print(f"WARNING: index setup skipped ({type(exc).__name__}: {exc})", flush=True)
    yield
    await close_database_connection()


app = FastAPI(
    title="VisionaryX API",
    description="AI-powered Future Self Decision Simulator & Digital Twin Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Too many requests ({exc.detail}). Please wait a moment and try again."},
    )


app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(habits.router)
app.include_router(journals.router)
app.include_router(digital_twin.router)
app.include_router(simulations.router)
app.include_router(chatbot.router)
app.include_router(memory.router)
app.include_router(analytics.router)
app.include_router(notifications.router)


@app.get("/")
async def root():
    return {"name": "VisionaryX API", "status": "online", "tagline": "Predict Possibilities. Shape Reality."}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
