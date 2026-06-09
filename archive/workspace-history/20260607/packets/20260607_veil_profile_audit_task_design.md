# VEIL Profile Audit Task Design

## 1. Parent Theme

- workstream: VEIL profile audit

## 2. Task Designs

### Task ID: T-A

- 親テーマ:
  - VEIL profile audit
- 親チェックポイント:
  - audit runtime added
- 目的:
  - rules 棚卸し補助を実装する
- このタスクが必要な理由:
  - current default profile を non-destructive に見える化するため
- 着手条件:
  - parent packet 読了
- 入力:
  - current rule runtime semantics
- 読んでよい場所:
  - `veil-lint.py`
  - `veil-normalize.py`
- 書いてよい場所:
  - `veil-profile-audit.py`
- 触ってはいけない場所:
  - `~/.veil/rules/`
- やること:
  - heading-aware parser
  - per-file counts
  - summary
- 期待する出力:
  - read-only audit script
- 合格条件:
  - text/json 両出力がある
- 失敗条件:
  - rules を更新してしまう
- 停止条件:
  - parser semantics が current runtime と大きくずれる
- 差し戻し条件:
  - summary design が packet とずれる
- 人判断へ上げる条件:
  - legacy flat を必須へ丸めるだけでよいか曖昧な場合
- 証拠:
  - sample output
- 結果の記録先:
  - code diff
- 最終判定者:
  - project operator

### Task ID: T-B

- 親テーマ:
  - VEIL profile audit
- 親チェックポイント:
  - docs entry added
- 目的:
  - README / design へ導線を追加する
- このタスクが必要な理由:
  - tool を作っても入口がないと運用されない
- 着手条件:
  - T-A 完了
- 入力:
  - updated script
- 読んでよい場所:
  - `README.md`
  - `docs/veil-design.md`
- 書いてよい場所:
  - `README.md`
  - `docs/veil-design.md`
- 触ってはいけない場所:
  - skills
- やること:
  - command 例
  - use case を最小追記
- 期待する出力:
  - docs entry
- 合格条件:
  - 入口から使い方が辿れる
- 失敗条件:
  - docs 導線がない
- 停止条件:
  - docs が mainline 説明を濁す
- 差し戻し条件:
  - script 仕様が変わった
- 人判断へ上げる条件:
  - support script を current authority に上げるか迷う場合
- 証拠:
  - doc diff
- 結果の記録先:
  - updated docs
- 最終判定者:
  - project operator
