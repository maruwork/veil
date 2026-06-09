# Detailed Design

## 1. Runtime Contract

### 1.1 New Fields

`veil-normalize.py --json` の各 item に、必要時だけ次を出す。

- `retention_hint`
- `retention_reason`

### 1.2 Emission Rule

- item が `selection_hint == 保留寄り` の場合のみ付与する
- `先に採る候補` と `外す寄り` には付けない

## 2. Decision Rules

### 2.1 `今は見送る`

条件:

- classification が曖昧寄り
- 一般動詞単体または意味範囲が広い
- 頻度 1

出力意図:

- 今回は採用も保留棚昇格もせず閉じられる

### 2.2 `後で再観察する`

条件:

- 説明語候補
- 一定の need はある
- ただし `先に採る候補` に届かない

出力意図:

- 次の会話で再出現したら見直す

### 2.3 `文脈不足で保留`

条件:

- 頻度だけでは弱い
- 文脈依存が強い
- project 固有語の可能性がある

出力意図:

- 今回だけでは決めない

## 3. Text Rendering Contract

`保留寄り` item の text block は次の順にする。

1. 基本情報
2. `選別目安`
3. `選別理由`
4. `保留処理`
5. `保留理由`

## 4. Skill / Docs Contract

skill と docs は `保留寄り` を見た時の行動を次の順に固定する。

1. `今は見送る`
   - 今回は採用しない
2. `後で再観察する`
   - 同文脈で再出現したら再評価
3. `文脈不足で保留`
   - owner 判断が必要になるまで保留

## 5. Error / Stop Conditions

- `retention_hint` が `保留寄り` 以外にも出る
  - fail
- skill/docs で 3 つの action 名がずれる
  - fail
- output が長くなりすぎて capture report 軽量化を壊す
  - stop and redesign

## 6. Verification Conditions

- JSON で `retention_hint` / `retention_reason` が確認できる
- text で `保留処理` / `保留理由` が確認できる
- README / design / 2 skills / current companion が同じ action 名を使う
