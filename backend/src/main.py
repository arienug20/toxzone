"""FastAPI application factory"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db, close_db


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    print("Starting ToxZone Backend...")
    init_db()
    print("Database initialized")
    yield
    print("Shutting down ToxZone Backend...")
    close_db()
    print("Database connection closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="ToxZone API",
        description="Emergency Exposure Boundary Planner API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from .api import chemicals, facilities, scenarios, calculations

    app.include_router(chemicals.router, prefix="/api/v1/chemicals", tags=["Chemicals"])
    app.include_router(facilities.router, prefix="/api/v1/facilities", tags=["Facilities"])
    app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["Scenarios"])
    app.include_router(calculations.router, prefix="/api/v1/calculations", tags=["Calculations"])

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "0.1.0"}

    @app.get("/")
    async def root():
        return {
            "name": "ToxZone API",
            "version": "0.1.0",
            "description": "Emergency Exposure Boundary Planner",
            "docs": "/docs",
        }

    return app


app = create_app()
