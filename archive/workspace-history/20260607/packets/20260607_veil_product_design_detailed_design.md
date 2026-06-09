# Detailed Design

## 1. Users

### Primary User

- AI-assisted technical writing を日常運用する個人または小規模チーム

### Secondary User

- 同じ canonical を使う別 AI tool / 別 profile operator

## 2. Product Goal

- 会話の中で出た高影響語を無理なく capture し
- candidate を review-first に整え
- canonical へ登録し
- sync で AI に読ませ
- lint で最終出力を止める

## 3. Non-Goals

- 全自然文の全面統制
- 汎用翻訳ツール化
- creative writing support
- UI を中心にした vocabulary app

## 4. Responsibility Split

### 4.1 capture

`capture` は extraction gate である。

- やること:
  - 会話や対象テキストから candidate を拾う
  - extract noise を初段で落とす
  - 採用候補 / 保留候補の review queue を作る
- やらないこと:
  - final level 決定
  - hard gate 判定
  - canonical write の自動確定

### 4.2 normalize

`normalize` は review preparation layer である。

- やること:
  - variant 統合
  - existing rule 照合
  - selection / retention / shortlist / level suggestion
  - review-first text / JSON 出力
- やらないこと:
  - 会話全体からの直接抽出
  - final owner decision の代行

### 4.3 sync

`sync` は publish layer である。

- canonical から mirror を更新する
- mirror から AI settings 面へ反映する

### 4.4 lint

`lint` は output gate である。

- registered rule に対する final answer 検査
- `必須` fail-close
- `推奨` warning
- `観察` skip

## 5. Candidate Rule

### 5.1 capture default rule

`capture` は次を current default とする。

1. 候補は意味が崩れない最短まとまりで拾う
2. 単語より複合語を優先する
3. `2回出現` を必要条件にする
4. ただし owner override がある高影響語は 1 回でも採用可能
5. single-word 一般語は原則候補へ送らない
6. single-word 一般動詞は候補へ送らない
7. lowercase phrase は 1 回では送らない
8. lowercase phrase が 2 回でも、用途が広いままなら強く採用候補へ上げない
9. 状態語 / 判断語 / 構造語 / 運用ラベルを優先する

### 5.2 normalize default rule

`normalize` は capture を通った candidate に対して次を current default とする。

1. 既存一致があれば統合候補を返す
2. `先に採る候補 / 保留寄り / 外す寄り` を返す
3. `保留寄り` には `今は見送る / 後で再観察する / 文脈不足で保留` を返す
4. low-priority candidate は compact に落とす
5. final adoption は owner judgment に残す

### 5.3 owner override points

owner は次を override できる。

- 1 回出現の高影響語を採用する
- single-word 一般語を project 固有語として採用する
- 2 回 phrase を高影響語として採用する
- suggested level を上下する

## 6. Storage and Publication

1. candidate 採用後は SQLite canonical に書く
2. mirror を regenerate する
3. sync で AI settings 面へ publish する

## 7. Representative End-to-End Flow

1. task close / 会話区切り
2. `capture`
3. `normalize`
4. owner review
5. canonical write
6. mirror regenerate
7. `sync`
8. final answer draft
9. `lint`
10. fix if required
11. final answer

## 8. Verification Route

VEIL completed claim には少なくとも次が必要である。

1. candidate rule が authority surface に固定されている
2. representative capture -> normalize -> sync -> lint flow の strong evidence がある
3. canonical / mirror / sync / lint / normalize の route が docs と runtime で矛盾しない
4. current blocker が none である

## 9. Remaining Owner Decisions

current product design は default decisions を持つが、最終 owner confirmation が必要なのは次である。

- `2回出現` を default 必要条件として維持するか
- 1 回高影響語 override の範囲
- single-word 一般語の project-specific 例外範囲
- 2 回 lowercase phrase をどこまで高影響扱いにするか
