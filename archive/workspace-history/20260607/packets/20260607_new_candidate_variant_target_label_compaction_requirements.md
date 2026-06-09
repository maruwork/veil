# Requirements

## Goal

`new-candidate` detail line の `variants/target:` label を短縮し、`existing-match` と同じ `variants` 契約へ寄せる。

## Scope

- `veil-normalize.py` の non-low-priority `new-candidate` text 出力
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Acceptance

- `new-candidate` detail line が `variants: ... | <target>` で出る
- `variants/target:` が code / README / design / skills から消える
- current companion が新 bundle を指し、verify/writeback まで閉じる
