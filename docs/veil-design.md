# VEIL 設計書

**Vocabulary Engine for Individual Language**

---

## 1. 目的

AIが出力する語彙をできる限り汎用的にしつつ、使用者の好みに統一すること。

Claude Code・Codex などのAIは同じ概念を異なる語で表現する。VEILはそのばらつきを個人ルールとして蓄積し、すべてのAIツール設定ファイルに自動で反映するループを提供する。

---

## 2. 設計方針

- **ローカル完結**: SQLite + Python 標準ライブラリのみ。外部サービス不要
- **依存ゼロ**: `pip install` 不要
- **事前制御優先**: AIの出力後に修正するのではなく、設定ファイルに語彙ルールを事前注入して出力を統一する
- **UIは補助**: Web UIは語彙DB管理・変換確認用。メインワークフローはスキルとveil-sync

---

## 3. アーキテクチャ

```
会話中のAI語彙
      ↓
/veil-capture スキル（Claude Code / Codex）
      ↓  ← AIが候補を抽出、ユーザーが採用語を決定
~/.veil/rules/{letter}.md（語彙ルール保存）
      ↓
veil-sync.py
      ↓
CLAUDE.md / AGENTS.md / .cursorrules 等
      ↓
次セッションのAI出力が統一される
```

---

## 4. コンポーネント詳細

### 4-1. veil-capture スキル

AIとの会話から英語・造語・略語を検出し、ユーザーが採用語を決定して `~/.veil/rules/` に書き込む。

**配置場所**

| ツール | パス |
|--------|------|
| Claude Code（グローバル） | `~/.claude/commands/veil-capture.md` |
| Codex（グローバル） | `~/.agents/skills/veil-capture/SKILL.md` |

**処理フロー**

1. 解析対象テキストを決定（`args` があればそれ、なければ会話全体）
2. 候補を抽出（意味単位・反復語のみ・固有名詞除外）
3. 候補リストを提示（AIは抽出役、採用はユーザーが決定）
4. ユーザーが採用語を確定した時点で即記録（`~/.veil/rules/{先頭文字}.md`）
5. `veil-sync.py` を実行して即時同期
- 例外確認のみ：複数候補の競合、または同一語に別訳が登録済みの場合

**ルールファイルテンプレート**

```markdown
# {letter}

- {元語} → {推奨表記}
```

### 4-2. ~/.veil/rules/

語彙ルールの保存場所。アルファベット1文字ごとにファイルを分割する。

```
~/.veil/
├── rules/
│   ├── m.md
│   ├── u.md
│   └── ...
├── targets.json    # 同期先ファイルパスのリスト
└── config.json     # veil-sync.py のパス（自動記録）
```

**設定の正本**

| データ | 場所 | 備考 |
|--------|------|------|
| 語彙ルール | `~/.veil/rules/` | ユーザーホーム。clone先を変えても引き継がれる |
| 同期先リスト | `~/.veil/targets.json` | ユーザーホーム。同上 |
| 語彙DB | `{repodir}/vocab.db` | リポジトリ内（`.gitignore` 済み）。clone先が変わったら `app.py` を起動し直すだけで再作成される |
| sync_scriptパス | `~/.veil/config.json` | `--add` 実行時に現在の `veil-sync.py` パスを自動記録。clone先変更後は `python veil-sync.py --add <path>` を再実行すること |

### 4-3. veil-sync.py

語彙ルールを各AIツール設定ファイルに同期するスクリプト。

**前提**: `app.py` が起動中であれば語彙DBの内容も同期する。未起動の場合は `~/.veil/rules/` の語彙ルールのみで同期する（エラー終了しない）。

**動作**

1. VEILサーバーの `/vocab/prompt` エンドポイントから語彙DBの内容を取得（サーバー未起動なら空として扱い、語彙ルールのみで処理）
2. `~/.veil/rules/` 以下の全 `.md` ファイルをアルファベット順に読み込む（語彙ルール）
3. 語彙DBと語彙ルールを結合してマーカー間に挿入・更新

**マーカー形式**

```markdown
<!-- VEIL_START -->
以下の語彙ルールに従って出力してください：
- close → 完了
...

表記統一ルール：
- uncommitted → 未コミット
<!-- VEIL_END -->
```

