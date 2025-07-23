"""Application configuration management."""

import logging

from pydantic_settings import BaseSettings


def setup_logging(log_level: str = "INFO") -> None:
    """Setup human-readable logging configuration."""
    # Configure the root logger with a more detailed format
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,  # Override any existing configuration
    )

    # Set specific log levels for external libraries to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("glean").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"🔧 Logging configured at level: {log_level}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    This class automatically loads configuration from environment variables
    or .env files, providing type validation and sensible defaults.
    """

    glean_instance: str
    glean_api_token: str
    debug: bool = False
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


# Global settings instance - lazy loaded to allow for testing
def get_settings() -> Settings:
    """Get settings instance, creating it if needed."""
    logger = logging.getLogger(__name__)
    try:
        settings = Settings()
        logger.info(f"✅ Configuration loaded successfully for instance: {settings.glean_instance}")
        return settings
    except Exception as e:
        logger.error(f"❌ Failed to load configuration: {e}")
        raise


# For convenience, create a settings instance at module level
# This can be overridden in tests by mocking the Settings class
try:
    settings = Settings()
except Exception:
    # Allow module to be imported even without proper environment configuration
    # This is useful for testing and development
    settings = None
