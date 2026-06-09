# veil ガバナンス入口

## Scope

- Applies only to `C:\Users\f_tan\project\veil`.
- delegated AI の入口はこの file、その次に `CLAUDE.md`
- この棚では local common、index governance、docs、runtime、workspace、archive を分離する

## First Read

1. `AGENTS.md`
2. `common/README.md`
3. `common/frameworks/project-progression-rule.md`
4. `index/project-template-adoption-packet.md`
5. `index/project-file-taxonomy.md`
6. `index/project-boundary-register.md`
7. `index/project-workspace-and-artifact-policy.md`
8. `index/project-current-work.md`
9. `README.md`
10. `docs/veil-design.md`
11. `shared/runtime/veil-sync.py`
12. `shared/runtime/veil-lint.py`
13. `shared/runtime/veil-normalize.py`

## Current Authority

- `common/` はこの project の共通ルール棚
- governance support は `index/` 配下
- `続行` 時の current companion は `index/project-current-work.md`
- 本線 authority: `README.md`, `docs/`, `shared/runtime/veil-sync.py`, `shared/runtime/veil-lint.py`, `shared/runtime/veil-normalize.py`, `shared/runtime/veil-status.py`
- current canonical route: `~/.veil/veil.db`
- AI-readable transition mirror: `~/.veil/rules/`
- profile support tools: `shared/tools/veil-profile-audit.py`, `shared/tools/veil-profile-export.py`, `shared/tools/veil-db.py`, `shared/tools/veil_rule_store.py`
- skill assets: `skills/`

## VEIL Operation Loop

- VEIL は `AI-assisted technical writing` 向けの terminology guardrail として扱う
- `veil-capture` は task close / 会話区切りで通す閉じ処理として扱う
- `veil-capture` は current phase では SQLite canonical への抽出・記録経路であり、記録後に `~/.veil/rules/` mirror を生成する。候補語を一気に全部登録せず、判別して高需要語から採用し、残りは保留へ回す
- `shared/runtime/veil-normalize.py` は記録前に候補語の正規化と既存ルール照合を補助する経路。出力は `既存一致:` / `新規候補:` の 2 グループ
- `shared/runtime/veil-status.py` は canonical / mirror / sync targets / skill の状態確認とセットアップ診断を行う経路
- `shared/runtime/veil-sync.py` は同期経路
- `shared/runtime/veil-lint.py` は最終日本語出力前の必須 gate として扱う
- `shared/runtime/veil-lint.py` は文章に使い、capture report や code block や意図的な原語列挙には使わない
- rule はすべて等価に hard gate として扱う（レベル区分なし）
- VEIL core は `capture / normalize / sync / lint / status` とその運用骨格であり、domain profile は rules、禁止語、高需要語、判別基準、厳格度を差し替える面とする
- `shared/tools/veil-profile-audit.py`、`shared/tools/veil-profile-export.py`、`shared/tools/veil-db.py`、`shared/tools/veil_rule_store.py` は support runtime であり、本線 authority ではない

## Stop Rule

Stop immediately if work would:

- `common/` を共通ルール棚ではなく現在のプロジェクト状態として扱うこと
- `archive/` を現在の authority に昇格させること
- hidden 補助棚 (`.agents/`, `.claude/`, `.remember/`) を明示指示なしで変更すること
- 事前読込なしで 1 つの仮定から複数の runtime/doc 棚を書き換えること
- UI / helper DB 系を、本線 (`rules / capture / normalize / sync / lint`) へ混ぜ戻すこと
