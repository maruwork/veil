# 実装監査チェックリスト

**使う場面**: 実装後に、設計整合、完了条件、副作用を確認する時に使う。  
**差し替える所**: verdict 名、test-data contract の扱い、関連 design record 名。  
**書かないこと**: 実装 plan 本文、今の状態の正本、project 固有の current board。

この checklist は
`../frameworks/project-progression-rule.md`
のうち、主に

- `検証`
- `前進の定義`
- `完了条件の確認`

を実装後の確認面で具体化する。

設計整合、完了条件、副作用、必要時の test-data 整合まで確認する reusable checklist。

## 1. Checklist

- [ ] design record exists
- [ ] approval record exists
- [ ] completion conditions are explicit
- [ ] implemented items match design
- [ ] non-target areas remain unchanged
- [ ] completion conditions are checked one by one
- [ ] no unexpected side effects or regressions
- [ ] test-data contract is checked when applicable

## 2. Verdict

- PASS
- REQUIRES_REVISION
- RE_DESIGN

## 3. Completion Rule

- result can be recorded with reason
- revision or redesign path can be stated clearly
