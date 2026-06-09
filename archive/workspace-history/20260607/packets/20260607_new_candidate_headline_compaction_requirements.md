# Requirements

## Goal

`veil-normalize.py` の text 出力で non-low-priority の `new-candidate` に headline 一行 compact を入れ、詳細 block を読む前の走査を速くする。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- low-priority compact branch の再設計
- `existing-match` compact branch の再設計
- JSON 契約変更
- schema / sync / lint change

## Acceptance

- non-low-priority `new-candidate` が headline 一行 compact を持つ
- headline に `normalized / level / count` が入る
- detail lines は必要情報を維持する
- low-priority compact branch unchanged
- `existing-match` branch unchanged
- JSON unchanged

