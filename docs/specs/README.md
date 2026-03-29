# Specs

Specs are optional design docs for non-trivial changes in Optio.

Use a spec when the change is:

- cross-cutting across packages or runtime surfaces
- deployment-affecting
- schema- or API-affecting
- local-first work you want to complete before cluster rollout

Small, contained fixes usually do not need a spec.

Use `docs/specs/SPEC_TEMPLATE.md` as the baseline.

Required structure:

- lifecycle header: `Status`, `Owner`, `Issue`, `Stage`
- design sections: `Goal`, `Why Now`, `Scope`, `Validation`, `Rollout`, `Links`
- execution checklist in `## Plan`

Rules:

- `Status` must stay within `Draft -> Accepted -> Implemented -> Superseded`.
- `## Plan` should be an actionable checklist, not free-form prose.
- `## Plan` is the execution checklist for both manual work and Optio task execution.
- Carry-over or deferred work must point to a GitHub issue such as `#123`.
- If a change set links a spec, update that same spec in the same change set so its `## Plan` and `Status` stay synchronized.
- Sensitive runtime, API, DB, worker, or deploy changes should either update a spec doc or pass an explicit spec reference through the PR/local gate.
