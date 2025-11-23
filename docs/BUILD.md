# Build and Deployment Guide

Comprehensive guide for building and deploying the multi-simulator platform.

## Table of Contents

1. [Local Development Build](#local-development-build)
2. [Docker Image Building](#docker-image-building)
3. [Container Registry](#container-registry)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Troubleshooting](#troubleshooting)

## Local Development Build

### Prerequisites

```bash
# System requirements
- Python 3.11+
- Docker 20.10+
- docker-compose 2.0+
- kubectl 1.25+ (for K8s deployment)
```

### Setup Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Database Setup

```bash
# Start PostgreSQL with Docker
docker run -d \
  --name gadget4-postgres \
  -e POSTGRES_USER=gadget4 \
  -e POSTGRES_PASSWORD=gadget4 \
  -e POSTGRES_DB=gadget4 \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize database
python -c "from src.common.database import engine, Base; from src.common.models import *; Base.metadata.create_all(engine)"

# Run migration to add simulator_type
python alembic_migration_add_simulator_type.py
```

### Start Services Locally

```bash
# Terminal 1: Start Redis
docker run -d --name gadget4-redis -p 6379:6379 redis:7-alpine

# Terminal 2: Start API
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start Gadget4 worker (requires Gadget4 binary)
celery -A src.workers.worker worker \
  --loglevel=info \
  --concurrency=1 \
  --queues=gadget4

# Terminal 4: Start CONCEPT worker (requires CONCEPT installation)
celery -A src.workers.worker worker \
  --loglevel=info \
  --concurrency=1 \
  --queues=concept
```

## Docker Image Building

### Build Order

Build images in this order to optimize layer caching:

1. Base simulator images (optional)
2. Worker images
3. API image

### Build Base Simulator Images

```bash
# Gadget4 base image
docker build \
  -f docker/Dockerfile.gadget4 \
  -t gadget4-base:latest \
  .

# CONCEPT base image
docker build \
  -f docker/Dockerfile.concept \
  -t concept-base:latest \
  .
```

### Build Worker Images

```bash
# Gadget4 worker
docker build \
  -f docker/Dockerfile.worker-gadget4 \
  -t gadget4-worker-gadget4:latest \
  .

# CONCEPT worker
docker build \
  -f docker/Dockerfile.worker-concept \
  -t gadget4-worker-concept:latest \
  .
```

### Build API Image

```bash
docker build \
  -f docker/Dockerfile.api \
  -t gadget4-api:latest \
  .
```

### Build All at Once

```bash
# Build script
cat > build-all.sh << 'EOF'
#!/bin/bash
set -e

echo "Building Gadget4 base..."
docker build -f docker/Dockerfile.gadget4 -t gadget4-base:latest .

echo "Building CONCEPT base..."
docker build -f docker/Dockerfile.concept -t concept-base:latest .

echo "Building Gadget4 worker..."
docker build -f docker/Dockerfile.worker-gadget4 -t gadget4-worker-gadget4:latest .

echo "Building CONCEPT worker..."
docker build -f docker/Dockerfile.worker-concept -t gadget4-worker-concept:latest .

echo "Building API..."
docker build -f docker/Dockerfile.api -t gadget4-api:latest .

echo "✓ All images built successfully!"
docker images | grep gadget4
EOF

chmod +x build-all.sh
./build-all.sh
```

## Container Registry

### Google Container Registry (GCR)

```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Tag images
PROJECT_ID="your-gcp-project-id"
docker tag gadget4-api:latest gcr.io/${PROJECT_ID}/gadget4-api:latest
docker tag gadget4-worker-gadget4:latest gcr.io/${PROJECT_ID}/gadget4-worker-gadget4:latest
docker tag gadget4-worker-concept:latest gcr.io/${PROJECT_ID}/gadget4-worker-concept:latest

# Push images
docker push gcr.io/${PROJECT_ID}/gadget4-api:latest
docker push gcr.io/${PROJECT_ID}/gadget4-worker-gadget4:latest
docker push gcr.io/${PROJECT_ID}/gadget4-worker-concept:latest

# Tag specific versions
VERSION="v1.0.0"
docker tag gadget4-api:latest gcr.io/${PROJECT_ID}/gadget4-api:${VERSION}
docker push gcr.io/${PROJECT_ID}/gadget4-api:${VERSION}
```

### Amazon ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name gadget4-api
aws ecr create-repository --repository-name gadget4-worker-gadget4
aws ecr create-repository --repository-name gadget4-worker-concept

# Tag and push
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com"
docker tag gadget4-api:latest ${REGISTRY}/gadget4-api:latest
docker push ${REGISTRY}/gadget4-api:latest
```

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install kustomize (optional)
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
```

### Configure kubectl

```bash
# For GKE
gcloud container clusters get-credentials <cluster-name> --region <region>

# For EKS
aws eks update-kubeconfig --region <region> --name <cluster-name>

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Create Secrets

```bash
# Database credentials
kubectl create secret generic gadget4-secrets \
  --from-literal=database-url='postgresql://user:pass@postgres:5432/gadget4' \
  -n gadget4-beta

# For production with external database
kubectl create secret generic gadget4-secrets \
  --from-literal=database-url='postgresql://user:pass@external-db-host:5432/gadget4' \
  -n gadget4-stable
```

### Deploy to Beta Environment

```bash
# Update image tags in k8s/overlays/beta/kustomization.yaml
# Then apply
kubectl apply -k k8s/overlays/beta/

# Watch deployment
kubectl get pods -n gadget4-beta -w

# Check logs
kubectl logs -f deployment/api -n gadget4-beta
kubectl logs -f deployment/gadget4-worker -n gadget4-beta
kubectl logs -f deployment/concept-worker -n gadget4-beta
```

### Deploy to Stable Environment

```bash
# Update image tags in k8s/overlays/stable/kustomization.yaml
kubectl apply -k k8s/overlays/stable/

# Monitor rollout
kubectl rollout status deployment/api -n gadget4-stable
kubectl rollout status deployment/gadget4-worker -n gadget4-stable
kubectl rollout status deployment/concept-worker -n gadget4-stable
```

### Update Deployments

```bash
# Update image tag
kubectl set image deployment/api \
  api=gcr.io/${PROJECT_ID}/gadget4-api:v1.0.1 \
  -n gadget4-stable

# Restart deployment
kubectl rollout restart deployment/api -n gadget4-stable

# Rollback if needed
kubectl rollout undo deployment/api -n gadget4-stable
```

### Scaling

```bash
# Scale workers
kubectl scale deployment gadget4-worker --replicas=10 -n gadget4-stable
kubectl scale deployment concept-worker --replicas=5 -n gadget4-stable

# Autoscaling (HPA)
kubectl autoscale deployment gadget4-worker \
  --cpu-percent=70 \
  --min=2 \
  --max=20 \
  -n gadget4-stable
```

## CI/CD Pipeline

### GitHub Actions Example

The workflow is already configured in `.github/workflows/build-and-deploy.yml`. See that file for details.

## Troubleshooting

### Image Build Issues

**Problem**: Docker build fails with "no space left on device"
```bash
# Clean up Docker
docker system prune -a
docker volume prune
```

**Problem**: Gadget4 compilation fails
```bash
# Check if repository is accessible
git clone https://gitlab.mpcdf.mpg.de/vrs/gadget4.git
# You may need authentication or use a fork
```

### Deployment Issues

**Problem**: Pods stuck in ImagePullBackOff
```bash
# Check image exists
docker pull gcr.io/${PROJECT_ID}/gadget4-api:latest

# Check credentials
kubectl get serviceaccount -n gadget4-beta
kubectl describe pod <pod-name> -n gadget4-beta
```

**Problem**: Database connection fails
```bash
# Test connection from pod
kubectl exec -it <api-pod> -n gadget4-beta -- bash
psql $DATABASE_URL

# Check secrets
kubectl get secret gadget4-secrets -n gadget4-beta -o yaml
```

### Performance Issues

**Problem**: Workers running slowly
```bash
# Check resource limits
kubectl top pods -n gadget4-stable

# Increase resources in deployment YAML
resources:
  limits:
    cpu: 8000m
    memory: 32Gi
```

## Best Practices

1. **Version Tags**: Always tag images with version numbers, not just `latest`
2. **Health Checks**: Implement proper liveness and readiness probes
3. **Resource Limits**: Set appropriate CPU/memory limits
4. **Secrets**: Never commit secrets to Git, use Kubernetes Secrets or secret managers
5. **Monitoring**: Set up Prometheus/Grafana for monitoring
6. **Backups**: Regular database backups
7. **Testing**: Test in beta before deploying to stable

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kustomize Documentation](https://kubectl.docs.kubernetes.io/references/kustomize/)




