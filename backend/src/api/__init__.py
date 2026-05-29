"""API routes"""

from .chemicals import router as chemicals_router
from .facilities import router as facilities_router
from .scenarios import router as scenarios_router
from .calculations import router as calculations_router

__all__ = ["chemicals_router", "facilities_router", "scenarios_router", "calculations_router"]
