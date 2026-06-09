# source label path compaction requirements

## Goal

`veil-normalize.py` の text 出力先頭 `参照ルール: <full path>` を短縮し、path 全体ではなく短い source label を出す。

## Scope

- `veil-normalize.py` の source label text 表示
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- JSON `source` 値の変更
- rules-dir / db 読取ロジック変更
- new-candidate / existing-match branch 変更

## Acceptance

- text 出力先頭が full path ではなく短い source label になる
- JSON の `source` は unchanged
- docs / skills / current companion が同契約へそろう
- compile / smoke / readback が通る
