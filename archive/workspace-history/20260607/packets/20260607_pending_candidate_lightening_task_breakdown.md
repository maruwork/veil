# Task Breakdown

## Parent Theme

VEIL tuning wave 6: 保留候補運用の軽量化

## Path

- CP-1 wave 6 packet fixed
- CP-2 runtime retention hint added
- CP-3 docs and skills aligned
- CP-4 verification and current writeback closed

## Tasks

### T1. Wave 6 Packet Fix

- outcome:
  - wave 6 の goal / path / checkpoint / task / design / traceability / quality gate を固定する
- target files:
  - `workspace/20260607_pending_candidate_lightening_*.md`
  - `index/project-current-work.md`
- dependency:
  - wave 5 close 済み
- acceptance:
  - current companion から wave 6 の戻り先が一意に読める
- verification:
  - readback

### T2. Runtime Retention Hint

- outcome:
  - `veil-normalize.py` が `保留寄り` に保留処理目安を返す
- target files:
  - `veil-normalize.py`
- dependency:
  - T1
- acceptance:
  - A1, A2
- verification:
  - `py_compile`
  - JSON / text smoke

### T3. Skill and Canonical Alignment

- outcome:
  - README / design / skills が保留処理目安を同じ言葉で説明する
- target files:
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
- dependency:
  - T2
- acceptance:
  - A3
- verification:
  - readback

### T4. Current Writeback and Evidence Close

- outcome:
  - execution report と current companion が wave 6 close を反映する
- target files:
  - `workspace/20260607_pending_candidate_lightening_execution_report.md`
  - `index/project-current-work.md`
- dependency:
  - T2
  - T3
- acceptance:
  - A4
- verification:
  - readback
