"""Celery tasks for Gadget4 simulations."""

from celery import Task
from datetime import datetime
import subprocess
import logging
from pathlib import Path

from workers.worker import app
from common.database import SessionLocal
from common.models import SimulationJob, JobStatus

logger = logging.getLogger(__name__)


class SimulationTask(Task):
    """Base task for simulations with automatic state updates."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        job_id = args[0] if args else None
        if job_id:
            db = SessionLocal()
            try:
                job = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()
                if job:
                    job.status = JobStatus.FAILED
                    job.error_message = str(exc)
                    job.error_traceback = str(einfo)
                    job.completed_at = datetime.utcnow()
                    db.commit()
            finally:
                db.close()


@app.task(base=SimulationTask, bind=True)
def run_simulation(self, job_id: str):
    """
    Run a Gadget4 N-body simulation.

    Args:
        job_id: UUID of the simulation job
    """
    db = SessionLocal()
    try:
        # Get job from database
        job = db.query(SimulationJob).filter(SimulationJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        logger.info(f"Starting simulation job {job_id}: {job.name}")

        # Update job status to running
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.commit()

        # Create working directory
        work_dir = Path(f"/tmp/gadget4/{job_id}")
        work_dir.mkdir(parents=True, exist_ok=True)

        # Generate Gadget4 parameter file
        param_file = work_dir / "params.txt"
        generate_parameter_file(param_file, job)

        # TODO: Run Gadget4 simulation
        # This is a placeholder - actual Gadget4 execution will be implemented
        # result = subprocess.run(
        #     ["gadget4", str(param_file)],
        #     cwd=work_dir,
        #     capture_output=True,
        #     text=True,
        #     check=True,
        # )

        # Simulate progress updates
        for progress in [25, 50, 75, 100]:
            job.progress = float(progress)
            db.commit()
            self.update_state(state="PROGRESS", meta={"progress": progress})

        # TODO: Upload results to cloud storage
        # result_path = upload_results(work_dir, job_id)
        result_path = f"gs://gadget4-results/{job_id}/"  # Placeholder

        # Update job as completed
        job.status = JobStatus.COMPLETED
        job.progress = 100.0
        job.result_path = result_path
        job.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Simulation job {job_id} completed successfully")

        return {
            "job_id": job_id,
            "status": "completed",
            "result_path": result_path,
        }

    except Exception as e:
        logger.error(f"Simulation job {job_id} failed: {e}")
        raise
    finally:
        db.close()


def generate_parameter_file(param_file: Path, job: SimulationJob):
    """Generate Gadget4 parameter file from job configuration."""
    # This is a simplified example - real parameter file will be more complex
    params = f"""
BoxSize              {job.box_size}
ParticleNumber       {job.num_particles}
OutputDir            ./output
TimeBetSnapshot      0.1
TimeMax              1.0
    """

    # Add any additional parameters from job.parameters
    if job.parameters:
        for key, value in job.parameters.items():
            params += f"{key}    {value}\n"

    param_file.write_text(params)
    logger.info(f"Generated parameter file: {param_file}")
