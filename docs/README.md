# Documentation Map

Optio keeps process and design documentation separated from product runtime docs.

## Process and governance

- `docs/process/*` reusable delivery workflow and operating rules.
- `docs/testing/*` test and validation policy.
- `docs/specs/*` optional design specs for non-trivial or pre-deploy changes.

## Historical artifacts

- `docs/roadmap/*` previous markdown-backlog and iteration artifacts retained for migration history.
- `docs/features/*` previous feature-spec artifacts retained for migration history.

## Priority of truth

1. `AGENTS.md` and `docs/process/*` define mandatory workflow behavior.
2. GitHub issues and PRs track active intent and delivery state.
3. `docs/specs/*` defines design intent for non-trivial changes and should carry the execution checklist when a spec is in play.
4. `README.md` and `CLAUDE.md` remain the primary product and architecture references.
5. `docs/roadmap/*` and `docs/features/*` are historical, not canonical for new work.
