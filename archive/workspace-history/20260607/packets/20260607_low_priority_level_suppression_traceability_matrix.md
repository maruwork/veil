# low-priority level suppression traceability matrix

- goal:
  - low-priority text line の固定 level を省く
- code evidence:
  - `veil-normalize.py` low-priority compact print
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
