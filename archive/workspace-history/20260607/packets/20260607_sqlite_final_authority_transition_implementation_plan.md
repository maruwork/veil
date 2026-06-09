# 実装計画テンプレート準拠

**Task**: VEIL-CANONICAL-003-FINAL-AUTHORITY  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-CANONICAL-003-FINAL-AUTHORITY` |
| goal | current authority docs を SQLite transition phase に合わせて更新する |
| owner_role | owner / delegated AI |
| scope_in | README, docs, AGENTS, index wording |
| scope_out | capture/sync code rewrite |
| next_gate | capture/sync final migration packet |

## 2. Implementation Decision Record

- background:
  - Stage 2 で read path switch は実装面として閉じた
- decision:
  - docs/governance を transitional authority wording へ更新する
- rationale:
  - current implementation を正直に示すため
- rejected alternatives:
  - full migration complete と書く
  - Markdown canonical を維持したまま書く
- completion conditions:
  - root authority 面から `rules-dir only canonical` wording が消える

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| scope が承認済み | PASS | current next action と一致 |
| dependency が利用可能 | PASS | Stage 2 reports exist |
| 関連 docs が current | PASS | current work updated |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_sqlite_final_authority_transition_*.md` | create | transition packet |
| `README.md` | modify | top authority wording update |
| `docs/veil-design.md` | modify | canonical/mirror wording update |
| `AGENTS.md` | modify | current authority wording update |
| `index/project-file-taxonomy.md` | modify | taxonomy wording update |
| `index/project-boundary-register.md` | modify | boundary wording update |
| `index/project-template-adoption-packet.md` | modify | canonical/support wording update |
| `index/project-current-work.md` | modify | next action writeback |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| C1 | README authority wording | readback |
| C2 | docs/veil-design canonical section | readback |
| C3 | AGENTS/index current authority | readback |
| C4 | current work next action | readback |

## 6. Verification Plan

- planned checks:
  - wording grep
  - packet readback
- evidence surface:
  - updated docs/governance files

## 7. 作業順序

1. packet を作る
2. README / design を更新する
3. AGENTS / index を更新する
4. current work を writeback する

## 8. Idempotency and Side Effects

- Idempotency type:
  - idempotent
- Writes:
  - docs/governance files only

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| docs wording が不十分 | medium | grep/readback で確認する |
