# existing-match single source suffix compaction requirements

## Goal

`veil-normalize.py` の 1 件 source `existing-match` 行末 `| source: <file>` を `| <file>` へ縮約する。

## Scope

- `veil-normalize.py` の single-source existing-match suffix を短縮する
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- grouped source header の再変更
- JSON 契約変更
- source grouping ロジック変更
- new-candidate branch の変更

## Acceptance

- 1 件 source の existing-match が `| t.md` のような file suffix になる
- grouped source header `c.md:` は維持される
- docs / skills / current companion が同契約へそろう
- compile / smoke / readback が通る
