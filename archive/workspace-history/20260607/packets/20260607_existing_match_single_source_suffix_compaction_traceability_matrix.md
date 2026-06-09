# existing-match single source suffix compaction traceability matrix

- goal:
  - single-source existing-match suffix の label を省く
- code evidence:
  - `veil-normalize.py` single-source line suffix
- doc evidence:
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
- current evidence:
  - `index/project-current-work.md`
- verification evidence:
  - `rtk python -B -m py_compile veil-normalize.py`
  - text smoke
  - JSON smoke
  - `rtk rg`
