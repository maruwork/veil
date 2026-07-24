# VEIL design authority

**Last updated**: 2026-07-09

This file is the root design authority entry for this repository.
It does not restate every design rule.
It fixes which VEIL-local files own design truth so runtime, vocabulary-review, and support behavior do not drift.

## Scope

- Applies only to `C:\Users\f_tan\project\veil`.
- Use this for visible runtime flow, review HTML behavior, capture/classification behavior, and tool-facing design questions.

## Authority Model

- `DESIGN.md` does not own every design rule directly.
- `DESIGN.md` names which VEIL-local files are authoritative for each design area.
- `common/pj-design-runtime/` is shared method only. It is not VEIL design truth.

## Read Order For Design Work

1. `docs/veil-design.md`
2. `docs/veil-capture-classification.md`
3. `README.md`
4. `common/pj-design-runtime/` only when design method, review, or handoff support is needed

## Authoritative Owners By Subject

- main runtime and support design truth:
  - `docs/veil-design.md`
- capture-classification behavior:
  - `docs/veil-capture-classification.md`
- developer-facing entry and repo route:
  - `README.md`

## Non-Authority Or Limited-Authority Surfaces

- `common/pj-design-runtime/`
  - shared design method only
- `workspace/`, `archive/`
  - non-authority
- root `AGENTS.md` and root `CLAUDE.md`
  - routing only

## Stop Rule

Stop if work would:

- treat `common/pj-design-runtime/` as VEIL design truth
- replace the existing main design authority in `docs/veil-design.md`
- create a second competing design owner instead of updating one of the named files above
