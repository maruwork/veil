# 実装計画テンプレート準拠

**Task**: VEIL-TUNING-001-CAPTURE-EXTRACTION-TIGHTENING  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-TUNING-001-CAPTURE-EXTRACTION-TIGHTENING` |
| goal | capture の候補抽出を少し厳しくする |
| owner_role | owner / delegated AI |
| scope_in | skills/docs/current |
| scope_out | runtime/schema/UI |
| next_gate | extraction contract readback 完了 |

## 2. Implementation Decision Record

- background:
  - wave 1-4 closed
- decision:
  - wave 5 は capture extraction tightening に入る
- rationale:
  - 候補を拾いすぎる問題を入口で減らすため
- completion conditions:
  - broad verb candidate を抑える抽出契約になる

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| wave 1-4 closed | PASS | reports exist |
| scope narrow | PASS | skills/docs only |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_capture_extraction_tightening_*.md` | create | wave 5 packet |
| `skills/codex/veil-capture/SKILL.md` | modify | extraction contract tightening |
| `skills/claude-code/veil-capture.md` | modify | extraction contract tightening |
| `README.md` | modify | capture overview update |
| `docs/veil-design.md` | modify | capture flow update |
| `index/project-current-work.md` | modify | wave 5 current writeback |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| A1 | skill extraction section | readback |
| A2 | README / design wording | readback |
| A3 | current companion | readback |

