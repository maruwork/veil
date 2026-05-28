# Vocabulary Engine for Individual Language（VEIL）

**Vocabulary Engine for Individual Language**

AIが生成した英語テキストを、あなたが使いたい日本語（または韓国語・中国語）に変換するツール。

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](shared/app.py)

---

## 何ができるか

Claude Code や Codex などのAIが出力するテキストには、開発者が使いたい表現と異なる語が混在することがあります（例: "close" → AIは「クローズ」と書くが、あなたは「完了」と呼んでいる）。

VEILはそのギャップをローカルで解消します。

- **APIコストなし** — DeepL 無料 API のみ利用（翻訳候補の自動生成用。任意）
- **依存ゼロ** — Python 標準ライブラリのみ。`pip install` 不要
- **外部送信なし** — 変換処理はすべて自サーバー内で完結

---

## セットアップ

Python 3.8 以上が必要です。

```bash
git clone https://github.com/fumimaruwork/veil.git
cd veil/shared
python app.py
```

ブラウザで `http://<ホスト名またはIPアドレス>:8080` を開く。
ローカルで起動した場合は `http://localhost:8080`。

これだけで動作します。

---

## 翻訳候補の自動生成（任意）

DeepL 無料 API キーがあると、語彙登録時に翻訳候補を自動取得できます。
キーがなくても手動入力で全機能が使えます。

`shared/.env` ファイルを作成して以下を記述：

```
DEEPL_API_KEY=your-api-key-here
```

または環境変数として設定：

```bash
# Mac / Linux
export DEEPL_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:DEEPL_API_KEY = "your-api-key-here"
```

DeepL 無料アカウントは https://www.deepl.com/pro-api から取得できます（月50万文字まで無料）。

---

## 使い方

### 基本フロー

1. AIが生成したテキストをテキストエリアに貼り付ける
2. **変換する**（または `Ctrl+Enter`）をクリック
3. 変換後テキストを確認。ハイライト語をクリックして別の候補に変更

### 語彙の登録

- サイドバーの **語彙を追加** フォームから手動登録
- 変換後テキストを選択すると **+ 登録** ボタンが浮き上がる（クイック登録）
- **未変換語** リストのチップをクリックしてフォームに自動入力

### 他のAIツールへの語彙同期

登録済み語彙を CLAUDE.md, AGENTS.md, .cursorrules 等に自動挿入できます。

```bash
# 同期先ファイルを登録
python veil-sync.py --add /path/to/CLAUDE.md

# 登録済み一覧の確認
python veil-sync.py --list

# 手動で全ファイルを同期
python veil-sync.py
```

対応ツール：Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, Aider

### Windows 自動起動（任意）

```bash
python install-startup.py           # 登録
python install-startup.py --remove  # 解除
python install-startup.py --status  # 確認
```

---

## 変換されないケース

以下のパターンは意図的に変換をスキップします。

| パターン | 例 |
|---------|-----|
| ファイル名・パスの一部 | `workflow_close.py` |
| ハイフン区切り識別子 | `task-close-workflow` |
| バッククォート内 | `` `close()` `` |
| `key=value` 形式 | `status=close` |
| チケット ID | `BRANCH-046` |

---

## ファイル構成

```
veil/shared/
├── app.py               # バックエンド（HTTPServer + SQLite）
├── index.html           # UI
├── style.css            # スタイル
├── locales.js           # UI文字列（日本語/韓国語/中国語）
├── main.js              # 初期化
├── js/
│   ├── state.js         # グローバル状態
│   ├── api.js           # サーバー通信
│   ├── convert.js       # 変換ロジック
│   ├── render.js        # DOM描画
│   └── ui.js            # イベントハンドラ
├── veil-sync.py         # 外部AIツール設定ファイルへの語彙同期
├── install-startup.py   # Windows自動起動の登録
└── docs/
    └── manual.html      # マニュアル（http://<host>:8080/manual）
```

---

## カテゴリ

| cat | 名称 | 変換対象 | 用途 |
|-----|------|---------|------|
| 1 | 説明語 | ✓ | 一般的な技術英語 |
| 2 | 固定値・対象外 | — | ALL_CAPS定数、変換しない語 |
| 5 | 固有名詞・製品名 | ✓ | ツール名・ライブラリ名 |
| 6 | プロジェクト固有 | ✓ | プロジェクト独自の用語 |
| 7 | 境界が曖昧 | ✓ | 文脈によって変換が必要な語 |

---

## ライセンス

[MIT License](LICENSE)
