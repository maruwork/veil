# 評価判定テンプレート

PASS / FAIL / PARTIAL などの verdict を evidence 付きで残す reusable template。

**使う場面**: 監査や評価の最後に、判定と根拠を残す時に使う。  
**差し替える所**: verdict の種類、判定者名、reroute 先、next action の書き方。  
**書かないこと**: 実装手順本文、要求定義本文、project 固有の current 運用。

## 1. Required Fields

- source of completion conditions
- required metrics
- optional metrics
- threshold
- measurement method
- task_id
- evaluation target
- auditor
- audit_scope
- criteria summary
- evidence_checked
- actuals
- verdict
- reason
- blocking findings
- reroute target
- next_action
- next handoff (optional)

## 2. Completion Rule

- 閾値が実測前に確定している
- required / optional が分離されている
- measurement method がある
- verdict と根拠がある
- next action か handoff がある
