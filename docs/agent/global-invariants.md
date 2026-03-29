# Global Invariants

- Every meaningful change should map to a GitHub issue when one exists.
- Non-trivial, rollout-sensitive, or local pre-deploy work should have a spec doc in `docs/specs/`.
- Spec lifecycle stays within `Draft`, `Accepted`, `Implemented`, `Superseded`, with checklist-style execution tracked in the spec.
- Repository documentation, code comments, and docstrings stay in English.
- Validation (`make check`) is required before declaring closure.
- Product-specific architecture and operations live in `README.md` and `CLAUDE.md`; planning docs should link to them instead of duplicating them.
