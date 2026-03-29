# Feature-Driven Development Guide

## Objective

Ship value in small, traceable feature slices with deterministic governance.

This workflow is layered on top of the existing Optio monorepo and does not replace product architecture docs in `README.md` or `CLAUDE.md`.

## Repository language rules

- Repository documentation, code comments, and docstrings must be written in English.
- User-facing conversation may use the user's preferred language.
- Non-English repository text requires an explicit `NON_ENGLISH_OK: <reason>` escape hatch.

## Artifact chain (mandatory)

1. Backlog item (`BLG-###`) in `docs/roadmap/BACKLOG.md`
2. Feature spec in `docs/features/`
3. Iteration execution bundle in `docs/roadmap/iterations/<id>/`
4. Validation evidence from `make check`
5. Iteration closure + backlog sync

GitHub intake/review helpers should mirror this chain:

- Feature and bug issue templates should collect enough context to become a backlog item without re-triaging from scratch.
- PRs should link backlog, feature, and iteration artifacts or explain why the chain is not needed.

## Backlog rules

- Keep one owner per item.
- Keep acceptance criteria observable.
- Keep unfinished work out of `Done`.
- Move completed items to `docs/roadmap/ARCHIVE_BACKLOG.md`.

## Feature spec rules

- One feature doc can cover one or more backlog items.
- Spec must include scope, non-goals, acceptance criteria, test plan, and rollout notes.
- Link feature docs from iteration artifacts.

## Iteration rules

Each iteration folder must include:

- `iteration.md`
- `execution-plan.md`
- `status-report.md`

`iteration.md` must define:

- Scope
- Definition of Done (DoD)
- Carry-over
- Closure

`execution-plan.md` is the canonical execution tracker:

- All actionable execution steps must be Markdown checkboxes (`- [ ]` / `- [x]`).
- `status-report.md` should summarize progress, risks, validation, and follow-ups without repeating checklist text.
- Closed iterations cannot leave open checkboxes in `execution-plan.md`.
- If a step cannot be completed but the iteration must close, resolve it as a checked disposition such as:
  - `- [x] Deferred: ... Follow-up: BLG-###`
  - `- [x] Carried over: ... Follow-up: BLG-###`

## Validation rules

Run before closing a slice:

- `make test`
- `make check`

Local meaning:

- `make test` runs validator unit tests and `pnpm turbo test`.
- `make governance-check` runs repository governance validators and validator unit tests.
- `make check` runs format checks, governance validators, typecheck, and tests.

If checks fail, iteration closure is blocked until resolved or explicitly deferred with backlog linkage.

## Local automation

- Husky remains the default JS/TS commit workflow for this repo.
- Husky `pre-commit` runs staged formatting plus `make hooks-pre-commit`.
- Husky `pre-push` runs `make hooks-pre-push`.
- Install `pre-commit` only if you want an optional Python-managed mirror of the governance checks.
- The optional `pre-commit` stage runs repository validators and validator unit tests.
- The optional `pre-push` stage runs `make check`.
- CI remains the hard gate even when local hooks are enabled.

## Scaffolding helpers

- `make new-backlog ID=BLG-### TITLE=\"...\"`
- `make new-feature NAME=feature-... BACKLOG=BLG-### ITERATION=ITR-###`
- `make new-iteration ID=ITR-### BACKLOG_IDS=\"BLG-###\"`
