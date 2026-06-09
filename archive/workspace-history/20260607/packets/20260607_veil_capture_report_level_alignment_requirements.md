# VEIL Capture Report Level Alignment Requirements

## 1. Overview

### 目的

`veil-capture` の完了報告を level-aware にし、`必須 / 推奨 / 観察 / 保留` が一目で分かる report 形式へ更新する。

### 背景

- current VEIL は level-aware write と lint semantics を持つ
- ただし capture の完了報告は旧来の `term → 候補1...` 形式中心で、level が見えない
- このままだと close 時に何を hard gate に上げたかが読みにくい

## 2. Scope

### In Scope

- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `README.md`
- 必要な最小限の `docs/veil-design.md`

### Out of Scope

- runtime script 変更
- level 自動決定ロジック変更
- `~/.veil/rules/` 実データ変更

## 3. Success Criteria

- 完了報告で各採用語の level が見える
- `保留` と `観察` が区別して扱われる
- 同期結果と返答前 lint gate の接続が report で読める

## 4. Functional Requirements

1. 採用語は `level` を付けて報告すること
2. `保留` は採用語と別枠で列挙すること
3. `観察` は採用済みでも hard gate 外であることが読めること
4. 同期結果を report に残すこと
5. main task prose へ戻る前に lint が必要だと report で分かること
