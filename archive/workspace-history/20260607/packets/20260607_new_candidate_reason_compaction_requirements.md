# Requirements

## Goal

`veil-normalize.py` の text 出力で non-low-priority `new-candidate` の理由行を compact にまとめ、review-first 出力の読み行数を減らす。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- headline compact branch の再設計
- low-priority compact branch の再設計
- `existing-match` compact branch の再設計
- JSON 契約変更

## Acceptance

- non-low-priority `new-candidate` の理由行が compact にまとまる
- `選別`, `review`, `判別` の理由が一行要約で読める
- `保留処理` と `書き込み候補` は維持する
- low-priority / existing-match / JSON unchanged

