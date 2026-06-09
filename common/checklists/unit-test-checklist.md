# Unit Test チェックリスト

**使う場面**: code が unit-test level で testable、covered、isolated、maintainable か確認する時に使う。  
**差し替える所**: test framework 名、mock 方針、summary の decision 語。  
**書かないこと**: 実装 plan 本文、結合テスト観点、project 固有の current 管理。

refactoring 前、PR merge 前、generated code の受け入れ前に使う。

この checklist は
`../frameworks/project-progression-rule.md`
のうち、主に

- `着手前確認`
- `検証`
- `完了条件を根拠から固定する`
- `局所進捗を前進と数えない`

を unit test 面で具体化する。

この checklist 自体は test plan の正本や current verdict の置き場ではない。
判定結果は project 側の verification record、current、follow-up task へ戻して使う。

| Severity | 意味 |
|---|---|
| A | test を不可能または不安定にする構造問題 |
| B | quality または maintainability のリスク |
| C | 改善機会 |

## 1. Testability

| Severity | Check | Result |
|---|---|---|
| A | unit に mock できない hidden external dependency がある | [ ] |
| A | uncontrolled side effect により、同じ input で result が変わる | [ ] |
| A | global state が test 間で leak する | [ ] |
| A | unit が結合しすぎており、isolation で instantiate / call できない | [ ] |
| B | 重要 logic が private method や large function の背後に隠れている | [ ] |
| B | 1 function / class が複数 responsibility を持つ | [ ] |

## 2. Coverage Quality

| Severity | Check | Result |
|---|---|---|
| A | happy path だけが test されている | [ ] |
| A | error path が未 test | [ ] |
| A | boundary values が未 test | [ ] |
| B | assertion が弱く、behavior を証明できない | [ ] |
| B | regression risk が focused test で覆われていない | [ ] |
| C | scenario variety が少ない | [ ] |

## 3. Isolation

| Severity | Check | Result |
|---|---|---|
| A | test result が execution order に依存する | [ ] |
| A | test が意図せず real network または external service を呼ぶ | [ ] |
| A | randomness、time、locale、timezone が制御されていない | [ ] |
| A | setup / teardown が state を復元しない | [ ] |
| B | shared fixture が理解または reset しにくい | [ ] |
| B | temporary files または test DB rows が cleanup されない | [ ] |

## 4. Test Correctness

| Severity | Check | Result |
|---|---|---|
| A | async error または rejected promise が捕捉されない | [ ] |
| B | test が behavior ではなく implementation detail に依存している | [ ] |
| B | 1 test に無関係な assertion が多すぎる | [ ] |
| B | exception を type だけで確認し、useful detail を見ていない | [ ] |
| B | floating-point comparison が tolerance を無視している | [ ] |
| B | mock が behavior under test より複雑である | [ ] |

## 5. Maintainability

| Severity | Check | Result |
|---|---|---|
| B | test name が condition と expected behavior を説明していない | [ ] |
| B | failed test が failing behavior を示さない | [ ] |
| B | test value の理由が明確でない | [ ] |
| C | test structure が file 間で一貫していない | [ ] |
| C | comment が non-obvious setup を説明していない | [ ] |

## 6. Generated Code Checks

| Severity | Check | Result |
|---|---|---|
| A | generated code 追加後に existing tests を実行していない | [ ] |
| A | test が検出できない形で error が握りつぶされる | [ ] |
| B | generated code が既存 behavior を reuse せず duplicate している | [ ] |
| B | generated code が focused test なしで受け入れられた | [ ] |
| C | generated name が test readability を下げている | [ ] |

## Summary

```text
A checks: ___
B checks: ___
C checks: ___
Decision: block / fix soon / accept with note
Required follow-up: ___
Writeback target: verification record / current / follow-up task
```
