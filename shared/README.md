# VEIL — shared/

このディレクトリが VEIL の実行ファイル一式です。

詳細なドキュメントはリポジトリルートの [README.md](../README.md) を参照してください。

---

## 起動

```bash
python app.py
```

ブラウザで `http://<ホスト名またはIPアドレス>:8080` を開く。
ローカルで起動した場合は `http://localhost:8080`。

---

## ファイル

| ファイル | 説明 |
|---------|------|
| `app.py` | バックエンド（HTTPServer + SQLite） |
| `index.html` | UI |
| `style.css` | スタイル |
| `main.js` | 初期化エントリーポイント |
| `locales.js` | UI文字列（多言語） |
| `js/state.js` | グローバル状態・定数 |
| `js/api.js` | バックエンド API 通信 |
| `js/convert.js` | テキスト変換エンジン（2パス） |
| `js/render.js` | DOM 描画 |
| `js/ui.js` | イベントハンドラ・UI操作 |
| `veil-sync.py` | 外部 AI ツール設定ファイルへの語彙同期 |
| `install-startup.py` | Windows ログイン時自動起動の登録 |
| `vocab.db` | SQLite DB（初回起動時に自動生成） |

---

## 依存関係

- Python 3.8 以上
- 標準ライブラリのみ（`pip install` 不要）
- DeepL 無料 API キー（任意 — 翻訳候補の自動生成用）
