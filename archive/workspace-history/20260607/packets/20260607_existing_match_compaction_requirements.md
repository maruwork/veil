# Requirements

## Theme

VEIL tuning wave 10: existing-match compaction

## Goal

`veil-normalize.py` の text 出力で、`existing-match` の既存一致候補を短く読めるようにする。

## Scope In

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Scope Out

- JSON contract change
- schema change
- lint runtime
- UI

## Required Outcome

1. `existing-match` は text 出力で短い要約にまとまる
2. 新規候補の詳細ブロックは維持する
3. JSON 契約は維持する
4. docs / skills / current companion が compact existing-match 契約を共有する

## Acceptance

- A1: existing-match が text で短い要約行になる
- A2: new-candidate の詳細は従来どおり見える
- A3: JSON output は構造不変
- A4: README / design / skills / current companion が同じ契約を持つ
