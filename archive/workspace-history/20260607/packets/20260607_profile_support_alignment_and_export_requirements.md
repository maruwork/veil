# Profile Support Alignment And Export Requirements

## 1. Overview

### 目的

- `veil-profile-audit.py` の governance 未整合を解消する
- `current default profile` を repo 外へ切り出せる `veil-profile-export.py` を追加し、domain profile 分離の実体を作る

### 背景

- `veil-profile-audit.py` は README / 設計書では使っているが、`index/` と `AGENTS.md` で位置づけが弱い
- current default profile の migration は完了し、次は profile tuning と domain profile 分離が主課題になった
- 新しい top-level shelf は作らず、既存 root runtime と `workspace/` を使って export 経路を作る必要がある

## 2. Scope

### In Scope

- `veil-profile-audit.py` の governance / docs / entry alignment
- `veil-profile-export.py` の追加
- `README.md`, `docs/veil-design.md`, `AGENTS.md`, `index/` への反映
- export の smoke verify

### Out of Scope

- runtime mainline loop の仕様変更
- `~/.veil/rules/` の内容再調整
- 新しい top-level shelf 作成

## 3. Success Criteria

- `veil-profile-audit.py` が governance 上 support runtime として明示される
- `veil-profile-export.py` が current default profile を section-aware のまま output dir へ書き出せる
- export output に profile summary が残る
- docs / AGENTS / index が export 導線を current canonical として説明する

## 4. Stop Conditions

- new top-level shelf が必要になる
- export 実装が `~/.veil/rules/` を mutate しそうになる
