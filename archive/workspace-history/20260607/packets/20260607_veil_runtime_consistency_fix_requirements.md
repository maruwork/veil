# VEIL Runtime Consistency Fix Requirements

## 1. Overview

### 目的

runtime / UI / helper script のコードレビューで確定した bug と不整合を、bounded scope で修正する。

### 今回の対象

1. `app.py` の schema migration が古い DB shape で起動失敗する
2. UI の再描画経路で unmatched / summary が stale になる
3. `veil-normalize.py` と `veil-lint.py` の plural / phrase 整合がずれている
4. canonicalized rule conflict が silent drop される
5. `veil-sync.py` の `targets.json` 読み込み破損に耐性がない

## 2. Scope

### In Scope

- `app.py` migration robustness 修正
- UI 再描画整合修正
- `veil-lint.py` / `veil-normalize.py` の plural / phrase 整合修正
- helper scripts に canonical conflict 可視化追加
- `veil-sync.py` の `targets.json` read-hardening
- 必要最小限の canonical docs 更新

### Out of Scope

- VEIL 全面 redesign
- DB schema の新規追加
- UI 大改修
- fuzzy merge や意味ベース同義語統合

## 3. Success Criteria

- timestamp のない旧 `vocab` shape でも `init_db()` が落ちない
- vocab 更新後に compare summary / unmatched が stale にならない
- normalize で統合された軽い plural/phrase が lint でも一貫して検出される
- rule conflict が silent drop されず、少なくとも warning として表面化する
- `targets.json` が壊れていても `veil-sync.py` が traceback で落ちず、説明可能に fail する

## 4. Verification

- `python -m py_compile ...`
- migration 再現スモーク
- lint / normalize スモーク
- UI 再描画経路の静的確認

## 5. Risks

- migration 補完列の扱いを誤ると既存データが欠ける
- lint plural 許容を広げすぎると false positive が増える
