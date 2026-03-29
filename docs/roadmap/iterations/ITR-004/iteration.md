# Iteration ITR-004: GitHub Templates And Language Scope

**Status:** Closed
**Date:** 2026-03-29
**Owner:** platform

Related backlog items:

- BLG-004

Related feature specs:

- `docs/features/BLG-004-github-templates-and-language-scope.md`

## Scope

- Included: aligning GitHub PR/issue templates with the backlog -> feature -> iteration workflow, broadening language lint coverage to more comment-bearing file types, and ignoring generated local artifacts that should not remain in git status.
- Explicitly out of scope: moving planning into GitHub-native artifacts or linting user-facing strings.

## Definition Of Done (DoD)

- Functional outcome gates:
  - GitHub templates reinforce the repository artifact chain and validation expectations.
  - Language lint covers JS-family comments, CSS comments, and additional hash-comment file types.
  - Generated local artifacts from governance tooling are ignored by git.
- Test gates:
  - `make test`
  - `make check`
- Documentation gates:
  - Governance docs and contributor guidance reflect the template alignment.

## Carry-over

- Inherited items from previous iteration:
  - `BLG-004` continues the governance polish after `ITR-003` completed CI and Husky integration.
- Ownership and disposition for each item:
  - Finish the remaining intake/review and policy polish in one closing slice so the governance layer is internally consistent.

## Closure

- Final status: Closed
- Completed items: BLG-004
- Deferred items + follow-ups: none required for this slice.
- Validation summary (latest successful checks): `make governance-check` and `make check` passed on 2026-03-29.
- Execution checklist status: all items in `execution-plan.md` resolved.
