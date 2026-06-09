# VEIL Operation Loop Hardening Implementation Plan

## 1. Packet Minimum Fields

- workstream: VEIL operation loop hardening
- first implementation wave: response lint introduction
- authority kept: `~/.veil/rules/`
- non-authority kept: `vocab.db`, `workspace/`

## 2. Implementation Decision Record

- add `veil-lint.py` as a new root runtime script
- keep `veil-sync.py` focused on sync only
- update canonical docs so trigger / workflow / fail-close are visible
- leave normalize/merge assistance as follow-up, not mixed into this wave

## 3. Files

### New

- `veil-lint.py`
- `workspace/20260607_veil_operation_loop_hardening_requirements.md`
- `workspace/20260607_veil_operation_loop_hardening_basic_design.md`
- `workspace/20260607_veil_operation_loop_hardening_implementation_plan.md`

### Update

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`

## 4. Execution Order

1. add workspace packet
2. implement `veil-lint.py`
3. update canonical docs and governance indexes
4. verify with `py_compile`
5. run smoke lint on sample clean / violation text

## 5. Acceptance Mapping

- FR1-FR4 -> `veil-lint.py`
- trigger / fail-close visibility -> `AGENTS.md`, `README.md`, `docs/veil-design.md`
- runtime surface registration -> `index/`

## 6. Verification Plan

- `python -m py_compile app.py veil-sync.py veil-lint.py install-startup.py`
- smoke case: text containing registered original term should return violation
- smoke case: clean Japanese text should return clean
- search current canonical docs for `veil-lint.py` presence

## 7. Risks

- parser may miss hand-edited rule lines
- lint may over-report intentional English explanations

## 8. Stop Conditions

- if rule file format in real `~/.veil/rules/` differs materially from documented template
- if adding a new runtime script would require redefining current authority beyond reviewed surfaces
