# VEIL veil-audit-db 導線整合 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

`veil-audit-db.py` を、既に実装済みの helper DB 監査補助として README と capture skill から自然に辿れる状態にする。

## 2. 背景

- `veil-audit-db.py` 自体は実装済みで、設計書、manual、AGENTS、index には反映済み
- しかし README のコンポーネント表とファイル構成には未登録で、入口導線が薄い
- capture skill 側にも helper DB 見直し導線がなく、既存 `vocab.db` の棚卸し補助として発見しづらい

## 3. 今回の範囲

- README のコンポーネント表に `veil-audit-db.py` を追加する
- README のファイル構成に `veil-audit-db.py` を追加する
- README の helper DB 説明に、監査補助の役割を短く補強する
- Codex / Claude Code の capture skill に、既存 helper DB 見直し時の補助導線を追加する

## 4. 今回の範囲外

- `veil-audit-db.py` の挙動変更
- `app.py` や UI からの audit 実行導線追加
- 監査結果に基づく自動 cleanup

## 5. 機能要件

### 5.1 README の入口整合

- README だけ読んでも `veil-audit-db.py` の存在と役割が分かる
- `veil-normalize.py`、`veil-sync.py`、`veil-lint.py` と並ぶ補助線として位置づける

### 5.2 skill の補助導線

- capture skill から見て、本流は `capture -> normalize -> write -> sync -> lint`
- ただし既存 `vocab.db` の見直しが必要な時だけ、別補助線として `veil-audit-db.py` を示す
- capture 自体が helper DB を更新するものではないことも崩さない

## 6. 非機能要件

- 人向け説明は日本語優先にする
- `veil-audit-db.py` を authority と誤認させず、helper DB 監査補助として明記する
- 導線の追加だけに留め、既存の主運用ループを膨らませすぎない

## 7. 完了条件

- README のコンポーネント表とファイル構成に `veil-audit-db.py` が入っている
- Codex / Claude Code の capture skill に helper DB 見直し時の補助導線がある
- README、skill、既存 docs の説明が矛盾していない
