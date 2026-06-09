# review group count suppression traceability matrix

- goal:
  - review group header から件数を外す
- code evidence:
  - `veil-normalize.py` group header print
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
