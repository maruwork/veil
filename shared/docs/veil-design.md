# VEIL 設計書

**Vocabulary Engine for Individual Language**
AIの出力テキストを、使用者の個人語彙ルールに沿った日本語に変換するローカルツール。

---

## 1. 設計方針

### 核となる制約

- **APIコスト不要**: DeepL 無料API（翻訳候補の自動生成用）のみ。LLM API は使わない。
- **依存ゼロ**: Python 標準ライブラリのみ。`pip install` 不要。
- **ローカル完結**: SQLite + Python の HTTP サーバー。インターネット接続なしで変換機能は全動作する。

### 解決する問題

Claude Code や Codex など LLM が生成するテキストには、開発者が使いたい日本語表現と異なる語が混在する（例: "close" → 使いたい語は「完了」だが AI は「クローズ」と書く）。VEIL はそれを手元で即座に変換する。

---

## 2. ファイル構成

```
veil/shared/
├── app.py              # バックエンド (HTTP サーバー + SQLite + API)
├── index.html          # UI エントリーポイント
├── style.css           # スタイル
├── main.js             # フロントエンドロジック全体
├── veil-sync.py        # 外部 AI ツール設定ファイルへの語彙同期
├── install-startup.py  # Windows ログイン時自動起動の登録
├── vocab.db            # SQLite DB（初回起動時自動生成、git 管理外）
└── docs/
    └── veil-design.md  # このファイル
```

---

## 3. データモデル

### vocab テーブル

| カラム     | 型        | 説明                                |
|-----------|-----------|-------------------------------------|
| id        | INTEGER   | PRIMARY KEY AUTOINCREMENT           |
| original  | TEXT      | 英語元語（UNIQUE）                  |
| p1        | TEXT      | 日本語1（主要変換先）               |
| p2        | TEXT      | カタカナ（任意）                    |
| p3        | TEXT      | 日本語2 補助候補（任意）            |
| cat       | INTEGER   | カテゴリ（下表参照）                |
| use_count | INTEGER   | 変換実行時のマッチ累積回数          |
| created_at| TIMESTAMP | 登録日時                            |
| updated_at| TIMESTAMP | 更新日時                            |

### カテゴリ定義

| cat | 名称             | 変換対象 | 用途                                     |
|-----|-----------------|---------|------------------------------------------|
| 1   | 説明語           | ✓       | 一般的な技術英語（"close"→完了 等）       |
| 2   | 固定値・対象外   | ✗       | ALL_CAPS 定数、変換したくない語           |
| 3   | 変数名           | ✗       | camelCase 変数名等（現在未使用）          |
| 4   | ID              | ✗       | BRANCH-046 などのチケット ID              |
| 5   | 固有名詞・製品名 | ✓       | ツール名・ライブラリ名等                  |
| 6   | プロジェクト固有 | ✓       | プロジェクト独自の用語                    |
| 7   | 境界が曖昧       | ✓       | 文脈によって変換が必要な語               |

**TARGET_CATS = [1, 5, 6, 7]** のみ変換対象。cat=2 は「変換しない（対象外）」として機能する。

### inferCat() — 自動カテゴリ推定

登録時に元語のパターンから cat を自動推定する。

```js
function inferCat(word) {
  if (/^[A-Z][A-Z0-9_]+$/.test(word)) return 2;   // ALL_CAPS → 固定値
  if (/^[A-Z]+-\d+$/.test(word))      return 4;   // LETTERS-000 → ID
  if (/[a-z][A-Z]|[A-Z]{2,}/.test(word)) return 5; // 内部大文字 → 固有名詞
  return 1;
}
```

---

## 4. バックエンド (app.py)

### HTTP エンドポイント

| メソッド | パス              | 説明                                  |
|---------|------------------|---------------------------------------|
| GET     | /                | index.html を返す                     |
| GET     | /style.css       | スタイルシートを返す                  |
| GET     | /main.js         | フロントエンド JS を返す              |
| GET     | /vocab           | 全語彙を JSON 配列で返す              |
| GET     | /vocab/prompt    | AI ツール向け語彙ルールテキストを返す |
| POST    | /vocab/upsert    | 語彙の追加・更新（upsert）            |
| POST    | /vocab/delete    | 語彙の削除                            |
| POST    | /vocab/increment | use_count をインクリメント            |
| POST    | /vocab/generate  | DeepL で翻訳候補を生成                |

### /vocab/prompt の出力形式

AI ツールの設定ファイルに埋め込む語彙ルールテキスト。cat IN (1,5,6,7) かつ翻訳あり の語のみ出力。

