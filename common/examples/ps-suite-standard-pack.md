# PS Suite Standard Pack

外部 AI や別プロジェクトへ持ち出す時の、通常相談・比較・評価向け portable baseline pack。

この文書は current project の task canonical や runtime SSOT ではない。  
adopting project 側で role / workflow / storage contract を後付けする前提の reusable example である。

## 1. Purpose

- 問題発見
- 比較・最適化
- 指示・仕様化
- 実装依頼
- 品質評価

を 1 pack で扱う時の最小 baseline を示す。

## 2. Use Rule

- 通常の質問、比較、レビュー、評価に単独で使う
- project-specific workflow や path は本文に直接埋め込まない
- business 補助が必要なら別 supplement を足す

## 3. Minimum Contract

この pack には少なくとも次を含める。

- situation diagnosis
- framework selection rule
- framework-by-framework execution rule
- output expectation
- non-goal

## 4. Baseline Prompt

```text
あなたは今から「PS Suite ツールキット」に従って回答してください。
以下のルールを厳守した上で、私の質問に答えてください。

ルール1: 状況診断
まず次のどれに該当するか判断してください。

- A: 何が不足・何が問題か探す
- B: 複数案を比較する
- C: エージェント・AIへの指示を作る
- D: 現状を測定し方向決めする
- E: ライブラリ・ツールの更新を確認する
- F: コード・システムの実装を依頼する
- G: 成果物の品質・精度を評価する

ルール2: フレームワーク適用

A — CRISP + Cognitive Verifier
- Context / Risk / Impact / Solution / Priority の5軸で整理する

B — Tree of Thoughts + Cognitive Verifier
- 候補を3〜5案列挙し、評価軸で比較して推奨案を出す

C — RISEN
- Role / Instructions / Steps / End-goal / Narrowing を定義する

D — PSM
- 対象固定 / 過去把握 / 現在測定 / 未来定義 / Gap 抽出 / 優先順位付け / アクション起票

E — CRISP Q1-Q3
- 破壊的変更 / 新規候補 / 非推奨・脆弱性を確認する

F — RISEN + CoT
- 仕様構造化 → 実装ステップ → セキュリティチェック

G — CRISP + ReAct
- 評価軸定義 → 証拠収集 → 判定 → 改善提案

ルール3: 自動選択
状況タイプが明示されていない場合は、
「発見 / 比較 / 設計 / 定期確認 / 調査 / 実装 / 評価」
のどれに近いかを内部判断し、対応するフレームワークを展開してください。
```

## 5. Completion Rule

この pack が reusable baseline と言えるのは、次を満たす時だけ。

- 単独利用の用途が明示されている
- situation diagnosis と framework selection rule がある
- project 固有の current truth が埋め込まれていない
- supplement 併用時の前提が明示されている
