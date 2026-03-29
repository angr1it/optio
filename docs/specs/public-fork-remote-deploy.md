# Public Fork Remote Deploy

Status: Draft
Owner: platform
Issue: N/A (local pre-deploy planning)
Stage: Local pre-deploy
Priority: P1

## Goal

Define a secure, reproducible remote deployment path for running Optio from a public fork on DigitalOcean Kubernetes with GitHub-hosted automation, GHCR-hosted images, and a tightly scoped public edge.

## Why Now

The repository already supports local Kubernetes development, but the remote deployment path is still incomplete and unsafe to execute from a public fork as-is.

The current gaps span image publishing, remote runtime prerequisites, edge exposure, and deployment workflow controls. Landing those changes without an explicit design would make it too easy to expose an operator shell, couple the deployment to unstable load-balancer IPs, or leak deploy assumptions into PR automation.

## Scope

- Included:
  - publishing `optio-api`, `optio-web`, and preset agent images to GHCR with a stable tag contract
  - making the remote runtime registry-aware for preset images and other deployment prerequisites
  - defining the GitHub Actions build and deploy flow for a public repository with protected environments
  - defining the DOKS and Traefik edge shape for exposing only the Optio UI and API over HTTPS
  - removing public shell exposure from the initial remote bootstrap path
- Non-goals:
  - introducing a multi-user auth model inside Optio for the first bootstrap slice
  - exposing browser-based shell access on the public edge
  - implementing external SSO or ForwardAuth in the same slice
  - designing a provider-agnostic multi-cloud deployment workflow

## Sequencing

- Blocked by:
  - `docs/specs/operator-bootstrap-and-cluster-access.md`
- Blocks:
  - the first live public-fork cluster rollout
  - any post-deploy hardening that assumes GHCR image publication and remote DOKS deployment already exist
- Parallelizable with:
  - local application changes that do not alter the remote deploy contract, image publication flow, or cluster edge shape

## Plan

- [ ] Define the image publication and tagging contract for API, web, and preset agent images.
- [ ] Define the remote runtime prerequisites, including registry-aware preset image resolution and `kubectl` availability in the API image.
- [ ] Define the GitHub Actions build and deploy flow for a public repository, including environment protection, permissions, and secret boundaries.
- [ ] Define the secure edge and deployment shape for DOKS and Traefik, including stable hostnames, HTTPS, source restrictions, and no public `/shell` path.
- [ ] Run `make governance-check`.
- [ ] Run `make check`.

## Validation

- Local checks:
  - `make governance-check`
  - `make check`
- Manual validation:
  - review the workflow, image, and manifest plan against the public-fork threat model
  - confirm the public surface is limited to UI and API routes only
- Deferred validation for cluster rollout:
  - publish the images to GHCR and deploy the manifests to DOKS
  - verify the configured public host serves the web UI and API over HTTPS
  - verify a smoke task can create or resume a repo pod in-cluster

## Rollout

- Cluster impact:
  - introduces the first supported public-fork remote deployment path and changes the required runtime container contract
- Rollout order:
  - land the local repository changes and docs
  - publish the required images to GHCR
  - create the protected GitHub environment and deploy secrets
  - deploy the edge layer and Optio workloads to DOKS
  - configure Optio app-level secrets and run a smoke task
- Rollback notes:
  - remove or disable the remote deployment workflows and public ingress
  - fall back to the documented local-only setup while reverting the remote-specific image and deploy changes if needed

## Links

- Issue: N/A (local pre-deploy planning)
- PR: pending
- Related docs: `AGENTS.md`, `CLAUDE.md`, `docs/process/feature-driven-development.md`, `docs/specs/operator-bootstrap-and-cluster-access.md`
