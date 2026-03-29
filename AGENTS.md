# AGENTS.md

## Repository intent

This repository is **Optio**, a monorepo for workflow orchestration around AI coding agents.

It uses an agent-first delivery workflow on top of the existing product/runtime documentation, build pipeline, and monorepo tooling.

## Non-negotiables

- Keep one canonical planning flow: **Backlog -> Feature spec -> Iteration -> Validation -> Closure**.
- Keep active work traceable to backlog IDs (`BLG-###`).
- Keep feature and iteration docs synchronized with implementation changes.
- Keep repository documentation, code comments, and docstrings in English.
- User-facing conversation may follow the user's language, but repository files must stay in English.
- Do not keep `Done` items in active backlog; move them to archive.
- Keep product-specific architecture and operational guidance in `README.md` and `CLAUDE.md`; do not replace them with generic template prose.
- Do not delete/rename staged files unless explicitly requested.

## Required planning artifacts

- Active backlog: `docs/roadmap/BACKLOG.md`
- Backlog archive: `docs/roadmap/ARCHIVE_BACKLOG.md`
- Backlog item template: `docs/roadmap/BACKLOG_TEMPLATE.md`
- Feature specs: `docs/features/*.md`
- Feature template: `docs/features/FEATURE_TEMPLATE.md`
- Iteration folders: `docs/roadmap/iterations/<iteration-id>/`
- Iteration template: `docs/roadmap/iterations/ITERATION_TEMPLATE.md`

## Feature-driven workflow (required)

1. Create or update a backlog item (`BLG-###`) with clear scope and acceptance.
2. If work is non-trivial, create/update a feature spec linked to the backlog item.
3. Plan the slice in a concrete iteration folder with:
   - `iteration.md`
   - `execution-plan.md`
   - `status-report.md`
4. Implement only what is in the current iteration scope.
5. Run validation gates and record evidence in iteration closure.
6. Move completed backlog items to archive in the same change set.

## Iteration governance

At iteration start:

- Define scope, non-goals, and Definition of Done.
- Link all in-scope backlog items and feature specs.
- Define required tests/validation checks.
- Track actionable execution steps in `execution-plan.md` as Markdown checkboxes (`- [ ]` / `- [x]`).

At iteration end:

- Update closure status in `iteration.md`.
- Resolve every `execution-plan.md` checkbox before closing the iteration.
- If a step cannot be completed, convert it to a checked disposition such as `Deferred:` or `Carried over:` and link the follow-up backlog item.
- Sync `status-report.md` and `execution-plan.md` without duplicating checklist text.
- Record completed/deferred items and follow-ups.
- Sync backlog state (archive `Done`, keep unfinished as non-`Done`).

## Validation gates

Required commands:

- `make governance-check`
- `make test`
- `make check`

Recommended command:

- `make smoke` (same as the full local validation gate)

Husky is the default local hook path. Governance validation logic lives in `tools/scripts/` and must stay green.

## Editing rules

- Prefer minimal, explicit edits.
- Preserve the established Optio architecture, terminology, and developer workflow.
- Use ASCII by default.
- Avoid rewriting product docs unless the change actually alters product behavior or operations.

## Directory ownership

- `docs/` process docs, planning artifacts, and product screenshots.
- `tools/scripts/` validation scripts and unit tests for governance checks.
- `var/` generated validation artifacts.
