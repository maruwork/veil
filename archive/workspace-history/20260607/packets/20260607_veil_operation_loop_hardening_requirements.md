# VEIL Operation Loop Hardening Requirements

## 1. Overview

### 目的

VEIL の語彙記録が実際の AI 出力へ反映されにくい、skill が日次運用フローへ食い込んでいない、抽出語の揺れが大きい、という 3 問題に対して、自然に回る運用ループを定義する。

この wave では特に「記録済み語彙を AI が使わない」問題を最優先で閉じる。

### 背景

- `~/.veil/rules/` は語彙ルールの正本として成立している
- `veil-sync.py` により各 AI 設定ファイルへ同期できる
- ただし、同期された語彙が実際の返答文で使われたかを検査する fail-close がない
- `veil-capture` は存在するが、どの phase で半自動または自動で使うかの operator path が弱い

### 参考 / 根拠

- `README.md`
- `docs/veil-design.md`
- `common/policies/spec-review-and-skill-policy.md`
- `common/policies/agent-workflow-policy.md`
- `common/policies/verification-and-retry-policy.md`

## 2. Scope

### In Scope

- `~/.veil/rules/*.md` を authority とするローカル lint スクリプトを追加する
- lint の trigger / fail-close / verification を canonical docs に明示する
- VEIL の運用フローを `capture -> sync -> lint -> report` の形で定義する
- `veil-capture` は抽出・正規化・記録・同期、`veil-lint` は返答前検査という責務分担を明文化する

### Out of Scope

- 外部 AI ツールへの自動 hook 注入
- 高度な形態素解析や意味ベースの同義語統合
- `app.py` / `vocab.db` の再設計
- 既存 rule format の全面変更

### Assumptions and Constraints

- 正本 authority は引き続き `~/.veil/rules/`
- lint は repo 内 script として実装するが、読む authority は repo 外正本である
- この wave では「抽出語の揺れ」へ直接コードで対処せず、次 wave の normalize/merge workstream として設計に残す

## 3. Success Criteria

- `python veil-lint.py <file>` または `python veil-lint.py --stdin` で返答文を検査できる
- 登録済み原語が prose に残っている場合、推奨語付きで検出される
- 検出なしなら clean を返し、検出ありなら non-zero exit で fail-close できる
- `README.md` / `docs/veil-design.md` / `AGENTS.md` から lint の phase / trigger / verification が辿れる

## 4. Functional Requirements

1. lint は `~/.veil/rules/*.md` を読み、`- original → preferred` 形式の rule を解釈できること
2. lint は code fence と inline code を保護し、そこでは一致判定しないこと
3. lint は original の一致箇所を line number つきで返し、preferred を提示すること
4. lint は rule 未配置時に異常終了せず、skip 理由を説明できること
5. lint は capture report 自体を authority にせず、通常の user-facing prose を対象にすること

## 5. Non-Functional Requirements

- 標準ライブラリのみ
- 破壊的変更なし
- UTF-8 で安定して読めること
- 数分で verify できる lightweight tool であること

## 6. Risks

- rule format の揺れが大きい場合、lint parser が一部行を拾えない
- prose 中に意図的な原語説明がある場合、lint が違反として出す
- code span 保護だけでは path / identifier の prose 記述を完全には除外できない

## 7. Deferred Follow-up

- 抽出語の normalize/merge 支援
- 既存 rule との近似照合
- `veil-capture` の半自動 trigger 改善
