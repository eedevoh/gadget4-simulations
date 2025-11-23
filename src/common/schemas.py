"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from .models import JobStatus


class SimulationJobCreate(BaseModel):
    """Schema for creating a new simulation job."""
    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    num_particles: int = Field(..., gt=0, description="Number of particles")
    box_size: float = Field(..., gt=0, description="Simulation box size in Mpc/h")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional Gadget4 parameters")


class SimulationJobUpdate(BaseModel):
    """Schema for updating a simulation job."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    progress: Optional[float] = Field(None, ge=0, le=100)


class SimulationJobResponse(BaseModel):
    """Schema for simulation job response."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    status: JobStatus
    progress: float
    num_particles: int
    box_size: float
    parameters: Optional[Dict[str, Any]]
    result_path: Optional[str]
    output_files: Optional[List[str]]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    celery_task_id: Optional[str]
    error_message: Optional[str]


class SimulationJobList(BaseModel):
    """Schema for list of simulation jobs."""
    jobs: List[SimulationJobResponse]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
