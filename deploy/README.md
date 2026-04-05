# Fork DOKS Deployment Layer

This directory contains fork-owned deployment assets for running Optio on DigitalOcean Kubernetes.

## Scope Boundary

Fork deployment customizations live only in:

- `.github/workflows/fork-*.yml`
- `deploy/scripts/*`
- `deploy/*`
- `docs/fork-*`

See `../docs/fork-sync-policy.md` for the full sync policy.

## Files

- `cluster-issuer.yaml`: cert-manager `ClusterIssuer` template used by fork bootstrap automation.
- `limitrange.yaml`: default namespace resource requests/limits so hook pods comply with quota.
- `values.fork-production.yaml`: fork production Helm overlay consumed by fork validate/deploy flows.
- `scripts/bootstrap-doks.sh`: installs cluster add-ons and applies `ClusterIssuer`.
- `scripts/deploy-production.sh`: pulls released chart artifacts and deploys to DOKS.
- `scripts/render-runtime-values.py`: renders runtime secrets into Helm values.
- `scripts/release-contract.sh`: enforces release tag contract for fork publish workflow.
- `scripts/verify-production.sh`: verifies public web and health endpoints after deploy.

## Related Workflows

- `.github/workflows/fork-validate-deploy.yml`: validates fork deployment chart inputs and namespace contract.
- `.github/workflows/fork-release.yml`: publishes fork images and Helm chart artifacts.
- `.github/workflows/fork-bootstrap-doks.yml`: installs ingress, cert-manager, and metrics-server.
- `.github/workflows/fork-deploy-production.yml`: deploys released artifacts to production DOKS.

## Operating Model

1. Cluster, managed PostgreSQL, and managed Valkey already exist in the same VPC.
2. Production secrets live in the GitHub `production` environment.
3. Release artifacts are published first, then deployed by immutable semver tag.
4. Namespace and Helm release are fixed to `optio` for fork deploy workflows.
5. Normal operations use Optio UI, terminal tools, and Kubernetes APIs instead of SSH.
