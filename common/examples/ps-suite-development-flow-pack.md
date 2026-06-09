# PS Suite Development Flow Pack

要件定義から品質ゲートまでを一気通貫で進める時の portable baseline pack。

この文書は current project 固有の task board や approval rule を含まない。  
adopting project は、この baseline に local workflow / owner / storage contract を後付けする。

## 1. Purpose

- 要件定義
- 基本設計
- 詳細設計
- タスク分解
- 追跡可能性
- 品質ゲート設計

を順序立てて進める。

## 2. Use Rule

- 設計から実装準備までを一気通貫で進めたい時に単独利用する
- 単なる比較・レビュー用途なら standard pack を優先する
- business 視点が必要なら supplement を追加する

## 3. Minimum Contract

この pack には少なくとも次を含める。

- phase order
- phase-by-phase framework
- output artifact per phase
- requirement-to-test traceability
- completion / non-completion distinction

## 4. Baseline Prompt

```text
あなたは今から「PS Suite 開発フロー」に従って回答してください。
以下のフェーズを順番に実行し、各フェーズで出力確認後に次へ進んでください。

フェーズ1: 要件定義（RISEN + CRISP A + EARS）
- Role / Instructions / Steps / End-goal / Narrowing を構造化
- Context / Risk / Impact / Solution / Priority で漏れを検出
- 要求文は EARS で標準化
- 異常系、状態依存、条件付き要求も分離

フェーズ2: 基本設計（Tree of Thoughts）
- 候補A/B/... を列挙
- 保守性 / パフォーマンス / 統合コスト / テスト容易性で比較
- 推奨案と却下理由を残す

フェーズ3: 詳細設計（RISEN + CoT）
- 各コンポーネントの責務、入出力、内部処理、非責務を定義
- 実装順を CoT で分解する

フェーズ4: タスク分解（CoT + PSX）
- task / dependency / complexity / owner 分解

フェーズ4.5: 追跡可能性検証（RTM）
- 要求 ↔ 実装 ↔ テストの対応表を作る

フェーズ5: 品質ゲート設計（PSE + CRISP G + BDD）
- BDD/Gherkin で受入条件をテスト可能にする
- completion 条件と監査チェックを定義する
```

## 5. Completion Rule

この pack が reusable baseline と言えるのは、次を満たす時だけ。

- phase order が明示されている
- 各 phase の出力 artifact が定義されている
- traceability と quality gate が含まれている
- project-specific task id / path / owner 名が埋め込まれていない
