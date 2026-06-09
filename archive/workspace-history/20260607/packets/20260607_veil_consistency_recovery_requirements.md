# VEIL Consistency Recovery Requirements

Project: VEIL current consistency recovery
Author: Codex
Date: 2026-06-07
Approver: f_tan

## 1. Overview

### 目的

VEIL の active surface に残っている旧多言語仕様の残骸と、現行運用と食い違う説明を除去し、現行仕様の正本を一貫した形で読める状態にする。

完成状態は次。

- active docs / governance / runtime explanation が単一仕様として読める
- 旧多言語仕様の残骸が active surface に残っていない
- `~/.veil/rules/` を正本、`vocab.db` を補助データとする説明が揃っている
- `veil-sync.py` の rules-only / behavior-aware 運用が文書と一致している

### 背景

VEIL は `~/.veil/rules/` 正本化と `veil-sync.py` の独立化へ寄っているが、`docs/manual.html` を中心に旧多言語仕様の残骸が残っている。また、`vocab.db` の置き場や変換仕様の説明にも、文書間のずれがある。

### 参考事例 / 参照資料

- 類似事例:
  - なし
- 参照仕様:
  - `common/frameworks/goal-path-checkpoint-task-design-framework.md`
  - `common/policies/execution-readiness-gate-policy.md`
- 関連 ADR / decision:
  - `workspace/veil_recent_fix_reconstruction_20260607.md`
  - `workspace/veil_current_assessment_and_session_fix_plan_20260607.md`

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
| VEIL owner | final decision maker | 現行仕様を迷わず判断できる |
| VEIL user | reader / operator | 古い説明に引っ張られない |
| future AI agent | maintainer | 正本と補助の境界を誤読しない |

## 2. Scope

### In Scope

- active surface に残る旧多言語仕様の残骸除去
- `vocab.db` authority 記述の現行実装への整合
- `veil-sync.py` の現行運用に合わせた文書整合
- `p1` / `p2` / `p3` の実変換仕様に関する説明整合
- 必要な範囲の governance doc 更新

### Out of Scope

- `veil-capture` 抽出ロジック自体の仕様変更
- UI デザイン刷新
- `vocab.db` から `~/.veil/rules/` への再構成機能追加
- DB スキーマ再設計
- 新しい多言語対応の再導入

### Assumptions and Constraints

- `common/` は reusable rule shelf であり scratch には使わない
- `workspace/` に設計と中間成果を置き、review 後に canonical へ反映する
- runtime code の大規模な挙動変更は避け、まず説明と authority を揃える

### Success Criteria

- active surface から旧多言語仕様の残骸が消えている
- `index/` と `app.py` の `vocab.db` 説明が一致している
- `docs/veil-design.md` と `ui/js/convert.js` の仕様差が文書上で解消されている
- 変更後の Python runtime files が `py_compile` を通る

### Primary User Workflow

1. 利用者:
   - VEIL owner / future maintainer
2. 開始条件:
   - VEIL の current docs と governance docs を読む
3. 主な操作:
   - 正本・補助・同期責務を判断する
   - manual / design / governance を参照する
4. 期待結果:
   - 古い多言語仕様や obsolete 説明なしに current VEIL を理解できる

## 3. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 | active docs から旧多言語仕様の残骸を除去する | `docs/manual.html` に旧多言語リンクや旧「言語ペア」表現が残らない | must |
| FR-2 | governance docs の `vocab.db` authority を現行実装へ合わせる | `index/` で `shared/vocab.db` 前提が消え、repo 直下 `vocab.db` の補助データ扱いで読める | must |
| FR-3 | `veil-sync.py` の現行運用を docs に反映する | docs が rules-only + behavior-aware sync と一致する | must |
| FR-4 | 変換仕様の説明を現行実装へ合わせる | `p1` 空時の fallback 仕様が設計書で説明されるか、実装が厳格化される | must |
| FR-5 | 変更内容を future AI が再利用できるよう中間設計を `workspace/` に残す | requirements / basic design / implementation plan が存在する | must |

### Edge Cases and Failure Conditions

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 | obsolete 表現が changelog や migration code に残る | active surface と historical / compatibility code を分けて扱う |
| EC-2 | runtime code を変更せず docs だけで整合できる | 挙動変更より docs 整合を優先する |
| EC-3 | old DB migration code が旧 `lang_pair` を参照する | compatibility logic として維持し、仕様残骸とは分けて扱う |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Reliability | runtime behavior を不要に壊さない | docs / governance 中心、最小変更 |
| NFR-2 | Maintainability | future AI が authority を一読で判断できる | root / docs / index 間の整合 |
| NFR-3 | Auditability | 今回の設計判断が `workspace/` に残る | 3 種の設計文書を保存 |

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| docs を直しても code と再ずれする | medium | medium | 実装参照を根拠に文書更新する |
| governance 更新範囲が広がる | medium | medium | `vocab.db` authority に直結する file へ限定する |
| obsolete 判定を広げすぎる | low | high | historical / migration / compatibility code は対象外と明記する |

## 6. Requirement Quality Check

- [x] 完了報告の主語が固定されている
- [x] In Scope / Out of Scope が衝突していない
- [x] Success Criteria が次工程へ進める条件として書かれている
- [x] Primary User Workflow の開始条件と期待結果が明示されている
- [x] Acceptance Criteria が requirement ごとに確認可能
- [x] 非機能要件に target が入っている
- [x] major edge case が拾えている
- [x] 前提・制約・完了条件が明示されている
- [x] unresolved な論点が hidden で残っていない

## 7. Glossary

| Term | Definition |
|---|---|
| active surface | current user / maintainer が現行仕様として読む面 |
| historical | changelog や migration logic のような履歴・互換面 |
| authority | どの file / shelf を正本として扱うかの定義 |

