# Current Default Profile Audit Execution Task Design

## 1. Parent Theme

- workstream: current default profile audit execution

## 2. Task Designs

### Task ID: T-A

- 親テーマ:
  - current default profile audit execution
- 親チェックポイント:
  - execution packet fixed
- 目的:
  - 実監査前の境界を固定する
- 着手条件:
  - `veil-profile-audit.py` 実装済み
- 読んでよい場所:
  - `veil-profile-audit.py`
  - `workspace/20260607_veil_profile_audit_*.md`
- 書いてよい場所:
  - `workspace/`
- 触ってはいけない場所:
  - `~/.veil/rules/`
- やること:
  - packet を作る
- 合格条件:
  - 実監査の scope が固定されている
- 証拠:
  - packet files

### Task ID: T-B

- 親テーマ:
  - current default profile audit execution
- 親チェックポイント:
  - audit run complete
- 目的:
  - real rules dir の summary を得る
- 着手条件:
  - T-A 完了
- 読んでよい場所:
  - `~/.veil/rules/`
  - `veil-profile-audit.py`
- 書いてよい場所:
  - `workspace/`
- 触ってはいけない場所:
  - `~/.veil/rules/`
- やること:
  - text / json audit を実行する
- 合格条件:
  - summary と per-file report が取れている
- 証拠:
  - command outputs

### Task ID: T-C

- 親テーマ:
  - current default profile audit execution
- 親チェックポイント:
  - audit artifact fixed
- 目的:
  - 監査結果を reusable artifact にする
- 着手条件:
  - T-B 完了
- 読んでよい場所:
  - audit outputs
- 書いてよい場所:
  - `workspace/20260607_current_default_profile_audit_report.md`
- 触ってはいけない場所:
  - `~/.veil/rules/`
- やること:
  - summary、注目点、次 wave 候補を report に書く
- 合格条件:
  - next cleanup wave に渡せる report になっている
- 証拠:
  - report file
