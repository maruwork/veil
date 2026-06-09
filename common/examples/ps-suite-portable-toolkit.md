# PS Suite Portable Toolkit Example

PS Suite を外部 AI や別プロジェクトへ持ち出す時の、portable pack の最小構成例。

この文書は current runtime や current task の正本ではなく、
`どのように portable prompt/toolkit pack を分けるか`
を示す reusable example である。

## 1. Recommended Split

portable toolkit は、少なくとも次の 3 pack に分ける。

| Pack | Purpose | Typical use |
|---|---|---|
| `standard` | 通常の質問、比較、評価 | 汎用相談、レビュー、比較 |
| `dev-flow` | 要件定義から品質ゲートまでの開発支援 | 設計、実装、テスト、受入条件整理 |
| `business-view supplement` | 事業価値、ROI、意思決定補助 | 技術回答へビジネス視点を追加 |

## 2. Why Split It

- 1ファイル巨大 prompt にすると再利用先で重い
- 利用場面ごとに pack を選べる
- business 補助は必要時だけ足せる
- adopting project 側で role / workflow / governance を混ぜ込まずに済む

## 3. Minimum Contract

各 pack には少なくとも次を明示する。

| Field | Meaning |
|---|---|
| `purpose` | 何の場面で使うか |
| `input expectation` | どんな依頼や文脈を想定するか |
| `output expectation` | 何を返すべきか |
| `non-goal` | 何をしないか |
| `combination rule` | 他 pack と併用するならどう足すか |

## 4. Adoption Rule

- `standard` は単独利用できるようにする
- `dev-flow` は設計・実装・品質ゲートの順序を含める
- `business-view supplement` は単独で使わず、`standard` または `dev-flow` に加える
- project-specific workflow や path は pack 本文に直接埋め込まない

## 5. Completion Rule

portable toolkit pack が整ったと言えるのは、次を満たした時だけ。

- 3 pack それぞれの用途が分離されている
- 単独利用と併用ルールが明示されている
- project 固有の current truth が埋め込まれていない
- adopting project が自分の workflow を後付けできる
