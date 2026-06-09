# Requirements テンプレート

**使う場面**: project や機能の要求を整理する時に使う。  
**差し替える所**: project 名、stakeholder、要求 ID の付け方、成功条件、参照資料。  
**書かないこと**: 実装方法の細部、今の状態の管理、project 固有の運用手順。

**Project**:
**Author**:
**Date**:
**Approver**:

## 1. Overview

### 目的

この project が達成すべきことを書く。
完成状態、完了報告の主語、今回この要求で閉じる範囲がぶれないように書く。

### 背景

なぜ今必要なのかを書く。
今回の scope と直接関係しない運用事情や将来構想を混ぜすぎない。

### 参考事例 / 参照資料

- 類似事例:
- 参照仕様:
- 関連 ADR / decision:

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
|  |  |  |

完了報告の主語が複数 project / 複数 capability にまたがる場合は、そのまま進めず goal または checkpoint の分割を検討する。

## 2. Scope

### In Scope

- TBD

複数 capability が混ざる場合は、1 要求のまま進めずに goal または checkpoint の分割を検討する。

### Out of Scope

- TBD

### Assumptions and Constraints

- TBD

### Success Criteria

- 何を満たせば「完了」とみなすか:
- どの状態まで検証できれば次工程へ進めるか:
- requirement を basic design に渡してよい条件になっているか:

completion gate として、上の 3 点が hidden で残る場合は basic design へ進めない。

### Primary User Workflow

1. 利用者:
2. 開始条件:
3. 主な操作:
4. 期待結果:

開始条件または期待結果が言えない場合は、workflow を補強するまで次工程へ進めない。

## 3. Functional Requirements

### Requirement Structuring Notes

- 主語、トリガー、期待結果が分かる形で書く
- 必須条件と任意条件を混ぜない
- 実装方法ではなく、満たすべき振る舞いを先に書く
- 1 requirement に複数 capability や複数状態が混ざる時は分割を検討する
- acceptance で確認できない requirement はそのまま流さない

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 |  |  | must / should / could |

### Edge Cases and Failure Conditions

task 設計へ渡す stop / failure 面を書く。

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 |  |  |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Performance |  |  |
| NFR-2 | Security |  |  |
| NFR-3 | Reliability |  |  |

複数 subsystem や複数 actor の独立 lane がある場合は、ここで抱え込まず split gate として分割を検討する。

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
|  | low / medium / high | low / medium / high |  |

approval boundary、外部書き込み、owner 未定 unresolved が見えている場合は stop gate として明示し、hidden のまま basic design へ渡さない。

## 6. Requirement Quality Check

- [ ] 完了報告の主語が固定されている
- [ ] In Scope / Out of Scope が衝突していない
- [ ] Success Criteria が次工程へ進める条件として書かれている
- [ ] Primary User Workflow の開始条件と期待結果が明示されている
- [ ] Acceptance Criteria が requirement ごとに確認可能
- [ ] 非機能要件に target が入っている
- [ ] major edge case が拾えている
- [ ] 前提・制約・完了条件が明示されている
- [ ] unresolved な論点が hidden で残っていない

## 7. Glossary

| Term | Definition |
|---|---|
|  |  |
