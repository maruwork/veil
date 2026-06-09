# 実装計画テンプレート準拠

**Task**: VEIL-CANONICAL-003-STAGE1  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-CANONICAL-003-STAGE1` |
| goal | SQLite Stage 1 の support code と smoke evidence を追加する |
| owner_role | owner / delegated AI |
| scope_in | schema, import, readback, workspace smoke |
| scope_out | lint/normalize read path 切替, generated Markdown route |
| next_gate | Stage 2 read path switch packet |

## 2. Implementation Decision Record

- background:
  - SQLite canonical migration packet は固定済み
- decision:
  - shared module `veil_rule_store.py` と CLI `veil-db.py` を追加する
- rationale:
  - current runtime を壊さず、schema/import/readback を先に導入するため
- rejected alternatives:
  - 既存 script へ直接 SQLite read path を入れる
- impact scope:
  - new support module / CLI
  - workspace smoke fixtures and evidence
- completion conditions:
  - py_compile と smoke readback が通る
- SSOT declaration when data contracts are involved:
  - Stage 1 schema は `veil_rule_store.py` の schema 定義

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| scope が承認済み | PASS | Stage 1 は packet 上で fixed |
| dependency が利用可能 | PASS | Python stdlib `sqlite3` を使う |
| 関連 docs が current | PASS | Stage 1 packet 作成済み |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `veil_rule_store.py` | create | schema/import/readback shared logic |
| `veil-db.py` | create | Stage 1 CLI entry |
| `workspace/veil_stage1_rules_fixture/` | create | import smoke 用 rules fixture |
| `workspace/veil_stage1_smoke_check.py` | create | smoke readback helper |
| `README.md` | modify | support route を最小追記 |
| `docs/veil-design.md` | modify | Stage 1 support route を最小追記 |
| `index/project-current-work.md` | modify | Stage 1 実装完了の current writeback |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| C1 | schema 初期化 | `veil-db.py init-db` が DB 作成 |
| C2 | Markdown import | `veil-db.py import-rules` が rows 取り込み |
| C3 | readback | `veil-db.py readback` が counts / rows を返す |
| C4 | current runtime non-breaking | `python -m py_compile` が既存 script と新規 script で通る |

## 6. Verification Plan

- planned checks:
  - `python -m py_compile veil_rule_store.py veil-db.py veil-lint.py veil-normalize.py veil-profile-audit.py`
  - workspace fixture import smoke
- planned tests:
  - init-db
  - import-rules
  - readback
- evidence surface:
  - workspace smoke DB
  - workspace smoke script output

## 7. 作業順序

1. shared module の schema と parser を実装する
2. CLI entry を実装する
3. workspace fixture を置く
4. smoke script で init/import/readback を確認する
5. docs / current work に Stage 1 完了だけを書き戻す

## 8. Idempotency and Side Effects

- Idempotency type:
  - first-run side effect
- Writes:
  - repo files
  - workspace smoke DB
- External calls:
  - なし
- Retry behavior:
  - smoke DB を作り直して再実行可能

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| parser と current runtime parser の差 | high | shared parsing helper にまとめる |
| docs を先に canonical update しすぎる | medium | Stage 1 support route の追記に留める |
| smoke が home dir path 依存になる | medium | workspace path を primary にする |
