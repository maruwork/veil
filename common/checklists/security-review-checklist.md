# Security Review Checklist

**使う場面**: security-sensitive な変更を review する時に使う。  
**差し替える所**: asset 名、boundary、control 名、follow-up task の扱い。  
**書かないこと**: threat model 本文そのもの、今の状態の正本、project 固有の current 運用。

security-sensitive な設計、runtime、DB 経路、外部連携、権限変更を review するときの portable checklist。

この checklist は
`../frameworks/project-progression-rule.md`
のうち、主に

- `着手前確認`
- `検証`
- `局所進捗を前進と数えない`
- `停止条件を明示する`

を security 面で具体化する。

この checklist 自体は current 正本や security 進行記録の置き場ではない。
判定結果は project 側の current / review artifact / follow-up task へ書き戻して使う。

## 0. Scope

- [ ] 対象変更を 1 文で言える
- [ ] in scope / out of scope が分かれている
- [ ] `基盤作成` / `日次運用` / `非本線` の分類が明示されている

## 1. Asset

- [ ] 守るべき data asset が列挙されている
- [ ] 守るべき control asset が列挙されている
- [ ] audit / evidence asset が列挙されている

## 2. Boundary

- [ ] trust boundary が書かれている
- [ ] actor / system / external service が分かれている
- [ ] allowed action と denied action が分かれている

## 3. Attack / Misuse

- [ ] abuse case が少なくとも 1 件ある
- [ ] accidental misuse case が少なくとも 1 件ある
- [ ] wrong-target / stale-context / privilege drift のどれが relevant か確認した

## 4. Control

- [ ] preventive control がある
- [ ] detective control がある
- [ ] corrective / recovery path がある
- [ ] fail-open ではなく fail-soft / fail-close 方針が説明されている

## 5. Evidence

- [ ] read-only verification がある
- [ ] dry-run / simulation の有無が明示されている
- [ ] security claim を single tool output だけで正当化していない

## 6. Residual Risk

- [ ] 未解決リスクが書かれている
- [ ] 人間判断が必要な点が分かれている
- [ ] follow-up task が必要なら明記されている

## Summary

```text
Decision: block / fix soon / accept with note
Primary risk: ___
Required follow-up: ___
Writeback target: current / review artifact / follow-up task
```
