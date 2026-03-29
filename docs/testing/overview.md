# Testing And Validation Policy

This repository validates the **process contract** for issue-driven delivery with optional spec docs.

## Required checks

- `make test`:
  - runs unit tests for validation scripts,
  - runs `pnpm turbo test`.
- `make lint`:
  - runs `pnpm format:check`,
  - validates docs links and required governance artifacts,
  - validates spec doc structure when spec docs are present,
  - validates path-aware spec coverage for sensitive runtime and deploy changes,
  - validates the English-only policy for repository docs, Python comments/docstrings, and TS/TSX comments.
- `make governance-check`:
  - runs the repository governance validators and validator unit tests without the project typecheck/test steps.
- `make check`:
  - runs lint + `pnpm turbo typecheck` + tests.

## Local hooks

- Husky is the primary local hook path for this repository.
- Husky `pre-commit` runs `make hooks-pre-commit`.
- Husky `pre-push` runs `make hooks-pre-push`.
- `.pre-commit-config.yaml` is an optional mirror for contributors who already use `pre-commit`.
- Optional `pre-commit` stage:
  - runs docs, language, and spec validators,
  - runs validator unit tests.
- Optional `pre-push` stage:
  - runs `make check`.
- Install with:
  - `python3 -m pip install pre-commit`
  - `pre-commit install --hook-type pre-commit --hook-type pre-push`

## Script locations

- `tools/scripts/docs_lint.py`
- `tools/scripts/language_lint.py`
- `tools/scripts/validate_specs.py`
- `tools/scripts/validate_change_scope.py`

## CI gate

- GitHub Actions workflow: `.github/workflows/ci.yml`
- Trigger: pull requests and pushes to `main`
- Governance job command: `make governance-check`
- Governance job checkout depth: full history for diff-aware spec validation
- Full project gate command: `make check`
