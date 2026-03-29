# Archive Backlog

## BLG-004: Align GitHub templates and broaden language policy coverage

**State:** Done
**Priority:** Medium
**Target iteration:** `ITR-004`
**Owner:** `platform`

## Context

- The governance overlay already documented the backlog -> feature -> iteration flow, but the GitHub issue/PR templates still followed the old generic contribution flow.
- `language_lint.py` covered docs, Python, TS/TSX comments, and a few config files, but other common comment-bearing source files still sat outside the repository language policy.
- Generated local artifacts such as `agentic-template/`, `var/docs/*.json`, `.DS_Store`, and Python cache directories were still polluting `git status`.

## Why

- Intake and PR review forms should reinforce the same artifact chain the repository expects during implementation.
- The language policy should cover the rest of the common source/config surface without flagging user-facing runtime strings.
- Generated local artifacts should not compete with real repository work in the working tree.

## Scope

- Included: aligning PR and issue templates with backlog/feature/iteration expectations, extending language validation to JS/CSS and other comment-only source/config files, and tightening `.gitignore` for generated local artifacts.
- Explicitly out of scope: replacing the docs-based planning flow with GitHub-native planning or linting arbitrary runtime strings/UI copy.

## Acceptance Criteria

- GitHub issue and PR templates ask for backlog-ready problem statements, artifact links, and validation evidence.
- `language_lint.py` validates JS-family comments, CSS comments, and additional hash-comment config/source files with unit coverage.
- Generated artifacts no longer pollute `git status`.

## Validation

- Required checks:
  - `make governance-check`
  - `make test`
  - `make check`

## Links

- Feature spec(s): `docs/features/BLG-004-github-templates-and-language-scope.md`
- Iteration docs: `docs/roadmap/iterations/ITR-004/iteration.md`

## Change history

- `2026-03-29`: created and completed as the governance follow-up for GitHub templates, broader language policy coverage, and local artifact ignores.

## BLG-003: Integrate governance into CI hooks and TS lint

**State:** Done
**Priority:** High
**Target iteration:** `ITR-003`
**Owner:** `platform`

## Context

- Phase 1 and the repo-pool gate repair established the governance overlay and restored a green local gate, but governance was still not wired into the main CI workflow or the default Husky hook path.
- `language_lint.py` also only covered docs, Python comments/docstrings, and a few config file types, leaving the main TS/TSX codebase outside the repository language policy.

## Why

- The governance workflow should be enforced in the same places contributors already rely on: CI and Husky.
- Repository language rules are not credible if they skip the primary application code.

## Scope

- Included: adding a dedicated governance CI job, making Husky the primary local hook path for governance checks, keeping `.pre-commit-config.yaml` as an optional mirror, and extending `language_lint.py` to scan TS/TSX comments.
- Explicitly out of scope: PR template changes, issue template changes, or replacing Husky with a Python-managed hook workflow.

## Acceptance Criteria

- `.github/workflows/ci.yml` includes a governance-specific job that runs without disturbing the existing pipeline jobs.
- Husky remains the default hook path and runs governance checks before commit/push.
- `.pre-commit-config.yaml` stays available as an optional mirror, not the primary hook strategy.
- `language_lint.py` validates TS/TSX comments and its unit tests cover the new behavior.

## Validation

- Required checks:
  - `make governance-check`
  - `make test`
  - `make check`

## Links

- Feature spec(s): `docs/features/BLG-003-governance-ci-hooks-ts-lint.md`
- Iteration docs: `docs/roadmap/iterations/ITR-003/iteration.md`

## Change history

- `2026-03-29`: created to complete phase 2 of the governance migration.
- `2026-03-29`: completed by wiring governance into CI, Husky, and TS/TSX comment validation.

## BLG-002: Restore a green `make check` gate after governance bootstrap

**State:** Done
**Priority:** High
**Target iteration:** `ITR-002`
**Owner:** `platform`

## Context

- Phase 1 successfully bootstrapped the governance overlay, but the full local `make check` gate still failed in existing `@optio/api` tests under `src/services/repo-pool-service.test.ts`.

## Why

- The governance workflow should end on a trustworthy local gate.
- Until `make check` is green end to end, iteration closure evidence remains partial.

## Scope

- Included: investigating the failing `repo-pool-service` tests, fixing the unit-test harness to match the current service behavior, and restoring a green local gate.
- Explicitly out of scope: broader CI workflow changes or hook strategy changes unless they are required by the fix.

## Acceptance Criteria

- `make check` passes locally without ignoring the failing `@optio/api` test cases.
- Repo-pool cleanup/counting behavior is covered by updated tests that reflect the current multi-pod implementation.
- Follow-up planning artifacts are synchronized with the fix.

## Validation

- Required checks:
  - `make test`
  - `make check`

## Links

- Feature spec(s): `docs/features/BLG-002-repo-pool-gate-repair.md`
- Iteration docs: `docs/roadmap/iterations/ITR-002/iteration.md`

## Change history

- `2026-03-29`: created as a follow-up from `ITR-001` after bootstrap uncovered existing `repo-pool-service` test failures.
- `2026-03-29`: completed by repairing the `repo-pool-service` unit-test harness and restoring a green local gate.

## BLG-001: Bootstrap Optio governance overlay

**State:** Done
**Priority:** High
**Target iteration:** `ITR-001`
**Owner:** `platform`

## Context

- Optio already had product documentation, CI, and monorepo tooling, but not a canonical backlog -> feature -> iteration workflow for agent-driven delivery.

## Why

- A lightweight governance layer makes non-trivial agent work traceable without replacing the existing runtime architecture or development commands.

## Scope

- Included: `AGENTS.md`, process docs, roadmap and feature templates, governance validators, and a repo-level `Makefile` that composes Optio's existing checks.
- Explicitly out of scope: CI rewiring, Husky integration changes, and deeper validator support for TypeScript comments.

## Acceptance Criteria

- The repository has one documented planning workflow for meaningful agent work.
- Governance validators and their unit tests run locally.
- `make check` composes the new governance checks with the existing Optio format, typecheck, and test commands.
- Product-facing docs remain intact and linked from the process layer.

## Validation

- Required checks:
  - `make test`
  - `make check`

## Links

- Feature spec(s): `docs/features/BLG-001-agentic-governance-bootstrap.md`
- Iteration docs: `docs/roadmap/iterations/ITR-001/iteration.md`

## Change history

- `2026-03-29`: completed phase 1 governance bootstrap for Optio.
- `2026-03-29`: follow-up `BLG-002` created for pre-existing `@optio/api` test failures that blocked a green `make check`.
