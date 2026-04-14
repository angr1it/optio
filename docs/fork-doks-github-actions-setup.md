# Fork DOKS + GitHub Actions Setup From Zero

Status: active

This runbook describes the fork deployment path for deploying Optio from this repository into DigitalOcean Kubernetes.

## Scope Boundary

Fork deployment docs and automation are isolated in:

- `.github/workflows/fork-*.yml`
- `deploy/scripts/*`
- `deploy/*`
- `docs/fork-*`

See `docs/fork-sync-policy.md` for upstream sync behavior.

## Target Outcome

At the end of setup you should have:

1. DOKS cluster in a dedicated VPC
2. Managed PostgreSQL and managed Valkey in the same VPC
3. `ingress-nginx`, `cert-manager`, and `metrics-server` installed
4. GitHub `production` environment with required approval
5. Working Optio deployment reachable over HTTPS
6. No SSH dependency for normal operations

## Prerequisites

Before starting, ensure you have:

1. DigitalOcean access to create Kubernetes, VPC, and managed database resources
2. Domain you can point to ingress load balancer
3. GitHub repository admin access
4. GitHub App or OAuth strategy for Optio auth

## Step 1: Protect the Repository

Configure repository settings:

1. Keep `main` reserved for upstream sync only
2. Protect `develop`
3. Require CI checks before merge into `develop`
4. Optionally protect `main` as well to prevent accidental fork commits there
5. Add `CODEOWNERS` coverage for:
   - `.github/workflows/`
   - `deploy/`
   - `docs/fork-*`
6. Create GitHub environment `production`
7. Add required reviewers to `production`

## Step 2: Create DigitalOcean Network

Recommended layout:

1. One dedicated VPC for Optio production
2. One DOKS cluster in that VPC
3. One managed PostgreSQL cluster in that VPC
4. One managed Valkey cluster in that VPC

Use private connection strings for PostgreSQL and Valkey.

## Step 3: Create DOKS Cluster

Suggested baseline:

1. Current supported Kubernetes version in your region
2. At least 2 worker nodes
3. Node size covering API, web, optio assistant, and transient repo pods

## Step 4: Provision Managed PostgreSQL and Valkey

Create:

1. Managed PostgreSQL for app state
2. Managed Valkey for BullMQ/pub-sub/queueing

Recommendations:

1. Keep both services in the same VPC as DOKS
2. Use private endpoints
3. Restrict trusted sources to cluster/VPC CIDR
4. Enable backups based on recovery requirements

## Step 5: Prepare GitHub Authentication

Optio needs:

1. User login for web UI
2. Repository automation credentials for clone/push/PR/checks

Recommended:

1. Use GitHub App for repository operations
2. Keep production values in GitHub `production` environment

## Step 6: Add Repository Variables

Add these repository variables:

1. `DO_CLUSTER_NAME`
2. `OPTIO_DOMAIN`
3. `OPTIO_PUBLIC_URL`
4. `LETSENCRYPT_EMAIL`
5. Optional agent image overrides:
   - `AGENT_IMAGE_REPOSITORY` (default: `ghcr.io/jonwiggins/optio-agent-base`)
   - `AGENT_IMAGE_PREFIX` (default: `ghcr.io/jonwiggins/optio-agent-`)
   - `AGENT_IMAGE_TAG` (default: `latest`)
   - `AGENT_IMAGE_PULL_POLICY` (default: `Always` when tag is `latest`, else `IfNotPresent`)

Suggested defaults:

```text
OPTIO_DOMAIN=optio.example.com
OPTIO_PUBLIC_URL=https://optio.example.com
```

## Step 7: Add Production Secrets

Add to GitHub `production` environment:

```text
DIGITALOCEAN_ACCESS_TOKEN
OPTIO_ENCRYPTION_KEY
EXTERNAL_DATABASE_URL
EXTERNAL_REDIS_URL
AUTH_GITHUB_CLIENT_ID
AUTH_GITHUB_CLIENT_SECRET
```

If GitHub App integration is enabled, also add:

```text
OPTIO_GITHUB_APP_ID
OPTIO_GITHUB_APP_CLIENT_ID
OPTIO_GITHUB_APP_CLIENT_SECRET
OPTIO_GITHUB_APP_INSTALLATION_ID
OPTIO_GITHUB_APP_PRIVATE_KEY
OPTIO_GITHUB_APP_BOT_NAME
OPTIO_GITHUB_APP_BOT_EMAIL
```

GitHub Actions secret names cannot start with `GITHUB_`, so the fork deploy
workflow reads GitHub App credentials from the `OPTIO_GITHUB_APP_*` secrets and
maps them to `GITHUB_APP_*` runtime environment variables during deploy.

## Step 8: Validate Fork Deploy Contract

Run workflow:

```text
Fork Validate Deploy Config
```

Expected result: Helm lint/template pass with fork overlay and namespace contract checks.

This workflow is wired to `develop` pushes and PRs, with `workflow_dispatch` available for manual runs.

## Step 9: Bootstrap the Cluster

Run workflow:

```text
Fork Bootstrap DOKS
```

This installs:

1. `ingress-nginx`
2. `cert-manager`
3. `metrics-server`
4. `letsencrypt-prod` `ClusterIssuer`

The bootstrap workflow enables nginx snippet annotations on the fork-owned
ingress controller because the upstream chart blocks `/api/internal/*` using an
`nginx.ingress.kubernetes.io/server-snippet`.

## Step 10: Point DNS

After bootstrap:

1. Find public ingress load balancer address
2. Point `OPTIO_DOMAIN` DNS record to that address
3. Wait for DNS propagation

Do not deploy app until DNS resolves correctly.

## Step 11: Publish a Fork Release

1. Create and push tag:

```bash
git checkout develop
git pull --ff-only origin develop
git tag v0.1.0
git push origin v0.1.0
```

2. Run workflow:

```text
Fork Release
```

Important: run `Fork Release` from ref `refs/tags/v0.1.0` (matching SemVer tag ref).

## Step 12: Deploy Optio

Run workflow:

```text
Fork Deploy Production
```

Input:

```text
release_tag=v0.1.0
```

Expected behavior:

1. GitHub requests approval for `production` environment
2. Workflow connects to DOKS via `doctl`
3. Workflow creates/updates GitHub App Kubernetes secret (if configured)
4. Workflow deploys chart and waits for rollout
5. Workflow runs `helm test` and checks public homepage + `/api/health`

## Step 13: Post-Deploy Verification

After deploy:

1. Confirm rollout checks passed for API, web, and optio
2. Confirm `helm test` passed
3. Check `https://optio.example.com`
4. Check `https://optio.example.com/api/health`

## Step 14: First Beta Validation

Validate real operator path:

1. Open web UI over HTTPS
2. Verify login works
3. Connect GitHub in Optio
4. Add at least one repository
5. Start interactive session
6. Execute one real task end-to-end

## Step 15: Rollback

If deploy is bad:

1. Re-run `Fork Deploy Production` with previous known-good tag
2. If needed, run `helm rollback`

Remember: application rollback does not roll back external PostgreSQL/Valkey state.

## Related Documents

- `docs/fork-sync-policy.md`
- `docs/fork-ci-cd-architecture.md`
- `docs/fork-doks-beta-readiness-checklist.md`
