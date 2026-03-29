# Operator Bootstrap And Cluster Access

Status: Draft
Owner: platform
Issue: N/A (local pre-deploy planning)
Stage: Local pre-deploy
Priority: P0

## Goal

Define the operator workflow for bootstrapping the remote Optio environment from a local machine, syncing required secrets safely, and accessing cluster workloads directly without relying on a public web shell.

## Why Now

The remote deployment path needs a repeatable bootstrap story for local operators. The current repository has local setup scripts, but it does not yet define how remote bootstrap should consume env files, apply secrets, or support direct pod and service access from a workstation.

This needs to be explicit before implementation so that convenience scripts do not become an informal secret store or recreate the same access surface that the public-edge design is trying to remove.

## Scope

- Included:
  - defining env-file boundaries for local development, remote bootstrap, and CI-managed secrets
  - defining init and sync script responsibilities for remote bootstrap and secret application
  - documenting the workstation access path through `doctl`, `kubectl`, `port-forward`, `exec`, and debug workflows
  - documenting optional operator tooling such as `kubectx`, `kubens`, `stern`, `k9s`, and when Telepresence is warranted
- Non-goals:
  - replacing GitHub Environment secrets as the CI source of truth
  - exposing browser-based shell access as an operator convenience
  - automating workstation package installation for every supported OS in the first slice
  - introducing a bastion, VPN, or external access broker in the same change set

## Sequencing

- Blocked by:
  - none
- Blocks:
  - `docs/specs/public-fork-remote-deploy.md`
  - the first live public-fork cluster rollout
- Parallelizable with:
  - local documentation cleanup that does not define remote bootstrap, secret sync, or operator access behavior

## Plan

- [ ] Define the env-file contract for local development, remote bootstrap, and CI-managed secrets.
- [ ] Define the responsibilities and safety constraints for remote init and secret-sync scripts, including how rendered secrets stay out of tracked files.
- [ ] Define the local operator access workflow around `doctl`, `kubectl`, `port-forward`, `exec`, and debug commands instead of public shell exposure.
- [ ] Define the optional operator tooling baseline and the threshold for using Telepresence instead of native Kubernetes access.
- [ ] Run `make governance-check`.
- [ ] Run `make check`.

## Validation

- Local checks:
  - `make governance-check`
  - `make check`
- Manual validation:
  - review the env-file and secret-handling rules for compatibility with a public fork
  - confirm the documented operator path does not require a public shell route
- Deferred validation for cluster rollout:
  - authenticate with `doctl` and fetch kubeconfig for the target cluster
  - verify direct `kubectl exec` and `kubectl port-forward` access to running Optio workloads
  - verify the init and secret-sync workflow against a live DOKS environment

## Rollout

- Cluster impact:
  - none by itself until the scripts and operator workflow are used against a live cluster
- Rollout order:
  - land the local docs and bootstrap scripts
  - verify the workstation toolchain and env-file conventions locally
  - apply the bootstrap and secret-sync flow to the target DOKS cluster
  - use direct cluster access for ongoing operations and debugging
- Rollback notes:
  - fall back to manual `kubectl`, `helm`, and secret application steps if the scripted workflow proves unreliable
  - remove the operator helper scripts without changing the core Optio runtime if necessary

## Links

- Issue: N/A (local pre-deploy planning)
- PR: pending
- Related docs: `AGENTS.md`, `CLAUDE.md`, `docs/process/feature-driven-development.md`, `docs/specs/public-fork-remote-deploy.md`
