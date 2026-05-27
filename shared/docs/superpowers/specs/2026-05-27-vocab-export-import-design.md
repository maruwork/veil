# VEIL エクスポート/インポート 設計書

**日付:** 2026-05-27  
**対象機能:** 語彙DBのJSONエクスポート・インポート  
**対象ファイル:** `shared/main.js`, `shared/index.html`, `shared/style.css`

---

## 前提確認

以下はすでに実装済みのため、本設計の対象外：

- SQLite化（`app.py` に完全実装済み）
- 検索機能（`main.js` の `onSearch()` / `clearSearch()` 実装済み）

---

## 実装方針：Approach A（クライアントサイド主体）

app.py への変更なし。既存の `/vocab` GET と `/vocab/upsert` POST を再利用する。

---

## エクスポート

### 処理フロー

1. `vocab`（すでにメモリ上に保持）を `JSON.stringify(vocab, null, 2)` で文字列化
2. `Blob` を生成し、`URL.createObjectURL` でダウンロードリンクを作成
3. ファイル名: `veil-vocab-YYYYMMDD.json`（実行日付を自動付与）
4. 一時 `<a>` 要素でクリックしてダウンロード → 要素を即削除

### 出力形式

```json
[
  { "id": 1, "o": "active", "p1": "有効", "p2": "アクティブ", "p3": "", "cat": 1, "n": 5 },
  ...
]
```

`/vocab` GETのレスポンス形式をそのまま出力する。追加変換なし。

---

## インポート

### 処理フロー

1. hidden `<input type="file" accept=".json">` をボタンクリックでトリガー
2. `FileReader.readAsText()` でファイル読み込み
3. `JSON.parse()` で配列に変換
4. 各エントリの `o`, `p1`, `p2`, `p3`, `cat` フィールドのみ使用して `upsertVocab()` を順次呼び出し（`id`, `n` は無視）
5. 全件完了後 `loadVocab()` でリスト再描画

### 重複時の挙動

インポート側で上書き（`/vocab/upsert` は `ON CONFLICT ... DO UPDATE` のため自動的に上書き）。

### エラーハンドリング

- JSONパース失敗時: `alert('JSONファイルが不正です')` を表示して中断
- 必須フィールド（`o`, `p1`）が空のエントリはスキップ

---

## UI配置

サイドバーの「登録済み」ラベル行に2ボタンを追加：

```
登録済み (22)         [↓] [↑]
──────────────────────────────
[検索...]          [×]
...リスト...
```

- `[↓]` = エクスポート（JSONダウンロード）
- `[↑]` = インポート（ファイル選択ダイアログを開く）
- ボタンはアイコン文字（↓↑）のみ。ツールチップ（`title`属性）で説明を付与

hidden の `<input type="file">` は DOM内に配置するが表示しない。

---

## 変更ファイルサマリー

| ファイル | 変更内容 |
|---|---|
| `main.js` | `exportVocab()`, `importVocab()` 関数を追加 |
| `index.html` | ↓↑ボタン2本 + `<input type="file" hidden>` を追加 |
| `style.css` | ボタンスタイル微調整（既存スタイルを流用） |
| `app.py` | **変更なし** |

---

## スコープ外（将来対応）

- インポート件数が数千件になった場合の一括エンドポイント（`POST /vocab/import`）
- CSV形式への対応
- プロジェクト別辞書の切り替えUI
