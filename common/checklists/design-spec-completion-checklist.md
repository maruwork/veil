# Design Spec Completion Checklist

**使う場面**: design spec が completion-level quality を満たすかを、review 時に素早く確認する時に使う。  
**関連**: `../policies/spec-review-and-skill-policy.md`
**差し替える所**: owner 名、完成判定の語、関連 policy 名。  
**書かないこと**: design spec 本文そのもの、今の状態の管理、project 固有の current 運用。

この checklist は
`../frameworks/project-progression-rule.md`
のうち、主に

- `完成の定義`
- `完了条件の明示化`
- `入口判定後に必要な設計粒度`

を design spec 完成判定の面で具体化する。

## 1. Problem / Scope

- [ ] 目的、解決したい問題、利用用途が本文だけで分かる
- [ ] 適用範囲が書かれている
- [ ] 非適用範囲が書かれている
- [ ] 対象外を何として扱うかが曖昧でない

## 2. Runtime / Trigger / IO

- [ ] どの場面で使うかが書かれている
- [ ] どのタイミングで起動 / 発火するかが書かれている
- [ ] 入力が書かれている
- [ ] 出力が書かれている
- [ ] 出力の置き場が書かれている

## 3. Branching / Owners

- [ ] 検知 / 判断 / 通知 / 記録 / 修正 / 自動修正 / 人間介入の分岐がある
- [ ] 自動実行部分と人間判断部分が分離されている
- [ ] trigger owner が書かれている
- [ ] execution owner が書かれている
- [ ] decision owner が書かれている
- [ ] storage owner が書かれている

## 4. Truth / Boundary

- [ ] current truth と history が分離されている
- [ ] artifact / evidence / cache の扱いが分離されている
- [ ] 既存機構との境界が書かれている
- [ ] 既存 truth / owner / workflow との非衝突条件が書かれている
- [ ] authority を持つ面と持たない面が明確

## 5. Contract / Phase

- [ ] 単独利用時の最小契約が書かれている
- [ ] 組込時の拡張契約が書かれている
- [ ] MVP が分離されている
- [ ] 段階実装が分離されている
- [ ] 将来拡張が分離されている
- [ ] 最終完成が分離されている

## 6. Operation / Verification

- [ ] 設置順が書かれている
- [ ] 初回起動順が書かれている
- [ ] 確認順が書かれている
- [ ] 日常運用時の参照順が書かれている
- [ ] テスト観点がある
- [ ] 回帰確認観点がある
- [ ] 非汚染確認観点がある
- [ ] 失敗時の挙動がある
- [ ] 再試行条件がある
- [ ] 保留条件がある
- [ ] 停止条件がある

## 7. Completion Judgment

- [ ] completion 条件が書かれている
- [ ] 未完成条件が書かれている
- [ ] 見かけ上の解決と根本解決が区別されている
- [ ] 採用理由がある
- [ ] 非採用案がある
- [ ] 手戻りリスクがある

## 8. Final Verdict

- [ ] この文書だけで、記憶を失った実装者や AI が全体像理解 → 設置 → 初回運用 → completion 判定まで進める
- [ ] 上を満たさない場合、この文書を completion-level design spec と呼ばない
