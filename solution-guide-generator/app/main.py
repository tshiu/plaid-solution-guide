"""Main FastAPI application entry point."""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings, setup_logging
from app.routers.api import router as api_router

# Initialize settings and logging
try:
    settings = get_settings()
    setup_logging(settings.log_level)
except Exception:
    # Fallback for development/testing
    class MockSettings:
        debug = True
        log_level = "INFO"
        glean_instance = "test-instance"

    settings = MockSettings()
    setup_logging("INFO")

logger = logging.getLogger(__name__)

# Get the absolute path to the static directory
STATIC_DIR = Path(__file__).parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"


# Add request logging middleware
async def log_requests(request: Request, call_next):
    """Middleware to log all HTTP requests and responses."""
    start_time = time.time()

    # Log incoming request
    logger.info(f"📥 Incoming {request.method} request to {request.url.path}")
    if request.query_params:
        logger.info(f"   Query params: {dict(request.query_params)}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} → {response.status_code} ({process_time:.3f}s)")

    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting Solution Guide Generator...")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info(f"🔧 Log level: {settings.log_level}")

    # Verify static files exist
    if not STATIC_DIR.exists():
        logger.warning(f"⚠️  Static directory not found: {STATIC_DIR}")
    if not INDEX_FILE.exists():
        logger.warning(f"⚠️  Index file not found: {INDEX_FILE}")
    else:
        logger.info(f"✅ Static files found at: {STATIC_DIR}")

    # Validate environment (optional, non-blocking)
    try:
        logger.info("🔍 Validating environment configuration...")
        from app.services.guide_generator import GuideGenerator

        generator = GuideGenerator()
        validation = await generator.validate_environment()

        if validation.get("configuration"):
            logger.info("✅ Environment validation passed - all systems ready")
            if validation.get("connectivity"):
                logger.info("✅ Glean API connectivity confirmed")
            else:
                logger.warning("⚠️  Glean API connectivity test failed")
        else:
            logger.warning("⚠️  Environment validation failed - check your .env file")
            logger.warning("   Make sure GLEAN_INSTANCE and GLEAN_API_TOKEN are set correctly")
    except Exception as e:
        logger.warning(f"⚠️  Environment validation skipped due to error: {e}")

    logger.info("🎉 Application startup complete - ready to serve requests")
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

# Add request logging middleware
app.middleware("http")(log_requests)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"🌐 CORS configured for {'all origins (debug mode)' if settings.debug else 'localhost only'}")

# Include API routes
app.include_router(api_router)
logger.info("🛤️  API routes mounted at /api/v1")

# Mount static files - only if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info(f"📁 Static files mounted from: {STATIC_DIR}")
else:
    logger.error(f"❌ Static directory not found: {STATIC_DIR}")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend application."""
    logger.info("🏠 Serving frontend application")
    try:
        if INDEX_FILE.exists():
            logger.info("✅ Serving index.html from static directory")
            return HTMLResponse(content=INDEX_FILE.read_text(encoding="utf-8"))
        else:
            logger.error(f"❌ Index file not found: {INDEX_FILE}")
            raise FileNotFoundError(f"Index file not found: {INDEX_FILE}")
    except FileNotFoundError:
        logger.warning("⚠️  Serving fallback frontend (static files missing)")
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
    logger.info("❤️  Health check requested")

    health_data = {
        "status": "healthy",
        "version": "0.1.0",
        "static_files": {
            "directory_exists": STATIC_DIR.exists(),
            "index_exists": INDEX_FILE.exists(),
            "static_path": str(STATIC_DIR),
        },
    }

    logger.info(f"❤️  Health check results: {health_data['status']}")
    return health_data


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"💥 UNHANDLED EXCEPTION on {request.method} {request.url}")
    logger.error(f"   Exception type: {type(exc).__name__}")
    logger.error(f"   Exception message: {str(exc)}")

    if settings.debug:
        import traceback

        logger.error("   Full traceback:")
        for line in traceback.format_exc().split("\n"):
            if line.strip():
                logger.error(f"     {line}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred",
            "error": str(exc) if settings.debug else "Internal server error",
        },
    )
