# VEIL

**Vocabulary Engine for Individual Language**

AIの出力テキストを受け取り側の個人語彙に合わせて変換するエンジン。

---

## 起動

```bash
python app.py
```

ブラウザで `http://localhost:8080` を開く。

---

## ファイル構成

```
veil/
├── app.py       # バックエンド（Python標準ライブラリのみ・SQLite）
├── index.html   # UI
├── style.css    # スタイル
├── main.js      # フロントエンドロジック
├── vocab.db     # SQLite（初回起動時に自動生成）
└── README.md
```

---

## 依存関係

- Python 3.8以上（標準ライブラリのみ、pip install不要）
- Claude APIキー不要（変換候補の自動生成時のみapi.anthropic.comに接続）

---

## 主な機能

- AIテキストの貼り付け → 変換前／変換後の2列表示
- 変換語をハイライト表示
- ハイライトクリックでカタカナ／日本語1／日本語2／自分で設定の4候補を選択
- 未登録候補はClaude APIで自動生成して補完
- 選択した候補はSQLiteに自動保存（次回から即時表示）
- 登録済み語彙の検索・絞り込み
- 語彙の手動追加・削除

---

## スキップ判定

以下はスキップされ、置き換えされない。

- スネークケース（`workflow_aggregate_packet.py`）
- ハイフン区切りのファイル名（`task-pier-workflow-implementation.md`）
- バッククォート内のコード名
- `key=value`形式の値部分
- IDパターン（`BRANCH-046`、`PARENT-006`）

---

## 今後の対応事項

- エクスポート（JSON/CSV）
- インポート
- プロジェクト別辞書の切り替え
- 使用頻度順・登録順のソート切り替え
- カテゴリフィルタ
- 変換後テキストのコピーボタン
