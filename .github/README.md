# GitHub Actions Workflows

This directory contains GitHub Actions workflows for CI/CD automation.

## Workflows

### `build-and-deploy.yml`

Main workflow that:
- Runs tests on every push and PR
- Builds Docker images for API and workers
- Pushes images to Google Container Registry (GCR)
- Updates Kubernetes manifests with new image tags
- Deploys to Kubernetes (beta/stable environments)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`

## Setup

See [SETUP.md](SETUP.md) for detailed configuration instructions.

## Quick Setup Checklist

- [ ] Configure `GCP_SA_KEY` secret (GCP service account JSON key)
- [ ] Configure `GCP_PROJECT_ID` secret (optional, defaults to `gadget-479011`)
- [ ] Configure `GKE_CLUSTER_NAME` secret (your GKE cluster name)
- [ ] Configure `GKE_REGION` secret (optional, defaults to `us-central1`)
- [ ] Enable workflow permissions: **Settings → Actions → General → Workflow permissions → Read and write**

## Workflow Permissions

The workflow requires write permissions to:
- Push commits (updating Kustomize image tags)
- Create releases (if configured)

These are configured in the workflow file:
```yaml
permissions:
  contents: write
  id-token: write
```

## Image Tags

Images are tagged with:
- **Branch-based tags:**
  - `main` → `stable-<sha>`
  - `develop` → `beta-<sha>`
- **Latest tags:**
  - `latest` (always points to most recent build)

## Deployment Environments

- **Beta:** Deployed from `develop` branch
- **Stable:** Deployed from `main` branch

Both environments are automatically deployed after successful builds.

## Troubleshooting

See [SETUP.md](SETUP.md) for common issues and solutions.

## Security

- Never commit secrets to the repository
- Use GitHub Secrets for all sensitive data
- Review workflow changes before merging
- Consider using Workload Identity Federation for better security

