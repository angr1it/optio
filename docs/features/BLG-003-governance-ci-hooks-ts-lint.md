# Governance CI Hooks And TS Lint

Status: Implemented
Owner: platform
Backlog: BLG-003

## Goal

Integrate the governance workflow into the default CI and Husky paths, and extend language validation to cover TS/TSX comments.

## Scope

- Included: a dedicated governance CI job, Husky pre-commit/pre-push integration, optional `pre-commit` mirror documentation, and TS/TSX comment coverage in `language_lint.py`.
- Non-goals: replacing the existing CI jobs, switching away from Husky, or redesigning repository planning templates.

## Design Notes

- Key decisions:
  - Add a lightweight `make governance-check` target so CI and Husky can reuse the same governance-only gate.
  - Keep Husky as the primary local hook path and add `.husky/pre-push` for the full `make check` gate.
  - Leave `.pre-commit-config.yaml` in place as an optional mirror for contributors who already use `pre-commit`.
  - Extend the language lint scanner to parse TS/TSX comments without attempting a full JS parser.
- Trade-offs:
  - The TS/TSX scanner is intentionally lightweight and may miss comments embedded inside complex template-string expressions, but it covers the dominant repository comment patterns without adding a new runtime dependency.

## Acceptance Criteria

- `ci.yml` runs a governance-specific job alongside the existing format/typecheck/test/build jobs.
- Husky pre-commit/pre-push hooks execute the governance and full local gates through Make targets.
- The repository docs clearly describe Husky as primary and `pre-commit` as optional.
- `language_lint.py` flags non-English TS/TSX comments and its unit tests pass.

## Test Plan

- Unit checks:
  - `make validator-test`
- Integration/process checks:
  - `make governance-check`
  - `make check`
- Required commands:
  - `make test`
  - `make check`

## Rollout

- Default behavior: contributors get governance checks through Husky by default, CI runs a dedicated governance job, and repository language rules now cover TS/TSX comments.
- Rollback/deprecation notes (if needed): remove the governance CI job, revert Husky hook changes, and drop TS/TSX scanning in one change set.

## Links

- Backlog: `docs/roadmap/ARCHIVE_BACKLOG.md`
- Iteration: `docs/roadmap/iterations/ITR-003/iteration.md`
- Related docs: `docs/process/feature-driven-development.md`, `docs/testing/overview.md`, `.github/workflows/ci.yml`
