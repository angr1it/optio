---
name: spec-to-issue
description: Read a concrete Optio spec doc and generate a copy-pasteable GitHub feature issue draft that stays within the spec's scope, validation, and rollout constraints.
metadata:
  short-description: Turn docs/specs/*.md into a GitHub issue draft
---

# Spec To Issue

Use this skill when the user already has a spec doc and wants a ready-to-paste GitHub issue message for Optio intake.

The source of truth is the spec file. Do not widen scope, invent acceptance criteria, or silently drop rollout and validation constraints.

## Workflow

1. Read the spec path the user provided.
2. Run `scripts/spec_to_issue.py <spec-path>`.
3. Return the result in chat as:
   - `Title: ...`
   - a fenced `md` block containing the issue body
4. If the script reports missing or malformed spec sections, stop and tell the user what needs to be fixed in the spec before generating the issue draft.

## Output shape

Target the repository's GitHub feature issue format:

- `## Summary`
- `## Why Now`
- `## Scope`
- `## Acceptance Criteria`
- `## Validation Signals`
- `## Related Context`
- `## Governance Follow-Up`

Keep the issue body faithful to the spec:

- `## Goal` -> `## Summary`
- `## Why Now` -> `## Why Now`
- `## Scope` -> `## Scope`
- `Priority` and `## Sequencing` -> `## Related Context`
- `## Plan` -> `## Acceptance Criteria` after filtering out pure validation steps
- `## Validation` and `## Rollout` -> `## Validation Signals`
- `## Links` and spec metadata -> `## Related Context` / `## Governance Follow-Up`

## Scripts

- `scripts/spec_to_issue.py <spec-path>`
- `scripts/spec_to_issue.py <spec-path> --body-only`
- `scripts/spec_to_issue.py <spec-path> --title-only`

## Notes

- Prefer spec paths inside `docs/specs/`.
- If the spec still says `Issue: N/A (local pre-deploy planning)`, keep that context in the generated draft so the new issue can become the durable backlog artifact.
- Deferred or carry-over work must remain GitHub issue/project state, not markdown backlog state.
