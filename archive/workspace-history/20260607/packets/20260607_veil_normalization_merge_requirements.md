# VEIL Normalization And Merge Requirements

## 1. Overview

### 目的

VEIL の capture 後に候補語の表記揺れを統合し、既存 rule との重複追加を減らす。

この wave では、候補抽出そのものではなく、抽出済み候補に対する normalize/merge 支援を実装する。

### 背景

- `veil-capture` は正規化を要求しているが、repo 内に専用 helper がない
- `current state` / `current-state` / `current_state` / `current states` のような揺れがあると、同一概念が別 rule として育ちやすい
- `common` 側では tool を運用に採るなら phase / trigger / authority / verification が canonical から辿れる必要がある

## 2. Scope

### In Scope

- candidate term list を正規化・統合する helper script を追加する
- helper は既存 `~/.veil/rules/*.md` と照合し、既存 rule へ merge すべき候補を提示する
- helper の運用 phase / trigger を canonical docs に反映する

### Out of Scope

- 自動抽出
- 自動書き込み
- 意味理解ベースの同義語統合
- 形態素解析器の導入

### Assumptions

- authority は `~/.veil/rules/*.md`
- 入力は capture 後の candidate list
- 英語系の軽い形態変化だけ扱う

## 3. Success Criteria

- `python veil-normalize.py --stdin` で candidate list を解析できる
- ハイフン / アンダースコア / 大文字小文字 / 単複の軽い揺れを統合できる
- 既存 rule と一致する normalized key があれば merge suggestion を返せる
- 新規候補には推奨 canonical key と target file が出せる

## 4. Functional Requirements

1. 入力候補の前後空白、先頭 bullet、重複行を吸収すること
2. 正規化は lowercase、separator 統一、space collapse、軽い singularize を行うこと
3. normalized key 単位で入力 variants を統合すること
4. 既存 rule の original も同じ正規化で index し、existing match を返すこと
5. 出力は text と json の両方を持つこと

## 5. Non-Functional Requirements

- 標準ライブラリのみ
- repo 外 rules dir を破壊しない read-only helper
- verify は smoke で十分な軽量 CLI

## 6. Risks

- 軽い singularize が一部語で過剰に効く
- 同義語ではなく表記揺れだけしか拾えない

## 7. Deferred Follow-up

- 近似語の fuzzy merge
- capture skill からの半自動呼び出し
- rule write 前の interactive merge confirm
