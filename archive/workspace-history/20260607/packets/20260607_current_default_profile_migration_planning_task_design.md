# Current Default Profile Migration Planning Task Design

## 1. Parent Theme

- workstream: current default profile migration planning

## 2. Task Designs

### Task ID: T-A

- 親テーマ:
  - current default profile migration planning
- 親チェックポイント:
  - initial batch fixed
- 目的:
  - 初回 migration batch を決める
- 着手条件:
  - audit report 読了
- 読んでよい場所:
  - `workspace/20260607_current_default_profile_audit_report.md`
- 書いてよい場所:
  - `workspace/20260607_current_default_profile_migration_initial_batch.md`
- 触ってはいけない場所:
  - `~/.veil/rules/`
- やること:
  - file 数と rule 数から初回 batch を選ぶ
- 合格条件:
  - first batch が明記されている
- 証拠:
  - batch artifact

### Task ID: T-B

- 親テーマ:
  - current default profile migration planning
- 親チェックポイント:
  - reclassification rule fixed
- 目的:
  - `必須 / 推奨 / 観察` 再配置の判断軸を固定する
- 着手条件:
  - T-A 完了
- 読んでよい場所:
  - audit report
  - current canonical docs
- 書いてよい場所:
  - `workspace/20260607_current_default_profile_migration_initial_batch.md`
- 触ってはいけない場所:
  - `~/.veil/rules/`
- やること:
  - 必須残留条件、推奨降格条件、観察送り条件を書く
- 合格条件:
  - 再配置判断軸が読める
- 証拠:
  - batch artifact
