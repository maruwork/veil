# Requirements

## Theme

SQLite canonical migration Stage 3: capture/sync write-generate route transition

## Goal

`~/.veil/veil.db` を current canonical route として使い、`capture` は SQLite へ記録し、`veil-sync.py` は SQLite から `~/.veil/rules/` markdown mirror を生成してから同期する。

## Scope In

- `veil_rule_store.py`
- `veil-db.py`
- `veil-sync.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Scope Out

- UI
- domain profile 拡張
- SQLite schema の大幅拡張
- 既存 `audit/normalize/lint` read route の再設計

## Problem

- current authority は SQLite canonical へ移ったが、`capture` の書込み手順はまだ markdown file 直書き前提
- `veil-sync.py` もまだ `~/.veil/rules/*.md` を直接 source としている
- そのため canonical/write route と read/authority route がねじれている

## Required Outcome

1. 新規 rule は SQLite canonical route へ書ける
2. markdown mirror は SQLite から生成できる
3. `veil-sync.py` は current phase で DB を優先し、mirror を更新してから同期できる
4. `veil-capture` skill は file 直書きではなく DB 記録 -> mirror 生成 -> sync の流れへ更新される

## Acceptance

- A1: `veil-db.py` に SQLite canonical へ 1 rule を追加更新する route がある
- A2: SQLite canonical から section-aware markdown mirror を生成できる
- A3: `veil-sync.py` が DB 優先で mirror を整備してから同期する
- A4: docs/skills/current work が Stage 3 write route に追従する
- A5: workspace smoke で `upsert -> export-mirror -> sync` の最小経路が確認できる

