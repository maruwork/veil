# Veil Current Work

Status: Active

## Purpose

`veil` の daily current / active bundle declaration / `continue` 戻り先を固定する。

## Active Bundle

- active bundle id:
  - なし（次の bundle 待ち）
- active bundle type:
  - —
- success subject:
  - `~/.veil/veil.db が初期化され、veil-status.py --check が全 OK になる`
- completion condition:
  - `VEIL-OP-001 T-01 / T-02 完了`
- in scope:
  - `~/.veil/veil.db` の初期化と mirror 取り込み（T-01）
  - readback + --check 検証（T-02）
- out of scope:
  - mirror ファイルへの変更
  - veil-sync.py 実行
  - shared/tools/veil-profile-export.py の level 定数除去（別 bundle）

## Current Position

- current position:
  - `VEIL-UX-002 全タスク完了 + README.md level 参照除去完了`
- next action:
  - VEIL-OP-001 実行（owner 承認後）
- stop reason if any:
  - なし
- writeback target:
  - `index/project-current-work.md`

## Bundle Read Order

- goal:
  - `index/veil-op-001-bundle.md` §要件マッピング
- path:
  - `index/veil-op-001-bundle.md` §F-01 操作設計
- checkpoint:
  - `index/veil-op-001-bundle.md` §チェックポイント構成
- task:
  - `index/veil-op-001-bundle.md` §T-01 / §T-02

## Checkpoint View

- path:
  - `CP-1 DB 初期化 -> CP-2 検証完了`
- next gate:
  - CP-1（T-01 完了後）

## 環境状態スナップショット（2026-06-09）

```
~/.veil/
  rules/       ← mirror 19 ファイル存在（a.md 〜 w.md）
  targets.json ← sync target 1 件登録済み
  config.json  ← sync_script 記録済み
  behavior.md  ← 存在
  veil.db      ← 存在しない（VEIL-OP-001 の対象）
```

`veil-status.py --check` 現在出力：

```
[ERROR] ~/.veil/veil.db
[OK]    ~/.veil/rules/
[OK]    ~/.veil/targets.json
[OK]    sync target
[OK]    skill
```

## 既知残課題

| ファイル | 内容 | 対応 |
|---|---|---|
| `shared/tools/veil-profile-export.py` | `LEVEL_REQUIRED / LEVEL_RECOMMENDED / LEVEL_OBSERVE / LEVEL_HEADING_RE` 残留 | 別 bundle で対応 |

## Prior Bundles

- VEIL-UX-002:
  - status: `complete`
  - summary: `normalize を 2 グループ出力に簡略化。veil-status.py 新設。docs を現行実装に一致させた。README.md level 参照全除去`
- VEIL-ORG-002:
  - status: `complete`
  - summary: `support runtime .py 4 本を shared/tools/ へ移し、参照パスを全書き戻し済み`
- VEIL-UX-001:
  - status: `superseded`
  - summary: `コード精査・構造精査・全修正を完了。VEIL-UX-002 に引き継ぎ`

## Continue Rule

- `続行` 時は最初にこの file を読む
- `README.md`、`docs/veil-design.md`、runtime files だけで active bundle を決めない
- residual を始める時は close 済み bundle の続きにせず、新しい bundle id を立てる
- bundle 実装前に `goal -> path -> checkpoint -> task -> design -> traceability -> gate` をこの file から辿れることを確認する

## Current Source Note

- `README.md` は product/current overview として維持する
- `docs/veil-design.md` は detailed design authority として維持する
- daily current / bundle declaration の正本はこの面で受ける
