"""Routes package exports."""

from app.routes.matching_routes import router as matching_router
from app.routes.health_routes import router as health_router

__all__ = ["matching_router", "health_router"]
