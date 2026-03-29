# Execution Plan: ITR-002

## Steps

- [x] Confirm the failing scope in `apps/api/src/services/repo-pool-service.test.ts` and map it to `BLG-002`.
- [x] Update subprocess and DB mocks so the unit tests reflect the current `repo-pool-service` implementation.
- [x] Run targeted repo-pool tests and the full `make check` gate before closure.

## Risks

- Test-harness fixes could hide a real production bug if expectations drift too far from the implementation.
- Shared DB mocks could still leak state between tests if reset behavior is incomplete.

## Mitigations

- Keep assertions tied to observable service behavior and current multi-pod ordering logic.
- Reset all relevant DB/runtime mocks in each test block.
