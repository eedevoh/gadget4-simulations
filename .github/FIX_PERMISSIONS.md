# Fix: GitHub Actions Permission Denied Error

## Problem

The workflow was failing with:
```
remote: Permission to eedevoh/gadget4-simulations.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/eedevoh/gadget4-simulations/': The requested URL returned error: 403
```

## Root Cause

The GitHub Actions workflow did not have write permissions to push commits back to the repository.

## Solution

### 1. Added Workflow Permissions

Added explicit permissions at the workflow level:

```yaml
permissions:
  contents: write  # Required to push commits
  id-token: write  # Required for GCP authentication
```

### 2. Created Complete Workflow

Created `.github/workflows/build-and-deploy.yml` with:
- ✅ Proper permissions configuration
- ✅ Test job
- ✅ Build job for all Docker images
- ✅ Push to GCR
- ✅ Update Kustomize manifests
- ✅ Commit and push changes
- ✅ Deploy to Kubernetes

### 3. Repository Settings

**You must also configure repository settings:**

1. Go to **Settings → Actions → General**
2. Under **Workflow permissions**, select:
   - ✅ **Read and write permissions**
   - ✅ **Allow GitHub Actions to create and approve pull requests**

## Verification

After applying these changes:

1. **Push the workflow file:**
   ```bash
   git add .github/workflows/build-and-deploy.yml
   git commit -m "fix: Add GitHub Actions workflow with proper permissions"
   git push
   ```

2. **Check workflow run:**
   - Go to **Actions** tab in GitHub
   - Verify workflow runs successfully
   - Check that commits are pushed (if applicable)

3. **Verify permissions:**
   - Workflow should be able to push commits
   - No more 403 errors

## Additional Configuration

### Required Secrets

Make sure these secrets are configured in **Settings → Secrets and variables → Actions**:

- `GCP_SA_KEY` - GCP service account JSON key
- `GCP_PROJECT_ID` - (optional) Your GCP project ID
- `GKE_CLUSTER_NAME` - Your GKE cluster name
- `GKE_REGION` - (optional) Your GKE region

See [SETUP.md](SETUP.md) for detailed setup instructions.

## Alternative Solutions

If you still encounter permission issues:

### Option 1: Use Personal Access Token (PAT)

Instead of relying on `GITHUB_TOKEN`, use a Personal Access Token:

1. Create a PAT with `repo` scope
2. Add it as a secret: `GITHUB_TOKEN_PAT`
3. Update workflow to use:
   ```yaml
   - name: Commit and push
     env:
       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN_PAT }}
     run: |
       git push https://${{ secrets.GITHUB_TOKEN_PAT }}@github.com/${{ github.repository }}.git
   ```

### Option 2: Use GitHub App

For more fine-grained permissions, use a GitHub App instead of the default token.

## Testing

Test the workflow locally with `act`:

```bash
# Install act
brew install act  # macOS

# Test the workflow
act push
```

## Related Files

- `.github/workflows/build-and-deploy.yml` - Main workflow file
- `.github/SETUP.md` - Complete setup guide
- `.github/README.md` - Workflow documentation

## Status

✅ **Fixed** - Workflow now has proper permissions to push commits

