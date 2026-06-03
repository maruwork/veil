# VEIL — Vocabulary Engine for Individual Language

AIが出力する語彙を、あなたの好みに統一するローカルツール。

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](app.py)

---

## VEILとは

Claude Code や Codex などのAIは、同じ概念を毎回異なる語で表現する。

- "close" と書いたり「完了」と書いたり「クローズ」と書いたり
- "merge" → 「マージ」「統合」「取り込み」が混在
- "untracked" をそのまま英語で出力する

VEILはこのばらつきを解消する。AIが使った語彙を捕捉・翻訳して個人ルールとして蓄積し、すべてのAIツールの設定ファイルに自動で反映する。

---

## 仕組み

```
会話中にAIが使った英語・造語・略語
        ↓
  /veil-capture（スキル）
        ↓
  AIが翻訳・判定
        ↓
 ~/.veil/rules/{letter}.md に書き込む
        ↓
  veil-sync.py が自動実行
        ↓
 CLAUDE.md / AGENTS.md / .cursorrules 等に反映
        ↓
次回セッションからAIが統一された語彙で出力する
```

この「キャプチャ → ルール → 同期」のループが核心。

---

## コンポーネント

| コンポーネント | 役割 |
|-------------|------|
| `/veil-capture` スキル | 会話からAI語彙を検出・翻訳・ルールファイルへ書き込む |
| `~/.veil/rules/{letter}.md` | 語彙ルールの保存場所（アルファベット別） |
| `veil-sync.py` | ルールをAIツール設定ファイルへ同期 |
| `app.py`（UI） | 語彙DBの管理・変換確認用Web UI（補助） |

---

## セットアップ

Python 3.8 以上が必要です。

```bash
git clone https://github.com/fumimaruwork/veil.git
cd veil
```

### 1. app.py を起動する

```bash
python app.py
```

`veil-sync.py` は `app.py` が起動中の場合に語彙DBも同期します。起動していない場合は `~/.veil/rules/` の base rules のみ同期します。

### 2. 同期先ファイルを登録する

VEILのルールを反映したいAIツールの設定ファイルを登録します。

```bash
python veil-sync.py --add /path/to/CLAUDE.md
python veil-sync.py --add /path/to/AGENTS.md
```

登録と同時に即時同期されます。対応ツールの例：

| ツール | 設定ファイル |
|--------|------------|
| Claude Code | `CLAUDE.md` |
| Codex | `AGENTS.md` |
| Cursor | `.cursorrules` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Gemini CLI | `GEMINI.md` |
| Aider | `.aider.conf.yml` |

### 3. スキルを配置する

`skills/` フォルダにスキルテンプレートが入っています。各AIツールのグローバルスキルフォルダにコピーしてください。

**Claude Code**

```bash
cp skills/claude-code/veil-capture.md ~/.claude/commands/veil-capture.md
```

**Codex**

```bash
cp -r skills/codex/veil-capture ~/.agents/skills/veil-capture
```

---

## 使い方

### AIの語彙を捕捉する（メインワークフロー）

Claude Code で会話後に実行：

```
/veil-capture
```

会話中にAIが使った英語・造語・略語を自動検出し、翻訳候補を提示します。確認後、`~/.veil/rules/` に書き込み、登録済みの全設定ファイルへ即時同期します。

外部テキスト（Codex の出力など）を解析する場合：

```
/veil-capture <対象テキストをここに貼り付け>
```

### ルールファイルの確認・編集

```
~/.veil/rules/
├── m.md    # m で始まる語のルール
├── u.md    # u で始まる語のルール
└── ...
```

各ファイルは直接編集できます。

```markdown
# u

- uncommitted → 未コミット
- untracked → 未追跡
```

### 手動で同期する

```bash
python veil-sync.py              # 全ターゲットを同期
python veil-sync.py --list       # 登録済み一覧
python veil-sync.py --add <path> # 同期先を追加
python veil-sync.py --remove <path> # 同期先を解除
```

---

## Web UI（補助機能）

語彙DBの確認・管理・変換テスト用のローカルUIです。メインワークフローには不要ですが、登録語彙の一覧確認や変換動作の確認に使えます。

```bash
python app.py
```

`http://127.0.0.1:8080` をブラウザで開く。

**DeepL翻訳候補の自動取得（任意）**

`.env` ファイルを作成して以下を記述：

```
DEEPL_API_KEY=your-api-key-here
```

---

## ファイル構成

```
veil/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── veil-sync.py            # ルール同期スクリプト（コアツール）
├── app.py                  # Web UI バックエンド
├── install-startup.py      # Windows自動起動
├── ui/                     # Web UI フロントエンド
│   ├── index.html
│   ├── style.css
│   ├── main.js
│   ├── locales.js
│   └── js/
│       ├── state.js
│       ├── api.js
│       ├── convert.js      # 2パス変換エンジン
│       ├── render.js
│       └── ui.js
├── skills/                 # スキルテンプレート
│   ├── claude-code/
│   │   └── veil-capture.md
│   └── codex/
│       └── veil-capture/
│           └── SKILL.md
└── docs/
    ├── veil-design.md      # 設計書
    └── manual.html         # UIマニュアル
```

---

## ライセンス

[MIT License](LICENSE)
