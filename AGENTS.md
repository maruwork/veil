# VEIL governance entry point

## Source Map

- Main route and boundary guidance in this file: `Source: project-local adaptation of shared pj-template`
- Project-specific authority, stop rules, and cautions in this file: `Source: project-local`
- Design routing in this file: `Source: project-local adaptation of shared design-runtime`

## Scope

- Applies only to `C:\Users\f_tan\project\veil`.
- This repository is a local-first vocabulary consistency system with runtime, sync, lint, and status tooling.

## First Read

1. `README.md`
2. `common/README.md`
3. `docs/governance/ai-agent-runtime-token-optimization.md`
4. `docs/veil-design.md`
5. the exact runtime or tool file under change in `shared/runtime/`, `shared/tools/`, or `skills/`

## Current Authority

- `README.md` is the developer entry route
- `docs/veil-design.md` is the main design authority
- `shared/runtime/` and `shared/tools/` hold the active implementation surfaces
- `common/` is the reusable shared rule shelf, not the project-current or canonical vocabulary store

## Boundaries

- The canonical vocabulary store is `~/.veil/veil.db`.
- Root `AGENTS.md` and `CLAUDE.md` are sync targets, not the source of record for vocabulary rules.
- Do not broad-read `workspace/`, `archive/`, or unrelated support shelves unless the task explicitly targets them.

## Local Runtime Notes

- Runtime token note: `docs/governance/ai-agent-runtime-token-optimization.md`
- Claude Code companion: root `CLAUDE.md` stays thin and points back to this file plus the runtime token note.

## Design Routing

If the task touches runtime-facing design, review HTML behavior, capture/classification behavior, or visible support flow:

1. read `DESIGN.md`
2. follow the VEIL-local authority files named there
3. use local `common/pj-design-runtime/` only for design method, review, or handoff support
