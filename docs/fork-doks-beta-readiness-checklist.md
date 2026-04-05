# Fork DOKS Beta Readiness Checklist

Status: active

This checklist tracks fork-specific work required to keep deployment safe and easy to sync with upstream.

## Scope Rule

Fork deployment customizations are allowed only in:

- `.github/workflows/fork-*.yml`
- `deploy/scripts/*`
- `deploy/*`
- `docs/fork-*`

See `docs/fork-sync-policy.md` for conflict-resolution policy.

## Part 1: Repository Work

These items should land as commits in this repository.

### 1.1 Keep release-to-deploy contract explicit

- [ ] `Fork Release` publishes immutable tags for `api`, `web`, `optio`, and `agent`
- [ ] `Fork Deploy Production` accepts only semver `release_tag` values
- [ ] Docs explain how to run release from matching tag refs

Done when:

- A maintainer can map one release tag to all runtime images without guessing.

### 1.2 Keep fork workflows hardened

- [ ] Third-party actions pinned to full SHAs
- [ ] Production workflows remain manual (`workflow_dispatch`)
- [ ] Production deploy uses explicit `concurrency`
- [ ] Pull request workflows do not receive production secrets

Done when:

- Fork deployment workflows are safe for a public repository.

### 1.3 Keep deployment assets isolated

- [ ] Runtime deploy logic stays in `deploy/scripts/*`
- [ ] Cluster bootstrap assets stay in `deploy/*`
- [ ] No deployment logic is added to non-`fork-*` workflows

Done when:

- Fork deployment logic is easy to identify by path alone.

### 1.4 Keep rollback path documented

- [ ] Re-deploy previous known-good tag path documented
- [ ] `helm rollback` fallback documented
- [ ] External PostgreSQL/Valkey rollback limitations documented

Done when:

- A maintainer can recover from bad deploy without ad hoc cluster surgery.

### 1.5 Keep post-deploy validation routine stable

- [ ] Standard checks include rollout, `helm test`, homepage, and `/api/health`
- [ ] First-beta validation includes login, GitHub connect, repo add, and one real task

Done when:

- Every production deploy uses one repeatable validation sequence.

### 1.6 Keep sync policy current

- [ ] `docs/fork-sync-policy.md` reflects current ownership boundaries
- [ ] Docs and site links point to `docs/fork-*`
- [ ] Reviewers enforce "upstream-first outside boundary" during sync PRs

Done when:

- Maintainers can resolve upstream sync conflicts quickly and consistently.

## Part 2: External Setup Work

These items are completed in GitHub settings, DigitalOcean, and DNS.

### 2.1 GitHub protection and environments

- [ ] Keep `main` reserved for upstream sync only
- [ ] Protect `develop`
- [ ] Require CI checks before merge into `develop`
- [ ] Add `CODEOWNERS` coverage for `.github/workflows/`, `deploy/`, and `docs/fork-*`
- [ ] Create environment `production`
- [ ] Require approvers for `production`

Done when:

- Deploy approvals are explicit and workflow changes are review-gated.

### 2.2 DOKS and managed services

- [ ] Dedicated VPC created
- [ ] DOKS cluster created in that VPC
- [ ] Managed PostgreSQL created in same VPC
- [ ] Managed Valkey created in same VPC
- [ ] Private connection strings configured

Done when:

- Cluster and stateful dependencies are reachable without public DB exposure.

### 2.3 Variables and secrets

- [ ] Repository variables set:
  - `DO_CLUSTER_NAME`
  - `OPTIO_DOMAIN`
  - `OPTIO_PUBLIC_URL`
  - `LETSENCRYPT_EMAIL`
- [ ] `production` environment secrets set:
  - `DIGITALOCEAN_ACCESS_TOKEN`
  - `OPTIO_ENCRYPTION_KEY`
  - `EXTERNAL_DATABASE_URL`
  - `EXTERNAL_REDIS_URL`
  - `AUTH_GITHUB_CLIENT_ID`
  - `AUTH_GITHUB_CLIENT_SECRET`
- [ ] Optional GitHub App secrets set when app mode is enabled

Done when:

- Fork bootstrap/deploy workflows run without manual secret injection.

### 2.4 Bootstrap and first deploy

- [ ] Run `Fork Validate Deploy Config`
- [ ] Run `Fork Bootstrap DOKS`
- [ ] Point DNS for `OPTIO_DOMAIN` to ingress load balancer
- [ ] Create and push semver tag (for example `v0.1.0`)
- [ ] Run `Fork Release` from matching tag ref
- [ ] Run `Fork Deploy Production` with `release_tag=v0.1.0`

Done when:

- Application is deployed to DOKS through fork workflows only.

### 2.5 Beta workload validation

- [ ] Open web UI over HTTPS
- [ ] Verify login
- [ ] Connect GitHub
- [ ] Add at least one repository
- [ ] Start interactive session
- [ ] Execute at least one real task end-to-end

Done when:

- Deployment is not only healthy but usable for real beta work.

## Exit Criteria

You can call the fork deployment path beta-ready when:

- [ ] Scope rule is enforced (`fork-*` workflows, `deploy/*`, `deploy/scripts/*`, `docs/fork-*`)
- [ ] `Fork Validate Deploy Config` passes on current `develop`
- [ ] `Fork Bootstrap DOKS` succeeded on target cluster
- [ ] `Fork Release` produced artifacts for release tag
- [ ] `Fork Deploy Production` succeeded for real release tag
- [ ] Public HTTPS URL and `/api/health` are reachable
- [ ] One real operator task was completed successfully
- [ ] Rollback path is documented and tested by maintainers

## Suggested Execution Order

1. Complete repository checklist items.
2. Configure GitHub protection and production environment.
3. Provision DOKS + managed services.
4. Populate variables and secrets.
5. Validate config and bootstrap cluster.
6. Configure DNS and wait for propagation.
7. Publish release and run first deploy.
8. Execute first-beta workload validation.
