# Feature-Driven Development Guide

## Objective

Ship value in small, traceable slices without duplicating the issue and PR workflow that Optio already automates.

This workflow is layered on top of the existing Optio monorepo and does not replace product architecture docs in `README.md` or `CLAUDE.md`.

## Repository language rules

- Repository documentation, code comments, and docstrings must be written in English.
- User-facing conversation may use the user's preferred language.
- Non-English repository text requires an explicit `NON_ENGLISH_OK: <reason>` escape hatch.

## Canonical artifact model

1. GitHub issue for the work item when one exists
2. Optional spec doc in `docs/specs/` for design-heavy or rollout-sensitive work
3. Optio task/runtime state in the application database
4. Pull request for code review, CI, and merge
5. Validation evidence from `make governance-check` and `make check`

GitHub and local docs should complement each other instead of duplicating each other:

- Issues track intent and backlog state.
- Specs capture design intent and local rollout planning.
- PRs capture delivery and validation.

## When a spec is required

Create or update a spec doc when the change:

- changes agent orchestration, queues, review flow, or PR lifecycle behavior
- changes API contracts, auth flow, database schema, or deployment behavior
- spans multiple packages or multiple runtime surfaces
- is intentionally being prepared locally before cluster rollout

## When a spec is optional

A spec is usually unnecessary for:

- small, isolated bug fixes
- narrow test-only changes
- contained UI polish with no behavioral or rollout risk

## Spec rules

Specs live in `docs/specs/*.md` and should include:

- `Status`, `Owner`, `Issue`, and `Stage` headers
- `## Goal`
- `## Why Now`
- `## Scope`
- `## Local Plan`
- `## Validation`
- `## Rollout`
- `## Links`
- a checkbox-based `## Local Plan`

`Status` is the lifecycle state for the spec and must stay within:

- `Draft`
- `Accepted`
- `Implemented`
- `Superseded`

`Issue:` should normally point to `#123`.

For local-first slices that exist before a GitHub issue is opened, use:

- `Issue: N/A (local pre-deploy planning)`

This exception is for temporary local planning only, especially when you want to make and validate several repo changes before the first cluster deployment.

If work is deferred or carried over, represent that in the `## Local Plan` checklist and point to the follow-up GitHub issue directly, for example:

- `- [ ] Carry over to #123: complete the rollout validation in-cluster`

## Validation rules

Run before asking for review:

- `make test`
- `make check`

Local meaning:

- `make test` runs validator unit tests and `pnpm turbo test`.
- `make governance-check` runs repository governance validators and validator unit tests.
- `make check` runs format checks, governance validators, typecheck, and tests.

If checks fail, the slice is not review-ready.

## Cross-artifact validation

The governance gate is path-aware for the highest-risk repository surfaces:

- `apps/api/src/db/`
- `apps/api/src/routes/`
- `apps/api/src/workers/`
- `helm/`
- `k8s/`

If a change touches those paths, one of the following must be true:

- a spec doc under `docs/specs/` is part of the same local change set
- the local run passes an explicit spec reference such as `make governance-check SPEC_REF=docs/specs/runtime-change.md`
- the PR description fills `- Spec:` with a spec doc path or explicit `N/A (reason)`

PR closure should also capture:

- commands that were actually run
- whether the spec lifecycle moved to `Implemented` or `Superseded`
- any carry-over follow-up issue IDs

## Local automation

- Husky remains the default JS/TS commit workflow for this repo.
- Husky `pre-commit` runs staged formatting plus `make hooks-pre-commit`.
- Husky `pre-push` runs `make hooks-pre-push`.
- Install `pre-commit` only if you want an optional Python-managed mirror of the governance checks.
- The optional `pre-commit` stage runs repository validators and validator unit tests.
- The optional `pre-push` stage runs `make check`.
- CI remains the hard gate even when local hooks are enabled.

## Scaffolding helpers

- `make new-spec NAME=spec-name ISSUE=\"#123\" STAGE=\"Local pre-deploy\"`
