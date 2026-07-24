# AI Agent Runtime Token Optimization

## Purpose

Reduce token waste during vocabulary-rule review, runtime script inspection, sync validation, and lint/status checks without weakening VEIL canonical authority.

## Adopt Now

- RTK for repetitive sync, lint, status, and validation output
- root `.claudeignore` to keep broad Claude reads out of archive, workspace, and hidden tool shelves
- thin entrypoint reading from `README.md`, `common/README.md`, `docs/governance/`, and `docs/veil-design.md`
- bounded reads in `docs/`, `shared/runtime/`, `shared/tools/`, `skills/`, and the exact file under change
- compact / plan discipline for longer validation or profile-review sessions
- keep reusable prompt blocks stable and move fast-changing task detail to the tail when repeated same-project work spans many turns
- ask for bounded output by default unless the actual deliverable must be long-form
- avoid bulk-reading generated outputs, archive residue, and unrelated support shelves unless the task explicitly targets them
- keep project-local implementation details under `common/pj-token-optimization/`

## Deferred

- retrieval helper
- code-understanding index
- integrated runtime layers such as Headroom
- heavier context-mode automation

## Scale Profile

veil should currently use the medium-to-large output profile.

## Operator Rules

1. Read the shortest active route first.
2. Prefer targeted reads of `docs/veil-design.md`, `shared/runtime/`, `shared/tools/`, and the exact file under change.
3. Let root `.claudeignore` carry the broad-read boundary for archive, workspace, and hidden tool shelves.
4. Use RTK-filtered command execution for repetitive sync, lint, status, and validation output.
5. Compression helpers do not decide vocabulary truth, sync-target truth, or canonical DB truth.
6. Keep reusable prompt blocks stable and move fast-changing task detail to the tail when repeated prompt reuse matters.
7. Ask for the shortest output that still completes the task unless the work product itself must be long-form.
