# Requirements

## Goal

`veil-normalize.py` の text 出力で `existing-match` を source header の下にさらに compact にまとめ、既存統合先の確認をもっと速くする。

## Scope

- `veil-normalize.py` text renderer
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- JSON 契約変更
- candidate clustering ロジック変更
- SQLite schema / sync / lint 変更
- UI / helper DB

## Acceptance

- `existing-match` は source header の下で一行 compact に出る
- `normalized / preferred / level / 表記ゆれ` が一行で読める
- source header grouping は維持する
- `new-candidate` branch は変更しない
- JSON 契約は変更しない

