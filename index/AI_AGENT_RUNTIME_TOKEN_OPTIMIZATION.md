# AI Agent Runtime Token Optimization

## Purpose

Reduce token waste during current-work updates, design review, and runtime inspection without weakening VEIL canonical authority.

## Adopt Now

- thin entrypoint reading from `AGENTS.md`, `CLAUDE.md`, `common/README.md`, and `index/`
- bounded reads in `index/`, `docs/`, and the exact runtime file under change
- compact runtime setup for longer current-work sessions
- avoid loading generated outputs or historical shelves unless the task explicitly targets them

## Deferred

- heavier automatic context staging
- project-specific retrieval helpers
- broad scans outside the active current-work route

## Scale Profile

VEIL should currently use the medium-scale token optimization profile.

## Operator Rules

1. Read the shortest current route first.
2. Prefer direct reads of the exact current-work or design file under change.
3. Compression helpers may reduce read cost, but they do not decide current-work truth.
