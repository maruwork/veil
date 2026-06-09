# Traceability Matrix

| Requirement | Design Section | Task | Evidence |
|---|---|---|---|
| A1 normalize result に保留処理目安が入る | detailed design 1, 2 | T2 | JSON smoke |
| A2 text 出力で保留処理目安が読める | detailed design 3 | T2 | text smoke |
| A3 skills/docs が短い扱い順を共有する | detailed design 4 | T3 | readback |
| A4 current companion が wave 6 completion condition を持つ | basic design 2, task breakdown T4 | T1, T4 | current readback |

## Scope Mapping

| Scope Type | Files |
|---|---|
| runtime | `veil-normalize.py` |
| canonical docs | `README.md`, `docs/veil-design.md` |
| operation skills | `skills/codex/veil-capture/SKILL.md`, `skills/claude-code/veil-capture.md` |
| current companion | `index/project-current-work.md` |

## Explicit Out of Scope

- `veil-lint.py`
- `veil-sync.py`
- SQLite schema
- markdown mirror generation
- UI
