# Fork Deployment Sync Policy

Status: active

## Why This Exists

This fork keeps a deployment layer for DigitalOcean Kubernetes that is intentionally isolated from upstream.

Goal: when syncing from upstream, maintainers should know exactly which files are fork-owned and which files can be accepted from upstream with minimal review.

## Hard Rule

Fork deployment customizations must live only in these paths:

- `.github/workflows/fork-*.yml`
- `deploy/scripts/*`
- `deploy/*`
- `docs/fork-*`

If a deployment change is needed, implement it in one of the paths above.

## Ownership Matrix

| Path                           | Owner          | Sync Rule                                                                                 |
| ------------------------------ | -------------- | ----------------------------------------------------------------------------------------- |
| `.github/workflows/fork-*.yml` | fork           | Keep fork behavior. Do not overwrite from upstream.                                       |
| `deploy/scripts/*`             | fork           | Keep fork behavior. Do not overwrite from upstream.                                       |
| `deploy/*`                     | fork           | Keep fork behavior. Do not overwrite from upstream.                                       |
| `docs/fork-*`                  | fork           | Keep fork docs behavior and naming.                                                       |
| everything else                | upstream-first | Accept upstream by default unless a local product feature explicitly requires divergence. |

## Current Deploy Contract

The fork deployment path is:

1. Validate deploy contract with `Fork Validate Deploy Config`.
2. Publish release artifacts with `Fork Release`.
3. Bootstrap cluster add-ons with `Fork Bootstrap DOKS`.
4. Deploy with `Fork Deploy Production`.

Runtime deploy logic is executed from `deploy/scripts/*` and consumes the fork deployment assets under `deploy/*`.

## Upstream Sync Procedure

1. Sync your branch with upstream `main`.
2. For conflicts outside the fork-owned paths above, take upstream by default.
3. For conflicts inside the fork-owned paths, keep fork behavior and only update when intentionally refactoring the fork deploy layer.
4. After conflict resolution, run:
   - `Fork Validate Deploy Config`
   - a dry run of `Fork Release` (sha tag path is acceptable)
5. Before production rollout, run `Fork Deploy Production` in the protected `production` environment with a released semver tag.

## Guardrails

- Do not add deployment logic to non-`fork-*` workflows.
- Do not introduce new fork deployment docs outside `docs/fork-*`.
- Treat upstream `ci.yml` and `release.yml` as upstream-owned unless there is a security or build-break emergency.
