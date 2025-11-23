# Quick Start Guide

Get your multi-simulator platform running in minutes!

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- kubectl (for Kubernetes deployment)
- Access to a Kubernetes cluster (optional, for production)

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd gadget4-simulations

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Start Services with Docker Compose

The project includes a `docker-compose.yml` file at the root. Simply run:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis queue
- FastAPI API
- 2x Gadget4 workers
- 1x CONCEPT worker

### 3. Initialize Database

```bash
# Run database migration to add simulator_type column
python alembic_migration_add_simulator_type.py

# Or create tables directly
python -c "from src.common.database import engine, Base; from src.common.models import *; Base.metadata.create_all(engine)"
```

### 4. Test the API

```bash
# Check health
curl http://localhost:8000/health

# Submit a CONCEPT simulation (fast)
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test CONCEPT simulation",
    "simulator_type": "concept",
    "num_particles": 10000,
    "box_size": 50.0
  }'

# List jobs
curl http://localhost:8000/api/v1/jobs
```

## Building Docker Images

### Build All Images

```bash
# API
docker build -f docker/Dockerfile.api -t gadget4-api:latest .

# Workers
docker build -f docker/Dockerfile.worker-gadget4 -t gadget4-worker-gadget4:latest .
docker build -f docker/Dockerfile.worker-concept -t gadget4-worker-concept:latest .

# Simulator base images (optional)
docker build -f docker/Dockerfile.gadget4 -t gadget4-base:latest .
docker build -f docker/Dockerfile.concept -t concept-base:latest .
```

### Push to Registry

```bash
# Tag images
docker tag gadget4-api:latest gcr.io/your-project/gadget4-api:latest
docker tag gadget4-worker-gadget4:latest gcr.io/your-project/gadget4-worker-gadget4:latest
docker tag gadget4-worker-concept:latest gcr.io/your-project/gadget4-worker-concept:latest

# Push to GCR
docker push gcr.io/your-project/gadget4-api:latest
docker push gcr.io/your-project/gadget4-worker-gadget4:latest
docker push gcr.io/your-project/gadget4-worker-concept:latest
```

## Kubernetes Deployment

### Deploy to Beta Environment

```bash
# Apply beta configuration
kubectl apply -k k8s/overlays/beta/

# Check deployment status
kubectl get pods -n gadget4-beta

# Watch logs
kubectl logs -f deployment/gadget4-worker -n gadget4-beta
kubectl logs -f deployment/concept-worker -n gadget4-beta
```

### Deploy to Stable (Production)

```bash
# Apply stable configuration
kubectl apply -k k8s/overlays/stable/

# Check status
kubectl get pods -n gadget4-stable
```

### Scale Workers

```bash
# Scale Gadget4 workers
kubectl scale deployment gadget4-worker --replicas=5 -n gadget4-stable

# Scale CONCEPT workers
kubectl scale deployment concept-worker --replicas=3 -n gadget4-stable
```

## Example Usage

### Python Client

```python
import requests
import time

API_URL = "http://localhost:8000"

# Submit a Gadget4 job
response = requests.post(
    f"{API_URL}/api/v1/jobs",
    json={
        "name": "My first Gadget4 simulation",
        "simulator_type": "gadget4",
        "num_particles": 1000000,
        "box_size": 100.0,
        "parameters": {
            "TimeMax": 1.0,
            "Omega0": 0.3,
            "OmegaLambda": 0.7
        }
    }
)

job = response.json()
job_id = job["id"]
print(f"Job submitted: {job_id}")

# Poll for completion
while True:
    response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
    job = response.json()
    status = job["status"]
    progress = job["progress"]
    
    print(f"Status: {status}, Progress: {progress}%")
    
    if status in ["completed", "failed", "cancelled"]:
        break
    
    time.sleep(5)

print(f"Final status: {status}")
if status == "completed":
    print(f"Results: {job['result_path']}")
```

### Compare Simulators

```python
import requests
from concurrent.futures import ThreadPoolExecutor

API_URL = "http://localhost:8000"

def submit_job(simulator_type, name):
    response = requests.post(
        f"{API_URL}/api/v1/jobs",
        json={
            "name": name,
            "simulator_type": simulator_type,
            "num_particles": 100000,
            "box_size": 50.0
        }
    )
    return response.json()

# Submit jobs to both simulators
with ThreadPoolExecutor() as executor:
    gadget4_future = executor.submit(submit_job, "gadget4", "Gadget4 test")
    concept_future = executor.submit(submit_job, "concept", "CONCEPT test")
    
    gadget4_job = gadget4_future.result()
    concept_job = concept_future.result()

print(f"Gadget4 job: {gadget4_job['id']}")
print(f"CONCEPT job: {concept_job['id']}")
```

## Monitoring

### View Logs

```bash
# Docker Compose
docker-compose logs -f api
docker-compose logs -f worker-gadget4
docker-compose logs -f worker-concept

# Kubernetes
kubectl logs -f deployment/api -n gadget4-beta
kubectl logs -f deployment/gadget4-worker -n gadget4-beta
kubectl logs -f deployment/concept-worker -n gadget4-beta
```

### Check Celery Status

```bash
# Connect to a worker container
docker exec -it <worker-container-id> bash

# Check Celery status
celery -A src.workers.worker inspect active
celery -A src.workers.worker inspect stats
```

## Troubleshooting

### API not starting
- Check database connection: `docker-compose logs postgres`
- Verify environment variables in docker-compose.yml

### Workers not processing jobs
- Check Redis connection: `docker-compose logs redis`
- Verify worker logs: `docker-compose logs worker-gadget4`
- Check Celery queues: See "Check Celery Status" above

### Simulations failing
- Check worker logs for specific errors
- Verify simulator binaries are present in Docker images
- Check resource limits (memory, CPU)

### Database migration errors
- Reset database: `docker-compose down -v` (WARNING: deletes data)
- Recreate tables: See "Initialize Database" section

## Next Steps

1. Read [SIMULATORS.md](SIMULATORS.md) for detailed simulator documentation
2. Explore API documentation at `http://localhost:8000/docs`
3. Set up monitoring with Prometheus/Grafana
4. Configure cloud storage for results (GCS/S3)
5. Set up CI/CD pipeline for automated deployments

## Resources

- [Main README](../README.md) - Project overview
- [SIMULATORS.md](SIMULATORS.md) - Simulator guide
- [BUILD.md](BUILD.md) - Build and deployment guide
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Kubernetes Docs](https://kubernetes.io/docs/) - K8s documentation

## Support

For issues or questions:
- Check existing GitHub issues
- Create a new issue with detailed description
- Include logs and error messages

