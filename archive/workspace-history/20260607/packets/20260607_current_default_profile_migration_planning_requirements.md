# Current Default Profile Migration Planning Requirements

## 1. Overview

### 目的

current default profile を legacy flat から section-aware profile へ移すための migration planning を固定する。

### 背景

- real audit では `19` file、`66` rule、`legacy_flat=66` が確認された
- current runtime は section-aware だが、実データは未移行
- 次に必要なのは、実編集前の順序、分類方針、停止条件の固定である

## 2. Scope

### In Scope

- migration の優先順
- file 単位の着手順
- `必須 / 推奨 / 観察` への再配置判断方針
- 実編集前の停止条件

### Out of Scope

- real `~/.veil/rules/` の編集
- 自動 migration script

## 3. Success Criteria

- どの file から始めるか決まっている
- `必須 / 推奨 / 観察` へ落とす判断軸が明記されている
- 実編集 wave に渡せる順序が決まっている
