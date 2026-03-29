"""
FraudShield AI — Backend API
Production-grade FastAPI application for fraud detection in banking transactions.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .core.config import settings
from .core.database import init_db
from .routers import auth, transactions, fraud, analytics, websocket

# ─── Logging Configuration ────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Rate Limiter ─────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─── Lifespan ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize database tables
    await init_db()
    logger.info("Database initialized")

    yield

    logger.info("Shutting down...")


# ─── Application Factory ──────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Production-grade AI-powered fraud detection system for banking transactions. "
        "Provides real-time fraud scoring, risk categorization, and audit trails."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Authentication", "description": "User registration, login, and token management"},
        {"name": "Transactions", "description": "Transaction ingestion and querying"},
        {"name": "Fraud Detection", "description": "Fraud alerts, logs, and manual review"},
        {"name": "Analytics", "description": "Dashboard KPIs and trend data"},
        {"name": "WebSocket", "description": "Real-time fraud alert streaming"},
        {"name": "System", "description": "Health checks and system info"},
    ],
)

# ─── Middleware ────────────────────────────────────

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ─── Global Error Handler ─────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ─── Register Routers ─────────────────────────────
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(fraud.router)
app.include_router(analytics.router)
app.include_router(websocket.router)


# ─── System Endpoints ─────────────────────────────
@app.get("/", tags=["System"])
async def root():
    """API root — service information."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
