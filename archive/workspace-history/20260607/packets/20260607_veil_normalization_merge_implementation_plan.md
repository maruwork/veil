# VEIL Normalization And Merge Implementation Plan

## 1. Decision

- add `veil-normalize.py` as a root runtime helper
- keep it read-only
- update canonical docs and governance indexes

## 2. Files

### New

- `veil-normalize.py`
- `workspace/20260607_veil_normalization_merge_requirements.md`
- `workspace/20260607_veil_normalization_merge_basic_design.md`
- `workspace/20260607_veil_normalization_merge_implementation_plan.md`

### Update

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`

## 3. Execution Order

1. add workspace packet
2. implement helper
3. connect helper into canonical workflow docs
4. verify compile and smoke output with workspace rules dir

## 4. Verification

- `python -m py_compile app.py veil-sync.py veil-lint.py veil-normalize.py install-startup.py`
- smoke cluster with mixed variants
- smoke existing rule match using workspace rules dir

## 5. Risks

- aggressive singularize
- over-clustering unrelated words
