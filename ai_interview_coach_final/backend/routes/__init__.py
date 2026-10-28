from backend.routes.auth import router as auth_router
from backend.routes.profile import router as profile_router
from backend.routes.interviews import router as interviews_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.reports import router as reports_router
from backend.routes.seed import router as seed_router

__all__ = [
    "auth_router",
    "profile_router",
    "interviews_router",
    "dashboard_router",
    "reports_router",
    "seed_router"
]
