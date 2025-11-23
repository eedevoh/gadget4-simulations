"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_reload: bool = False

    # Database
    database_url: str = "postgresql://gadget4:gadget4@postgres:5432/gadget4"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # Cloud Storage
    gcs_bucket: Optional[str] = None  # Google Cloud Storage bucket name
    s3_bucket: Optional[str] = None   # AWS S3 bucket name
    storage_type: str = "gcs"  # "gcs" or "s3"

    # Environment
    environment: str = "development"  # "development", "beta", "production"

    # Logging
    log_level: str = "INFO"

    # Simulation Settings
    max_simulation_time: int = 3600  # Max time per simulation in seconds
    default_particles: int = 1000000  # Default number of particles


# Global settings instance
settings = Settings()
