# Task Breakdown

## Parent Theme

VEIL tuning wave 7: 一般動詞の追加保守 tuning

## Path

- CP-1 wave 7 packet fixed
- CP-2 runtime verb family tuning added
- CP-3 docs and skills aligned
- CP-4 verification and current writeback closed

## Tasks

### T1. Wave 7 Packet Fix

- outcome:
  - wave 7 の bundle packet と current companion を固定する
- target files:
  - `workspace/20260607_general_verb_conservative_tuning_*.md`
  - `index/project-current-work.md`
- dependency:
  - wave 6 close
- acceptance:
  - current companion から wave 7 の戻り先が一意に読める

### T2. Runtime Verb Family Tuning

- outcome:
  - `veil-normalize.py` が一般動詞 family を保守側に倒す
- target files:
  - `veil-normalize.py`
- dependency:
  - T1
- acceptance:
  - A1, A2

### T3. Skill and Canonical Alignment

- outcome:
  - docs / skills が一般動詞の追加保守 tuning を共有する
- target files:
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
- dependency:
  - T2
- acceptance:
  - A3

### T4. Current Writeback and Evidence Close

- outcome:
  - execution report と current companion が wave 7 close を反映する
- target files:
  - `workspace/20260607_general_verb_conservative_tuning_execution_report.md`
  - `index/project-current-work.md`
- dependency:
  - T2
  - T3
