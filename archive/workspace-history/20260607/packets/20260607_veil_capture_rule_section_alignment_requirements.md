# VEIL Capture Rule Section Alignment Requirements

## 1. Overview

### 目的

`veil-normalize.py` の level 提案と、`veil-capture` の rule 書き込み手順を一致させる。

この wave では特に次を行う。

- `veil-capture` の書き込み先決定とファイル書き込み手順を section-aware にする
- `必須 / 推奨 / 観察` をどこへ書くかを skill と docs で明確化する

### 背景

- current runtime は `## 必須 / ## 推奨 / ## 観察` を解釈できる
- `veil-normalize.py` は new candidate に level 提案を返せる
- ただし `veil-capture` の task 7-8 は flat line 前提で、section へ書く手順が未反映

## 2. Scope

### In Scope

- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- 必要な最小限の `README.md`
- 必要な最小限の `docs/veil-design.md`

### Out of Scope

- runtime script 変更
- `~/.veil/rules/` 実データ migration
- level 自動決定ロジック変更

## 3. Success Criteria

- skill の task 7-8 が `section heading` を前提に読める
- level 提案を見て `必須 / 推奨 / 観察` のどこへ書くか分かる
- heading がない既存 file を壊さない手順になっている

## 4. Functional Requirements

1. 書き込み先決定では file だけでなく section も確定すること
2. ファイル書き込みでは `# {letter}` と `## level` の両方を扱うこと
3. existing flat rule line がある file では backward compatibility により `必須` と見なすこと
4. 最終判断は user 側で、level 提案は補助であると明記すること

## 5. Risks

- skill の手順が長くなりすぎる
- existing flat file への追記手順が曖昧だと誤編集を招く
