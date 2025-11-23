# Gadget4 Simulations

Distributed N-body cosmological simulations platform built on Kubernetes.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   FastAPI       │────▶│   Redis/Celery   │────▶│  Workers Pool   │
│   REST API      │     │   Task Queue     │     │  (Gadget4 runs) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                                 │
         │                                                 │
         ▼                                                 ▼
┌─────────────────┐                              ┌─────────────────┐
│   PostgreSQL    │◀─────────────────────────────│   GCS/S3        │
│   Metadata DB   │                              │   Results       │
└─────────────────┘                              └─────────────────┘
```

## Components

### API (`src/api/`)
FastAPI REST API for:
- Submitting simulation jobs
- Monitoring job status
- Retrieving results
- Managing simulation parameters

### Workers (`src/workers/`)
Celery workers that:
- Execute Gadget4 simulations
- Handle distributed computation
- Store results to object storage
- Update job status in database

### Common (`src/common/`)
Shared code:
- Database models (SQLAlchemy)
- Configuration management
- Utilities and helpers

## Technology Stack

- **API**: FastAPI, Pydantic, SQLAlchemy
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL
- **Storage**: Google Cloud Storage (GCP) / S3 (AWS)
- **Container**: Docker multi-stage builds
- **Orchestration**: Kubernetes + ArgoCD (GitOps)
- **Simulation**: Gadget4 N-body code

## Development

### Prerequisites
- Python 3.11+
- Docker
- kubectl (for local K8s testing)

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run API locally
cd src/api
uvicorn main:app --reload

# Run worker locally
cd src/workers
celery -A worker worker --loglevel=info
```

### Docker Build

```bash
# Build API
docker build -f docker/Dockerfile.api -t gadget4-api:latest .

# Build Worker
docker build -f docker/Dockerfile.worker -t gadget4-worker:latest .
```

## Deployment

Deployment is managed via GitOps with ArgoCD:

1. **Code changes** → Push to `main` or `develop`
2. **CI/CD** → Build Docker images, push to GCR/ECR
3. **Update manifests** → Update image tags in `k8s/overlays/`
4. **ArgoCD sync** → Automatic deployment to cluster

### Environments

- **Beta** (`overlays/beta/`): Development/testing environment
- **Stable** (`overlays/stable/`): Production environment

## API Endpoints

### Jobs

- `POST /api/v1/jobs` - Submit new simulation
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/{job_id}` - Get job details
- `DELETE /api/v1/jobs/{job_id}` - Cancel job

### Simulations

- `GET /api/v1/simulations/{job_id}/status` - Get simulation status
- `GET /api/v1/simulations/{job_id}/results` - Download results
- `GET /api/v1/simulations/{job_id}/logs` - View logs

### Health

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Configuration

Environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/gadget4

# Redis
REDIS_URL=redis://redis:6379/0

# Storage
GCS_BUCKET=gadget4-results  # GCP
# or
S3_BUCKET=gadget4-results    # AWS

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Monitoring

- **Metrics**: Prometheus + Grafana
- **Logs**: Loki or Cloud Logging
- **Tracing**: (Future) OpenTelemetry

## License

MIT

## Related Repositories

- [gadget4-on-cloud](https://github.com/eedevoh/gadget4-on-cloud) - Infrastructure as Code (Pulumi + K8s)
