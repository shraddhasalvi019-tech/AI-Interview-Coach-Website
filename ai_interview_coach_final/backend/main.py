import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi import Request

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import settings
from backend.database import init_db
from backend.routes import (
    auth_router,
    profile_router,
    interviews_router,
    dashboard_router,
    reports_router,
    seed_router
)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Production-grade academic software system for intelligent interview preparation, "
        "dynamic GenAI question generation, multi-dimensional scoring, skill-gap analysis, "
        "and candidate coaching using Cloud-based Large Language Models."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

from backend.services.ai_service import ai_service, AIServiceError

@app.exception_handler(AIServiceError)
async def ai_service_error_handler(request: Request, exc: AIServiceError):
    return JSONResponse(
        status_code=503,
        content={"detail": f"AI service unavailable: {exc}"}
    )

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print(f"[STARTUP] Initializing {settings.APP_NAME}...")
    init_db()
    print("[STARTUP] Application startup completed successfully.")

# Include API Routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(interviews_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(seed_router)

# Serve Frontend Static Files if frontend directory exists
frontend_path = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(frontend_path):
    class NoCacheStaticFiles(StaticFiles):
        """Always serve the latest HTML/JS so the browser never runs a stale copy."""
        async def get_response(self, path, scope):
            response = await super().get_response(path, scope)
            response.headers["Cache-Control"] = "no-store, max-age=0"
            return response

    app.mount("/app", NoCacheStaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "OPERATIONAL",
        "app_name": settings.APP_NAME,
        "genai_provider": settings.GENAI_PROVIDER,
        "genai_model": settings.GENAI_MODEL,
        "docs": "/docs"
    }

@app.get("/api/health/ai", tags=["Health"])
def ai_health_check():
    """Makes a real Gemini call to verify the API key / model are working."""
    try:
        ai_service._call_llm('Reply with this JSON only: {"ok": true}')
        idx, model = ai_service._working
        return {"gemini_working": True, "mode": ai_service.clients[idx][0], "model": model}
    except AIServiceError as e:
        return {"gemini_working": False, "error": str(e)}

@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "status": "OPERATIONAL",
        "swagger_docs": "/docs",
        "web_app": "/app/index.html"
    }
