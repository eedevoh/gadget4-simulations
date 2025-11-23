"""API endpoints for simulation jobs."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.database import get_db
from common.models import SimulationJob, JobStatus
from common.schemas import (
    SimulationJobCreate,
    SimulationJobResponse,
    SimulationJobList,
)


router = APIRouter()


@router.post(
    "/jobs",
    response_model=SimulationJobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(job: SimulationJobCreate, db: Session = Depends(get_db)):
    """Create a new simulation job."""
    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Create job in database
    db_job = SimulationJob(
        id=job_id,
        name=job.name,
        description=job.description,
        num_particles=job.num_particles,
        box_size=job.box_size,
        parameters=job.parameters,
        status=JobStatus.PENDING,
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # TODO: Submit job to Celery worker
    # from workers.tasks import run_simulation
    # task = run_simulation.delay(job_id)
    # db_job.celery_task_id = task.id
    # db.commit()

    return db_job


@router.get("/jobs", response_model=SimulationJobList)
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: JobStatus | None = None,
    db: Session = Depends(get_db),
):
    """List all simulation jobs with optional filtering."""
    query = db.query(SimulationJob)

    # Apply status filter if provided
    if status_filter:
        query = query.filter(SimulationJob.status == status_filter)

    # Get total count
    total = query.count()

    # Apply pagination
    jobs = (
        query.order_by(SimulationJob.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return SimulationJobList(
        jobs=jobs,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
    )


@router.get("/jobs/{job_id}", response_model=SimulationJobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get details of a specific simulation job."""
    job = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    return job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """Cancel a simulation job."""
    job = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    if job.status in [
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job in {job.status} state",
        )

    # TODO: Cancel Celery task
    # if job.celery_task_id:
    #     from celery import current_app
    #     current_app.control.revoke(job.celery_task_id, terminate=True)

    job.status = JobStatus.CANCELLED
    db.commit()

    return None