```
以下の語彙ルールに従って出力してください：
- close → 完了 / クローズ
- branch → ブランチ
- workflow → ワークフロー
```

### /vocab/generate — DeepL 翻訳

`DEEPL_API_KEY` 環境変数が設定されている場合のみ動作。

```python
# カタカナ比率 > 50% の場合は p2（カタカナ）、それ以外は p1（日本語1）に格納
if is_katakana(result):
    return {"p1": "", "p2": result, "p3": ""}
return {"p1": result, "p2": "", "p3": ""}
```

APIキーがない場合は `{"p1":"","p2":"","p3":""}` を返す（エラーにはしない）。

### 環境変数ロード

```python
ENV_PATH = r"C:\Users\f_tan\keys\veil\env\.env"
```

`key=value` 形式のファイルを起動時に読み込む。`.env` ファイルは git 管理外。

### 自動 veil-sync (trigger_sync)

語彙の追加・削除が発生した際、バックグラウンドスレッドで `veil-sync.py --stdin` を呼び出す。

```python
def trigger_sync():
    def _run():
        text = get_vocab_prompt().encode("utf-8")
        subprocess.run([sys.executable, SYNC_SCRIPT, "--stdin"],
            input=text, timeout=10, capture_output=True)
    threading.Thread(target=_run, daemon=True).start()
```

**--stdin モードを使う理由**: veil-sync がサーバーの `/vocab/prompt` を HTTP で取得しようとすると、シングルスレッドの HTTPServer がデッドロックする。stdin 経由で渡すことで回避。

---

## 5. フロントエンド (main.js)

### 変換ロジック — 2パスアーキテクチャ

**問題**: "reflection branch" と "branch" を個別に登録した場合、"branch" のマッチが "reflection branch" の中に食い込む。

**解決**: 全登録語で領域を確保してから変換フィルタを適用する。

```
パス1（領域確保）: 全語彙エントリを長さ降順で処理
  → cat や翻訳の有無に関わらず全語が領域を主張
  → 先に確保した領域にはサブワードが入り込めない

パス2（変換フィルタ）: claimed 領域のうち TARGET_CATS かつ翻訳ありのみ置換
  → 翻訳なし・対象外の語が占めた領域は変換されず素通し
```

これにより「翻訳なし・cat=2 のエントリ」が**保護マーカー**として機能する。

### isProtected() — 誤マッチ防止

以下の文脈は変換対象から除外する。

