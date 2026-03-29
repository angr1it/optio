# Execution Plan: ITR-004

## Steps

- [x] Map the remaining governance follow-up work to `BLG-004`.
- [x] Align GitHub issue and PR templates with the backlog, feature, iteration, and validation workflow.
- [x] Extend language lint coverage and `.gitignore`, then rerun the governance and full repository gates before closure.

## Risks

- Template changes could accidentally demand docs artifacts for trivial work without allowing an explicit `N/A` path.
- Broader language scanning could create false positives if it starts reading runtime strings instead of comments.
- New ignore rules could hide files that should be intentionally tracked.

## Mitigations

- Keep explicit `N/A` guidance in the PR template for cases where the artifact chain does not apply.
- Restrict the expanded scanners to comment-bearing surfaces only.
- Ignore only clearly generated/local artifacts such as cache directories, validator reports, and the template reference copy.