YAML系ファイル（.yml/.yaml/.toml 等）は `# VEIL_START` / `# VEIL_END` を使用。

**コマンド**

```bash
python veil-sync.py                  # 全ターゲットを同期
python veil-sync.py --add <path>     # 同期先を登録（即時同期）
python veil-sync.py --list           # 登録済み一覧
python veil-sync.py --remove <path>  # 登録を解除
python veil-sync.py --stdin          # stdin から語彙を受け取って同期（サーバー内部用）
```

**アトミック書き込み**: tempfile + shutil.move を使用。書き込み途中のファイル破損を防ぐ。

**ポップアップ選択と優先順の更新**

変換結果をクリックしてポップアップから別候補を選ぶと、表示の切替だけでなく語彙DBの優先順も更新される（`ui/js/ui.js selectCand()`）。選んだ語が p1 に繰り上がり、残りが p2/p3 にずれる。次回以降の変換に即時反映される。

### 4-4. app.py（Web UI バックエンド）

語彙DB（SQLite）の管理と変換テスト用ローカルサーバー。ポート 8080。`ui/` ディレクトリの静的ファイルを配信する。

**エンドポイント**

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | index.html |
| GET | `/manual` | UIマニュアル |
| GET | `/vocab` | 全語彙をJSON配列で返す |
| GET | `/vocab/prompt` | AI設定ファイル向け語彙ルールテキスト |
| POST | `/vocab/upsert` | 語彙の追加・更新 |
| POST | `/vocab/delete` | 語彙の削除 |
| POST | `/vocab/increment` | use_count インクリメント |

**自動同期（trigger_sync）**

語彙の追加・削除時にバックグラウンドスレッドで `veil-sync.py --stdin` を呼び出す。
`--stdin` を使う理由：シングルスレッドの HTTPServer がデッドロックするため、HTTP経由ではなく stdin で語彙を渡す。

---

## 5. 語彙DB スキーマ

```sql
CREATE TABLE vocab (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  original   TEXT UNIQUE NOT NULL,  -- 元語（英語）
  p1         TEXT DEFAULT '',       -- 日本語1（主変換先）
  p2         TEXT DEFAULT '',       -- カタカナ
  p3         TEXT DEFAULT '',       -- 日本語2（補助候補）
  cat        INTEGER DEFAULT 1,     -- カテゴリ（下表）
  use_count  INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**カテゴリ定義**

| cat | 名称 | 変換対象 | 使い分け |
|-----|------|---------|---------|
| 1 | 説明語 | ✓ | 汎用的な英語語彙。デフォルト |
| 2 | 固定値・対象外 | ✗ | 変換させたくない語（保護マーカーとして機能） |
| 5 | 固有名詞・製品名 | ✓ | 製品名・サービス名を日本語表記に統一したいとき |
| 6 | プロジェクト固有 | ✓ | 特定リポジトリ・チーム内だけで使う用語 |
| 7 | 境界が曖昧 | ✓ | 登録はしたいが分類が確定していない語の一時置き場 |

---

## 6. 変換エンジン（js/convert.js）

2パスアーキテクチャでサブワード誤マッチを防ぐ。

**パス1（領域確保）**: 全語彙を長さ降順で処理し、先に確保した領域にはサブワードが入り込めない。

**パス2（変換フィルタ）**: cat IN (1,5,6,7) かつ翻訳ありの語のみ置換。cat=2 のエントリは保護マーカーとして機能し、その部分は変換されず素通しになる。

**isProtected()**: バッククォート内・ダブルクォート内・`=`の直後・`key=value`行・ファイル名パターン（`._-`隣接）を変換対象から除外。

---

## 7. セキュリティ

- バインド: `127.0.0.1:8080` のみ（ネットワーク公開なし）
- CORS: `Access-Control-Allow-Origin: http://127.0.0.1:8080`（ワイルドカード不使用）
- パストラバーサル防止: `_serve_static` で case-insensitive チェック（`ui/` 配下のみ配信）。`/` と `/manual` はハードコードパスで直接提供するため `_serve_static` を通らない
- `.env`・`vocab.db` は `.gitignore` で git 管理外
