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
  - `2026-06-10 UX セッション完了 — veil-capture 書き直し・veil.html 新設・hooks 設定・install.sh 追加`
- next action:
  - veil-sync に veil.html 自動生成を実装（現在は静的ハードコード）
  - install.sh にフック設定を追加（現在はスキルファイルのコピーのみ）
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

## 環境状態スナップショット（2026-06-10）

```
~/.veil/
  rules/       ← ミラー 10 ファイル（10 語登録済み）
  targets.json ← 同期対象 1 件登録済み
  config.json  ← sync_script 記録済み（veil プロジェクトパスに修正済み）
  behavior.md  ← 存在
  veil.db      ← 存在（10 語登録済み）
  veil.html    ← 存在（静的ハードコード、10 語表示）
```

インストール済みスキル：
- `~/.claude/commands/veil-capture.md` ← 3 セクション版
- `~/.agents/skills/veil-capture/SKILL.md` ← 3 セクション版

SessionStart フック：
- Claude Code: `~/.claude/settings.json` に設定済み
- Codex: `~/.codex/hooks.json` に設定済み、`~/.codex/config.toml` の `codex_hooks = true`

## 既知残課題

| 内容 | 対応 |
|---|---|
| `veil.html` が静的ハードコード（veil-sync が自動生成していない） | veil-sync に HTML 生成を実装する |
| `install.sh` がフック設定を含まない（スキルコピーのみ） | フック設定ステップを追加する |
| `shared/tools/veil-profile-export.py` の `LEVEL_*` 定数残留 | 別 bundle で対応 |

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
