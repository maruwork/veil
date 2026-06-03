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

VEILはこのばらつきを解消する。AIが使った語彙を捕捉・個人ルールとして蓄積し、すべてのAIツールの設定ファイルに自動で反映する。

**語彙ルールの正本は `~/.veil/rules/` です。`vocab.db` は Web UI の補助データであり、正本ではありません。**

---

## 仕組み

```
会話中にAIが使った英語・造語・略語
        ↓
  /veil-capture（スキル）
        ↓
  AIが候補を抽出、ユーザーが採用語を決定
        ↓
 ~/.veil/rules/{letter}.md に書き込む  ← 正本
        ↓
  veil-sync.py が自動実行
        ↓
 CLAUDE.md / AGENTS.md / .cursorrules 等に反映
        ↓
次回セッションからAIが統一された語彙で出力する
```

---

## コンポーネント

| コンポーネント | 役割 |
|-------------|------|
| `/veil-capture` スキル | 会話からAI語彙を検出し `~/.veil/rules/` に書き込む |
| `~/.veil/rules/{letter}.md` | 語彙ルールの正本（アルファベット別） |
| `veil-sync.py` | ルールをAIツール設定ファイルへ同期 |
| `app.py`（UI） | 語彙DBの管理・変換確認用 Web UI（補助） |

---

## セットアップ

Python 3.8 以上が必要です。

```bash
git clone https://github.com/fumimaruwork/veil.git
cd veil
```

### 1. 同期先ファイルを登録する

**この手順でスキルが参照する `~/.veil/config.json` が作成されます。スキルを使う前に必ず実行してください。**

```bash
python veil-sync.py --add /path/to/CLAUDE.md
python veil-sync.py --add /path/to/AGENTS.md
```

登録と同時に即時同期されます。対応ツールの例：

| ツール | 設定ファイル | マーカー形式 |
|--------|------------|------------|
| Claude Code | `CLAUDE.md` | `<!-- VEIL_START -->` |
| Codex | `AGENTS.md` | `<!-- VEIL_START -->` |
| Cursor | `.cursorrules` | `<!-- VEIL_START -->` |
| GitHub Copilot | `.github/copilot-instructions.md` | `<!-- VEIL_START -->` |
| Gemini CLI | `GEMINI.md` | `<!-- VEIL_START -->` |
| Aider | `.aider.conf.yml` | `# VEIL_START` |

`.yml` / `.yaml` / `.toml` / `.ini` / `.cfg` 拡張子のファイルは `# VEIL_START` / `# VEIL_END` マーカーを使用します。

### 2. スキルを配置する

**Claude Code**

```bash
# macOS / Linux
cp skills/claude-code/veil-capture.md ~/.claude/commands/veil-capture.md
```

```powershell
# Windows (PowerShell)
Copy-Item skills\claude-code\veil-capture.md $env:USERPROFILE\.claude\commands\veil-capture.md
```

**Codex**

```bash
# macOS / Linux
cp -r skills/codex/veil-capture ~/.agents/skills/veil-capture
```

```powershell
# Windows (PowerShell)
Copy-Item -Recurse skills\codex\veil-capture $env:USERPROFILE\.agents\skills\veil-capture
```

---

## 使い方

### AIの語彙を捕捉する（メインワークフロー）

Claude Code で会話後に実行：

```
/veil-capture
```

AIが抽出した候補を提示します。ユーザーが採用語を決定した時点で `~/.veil/rules/` に書き込み、登録済みの全設定ファイルへ即時同期します。

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

語彙DBの確認・管理・変換テスト用のローカルUIです。メインワークフローには不要です。起動中は語彙DBの内容も同期に加わります。未起動の場合は `~/.veil/rules/` の語彙ルールのみ同期します。

```bash
python app.py
```

`http://127.0.0.1:8080` をブラウザで開く。詳細は [`docs/veil-design.md`](docs/veil-design.md) を参照。

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
│       ├── api.js
│       ├── convert.js      # 2パス変換エンジン
│       ├── render.js
│       ├── state.js
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
