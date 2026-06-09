# existing-match source label compaction requirements

## Goal

`veil-normalize.py` の grouped `existing-match` source header から `source:` ラベルを外し、`<file>:` の短い header にする。

## Scope

- `veil-normalize.py` の grouped source header を `source: c.md` から `c.md:` へ変更する
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- 1 件 source の item 行末 `| source: <file>` 変更
- JSON 契約変更
- source grouping ロジック変更
- normalize/capture の判定ロジック変更

## Acceptance

- grouped `existing-match` source header が `<file>:` になる
- 1 件 source の item 行末 `| source: <file>` は維持される
- docs / skills / current companion が同契約へそろう
- compile / smoke / readback が通る
