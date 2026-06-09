# Profile Support Alignment And Export Implementation Plan

## 1. Tasks

1. governance surface に profile support runtime を追加する
2. `veil-profile-export.py` を実装する
3. canonical docs と AGENTS を export 導線へ追従させる
4. py_compile と export smoke を実行する
5. execution report を残す

## 2. Files

### Read

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`
- `veil-profile-audit.py`

### Write

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`
- `veil-profile-export.py`
- `workspace/20260607_profile_support_alignment_and_export_execution_report.md`

## 3. Verification

- `python -m py_compile veil-profile-audit.py veil-profile-export.py`
- `python veil-profile-export.py --profile-name technical-writing-default`
- output dir readback
