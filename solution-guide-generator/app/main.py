"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

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

# Get the absolute path to the static directory
STATIC_DIR = Path(__file__).parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Solution Guide Generator...")

    # Verify static files exist
    if not STATIC_DIR.exists():
        logger.warning(f"Static directory not found: {STATIC_DIR}")
    if not INDEX_FILE.exists():
        logger.warning(f"Index file not found: {INDEX_FILE}")
    else:
        logger.info(f"✅ Static files found at: {STATIC_DIR}")

    # Validate environment (optional, non-blocking)
    try:
        from app.services.guide_generator import GuideGenerator

        generator = GuideGenerator()
        validation = await generator.validate_environment()
        if validation.get("configuration"):
            logger.info("✅ Environment validation passed")
        else:
            logger.warning("⚠️ Environment validation failed - check your .env file")
    except Exception as e:
        logger.warning(f"⚠️ Environment validation skipped: {e}")

    yield

    # Shutdown
    logger.info("👋 Shutting down Solution Guide Generator...")


# Create FastAPI app
app = FastAPI(
    title="Solution Guide Generator",
    description="Generate technical solution guides from call transcripts using Glean API",
    version="0.1.0",
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

# Mount static files - only if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info(f"📁 Static files mounted from: {STATIC_DIR}")
else:
    logger.error(f"❌ Static directory not found: {STATIC_DIR}")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend application."""
    try:
        if INDEX_FILE.exists():
            return HTMLResponse(content=INDEX_FILE.read_text(encoding="utf-8"))
        else:
            logger.error(f"Index file not found: {INDEX_FILE}")
            raise FileNotFoundError(f"Index file not found: {INDEX_FILE}")
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Solution Guide Generator</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                               max-width: 800px; margin: 2rem auto; padding: 2rem;
                               line-height: 1.6; color: #333; }
                        .error { background: #fee; border: 1px solid #fcc;
                                border-radius: 4px; padding: 1rem; margin: 1rem 0; }
                        a { color: #0066cc; }
                    </style>
                </head>
                <body>
                    <h1>🚧 Solution Guide Generator</h1>
                    <div class="error">
                        <h3>Frontend files not found</h3>
                        <p>The static frontend files are not available. This usually means:</p>
                        <ul>
                            <li>The application wasn't installed properly</li>
                            <li>Static files weren't included in the package</li>
                        </ul>
                        <p><strong>You can still use the API:</strong></p>
                        <ul>
                            <li><a href="/docs">Interactive API Documentation</a></li>
                            <li><a href="/health">Health Check</a></li>
                        </ul>
                    </div>
                </body>
            </html>
            """,
            status_code=503,
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "static_files": {
            "directory_exists": STATIC_DIR.exists(),
            "index_exists": INDEX_FILE.exists(),
            "static_path": str(STATIC_DIR),
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred",
            "error": str(exc) if settings.debug else "Internal server error",
        },
    )
