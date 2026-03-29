# Roadmap Governance

Optio uses a **single backlog** and **single iteration stream** for agent-facing planning artifacts.

## Files

- Active backlog: `docs/roadmap/BACKLOG.md`
- Archive backlog: `docs/roadmap/ARCHIVE_BACKLOG.md`
- Backlog item template: `docs/roadmap/BACKLOG_TEMPLATE.md`
- Iterations index: `docs/roadmap/iterations/README.md`

## Lifecycle

`Proposed -> Ready -> In Progress -> Done`

Optional states:

- `Blocked`
- `Deferred`

## Rules

- Keep each item in exactly one canonical location (active backlog or archive).
- Move `Done` items from active backlog to archive in the same change set.
- Keep `Target iteration` as `TBD` when not committed.
- Reference backlog IDs from feature specs and iteration artifacts.
- Track execution steps in `execution-plan.md` with Markdown checkboxes.
- Closed iterations must not leave open checkboxes in `execution-plan.md`.
