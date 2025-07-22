"""Main FastAPI application for the Solution Guide Generator."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers.api import router as api_router

# Initialize settings
try:
    settings = get_settings()
except Exception:
    # Fallback for development/testing
    class MockSettings:
        debug = True
        log_level = "INFO"
        glean_instance = "test-instance"

    settings = MockSettings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting Solution Guide Generator application")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Glean instance: {settings.glean_instance}")

    # Validate environment on startup
    try:
        from app.services.guide_generator import GuideGenerator

        generator = GuideGenerator()
        validation = await generator.validate_environment()

        if all(validation.values()):
            logger.info("Environment validation successful")
        else:
            logger.warning(f"Environment validation issues: {validation}")
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Solution Guide Generator application")


# Create FastAPI application
app = FastAPI(
    title="Solution Guide Generator",
    description="Generate technical solution guides from call transcripts using Glean API",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend application."""
    try:
        with open("app/static/index.html") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Solution Guide Generator</title></head>
                <body>
                    <h1>Solution Guide Generator</h1>
                    <p>Frontend not yet available. Use the API at <a href="/docs">/docs</a></p>
                </body>
            </html>
            """
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )
