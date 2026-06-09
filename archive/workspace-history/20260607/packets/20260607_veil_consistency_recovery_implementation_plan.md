# VEIL Consistency Recovery Implementation Plan

Task: VEIL current consistency recovery
Author: Codex
Date: 2026-06-07
Status: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | VEIL-20260607-consistency-recovery |
| goal | active surface と governance を current VEIL へ整合させる |
| owner_role | VEIL owner |
| scope_in | docs/manual, design doc, index authority, obsolete multilingual residue |
| scope_out | new feature, DB redesign, extractor redesign |
| next_gate | implementation after plan review by active execution |

## 2. Implementation Decision Record

- background:
  - VEIL は rules-first 運用へ移っているが、old multilingual residue と authority mismatch が残っている
- decision:
  - runtime truth を基準に active docs / governance docs を更新する
- rationale:
  - 最小変更で current understanding を揃えられる
- rejected alternatives:
  - runtime redesign
  - `shared/vocab.db` への即時移設
- impact scope:
  - `docs/manual.html`
  - `docs/veil-design.md`
  - `index/project-file-taxonomy.md`
  - `index/project-template-adoption-packet.md`
  - possibly `index/project-boundary-register.md`
- completion conditions:
  - obsolete multilingual residue removal
  - `vocab.db` authority alignment
  - `p1` fallback spec alignment
- SSOT declaration when data contracts are involved:
  - runtime truth for current behavior:
    - `app.py`
    - `veil-sync.py`
    - `ui/js/convert.js`

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| scope が承認済み | PASS | user requested start and multilingual residue removal |
| dependency が利用可能 | PASS | local files only |
| 関連 docs が current | FAIL | this task exists because current docs are not fully aligned |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `docs/manual.html` | modify | old multilingual residue removal |
| `docs/veil-design.md` | modify | current sync / fallback behavior documentation |
| `index/project-file-taxonomy.md` | modify | `vocab.db` authority alignment |
| `index/project-template-adoption-packet.md` | modify | runtime-sensitive path alignment |
| `index/project-boundary-register.md` | modify | support shelf / helper data alignment if needed |
| `workspace/20260607_veil_consistency_recovery_*.md` | create | design evidence |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| C1 | `docs/manual.html` old multilingual cleanup | `rg` search no hit for old manual links / language pair |
| C2 | `index/` authority alignment | `rg` search no hit for `shared/vocab.db` in active governance docs |
| C3 | `docs/veil-design.md` spec alignment | matching text against `ui/js/convert.js` behavior |
| C4 | runtime safety | `python -m py_compile app.py veil-sync.py install-startup.py` |

## 6. Verification Plan

- planned checks:
  - `rg` over active surfaces for obsolete residue
  - diff review against runtime truth
- planned tests:
  - `python -m py_compile app.py veil-sync.py install-startup.py`
- evidence surface:
  - updated files
  - command outputs
  - workspace design docs

## 7. 作業順序

1. active docs / governance の obsolete / mismatch inventory を確定する
2. `docs/manual.html` の old multilingual residue を除去する
3. `index/` authority docs を repo 直下 `vocab.db` に合わせる
4. `docs/veil-design.md` を runtime truth に合わせる
5. 検証コマンドを実行し、残課題をまとめる

## 8. Idempotency and Side Effects

- Idempotency type: idempotent
- Writes:
  - repo files only
- External calls:
  - none
- Retry behavior:
  - safe to re-run searches and py_compile

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| obsolete residue を取り切れない | medium | repo-wide search with explicit keywords |
| docs が runtime から再びずれる | medium | runtime files を source of truth にする |
| governance 変更が広がる | low | `vocab.db` authority 直結 file に限定 |

