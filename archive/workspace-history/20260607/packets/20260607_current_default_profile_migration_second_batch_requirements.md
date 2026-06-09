# Current Default Profile Migration Second Batch Requirements

## 1. Overview

### 目的

current default profile の second batch として `a.md / l.md / t.md / b.md / h.md` を section-aware 形式へ移行する。

### 背景

- initial batch `c/s/d/p/r` は完了した
- 残り `14` file のうち、この `5` file は rule 数が少なく、保守的な再分類で先に legacy flat を減らしやすい
- exact usage evidence が弱い語が多いため、hard gate は最小限に絞る

## 2. Scope

### In Scope

- `a.md / l.md / t.md / b.md / h.md` の current readback
- 各 file の保守的な level 再分類
- 各 file の section-aware migration
- post-batch audit

### Out of Scope

- 残り file の migration
- rule 新規追加
- runtime / doc 変更

## 3. Batch Decisions

### a.md

- `audit` は `推奨`
- `allowlist` は `推奨`
- `active disposition` は `観察`
- `analysis` は `観察`

### l.md

- `live proof` は `推奨`
- `latest close detail` は `観察`
- `latest result` は `観察`
- `local reference` は `観察`

### t.md

- `task` は `必須`
- `tool portability` は `観察`
- `tracked row` は `観察`

### b.md

- `bounded work` は `推奨`
- `bounded goal` は `観察`
- `bounded fix` は `観察`

### h.md

- `hardening` は `推奨`
- `healthcheck` は `推奨`
- `hidden premise` は `観察`

## 4. Success Criteria

- 5 file すべてが `## 必須 / ## 推奨 / ## 観察` 形式になる
- 5 file の legacy flat が `0` になる
- post-batch audit で legacy flat files がさらに減る

## 5. Stop Conditions

- readback が planned source と大きく異なる
- current session の evidence だけでは過度に強い level を置きそうになる
