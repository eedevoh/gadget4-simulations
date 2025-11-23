# GitHub Actions Setup Guide

This guide explains how to configure GitHub Actions for automated builds and deployments.

## Required GitHub Secrets

Configure these secrets in your repository settings: **Settings → Secrets and variables → Actions**

### 1. GCP Service Account Key

**Secret Name:** `GCP_SA_KEY`

**How to create:**
```bash
# Create a service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding gadget-479011 \
  --member="serviceAccount:github-actions@gadget-479011.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding gadget-479011 \
  --member="serviceAccount:github-actions@gadget-479011.iam.gserviceaccount.com" \
  --role="roles/container.developer"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@gadget-479011.iam.gserviceaccount.com
```

**Value:** Copy the entire contents of `github-actions-key.json` (including `{` and `}`)

### 2. GCP Project ID (Optional)

**Secret Name:** `GCP_PROJECT_ID`

**Value:** `gadget-479011` (or your project ID)

**Note:** If not set, defaults to `gadget-479011` from the workflow

### 3. GKE Cluster Name

**Secret Name:** `GKE_CLUSTER_NAME`

**Value:** Your GKE cluster name (e.g., `gadget4-cluster`)

### 4. GKE Region (Optional)

**Secret Name:** `GKE_REGION`

**Value:** `us-central1` (or your cluster region)

**Note:** If not set, defaults to `us-central1`

## Repository Permissions

### Enable Workflow Permissions

1. Go to **Settings → Actions → General**
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**

Or add this to your workflow file (already included):
```yaml
permissions:
  contents: write
  id-token: write
```

## Workflow Behavior

### On Push to `main` or `develop`:

1. **Test** - Runs unit tests and linting
2. **Build** - Builds all Docker images:
   - `gadget4-api`
   - `gadget4-worker-gadget4`
   - `gadget4-worker-concept`
3. **Push** - Pushes images to GCR with tags:
   - `stable-<sha>` or `beta-<sha>`
   - `latest`
4. **Update Kustomize** - Updates image tags in `k8s/overlays/`
5. **Commit** - Commits and pushes Kustomize changes
6. **Deploy** - Deploys to Kubernetes (if configured)

### On Pull Request:

- Only runs **Test** job
- Does not build or deploy

## Troubleshooting

### Error: "Permission denied to github-actions[bot]"

**Solution:**
1. Check workflow permissions in repository settings
2. Ensure `contents: write` permission is granted
3. Verify the workflow file has `permissions:` section

### Error: "GCP authentication failed"

**Solution:**
1. Verify `GCP_SA_KEY` secret is correctly set
2. Check service account has required permissions
3. Ensure JSON key is complete (starts with `{` and ends with `}`)

### Error: "kubectl: command not found"

**Solution:**
The workflow uses `gcloud container clusters get-credentials` which sets up kubectl automatically. If this fails:
1. Check `GKE_CLUSTER_NAME` and `GKE_REGION` secrets
2. Verify service account has `container.developer` role

### Images not pushing to GCR

**Solution:**
1. Verify service account has `storage.admin` role
2. Check GCR is enabled: `gcloud services enable containerregistry.googleapis.com`
3. Verify project ID is correct

## Manual Testing

Test the workflow locally:

```bash
# Install act (GitHub Actions local runner)
brew install act  # macOS
# or download from: https://github.com/nektos/act

# Test workflow
act push -e .github/workflows/test-event.json
```

## Security Best Practices

1. **Never commit secrets** - Always use GitHub Secrets
2. **Rotate keys regularly** - Update service account keys periodically
3. **Minimal permissions** - Grant only necessary IAM roles
4. **Review workflow changes** - Always review PRs that modify workflows
5. **Use environment protection** - Protect production environment in GitHub

## Alternative: Using Workload Identity

For better security, use Workload Identity Federation instead of service account keys:

1. Set up Workload Identity Pool
2. Configure OIDC in GitHub Actions
3. Remove `GCP_SA_KEY` secret
4. Update workflow to use `google-github-actions/auth@v2`

See: https://github.com/google-github-actions/auth

## Support

If you encounter issues:
1. Check workflow logs in **Actions** tab
2. Verify all secrets are set correctly
3. Test GCP authentication locally
4. Review IAM permissions

