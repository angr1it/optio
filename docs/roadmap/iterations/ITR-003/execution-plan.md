# Execution Plan: ITR-003

## Steps

- [x] Confirm the phase 2 scope and map it to `BLG-003`.
- [x] Add a reusable governance-only Make target, wire it into CI, and make Husky the primary local governance hook path.
- [x] Extend `language_lint.py` and its unit tests to cover TS/TSX comments, then run the full validation gate before closure.

## Risks

- CI integration could accidentally duplicate or replace the existing project jobs instead of adding a governance-specific check.
- TS/TSX comment scanning could create false positives if the parser is too naive around strings or block comments.

## Mitigations

- Keep the CI addition as a separate `governance` job and leave the existing jobs untouched.
- Cover the TS/TSX scanner with targeted unit tests for line comments, block comments, and comment-like strings.
