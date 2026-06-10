# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Note**: Entries from this point forward are written in English.
> Entries below [0.5.0] document the earlier web-UI architecture and remain in Japanese.

---

## [Unreleased]

### Added
- `locale/en.json` and `locale/ja.json` — locale string files covering all 7 Python runtime/tool files
- `shared/tools/veil_locale.py` — `detect_lang()` (env var → `~/.veil/config.json` → OS locale → `en` fallback) and `t(key, **kwargs)` for locale-aware terminal output
- Language override via `VEIL_LANG` environment variable or `lang` key in `~/.veil/config.json`

### Changed
- All Japanese terminal output strings in `veil-sync.py`, `veil-status.py`, `veil-lint.py`, `veil-normalize.py`, `veil-db.py`, `veil-profile-audit.py`, `veil-profile-export.py` replaced with `t()` calls
- Output language now follows OS locale automatically (Japanese users get Japanese, English users get English, no configuration required)
- `veil-sync.py`: renamed loop variable `t` → `target` to avoid shadowing the imported `t()` function
- `README.md` and `docs/veil-design.md` rewritten in English
- `LEVEL_REQUIRED`, `LEVEL_RECOMMENDED`, `LEVEL_OBSERVE` constants in `veil-profile-export.py` kept as Japanese — they match section headings in rules files (`## 必須` etc.) and are part of the file format, not output strings
- **veil-capture restructured**: replaced 11-step procedure list with a 3-section structure (output spec / adoption criteria / post-selection processing); intermediate output structurally suppressed
- **pending concept removed**: unified to adopt/skip binary; all VEIL-specific pending references removed from docs and skill files

---

## [1.0.0] - 2026-06-09

### Added
- **veil-capture skill (Claude Code)**: detects AI vocabulary from conversation, records to `~/.veil/veil.db` canonical, regenerates mirror, and syncs (`skills/claude-code/veil-capture.md`)
- **veil-capture skill (Codex)**: Codex-compatible version (`skills/codex/veil-capture/SKILL.md`)
- **veil-status.py**: status and setup diagnostics for canonical / mirror / sync targets / skill files
- **SQLite canonical route**: established `~/.veil/veil.db` as canonical; mirror maintained as transition surface
- **base rules integration**: reads `~/.veil/rules/{letter}.md` in alphabetical order and reflects vocabulary block to sync targets
- **veil-sync.py**: saves its own path to `~/.veil/config.json` on `--add`
- **veil.html**: generates `~/.veil/veil.html` — a searchable browser list of registered terms with per-term copy buttons for AI change instructions
- **install.sh**: installer script that copies skill files to Claude Code / Codex destinations

### Changed
- README fully rewritten (restructured around the veil-capture / veil-sync loop)
- `docs/veil-design.md` rewritten to match the current architecture
- `veil-sync.py` simplified to rules-only sync; automatic coupling with `app.py` removed

### Removed
- Multi-language support (Korean, Chinese) removed; simplified to en/ja only
- Legacy HTTP server UI moved to `archive/retired-support/`

---

## [0.5.0] - 2026-05-27

### Added
- **未変換語リスト**: 変換後テキストの未マッチ英単語をサイドバーにチップ表示。クリックで登録フォームに自動入力
- **クイック登録**: 変換後テキストをマウス選択すると `+ 登録` ボタンが浮き上がる。クリックでフォームに自動入力
- **Ctrl+Enter** ショートカットで変換実行
- **自動 veil-sync**: 語彙の追加・削除のたびにバックグラウンドで同期ファイルを自動更新
- **Windows 自動起動**: `install-startup.py` でログオン時に自動起動を登録（Task Scheduler 使用）
- **変換しない（対象外へ）**: 変換候補ポップアップから cat=2 に変更してスキップ登録
- **Export / Import**: 語彙を JSON ファイルでエクスポート・インポート。フッターに配置
- **登録フィードバック**: 追加ボタンが一時的に緑色に変化して登録完了を通知
- **リアルタイム反映**: 語彙変更後に変換後表示を即時再レンダリング
- **フッター 登録ボタン**: 変換エリア近くから登録操作できる

### Changed
- Export / Import ボタンをフッターへ移動（後のバージョンでサイドバーに戻された）

---

## [0.4.0] - 2026-05-27

### Added
- **veil-sync.py**: CLAUDE.md / AGENTS.md / .cursorrules 等に語彙ルールブロックを自動挿入・更新するスクリプト
- **`/vocab/prompt` エンドポイント**: AI ツール向けの語彙ルールテキストを返す
- ファイル種別に応じたマーカー形式（HTML コメント / `#` コメント）

---

## [0.3.0] - 2026-05-27

### Added
- **2パス変換アーキテクチャ**: 全登録語が領域を確保してからフィルタリング。翻訳なしのエントリが保護マーカーとして機能し、複合フレーズ（"reflection branch" と "branch" など）の誤マッチを防止

### Fixed
- 複合フレーズが部分一致でサブワードに分割されてしまう問題
- 対象外カテゴリの語が変換される問題

---

## [0.2.0] - 2026-05-27

### Added
- **変換候補の p1 昇格**: ポップアップで別候補を選択すると p1 に自動昇格して DB に保存
- テキスト選択でのクイック登録フォーム自動入力

### Fixed
- p2 のみ（カタカナのみ）で登録しようとするとガードされて保存できなかった問題
- 候補選択後に DB が更新されず次回変換に反映されなかった問題
- 登録ボタンの `cssText` 書き換えが既存スタイルを破壊していた問題

---

## [0.1.0] - 2026-05-27

### Added
- Python 標準ライブラリのみの HTTP サーバー（ポート 8080）
- SQLite による語彙 DB（`vocab.db`）
- 変換前 / 変換後の 2 列比較 UI
- 変換語のハイライト表示
- ハイライトクリックで変換候補（p1 / p2 / p3 / 自分で設定）を選択
- `isProtected()`: ファイル名・バッククォート内・`key=value` などを変換対象から除外
- `inferCat()`: 元語のパターンから自動カテゴリ推定（ALL_CAPS → 固定値、camelCase → 固有名詞 等）
- 語彙の手動追加・削除・検索・フィルタ
- 使用頻度順 / 登録順のソート切り替え
- カテゴリフィルタ（説明語 / 固有名詞 / プロジェクト固有 / 境界曖昧 / 対象外）
- シードデータ（22語の初期語彙）
