# VEIL Profile Audit Implementation Plan

## 1. Tasks

- T-A: audit parser / report script を追加する
- T-B: README / design に導線を追加する
- T-C: sample rules で verify する

## 2. Files

- new:
  - `veil-profile-audit.py`
  - `workspace/20260607_veil_profile_audit_requirements.md`
  - `workspace/20260607_veil_profile_audit_basic_design.md`
  - `workspace/20260607_veil_profile_audit_implementation_plan.md`
- update:
  - `README.md`
  - `docs/veil-design.md`

## 3. Verification

- `python -m py_compile veil-profile-audit.py`
- sample rules dir で text / json output を確認する
