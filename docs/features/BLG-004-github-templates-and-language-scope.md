# GitHub Templates And Language Scope

Status: Implemented
Owner: platform
Backlog: BLG-004

## Goal

Bring GitHub intake/review templates in line with the docs-based governance flow and extend repository language validation to the rest of the common comment-bearing source/config surface.

## Scope

- Included: backlog-aware PR and issue templates, broader comment scanning for JS-family files, CSS, shell, YAML, TOML, Dockerfiles, and `.gitignore` coverage for local generated artifacts.
- Non-goals: replacing the docs-based planning model with GitHub Issues, linting arbitrary runtime strings/UI copy, or changing the product runtime behavior.

## Design Notes

- Key decisions:
  - Keep GitHub templates as intake/review helpers that point back to `docs/` instead of introducing a second planning system.
  - Expand language policy only across comment/doc surfaces so user-facing strings remain out of scope.
  - Ignore generated validator outputs and local reference directories so repository status stays focused on intentional changes.
- Trade-offs:
  - Lightweight comment scanning remains heuristic-based and does not try to parse every language grammar fully.
  - GitHub templates can encourage artifact linkage, but the canonical state still lives in the docs tree.

## Acceptance Criteria

- PRs request backlog/feature/iteration links plus governance validation evidence.
- Feature and bug issue templates collect information that maps cleanly into backlog items.
- `language_lint.py` covers JS-family comments, CSS comments, and additional hash-comment config/source files with unit tests.
- Local generated artifacts added by the governance workflow are ignored by git.

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

- Default behavior: GitHub forms now reinforce the repository artifact chain, language lint covers more repository comment surfaces, and generated governance artifacts stay out of `git status`.
- Rollback/deprecation notes (if needed): revert the template updates, restore the narrower lint scope, and drop the new `.gitignore` entries in one change set.

## Links

- Backlog: `docs/roadmap/ARCHIVE_BACKLOG.md`
- Iteration: `docs/roadmap/iterations/ITR-004/iteration.md`
- Related docs: `docs/process/feature-driven-development.md`, `.github/pull_request_template.md`, `tools/scripts/language_lint.py`
