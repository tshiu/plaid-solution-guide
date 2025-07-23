"""Application configuration management."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    This class automatically loads configuration from environment variables
    or .env files, providing type validation and sensible defaults.
    """

    glean_instance: str
    glean_api_token: str
    debug: bool = False
    log_level: str = "INFO"

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8", "case_sensitive": False}


# Global settings instance - lazy loaded to allow for testing
def get_settings() -> Settings:
    """Get settings instance, creating it if needed."""
    return Settings()


# For convenience, create a settings instance at module level
# This can be overridden in tests by mocking the Settings class
try:
    settings = Settings()
except Exception:
    # Allow module to be imported even without proper environment configuration
    # This is useful for testing and development
    settings = None
