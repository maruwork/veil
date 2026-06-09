# VEIL veil-audit-db 導線整合 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. README のコンポーネント表へ `veil-audit-db.py` を追加する
2. README の Web UI 補助説明を短く補強する
3. README のファイル構成へ `veil-audit-db.py` を追加する
4. Codex / Claude Code の capture skill に helper DB 見直し導線を追加する
5. `rg` で露出面を確認する

## 2. 変更対象

- `README.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`

## 3. 完了確認

- `veil-audit-db.py` が README の入口表面に載っている
- skill から helper DB 監査補助へ自然に辿れる
- `veil-audit-db.py` の位置づけが docs / AGENTS / index と一致している
