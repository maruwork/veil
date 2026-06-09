# existing-match source label compaction traceability matrix

- goal:
  - grouped `existing-match` source header の label を省く
- code evidence:
  - `veil-normalize.py` grouped source header print
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
