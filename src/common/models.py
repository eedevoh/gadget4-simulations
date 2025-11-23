"""Database models for simulation jobs."""

from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.sql import func

from .database import Base


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SimulationJob(Base):
    """Simulation job model."""
    __tablename__ = "simulation_jobs"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Status
    status = Column(
        SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True
    )
    progress = Column(Float, default=0.0)  # 0.0 to 100.0

    # Simulation parameters
    num_particles = Column(Integer, nullable=False)
    box_size = Column(Float, nullable=False)  # Mpc/h
    parameters = Column(JSON, nullable=True)  # Additional Gadget4 parameters

    # Results
    result_path = Column(String, nullable=True)  # Path in GCS/S3
    output_files = Column(JSON, nullable=True)  # List of output files

    # Timing
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Celery task
    celery_task_id = Column(String, nullable=True, index=True)

    # Error tracking
    error_message = Column(String, nullable=True)
    error_traceback = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<SimulationJob(id={self.id}, name={self.name}, status={self.status})>"
