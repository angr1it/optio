# Fork CI/CD Architecture for DOKS Deployments

Status: active

## Goal

Provide a minimal and secure deployment path for this fork to deploy Optio into DigitalOcean Kubernetes while keeping upstream sync conflicts low.

## Design Principles

1. Keep fork deployment logic isolated from upstream-owned CI/release workflows.
2. Do not expose production secrets to pull request jobs.
3. Keep production deployment approval explicit via GitHub Environments.
4. Deploy immutable release tags only.
5. Keep runtime operations in Optio UI, terminal tools, and Kubernetes APIs instead of SSH.

## Boundary Rule

Fork deployment customizations live only in:

- `.github/workflows/fork-*.yml`
- `deploy/scripts/*`
- `deploy/*`
- `docs/fork-*`

See `docs/fork-sync-policy.md` for upstream sync rules.

## Branch Model

- `main` tracks upstream and stays deploy-neutral.
- `develop` is the fork-owned integration, release, and deploy branch.

## Trust Boundaries

### Untrusted

- Pull requests from forks
- Pull request code before review and merge
- Any workflow that executes contributor branch code

### Trusted

- Maintainer-triggered `workflow_dispatch` runs
- Pushes to protected branches
- Maintainer-created release tags
- The GitHub `production` environment after reviewer approval

## Pipeline Layout

### Upstream CI Baseline

Source: `.github/workflows/ci.yml`

Purpose:

- format checks
- type checks
- test suite
- build verification

Rules:

- Runs on pull requests
- Uses no production secrets
- Uses minimal `GITHUB_TOKEN` permissions

### Fork Release

Source: `.github/workflows/fork-release.yml`

Purpose:

- resolve release contract for image/chart tags
- build and publish service and agent images
- package and publish Helm chart

Rules:

- Maintainer-triggered `workflow_dispatch`
- SemVer tags (`vX.Y.Z`) must run from matching tag refs
- Does not touch the live cluster

### Fork Deploy Contract Validation

Source: `.github/workflows/fork-validate-deploy.yml`

Purpose:

- lint and render chart with fork production overlay
- enforce fixed namespace contract for fork deploy

Rules:

- Runs on PR, push to `develop`, and manual dispatch
- Uses no production secrets

### Fork Cluster Bootstrap

Source: `.github/workflows/fork-bootstrap-doks.yml`

Purpose:

- install ingress-nginx
- install cert-manager
- install metrics-server
- apply shared `ClusterIssuer`

Rules:

- Manual only
- Protected by GitHub `production` environment
- Safe to re-run

### Fork Production Deploy

Source: `.github/workflows/fork-deploy-production.yml`

Purpose:

- render runtime Helm values from environment secrets
- create or update Kubernetes GitHub App secret
- deploy chart into fixed `optio` namespace and release
- verify rollout and run Helm tests

Rules:

- Manual only
- Protected by GitHub `production` environment
- Deploys explicit released semver tag via `release_tag`
- Serialized with `concurrency`

## Secret Model

### Repository Variables

Use repository variables for non-secret coordinates:

- `DO_CLUSTER_NAME`
- `OPTIO_DOMAIN`
- `OPTIO_PUBLIC_URL`
- `LETSENCRYPT_EMAIL`
- Optional agent image overrides:
  - `AGENT_IMAGE_REPOSITORY`
  - `AGENT_IMAGE_PREFIX`
  - `AGENT_IMAGE_TAG`
  - `AGENT_IMAGE_PULL_POLICY`

### Production Environment Secrets

Use GitHub `production` environment secrets for production-only data:

- `DIGITALOCEAN_ACCESS_TOKEN`
- `OPTIO_ENCRYPTION_KEY`
- `EXTERNAL_DATABASE_URL`
- `EXTERNAL_REDIS_URL`
- `AUTH_GITHUB_CLIENT_ID`
- `AUTH_GITHUB_CLIENT_SECRET`
- GitHub App credentials, if enabled

## Deployment Flow

1. Sync local `main` from upstream `main`.
2. Merge `main` into `develop`.
3. Land fork changes in `develop`.
4. Run `Fork Validate Deploy Config` on `develop`.
5. Create and push a release tag like `v0.1.0` from `develop`.
6. Run `Fork Release` from that tag ref.
7. Run `Fork Deploy Production` with `release_tag=v0.1.0`.
8. Approve `production` environment when prompted.
9. Workflow deploys with Helm, checks rollout, runs `helm test`, and verifies public endpoints.

## Rollback Strategy

1. Re-run `Fork Deploy Production` with a previous known-good tag.
2. If chart-level rollback must be immediate, use `helm rollback`.
3. Keep database and Redis/Valkey state external to release rollback.

## Related Documents

- `docs/fork-sync-policy.md`
- `docs/fork-doks-github-actions-setup.md`
- `docs/fork-doks-beta-readiness-checklist.md`
