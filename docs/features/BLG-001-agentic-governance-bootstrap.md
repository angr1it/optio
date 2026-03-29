# Optio Agentic Governance Bootstrap

Status: Implemented
Owner: platform
Backlog: BLG-001

## Goal

Bootstrap a reusable planning and validation layer for Optio without replacing the current monorepo and runtime workflow.

## Scope

- Included: repository operating rules, backlog/feature/iteration templates, governance validators, and a root `Makefile` that composes existing Optio checks.
- Non-goals: product feature work, CI rewiring, or replacing Husky with a new hook manager.

## Design Notes

- Keep one active backlog and one archive.
- Enforce deterministic iteration artifact shape for agent work.
- Keep product architecture in `README.md` and `CLAUDE.md`; keep planning artifacts in `docs/`.
- Compose governance validation with `pnpm format:check`, `pnpm turbo typecheck`, and `pnpm turbo test`.
- Enforce English-only repository documentation, comments, and docstrings with an explicit escape hatch.
- Use `execution-plan.md` checkboxes as the canonical execution tracker for iteration work.

## Acceptance Criteria

- Core planning templates and process docs exist in the root repository.
- `AGENTS.md` defines the repository workflow and points agents to product context.
- Governance validators fail on structural violations.
- The root `Makefile` exposes `make test` and `make check` for Optio plus governance validation.
- Product docs remain intact and linked from the new process layer.

## Test Plan

- Unit checks: `python3 -m unittest discover -s tools/scripts -p 'test_*.py'`
- Integration/process checks: `make check`
- Required commands:
  - `make test`
  - `make check`

## Rollout

- Default behavior: non-trivial agent work follows the backlog -> feature -> iteration flow.
- Rollback/deprecation notes (if needed): remove the governance overlay in one change set without changing the runtime stack.

## Links

- Backlog: `docs/roadmap/ARCHIVE_BACKLOG.md`
- Iteration: `docs/roadmap/iterations/ITR-001/iteration.md`
- Related docs: `docs/process/feature-driven-development.md`, `AGENTS.md`, `CLAUDE.md`
