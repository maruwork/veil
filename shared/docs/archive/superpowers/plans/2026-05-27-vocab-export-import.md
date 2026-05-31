# Vocab Export/Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 語彙DBをJSONでエクスポート・インポートできるようにする

**Architecture:** クライアントサイドのみ。エクスポートはメモリ上の `vocab` 配列を Blob ダウンロード、インポートはファイル選択 → JSON パース → 既存の `upsertVocab()` を順次呼び出し。app.py への変更なし。

**Tech Stack:** Vanilla JS (Blob API, FileReader API), HTML5 file input

---

## ファイル構成

| ファイル | 変更内容 |
|---|---|
| `shared/main.js` | `exportVocab()`, `importVocab()`, `handleImportFile()` を追加 |
| `shared/index.html` | `.lbl-row` ラッパー + ↓↑ボタン + `<input type="file" hidden>` を追加 |
| `shared/style.css` | `.lbl-row` スタイルを追加 |
| `shared/app.py` | 変更なし |

---

### Task 1: main.js にエクスポート関数を追加

**Files:**
- Modify: `shared/main.js` — ファイル末尾に追加

- [ ] **Step 1: `exportVocab()` 関数を追加**

`main.js` の `// ── 初期化` セクションの直前に以下を挿入：

```js
// ── エクスポート / インポート ─────────────────────────
function exportVocab() {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const json = JSON.stringify(vocab, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `veil-vocab-${date}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function importVocab() {
  document.getElementById('import-file').click();
}

async function handleImportFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const text = await file.text();
  let entries;
  try {
    entries = JSON.parse(text);
    if (!Array.isArray(entries)) throw new Error();
  } catch {
    alert('JSONファイルが不正です');
    e.target.value = '';
    return;
  }
  for (const v of entries) {
    if (!v.o || !v.p1) continue;
    await upsertVocab(v.o, v.p1, v.p2 || '', v.p3 || '', v.cat || 1);
  }
  e.target.value = '';
}
```

- [ ] **Step 2: 動作確認（ブラウザコンソール）**

`python shared/app.py` でサーバー起動後、ブラウザのコンソールで：

```js
exportVocab()
```

`veil-vocab-YYYYMMDD.json` がダウンロードされ、中身が vocab 配列の JSON であることを確認。

---

### Task 2: index.html にUI要素を追加

**Files:**
- Modify: `shared/index.html`

- [ ] **Step 1: 「登録済み」ラベル行をラッパーで囲みボタンを追加**

`index.html` の以下の行を：

```html
  <div class="lbl">登録済み <span id="cnt" style="color:#555;"></span></div>
```

次のように置き換える：

```html
  <div class="lbl-row">
    <div class="lbl">登録済み <span id="cnt" style="color:#555;"></span></div>
    <div class="lbl-actions">
      <button class="btn-icon" onclick="exportVocab()" title="JSONエクスポート">↓</button>
      <button class="btn-icon" onclick="importVocab()" title="JSONインポート">↑</button>
    </div>
  </div>
  <input type="file" id="import-file" accept=".json" hidden onchange="handleImportFile(event)">
```

- [ ] **Step 2: ブラウザでUI確認**

「登録済み」ラベルの右に `↓` `↑` ボタンが表示されていることを確認。

---

### Task 3: style.css に `.lbl-row` スタイルを追加

**Files:**
- Modify: `shared/style.css`

- [ ] **Step 1: `.lbl-row` と `.btn-icon` スタイルを追加**

`style.css` の `.lbl {` ブロックの直前に以下を挿入：

```css
.lbl-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.lbl-row .lbl { margin-bottom: 0; }
.lbl-actions { display: flex; gap: 4px; }
.btn-icon {
  background: none;
  border: 1px solid #2a2a2a;
  color: var(--text4);
  font-size: 11px;
  padding: 1px 5px;
  cursor: pointer;
  line-height: 1.4;
  text-transform: none;
  letter-spacing: 0;
}
.btn-icon:hover { border-color: #555; color: var(--text2); }
```

- [ ] **Step 2: ブラウザでスタイル確認**

`↓` `↑` ボタンが小さく右寄せで表示され、ラベル行と高さが揃っていることを確認。

---

### Task 4: インポート動作確認

- [ ] **Step 1: エクスポートしたJSONをインポートする**

1. `↓` ボタンでJSONをダウンロード
2. ダウンロードしたJSONを `↑` ボタンで選択
3. 「登録済み」リストが変わらず正常に表示されることを確認（上書きなので件数変化なし）

- [ ] **Step 2: 不正なファイルでエラー確認**

テキストファイル（`.txt`）をインポートしようとした際に `alert('JSONファイルが不正です')` が表示されることを確認。

- [ ] **Step 3: 新語彙を追加してエクスポート → インポート確認**

1. 「語彙を追加」フォームで新語彙を登録（例: `deploy` → `デプロイ`）
2. `↓` でエクスポート
3. `×` で削除
4. `↑` でインポート → 語彙が復活することを確認

---

### Task 5: コミット

- [ ] **Step 1: 変更ファイルを確認**

```
git status
```

Expected: `shared/main.js`, `shared/index.html`, `shared/style.css` が変更済み

- [ ] **Step 2: コミット**

```bash
git add shared/main.js shared/index.html shared/style.css
git commit -m "feat: add JSON export/import for vocab DB"
```
