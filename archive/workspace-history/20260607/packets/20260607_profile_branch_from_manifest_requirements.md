# Profile Branch From Manifest Requirements

## 1. Overview

### 目的

既存 profile pack の manifest から、新しい domain profile pack を分岐できる route を `veil-profile-export.py` に追加する。

### 背景

- 現状でも `--rules-dir` を使えば branch は作れる
- ただし domain / intended_use / base_profile を人手で再指定する必要があり、branch 経路としては弱い
- exported pack の `manifest.json` を base contract として再利用できる方が自然

## 2. Scope

### In Scope

- `veil-profile-export.py` に `--base-manifest` を追加
- base manifest から `rules_dir` / `profile_name` / `intended_use` を継承する
- README / 設計書へ branch recipe を追従

### Out of Scope

- 新しい root support tool 追加
- 実 branch rule の編集

## 3. Success Criteria

- `--base-manifest` だけで base pack から派生 export が始められる
- `base_profile` が自動で base manifest の `profile_name` を拾える
- branch sample を smoke できる
