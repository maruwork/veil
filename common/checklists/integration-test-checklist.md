# 結合テストチェックリスト

**使う場面**: module boundary、state transition、external dependency、operational behavior が一体として機能するか確認する時に使う。  
**差し替える所**: target environment 名、external dependency 名、summary の decision 語。  
**書かないこと**: unit test の細部、実装 plan 本文、project 固有の current 管理。

release 前、cross-module change の merge 前、新しい integration point 追加時に使う。unit test は事前に通っている前提とする。

この checklist は
`../frameworks/project-progression-rule.md`
のうち、主に

- `checkpoint を 1 つずつ前進させる`
- `検証`
- `停止条件を明示する`
- `書き戻し`

を結合面で具体化する。

この checklist 自体は integration flow の current 正本ではない。
判定結果は project 側の verification record、runbook、follow-up task へ書き戻して使う。

| Severity | 意味 |
|---|---|
| A | data loss、security failure、outage、invalid state のリスク |
| B | reliability または maintainability のリスク |
| C | 改善機会 |

## 1. Interface and Data Transfer

| Severity | Check | Result |
|---|---|---|
| A | data shape、type、required fields が module 間で一致している | [ ] |
| A | null、empty、malformed value が boundary を越えても安全に扱われる | [ ] |
| A | error object format が caller expectation と一致している | [ ] |
| B | request / response contract が documented interface と一致している | [ ] |
| B | encoding、timezone、date format が一貫している | [ ] |

## 2. State Propagation

| Severity | Check | Result |
|---|---|---|
| A | cross-module transaction が正しく rollback または compensate される | [ ] |
| A | async operation が required completion より先に race しない | [ ] |
| B | ある step の state が次 step へ正しく引き継がれる | [ ] |
| B | event または queue ordering の assumption が検証されている | [ ] |

## 3. External Boundaries

| Severity | Check | Result |
|---|---|---|
| A | external outage または timeout に safe fallback または clear failure がある | [ ] |
| A | retry behavior に上限があり、write を重複させない | [ ] |
| B | DB、API、file、queue connectivity が target environment で機能する | [ ] |
| B | timeout setting が実際に exercised されている | [ ] |
| B | 遅い external response が正しく扱われる | [ ] |

## 4. Authorization and Security

| Severity | Check | Result |
|---|---|---|
| A | authentication token または credential が安全に propagate される | [ ] |
| A | authorization check が layer をまたいで機能する | [ ] |
| A | expired / revoked session が正しく扱われる | [ ] |
| B | logs と errors が secrets や personal data を露出しない | [ ] |

## 5. Data Integrity

| Severity | Check | Result |
|---|---|---|
| A | concurrent update が shared data を破壊しない | [ ] |
| A | delete / update effect が dependent module へ propagate される | [ ] |
| B | cache と persistent storage が silent drift しない | [ ] |
| B | derived record を regenerate または reconcile できる | [ ] |

## 6. Error Propagation

| Severity | Check | Result |
|---|---|---|
| A | downstream error が caller または alerting path へ届く | [ ] |
| A | broad catch block が error を握りつぶさない | [ ] |
| B | useful context が error boundary を越えて残る | [ ] |

## 7. Idempotency and Retry

| Severity | Check | Result |
|---|---|---|
| A | 同じ request の再実行で intended result が変わらない | [ ] |
| A | retry が duplicate side effect を作らない | [ ] |
| A | duplicate input が検出または安全に処理される | [ ] |

## 8. Configuration and Environment

| Severity | Check | Result |
|---|---|---|
| A | production、staging、test configuration が分離されている | [ ] |
| B | required environment variable が早期に validate される | [ ] |
| B | configuration change が関連 module すべてへ propagate される | [ ] |
| B | startup / shutdown order が検証されている | [ ] |

## 9. Performance and Observability

| Severity | Check | Result |
|---|---|---|
| A | concurrent usage が deadlock または resource exhaustion を起こさない | [ ] |
| B | cross-module call が明らかな N+1 または polling explosion を避けている | [ ] |
| B | response time が expected range 内である | [ ] |
| B | failure diagnosis に十分な context が log に含まれる | [ ] |
| C | start / end / duration が traceable である | [ ] |

## Summary

```text
A checks: ___
B checks: ___
C checks: ___
Decision: block / fix soon / accept with note
Required follow-up: ___
Writeback target: verification record / runbook / follow-up task
```
