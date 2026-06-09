# Task Specification チェックリスト

**使う場面**: task specification が実装・検証できるほど明確か review する時に使う。  
**差し替える所**: task ID の形式、approval の扱い、project 固有の evidence 名。  
**書かないこと**: task specification 本文そのもの、今の状態の管理、project 固有の workflow 詳細。

## 1. Basic Information

- [ ] Task ID と title が明確である。
- [ ] owner または role が特定されている。
- [ ] dependencies が明示されている、または none と記載されている。
- [ ] preconditions と postconditions が具体的である。
- [ ] referenced documents または issues が存在する。

## 2. Scope

- [ ] in-scope work が具体的である。
- [ ] out-of-scope work が明示されている。
- [ ] affected files または components が分かる範囲で列挙されている。
- [ ] 未列挙 file の変更には approval または task update が必要である。

## 3. Implementation Guidance

- [ ] required interfaces、APIs、schemas、contracts が指定されている。
- [ ] constraints が測定可能である。
- [ ] external dependencies が特定されている。
- [ ] sequence が重要な場合、order of work が定義されている。

## 4. Acceptance Criteria

- [ ] 各 criterion に ID がある。
- [ ] 各 criterion が測定可能である。
- [ ] 各 criterion が test、command、review evidence のいずれかに対応している。
- [ ] security、performance、data integrity が関係する場合、criteria に含まれている。

## 5. Side Effects and Idempotency

- [ ] writes が列挙されている。
- [ ] external calls が列挙されている。
- [ ] re-run behavior が定義されている。
- [ ] 必要な場合、rollback または cleanup path が説明されている。

## 6. Final Decision

```text
Ready for implementation: yes / no
Blocking issues:
Reviewer:
Date:
```
