# Spec Doc Integration

Status: Implemented
Owner: platform
Issue: N/A (local pre-deploy planning)
Stage: Local pre-deploy

## Goal

Introduce a lightweight spec doc workflow for Optio so substantial local changes can be planned and validated before the first cluster rollout.

## Why Now

The repository already automates issue intake, task execution, PR watching, and review. A spec doc is still useful for local-first, cross-cutting, and rollout-sensitive changes without introducing a second planning system.

## Scope

- Included:
  - `docs/specs/` with a reusable template
  - governance rules for when a spec is required
  - validator and scaffolding support for spec docs
  - contributor and PR guidance aligned to issue + spec flow
- Non-goals:
  - replacing Optio runtime task state with docs
  - making a spec mandatory for every small change

## Local Plan

- [x] Update process docs so issues remain the default work item and specs become the optional design artifact.
- [x] Add a spec validator and scaffold command so the workflow is easy to use locally.
- [x] Keep support for `Issue: N/A (local pre-deploy planning)` to allow local repo work before GitHub issue creation or cluster deployment.
- [x] Carry deferred follow-ups through GitHub issues or project fields instead of markdown backlog state.

## Validation

- Local checks:
  - `make governance-check`
  - `make check`
- Manual validation:
  - Confirm PR and issue templates point contributors to `docs/specs/`.
- Deferred validation for cluster rollout:
  - Exercise the updated workflow in a real implementation slice before deployment.

## Rollout

- Cluster impact:
  - None directly; this is a repository workflow and governance change.
- Rollout order:
  - Adopt the new spec flow for the next substantial local change set.
- Rollback notes:
  - Revert the spec validators and docs/template changes in one change set if the new flow proves insufficient.

## Links

- Issue: N/A (local pre-deploy planning)
- PR: pending
- Related docs: `docs/process/feature-driven-development.md`, `docs/testing/overview.md`, `AGENTS.md`
