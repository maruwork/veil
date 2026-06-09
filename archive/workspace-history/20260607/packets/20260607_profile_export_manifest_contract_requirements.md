# Profile Export Manifest Contract Requirements

## 1. Overview

### 目的

`veil-profile-export.py` の manifest に domain profile 分岐用の最小契約を追加する。

### 背景

- profile pack export 自体は実装済み
- 次は technical writing default から業界別 profile へ分岐できる manifest 契約が必要
- 現状 manifest は summary だけで、分岐元や intended use が弱い

## 2. Scope

### In Scope

- `veil-profile-export.py` に metadata option を追加
- manifest に `domain`, `intended_use`, `base_profile` を追加
- docs 追従

### Out of Scope

- 実際の業界別 profile ルール追加

## 3. Success Criteria

- export 時に metadata を指定できる
- manifest に domain branch の最小情報が残る
