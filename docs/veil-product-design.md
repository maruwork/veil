# VEIL Product Design

VEIL 本体の製品設計書。overview は [README.md](../README.md)、runtime / support の詳細は [veil-design.md](./veil-design.md) を参照。

---

## 1. Product

VEIL は `AI-assisted technical writing` 向け terminology guardrail である。

- goal:
  - AI が使う高影響語を事前ルールで安定化させる
- non-goal:
  - 自然文全体の全面統制
  - 汎用翻訳ツール
  - creative writing support
  - UI 中心の vocabulary app

---

## 2. Primary User

- AI を使って技術文書、運用文書、手順書、内部ドキュメントを書く個人または小規模チーム

---

## 3. Product Backbone

VEIL の本線は `capture -> normalize -> sync -> lint` で完結する。

- canonical:
  - `~/.veil/veil.db`
- AI-readable surface:
  - `~/.veil/rules/`
- publish route:
  - `shared/runtime/veil-sync.py`
- output gate:
  - `shared/runtime/veil-lint.py`

---

## 4. Responsibility Split

### 4.1 capture

`capture` は extraction gate である。

担当:
- 会話や対象テキストから candidate を拾う
- extract noise を初段で抑える
- review すべき候補だけを残す

非担当:
- final level 決定
- final canonical write の自動確定
- final hard gate 判定

### 4.2 normalize

`normalize` は review preparation layer である。

担当:
- variant 統合
- existing rule 照合
- 既存一致 / 新規候補 の 2 グループ出力

非担当:
- 会話からの直接抽出
- owner judgment の代行

### 4.3 sync

`sync` は publish layer である。

担当:
- canonical からミラーを regenerate
- ミラーを AI settings 面へ反映

### 4.4 lint

`lint` は output gate である。

担当:
- final answer の registered rule 検査
- 登録済みルールの違反を fail-close として返す

---

## 5. Candidate Rule

### 5.1 capture default

VEIL の current product decision として、`capture` は次を default にする。

1. 候補は意味が崩れない最短まとまりで拾う
2. 単語より複合語を優先する
3. 高影響語だけを強く拾い、それ以外は review 負荷を増やさない範囲で拾う
4. 状態語 / 判断語 / 構造語 / 運用ラベルを優先する
5. single-word 一般語や一般動詞は、原則として強い採用候補へ上げない
6. 用途が広い phrase も、回数だけで強い採用候補へ上げない
7. 低頻度語、曖昧語、文脈依存語はスキップする
8. candidate を拾っても、自動採用しない

### 5.2 normalize default

VEIL の current product decision として、`normalize` は次を default にする。

1. 既存一致があれば preferred と source_file を `既存一致:` グループで返す
2. 既存一致がなければ target_file を `新規候補:` グループで返す
3. final adoption は owner judgment に残す

### 5.3 owner override

owner は次を override できる。

- 高影響語を採用する
- 一般語を project 固有語として採用する
- phrase を高影響語として採用する

---

## 6. Storage

1. owner が採用を決める
2. SQLite canonical に書く
3. markdown ミラーを regenerate する
4. sync で AI 面へ反映する

---

## 7. Adoption Principle

VEIL の原則は `全部を自動採用しない` である。

- candidate を拾うこと
- canonical に採用すること
- final answer を止めること

は別段階として扱う。

---

## 8. Representative Flow

1. task close / 会話区切り
2. `capture`
3. `normalize`
4. owner review
5. canonical write
6. ミラー再生成
7. `sync`
8. final answer draft
9. `lint`
10. fix if required
11. final answer

---

## 9. Verification

VEIL completed claim には、少なくとも次が必要である。

1. candidate rule が authority surface に固定されている
2. representative `capture -> normalize -> sync -> lint` flow の strong evidence がある
3. canonical / ミラー / sync / lint / normalize の route が docs と runtime で矛盾しない
4. current blocker が none である

---

## 10. Remaining Owner Decisions

この product design は current product decision を持つが、最終 owner confirmation が必要なのは次である。

- 高影響語の範囲
- single-word 一般語の project-specific 例外範囲
- phrase を高影響扱いにする条件
- `capture` でどこまで絞り、`normalize` でどこまでスキップに回すか

---

## 12. Public Release Research （2026-06-07 調査）

### 結論

- Go: AI で product / technical documentation を作る B2B チーム向け用語統制に絞るなら公開価値あり
- No-Go: AI ガバナンス全般、一般向け AI 用語管理ツールとして出すなら弱い
- 最初の狙い目: 複数人執筆・AI 利用が日常・用語統制が重要・間違えると compliance / trust に響く B2B 組織

### 差別化仮説

既存代替（Acrolinx / Writer / Grammarly Business / Vale）の多くは「ルールを置く」または「書く時に助言する」。VEIL は `会話から拾う -> 正規化する -> AI に読ませる -> 出力前に違反検査する` を閉じられる点が差別化候補である。

### ポジショニング文

`VEIL is a terminology guardrail for AI-assisted technical writing. It captures unstable terms from real work, turns them into approved language rules, and checks AI output before it ships.`

### ターゲット優先順位

1. Product / Technical Documentation チーム（最優先）
2. 規制業界の説明文書チーム（医療・金融・製造・法務）
3. 多言語展開前の source content を整えたい localization-heavy team

### 注意

- 統制を強めすぎると過剰統制と嫌がられる
- term owner がいない組織へ入ると機能しない
- Acrolinx / Writer との正面衝突は避ける

---

## 11. Product Boundary

VEIL は「全部を縛る」道具ではない。

- 強く縛る:
  - flow
  - high-impact terminology
  - final answer violations
- 弱く扱う:
  - 低頻度語
  - 文脈依存語
  - 曖昧語
  - 自然な言い換え

この boundary を超えて全自然文統制へ拡張しない。
