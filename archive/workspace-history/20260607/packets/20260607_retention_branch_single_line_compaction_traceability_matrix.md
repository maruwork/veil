# Traceability Matrix

- requirement: retention branch becomes one-line compact
  - design: `20260607_retention_branch_single_line_compaction_basic_design.md`
  - implementation: `veil-normalize.py`
  - verification: text smoke
- requirement: no separate `判別/priority/level` line remains in retention branch
  - design: `20260607_retention_branch_single_line_compaction_detailed_design.md`
  - implementation: `veil-normalize.py`
  - verification: text smoke
- requirement: surface alignment
  - implementation: `README.md`, `docs/veil-design.md`, `skills/*/veil-capture.md`, `index/project-current-work.md`
  - verification: readback search
