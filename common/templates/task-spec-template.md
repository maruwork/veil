# Task Specification テンプレート

**使う場面**: 1 つの task で何を作るか、何を変えるか、何を検証するかを固定する時に使う。  
**差し替える所**: task ID 形式、対象 component 名、verification の書き方、side effect の扱い。  
**書かないこと**: project 全体の要求定義、今の状態の正本、最終 verdict 本文。

**Task ID**:
**Task Name**:
**Type**: mock / production / research / maintenance / poc
**Owner**:
**Dependencies**:
**Preconditions**:
**Postconditions**:
**References**:

## 1. Scope

実装する内容を書く。
1 task = 1 clear outcome を原則にする。複数 outcome を持つ場合は task 分割を検討する。
requirements / basic design と別の主語や別の outcome になった時は split gate として分割を検討する。

**Out of scope**:

- TBD

## 2. Target Files or Components

create / modify / delete と role が task outcome に対して過不足ないことを確認する。

| Path / Component | Operation | Role |
|---|---|---|
|  | create / modify / delete |  |

## 3. Implementation Requirements

### Requirement 1

behavior、constraints、interface expectation を書く。
実装手順だけでなく acceptance へつながる振る舞いを書く。
behavior ではなく手順だけが残る場合は completion とせず停止する。

### DB Test Data Requirements

DB を使う場合は、NOT NULL / CHECK / foreign key / seed prerequisites を書く。

## 4. Interface Contract

| Kind | Name | Definition | Notes |
|---|---|---|---|
| Function / API / DB / File |  |  |  |

interface が指定されていない場合は、`No interface specified; implementation may choose the internal shape.` と書く。
contract 未定のまま実装開始しない。

## 5. Acceptance Criteria

第三者が pass / fail を判定できる観測条件を書く。

| ID | Criterion | Verification |
|---|---|---|
| C1 |  |  |

acceptance が upstream requirement を見失う、または第三者が開始できない場合は completion としない。

## 6. Idempotency and Side Effects

- Idempotency type:
- File writes:
- DB writes:
- External calls:
- Re-run behavior:

approval が必要な write や re-run 時の扱いを hidden にしない。

## 7. Implementation Order

依存関係が分かる順で書く。

1. TBD
2. TBD
3. TBD

requirements / basic design の path と別順になる場合は、その理由を明示するか task 分割を検討する。

## 8. Downstream Impact and Review Notes

- Downstream impact:
- Material change review needed:
- Human decision gate:

human decision gate は hidden にせず、必要なら停止条件としてここで明示する。
approval boundary、external write、policy change がある場合は stop gate として扱い、execution readiness へ隠したまま渡さない。
