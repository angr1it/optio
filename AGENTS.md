# AGENTS.md

## Repository intent

This repository is **Optio**, a monorepo for workflow orchestration around AI coding agents.

It uses an agent-first delivery workflow on top of the existing product/runtime documentation, build pipeline, and monorepo tooling.

## Non-negotiables

- Keep one canonical planning flow: **Issue -> Optional spec -> Task -> PR -> Validation**.
- Keep non-trivial work traceable to a GitHub issue when one exists.
- Keep substantial local pre-cluster changes captured in a spec doc before cluster rollout work begins.
- Keep spec docs synchronized with implementation changes when a spec is in play.
- Keep deferred or carry-over work linked through GitHub issues/projects, not markdown backlog state.
- Keep repository documentation, code comments, and docstrings in English.
- User-facing conversation may follow the user's language, but repository files must stay in English.
- Keep product-specific architecture and operational guidance in `README.md` and `CLAUDE.md`; do not replace them with generic template prose.
- Do not delete/rename staged files unless explicitly requested.

## Planning artifacts

- Default work item: GitHub issue.
- Optional design specs: `docs/specs/*.md`
- Spec template: `docs/specs/SPEC_TEMPLATE.md`

## Spec-driven workflow (required)

1. Start from a GitHub issue when one exists.
2. If the work is cross-cutting, deployment-affecting, schema-affecting, or intentionally local-first before cluster rollout, create/update a spec doc under `docs/specs/`.
3. Local pre-cluster planning may use `Issue: N/A (local pre-deploy planning)` until a GitHub issue exists.
4. Implement only what is in the issue/spec scope.
5. Run validation gates before asking for review.
6. Link the issue and spec doc from the PR, or explicitly mark them as `N/A`.

## Spec rules

- A spec is required for:
  - orchestration, agent workflow, queue, or PR lifecycle changes
  - database, API contract, auth, or deployment changes
  - multi-package changes
  - local change sets you want to complete before the first cluster rollout
- A spec should state goal, scope, local plan, validation, rollout impact, and links.
- `Status` is lifecycle state, and must be one of: `Draft`, `Accepted`, `Implemented`, `Superseded`.
- `## Local Plan` must be a checklist. If an item is deferred or carried over, link the follow-up issue directly in that checklist item.
- A spec is optional for small, self-contained fixes that do not materially change runtime behavior or deployment shape.
- Sensitive changes under `apps/api/src/db/`, `apps/api/src/routes/`, `apps/api/src/workers/`, `helm/`, and `k8s/` must either touch a spec doc or provide an explicit spec reference through the local/PR validation path.

## Validation gates

Required commands:

- `make governance-check`
- `make test`
- `make check`

If a sensitive change is intentionally reusing an existing spec without editing it, run the local gate with `SPEC_REF=docs/specs/<name>.md` or use `SPEC_REF='N/A (reason)'` when a spec is explicitly not needed.

Recommended command:

- `make smoke` (same as the full local validation gate)

Husky is the default local hook path. Governance validation logic lives in `tools/scripts/` and must stay green.

## Editing rules

- Prefer minimal, explicit edits.
- Preserve the established Optio architecture, terminology, and developer workflow.
- Use ASCII by default.
- Avoid rewriting product docs unless the change actually alters product behavior or operations.

## Directory ownership

- `docs/` process docs, specs, historical planning artifacts, and product screenshots.
- `tools/scripts/` validation scripts and unit tests for governance checks.
- `var/` generated validation artifacts.
