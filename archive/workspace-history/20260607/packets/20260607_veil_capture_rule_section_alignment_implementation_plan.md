# VEIL Capture Rule Section Alignment Implementation Plan

## 1. Tasks

- T-A: skill の task 7 を file + section 決定へ更新する
- T-B: skill の task 8 を section-aware 書き込みへ更新する
- T-C: README / design の補足を必要最小限で追従させる
- T-D: surface 整合確認

## 2. Files

- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `README.md`
- `docs/veil-design.md`

## 3. Verification

- `rtk rg` で `section`, `必須`, `推奨`, `観察`, `heading のない既存` を確認する
- skill の task 7-8 が flat format 前提のまま残っていないことを確認する
