# single-count headline suppression traceability matrix

- goal:
  - single count `x1` を headline から外す
- code evidence:
  - `veil-normalize.py` headline renderer
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
