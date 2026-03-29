# Iteration ITR-003: Governance CI Hooks And TS Lint

**Status:** Closed
**Date:** 2026-03-29
**Owner:** platform

Related backlog items:

- BLG-003

Related feature specs:

- `docs/features/BLG-003-governance-ci-hooks-ts-lint.md`

## Scope

- Included: wiring governance into `.github/workflows/ci.yml`, making Husky the default governance hook path, and extending `language_lint.py` to scan TS/TSX comments.
- Explicitly out of scope: PR/issue template work and broader workflow redesign beyond the listed migration tasks.

## Definition Of Done (DoD)

- Functional outcome gates:
  - Governance runs in CI without replacing the existing project jobs.
  - Husky is the default local hook path for governance and full-gate checks.
  - TS/TSX comments are covered by repository language validation.
- Test gates:
  - `make test`
  - `make check`
- Documentation gates:
  - Planning docs and contributor docs reflect the CI/hook strategy and TS/TSX lint coverage.

## Carry-over

- Inherited items from previous iteration:
  - `BLG-003` continues the governance migration after `ITR-001` and `ITR-002` established the overlay and restored the local gate.
- Ownership and disposition for each item:
  - Finish CI and hook integration in one slice so the governance workflow is coherent end to end.

## Closure

- Final status: Closed
- Completed items: BLG-003
- Deferred items + follow-ups: none required for this phase; future work can focus on optional workflow polish such as PR/issue template alignment.
- Validation summary (latest successful checks): `make governance-check`, `make validator-test`, and `make check` passed on 2026-03-29.
