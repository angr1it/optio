# Execution Plan: ITR-001

## Steps

- [x] Copy the governance scaffold from `agentic-template/` into the root `optio` repository.
- [x] Adapt `AGENTS.md`, docs, and `Makefile` to Optio-specific commands and product context.
- [x] Replace template sample backlog, feature, and iteration history with an Optio bootstrap slice.
- [x] Deferred: full `make check` closure is blocked by existing `@optio/api` failures in `src/services/repo-pool-service.test.ts`. Follow-up: BLG-002.

## Risks

- Governance rules drift away from the actual project workflow.
- Template examples remain in the repo and confuse future work.

## Mitigations

- Keep the process layer additive and link back to `README.md` and `CLAUDE.md`.
- Remove template history and keep only Optio-specific planning artifacts.
