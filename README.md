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
- Execute simulations with **Gadget4** or **CONCEPT**
- Handle distributed computation across multiple simulators
- Store results to object storage
- Update job status in database
- Support dedicated worker pools per simulator type

### Common (`src/common/`)
Shared code:
- Database models (SQLAlchemy)
- Configuration management
- Utilities and helpers

## Supported Simulators

### Gadget4
- State-of-the-art N-body and SPH code
- Highly optimized for large-scale cosmological simulations
- Supports MPI parallelization
- Ideal for: High-resolution dark matter simulations, galaxy formation

### CONCEPT
- COsmological N-body CodE in PyThon
- Python-based with Cython performance optimizations
- Multiple gravitational solvers
- Supports particles and fluid dynamics
- Ideal for: Rapid prototyping, educational purposes, parameter exploration

See [docs/SIMULATORS.md](docs/SIMULATORS.md) for detailed information.

## Technology Stack

- **API**: FastAPI, Pydantic, SQLAlchemy
- **Task Queue**: Celery + Redis (with separate queues per simulator)
- **Database**: PostgreSQL
- **Storage**: Google Cloud Storage (GCP) / S3 (AWS)
- **Container**: Docker multi-stage builds
- **Orchestration**: Kubernetes + ArgoCD (GitOps)
- **Simulators**: Gadget4 & CONCEPT N-body codes

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

# Build Workers
docker build -f docker/Dockerfile.worker-gadget4 -t gadget4-worker-gadget4:latest .
docker build -f docker/Dockerfile.worker-concept -t gadget4-worker-concept:latest .

# Build simulator base images (optional, for testing)
docker build -f docker/Dockerfile.gadget4 -t gadget4-base:latest .
docker build -f docker/Dockerfile.concept -t concept-base:latest .
```

See [docs/BUILD.md](docs/BUILD.md) for detailed build instructions.

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
  - **Query parameters**: `simulator_type` (gadget4|concept)
  - **Example**:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/jobs" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Dark matter simulation",
        "simulator_type": "gadget4",
        "num_particles": 1000000,
        "box_size": 100.0,
        "parameters": {"TimeMax": 1.0}
      }'
    ```
- `GET /api/v1/jobs` - List all jobs
  - **Query parameters**: `status_filter`, `simulator_filter` (gadget4|concept)
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

# Simulator Configuration
SIMULATOR_TYPE=gadget4      # For workers: 'gadget4' or 'concept'
CONCEPT_DIR=/opt/concept    # Required for CONCEPT workers
MAX_SIMULATION_TIME=3600    # Max time per simulation (seconds)
```

See [config.example.env](config.example.env) for complete configuration options.

## Monitoring

- **Metrics**: Prometheus + Grafana
- **Logs**: Loki or Cloud Logging
- **Tracing**: (Future) OpenTelemetry

## License

MIT

## Documentation

All documentation is located in the [`docs/`](docs/) directory:

- **[docs/README.md](docs/README.md)** - Documentation index and overview
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Get started in minutes with Docker Compose
- **[docs/SIMULATORS.md](docs/SIMULATORS.md)** - Detailed guide for Gadget4 and CONCEPT simulators
- **[docs/BUILD.md](docs/BUILD.md)** - Build and deployment instructions
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Version history and changes
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Complete implementation overview
- **[API Documentation](http://localhost:8000/docs)** - Interactive OpenAPI/Swagger docs (when running locally)

## Related Repositories

- [gadget4-on-cloud](https://github.com/eedevoh/gadget4-on-cloud) - Infrastructure as Code (Pulumi + K8s)
