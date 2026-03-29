# Repo Pool Gate Repair

Status: Implemented
Owner: platform
Backlog: BLG-002

## Goal

Restore a trustworthy local `make check` gate by repairing the failing `repo-pool-service` unit tests after the governance bootstrap.

## Scope

- Included: aligning `repo-pool-service.test.ts` with the current multi-pod cleanup and reconciliation logic, mocking subprocess calls used by network policy cleanup, and validating the full gate.
- Non-goals: changing production repo-pool behavior unless the tests prove the implementation is actually wrong.

## Design Notes

- Key decisions:
  - Mock dynamic `node:child_process` and `node:util` imports at module scope so `deleteNetworkPolicy()` stays unit-testable.
  - Reset DB mock chain behavior explicitly between tests to avoid stale implementations leaking across query shapes.
  - Update cleanup assertions to reflect instance-index ordering in the current scale-down logic.
- Trade-offs:
  - The fix stays mostly in tests because the failures came from drift between the mocks and the current service implementation, not from a proven production bug.

## Acceptance Criteria

- `apps/api/src/services/repo-pool-service.test.ts` passes.
- `make check` passes locally.
- Planning artifacts document the repair and closure.

## Test Plan

- Unit checks:
  - `pnpm --filter @optio/api exec vitest run src/services/repo-pool-service.test.ts`
- Integration/process checks:
  - `make check`
- Required commands:
  - `make test`
  - `make check`

## Rollout

- Default behavior: repo-pool unit tests now exercise the current multi-pod code paths without depending on real subprocess execution.
- Rollback/deprecation notes (if needed): if repo-pool behavior changes again, update the mocks and expectations in the same change set.

## Links

- Backlog: `docs/roadmap/ARCHIVE_BACKLOG.md`
- Iteration: `docs/roadmap/iterations/ITR-002/iteration.md`
- Related docs: `apps/api/src/services/repo-pool-service.ts`, `AGENTS.md`
