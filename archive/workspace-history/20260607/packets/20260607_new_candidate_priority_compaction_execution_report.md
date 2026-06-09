# Execution Report

## Bundle

- bundle id:
  - `VEIL-TUNING-018`
- theme:
  - `new-candidate priority compaction`

## Implemented

- `veil-normalize.py`
  - non-low-priority `new-candidate` の priority 行を compact 化
  - `priority: <hint>` の形で出力
  - reason compact / level compact / retention compact / variant compact / target compact / low-priority compact / existing-match compact は維持
  - JSON 契約は維持
- `README.md`
  - priority compact 契約を追記
- `docs/veil-design.md`
  - priority compact の条件と形を明記
- `skills/codex/veil-capture/SKILL.md`
  - priority compact の読み方を追記
- `skills/claude-code/veil-capture.md`
  - priority compact の読み方を追記
- `index/project-current-work.md`
  - wave 22 close 済み位置へ更新

## Verification

- `rtk python -m py_compile veil-normalize.py`
- mixed text smoke で `summary` が `priority: 次に見る`、`close` が low-priority compact のまま
- JSON smoke で key contract unchanged
- `rtk rg` で README / design / skills / current の契約が揃うことを確認

## Result

- wave 22 complete
- review-first 出力の priority 行がさらに短くなった
- reason compact / level compact / retention compact / variant compact / target compact / low-priority compact / existing-match compact / JSON に回帰なし
