# Requirements

## Goal

`veil-normalize.py` の `existing-match` で、`normalized` と同じ単一 variant が 1 回だけの時は `表記ゆれ:` を省き、行をさらに軽くする。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- multi-variant existing-match の変更
- new-candidate branch の変更
- JSON 契約変更

## Acceptance

- `existing-match` で sole variant が `normalized` と同じ、かつ count が 1 の時は `表記ゆれ:` を省く
- それ以外の existing-match は `表記ゆれ:` を維持する
- source suffix / source header 契約は維持する
- JSON unchanged