```js
function isProtected(str, offset, matchLen) {
  const b = str[offset - 1] || '';
  const a = str[offset + matchLen] || '';
  if ('._-'.includes(b) || '._-'.includes(a)) return true;  // ファイル名・変数名
  const pre = str.slice(0, offset);
  if ((pre.match(/`/g) || []).length % 2 === 1) return true; // バッククォート内
  if ((pre.match(/"/g) || []).length % 2 === 1) return true; // ダブルクォート内
  if (b === '=') return true;                                  // = の直後
  const lineStart = str.lastIndexOf('\n', offset - 1) + 1;
  if (/\S+=/.test(str.slice(lineStart, offset))) return true; // key=value 行
  return false;
}
```

### ポップアップ — 変換候補選択

変換語（ハイライト）をクリックすると表示。

- p1 / p2 / p3 の候補をリスト表示（空欄のものは非表示）
- 別候補を選ぶと p1 に昇格し DB に自動保存（ローテーション）
- 「自分で設定」でインライン入力も可能
- 「元に戻す」で変換を取り消し（DB は変更しない）
- 「変換しない（対象外へ）」で cat=2 に変更し以後スキップ

### 未変換語リスト (renderUnmatched)

変換後テキストの非置換部分から英単語を抽出し、サイドバーに候補チップとして表示。

- 3文字以上の英単語が対象
- STOP_WORDS（約60語）と既登録語を除外
- 出現回数の多い順に最大24語表示
- チップをクリックすると登録フォームに自動入力 + DeepL 候補取得

### クイック登録

変換後テキストをマウスで選択すると `+ 登録` ボタンが浮き上がる。クリックで登録フォームに反映 + DeepL 候補取得。

### リアルタイム反映

```
語彙追加 / 削除
    ↓
loadVocab() が vocab[] を更新
    ↓
lineData が存在すれば reRenderCompare() を呼び出す
    ↓
buildSegments() を全行に再実行して変換後表示を即更新
```

---

## 6. veil-sync.py — 外部 AI ツールへの語彙同期

### 目的

CLAUDE.md, AGENTS.md, .cursorrules 等の AI ツール設定ファイルに VEIL の語彙ルールを埋め込む。語彙が変わるたびに自動で更新される。

### 設定ファイル

`~/.veil/targets.json` — 同期先ファイルパスのリスト。

### マーカー形式

```
<!-- ファイル種別が .md, .html 等の場合 -->
<!-- VEIL_START -->
以下の語彙ルールに従って出力してください：
...
<!-- VEIL_END -->

# ファイル種別が .yml, .yaml, .toml 等の場合
# VEIL_START
...
# VEIL_END
```

初回登録時はファイル末尾に追記。次回以降は既存ブロックを置換。

### コマンド一覧

```bash
python veil-sync.py --add <path>     # 同期先を登録（即時同期も実行）
python veil-sync.py --list           # 登録済み一覧
python veil-sync.py --remove <path>  # 登録を解除
python veil-sync.py                  # 手動で全ターゲットを同期
python veil-sync.py --stdin          # stdin から語彙テキストを受け取って同期（サーバー内部用）
```

---

## 7. install-startup.py — Windows 自動起動

Windows タスクスケジューラを使いログオン時に自動起動する。

```bash
python install-startup.py           # 登録
python install-startup.py --remove  # 解除
python install-startup.py --status  # 確認
```

- `pythonw.exe` が存在する場合はそちらを使用（コンソールウィンドウを非表示）
- タスク名: `VEIL Server`
- トリガー: ONLOGON
- 権限: LIMITED（管理者権限不要）

---

## 8. Export / Import

### Export

`vocab` 配列全体を JSON ファイルとしてダウンロード。

```
ファイル名: veil-vocab-YYYYMMDD.json
内容: [{id, o, p1, p2, p3, cat, n}, ...]
```

### Import

JSON ファイルを選択してアップロード。`o`（元語）と `p1`（日本語1）が必須。既存語は upsert（上書き更新）される。

---

## 9. UI レイアウト

```
┌────────────────────────────────────────────┐
│ VEIL  Vocabulary Engine for Individual...  │  ← header
├──────────────────────────────┬─────────────┤
│  input-area (textarea)       │  sidebar    │
├──────────────────────────────┤  ├ 語彙追加フォーム
│  col-headers [変換前 | 変換後]│  ├ 未変換語チップ
├──────────────────────────────┤  ├ 登録済み語彙リスト
│  compare-wrap                │  │  (検索/フィルタ)
│  ├ row: cell-in | cell-out   │  └ ...
│  └ ...                       │
├──────────────────────────────┴─────────────┤
│ [変換する] [登録する]  N語置き換え済み  [Export] [Import] │  ← footer
└────────────────────────────────────────────┘
```

**レイアウト実装**: CSS Grid `grid-template-columns: 1fr 240px; grid-template-rows: 36px 1fr 36px`

---

## 10. キーボードショートカット

| ショートカット    | 動作               |
|----------------|-------------------|
| Ctrl+Enter     | 変換実行           |
| Cmd+Enter (Mac)| 変換実行           |

---

## 11. 他 AI ツールとの統合

| ツール       | 設定ファイル                          | マーカー形式    |
|-------------|--------------------------------------|----------------|
| Claude Code | CLAUDE.md                            | HTML コメント  |
| Codex       | AGENTS.md                            | HTML コメント  |
| Cursor      | .cursorrules                         | HTML コメント  |
| GitHub Copilot | .github/copilot-instructions.md  | HTML コメント  |
| Gemini CLI  | GEMINI.md                            | HTML コメント  |
| Aider       | .aider.conf.yml                      | # コメント     |

`veil-sync.py --add <path>` で任意のファイルを登録できる。

---

## 12. 多言語対応（将来設計メモ）

現状は EN→JA 専用。将来的に EN→ZH や EN→KO を追加する場合の方針：

- DB に `lang_pair TEXT DEFAULT 'en-ja'` カラムを追加（`en-zh`, `en-ko` 等）
- `/vocab?lang=en-zh` のようにクエリパラメータでフィルタリング
- UI で言語ペアを切り替えるセレクタを追加
- DeepL の `target_lang` を切り替えるだけで翻訳候補生成は流用可能
- 既存データへの影響ゼロ（デフォルト値 `en-ja` を使えば後方互換）

---

## 13. セキュリティ・注意事項

- CORS: `Access-Control-Allow-Origin: *`（ローカルサーバーのみ公開を前提）
- ポート: 8080 固定
- `.env` ファイルは git 管理外（`.gitignore` で除外済み）
- `vocab.db` も git 管理外
