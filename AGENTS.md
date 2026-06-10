# veil ガバナンス入口

## Scope

- Applies only to `C:\Users\f_tan\project\veil`.
- delegated AI の入口はこの file、その次に `CLAUDE.md`

## First Read

1. `AGENTS.md`
2. `README.md`
3. `docs/veil-design.md`
4. files relevant to the task

## Current Authority

- 本線 authority: `README.md`, `docs/`, `shared/runtime/veil-sync.py`, `shared/runtime/veil-lint.py`, `shared/runtime/veil-normalize.py`, `shared/runtime/veil-status.py`
- current canonical route: `~/.veil/veil.db`
- AI-readable 遷移ミラー: `~/.veil/rules/`
- profile support tools: `shared/tools/veil-profile-audit.py`, `shared/tools/veil-profile-export.py`, `shared/tools/veil-db.py`, `shared/tools/veil_rule_store.py`
- skill assets: `skills/`

## VEIL Operation Loop

- VEIL は `AI-assisted technical writing` 向けの terminology guardrail として扱う
- `veil-capture` は task close / 会話区切りで通す閉じ処理として扱う
- `veil-capture` は current phase では SQLite canonical への抽出・記録経路であり、記録後に `~/.veil/rules/` ミラーを生成する。候補語を一気に全部登録せず、判別して高需要語から採用し、残りはスキップする
- `shared/runtime/veil-normalize.py` は記録前に候補語の正規化と既存ルール照合を補助する経路。出力は `既存一致:` / `新規候補:` の 2 グループ
- `shared/runtime/veil-status.py` は canonical / ミラー / 同期対象 / skill の状態確認とセットアップ診断を行う経路
- `shared/runtime/veil-sync.py` は同期経路
- `shared/runtime/veil-lint.py` は最終日本語出力前の必須 gate として扱う
- `shared/runtime/veil-lint.py` は文章に使い、capture report や code block や意図的な原語列挙には使わない
- rule はすべて等価に hard gate として扱う（レベル区分なし）
- VEIL core は `capture / normalize / sync / lint / status` とその運用骨格であり、domain profile は rules、禁止語、高需要語、判別基準、厳格度を差し替える面とする
- `shared/tools/veil-profile-audit.py`、`shared/tools/veil-profile-export.py`、`shared/tools/veil-db.py`、`shared/tools/veil_rule_store.py` は support runtime であり、本線 authority ではない

## Stop Rule

Stop immediately if work would:

- `archive/` を現在の authority に昇格させること
- hidden 補助棚 (`.agents/`, `.claude/`, `.remember/`) を明示指示なしで変更すること
- 事前読込なしで 1 つの仮定から複数の runtime/doc 棚を書き換えること
- UI / helper DB 系を、本線 (`rules / capture / normalize / sync / lint`) へ混ぜ戻すこと
