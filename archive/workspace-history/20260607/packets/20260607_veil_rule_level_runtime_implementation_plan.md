# VEIL Rule Level Runtime Implementation Plan

## 1. Packet Minimum Fields

- workstream: VEIL rule level runtime
- objective: rule 3 層を physical format と lint semantics に落とす
- authority kept: `~/.veil/rules/`, `README.md`, `docs/veil-design.md`, `veil-lint.py`, `veil-normalize.py`
- compatibility policy: heading なし既存 rule は `必須`

## 2. Implementation Decision Record

- section heading 方式を採る
- `## 必須 / ## 推奨 / ## 観察` を rule file level marker とする
- `veil-lint.py` は `violations` と `warnings` を分ける
- `veil-normalize.py` は existing level を返す

## 3. Tasks

- T-A: rule level parser を `veil-lint.py` に入れる
- T-B: lint output / exit semantics を `WARN` 対応へ更新する
- T-C: rule level parser を `veil-normalize.py` に入れる
- T-D: docs を physical format に追従させる
- T-E: `py_compile` と smoke verify

## 4. Files

### New

- `workspace/20260607_veil_rule_level_runtime_requirements.md`
- `workspace/20260607_veil_rule_level_runtime_basic_design.md`
- `workspace/20260607_veil_rule_level_runtime_implementation_plan.md`

### Update

- `veil-lint.py`
- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`

## 5. Execution Order

1. packet を作る
2. `veil-lint.py` の parser と result bucket を更新する
3. `veil-normalize.py` の parser を更新する
4. docs を追従させる
5. `py_compile` と sample rules で smoke する

## 6. Acceptance Mapping

- FR1-F6 -> `veil-lint.py`
- FR7 -> `veil-normalize.py`
- format visibility -> `README.md`, `docs/veil-design.md`

## 7. Verification Plan

- `python -m py_compile veil-lint.py veil-normalize.py`
- sample rules dir で
  - required hit -> exit 1
  - warning only -> exit 0
  - observe only -> clean
- normalize existing match に level が出ることを確認する

## 8. Stop Conditions

- section heading 方式が current rule line format と両立しない
- warning / observe を入れると current json contract を大きく壊す
