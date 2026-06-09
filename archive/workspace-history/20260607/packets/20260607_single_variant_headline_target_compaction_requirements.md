# Requirements

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` detail branch で、single-variant かつ variant 情報が headline と重複する時だけ `target` を headline へ寄せ、`variants/target` 行を省く。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- low-priority branch の再設計
- existing-match branch の変更
- JSON 契約変更

## Acceptance

- single-variant で `normalized` と variant 情報が重複する non-low-priority `new-candidate` は headline に `| <target>` が付き、`variants/target` 行を省く
- multi-variant または variant 情報が冗長でない場合は `variants/target` 行を維持する
- low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
