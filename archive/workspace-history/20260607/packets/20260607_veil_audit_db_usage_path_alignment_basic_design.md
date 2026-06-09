# VEIL veil-audit-db 導線整合 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- runtime は変えず、入口文書と skill 文書の導線だけを整える
- `veil-audit-db.py` は主運用ループの必須工程には昇格させない
- helper DB が汚れた時、既存 `vocab.db` を見直したい時の非破壊補助として置く

## 2. 反映面

### 2.1 README

- コンポーネント表
  - `veil-audit-db.py` を helper DB 監査補助として追加
- Web UI 補助説明
  - 既存 `vocab.db` の棚卸し、keep / review / drop-candidate の見方を一言補強
- ファイル構成
  - root runtime file 一覧へ追加

### 2.2 skills

- Codex `skills/codex/veil-capture/SKILL.md`
- Claude Code `skills/claude-code/veil-capture.md`

両方に共通で、正規化補助の近くに以下を足す。

- 既存 helper DB を見直したい時は `python veil-audit-db.py` を使う
- これは `vocab.db` を読むだけの非破壊監査補助である
- capture の authority は引き続き `~/.veil/rules/*.md`

## 3. 表現ルール

- `helper DB`
  - 正本ではない
  - 補助棚の見直し対象
- `veil-audit-db.py`
  - cleanup 実行器ではない
  - keep / review / drop-candidate を返す監査補助

## 4. 検証方針

- `rg` で `veil-audit-db.py` の露出面を確認する
- README、2つの skill、AGENTS、docs、index の表現が矛盾していないか見る
