const BASE = '';
const TARGET_CATS = [1, 5, 6, 7];

let vocab = [];
let lineData = [];
let popTarget = null;
let sortBy = 'freq'; // 'freq' | 'id'
let catFilter = 0;   // 0=全て -1=対象外 1/5/6/7=指定カテゴリ

// ── DB操作 ──────────────────────────────────────────

async function loadVocab() {
  const res = await fetch(BASE + '/vocab');
  vocab = await res.json();
  renderList(document.getElementById('search-input')?.value || '');
  if (lineData.length) reRenderCompare();
}

function reRenderCompare() {
  let total = 0;
  lineData = lineData.map(({ orig }) => {
    const { segs, count } = buildSegments(orig);
    total += count;
    return { orig, segs };
  });
  renderCompare();
  document.getElementById('rep-count').textContent = total ? `— ${total}語` : '';
  document.getElementById('summary').textContent = total ? `${total}語置き換え済み` : '置き換えなし';
}

async function upsertVocab(original, p1, p2, p3, cat) {
  await fetch(BASE + '/vocab/upsert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original, p1, p2, p3, cat })
  });
  await loadVocab();
}

async function deleteVocab(id) {
  await fetch(BASE + '/vocab/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id })
  });
  await loadVocab();
}

async function incrementCount(original) {
  await fetch(BASE + '/vocab/increment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original })
  });
}

// ── カテゴリ推定 ─────────────────────────────────────

function inferCat(word) {
  if (/^[A-Z][A-Z0-9_]+$/.test(word)) return 2;    // ALL_CAPS → 固定値
  if (/^[A-Z]+-\d+$/.test(word)) return 4;           // LETTERS-000 → ID
  if (/[a-z][A-Z]|[A-Z]{2,}/.test(word)) return 5;  // 内部大文字 → 固有名詞
  return 1;
}

// ── 変換ロジック ─────────────────────────────────────

function isProtected(str, offset, matchLen) {
  const b = str[offset - 1] || '';
  const a = str[offset + matchLen] || '';
  if ('._-'.includes(b) || '._-'.includes(a)) return true;
  const pre = str.slice(0, offset);
  if ((pre.match(/`/g) || []).length % 2 === 1) return true;
  if ((pre.match(/"/g) || []).length % 2 === 1) return true;
  if (b === '=') return true;
  // key=value 形式の行：= の後に続く複数語も保護
  const lineStart = str.lastIndexOf('\n', offset - 1) + 1;
  if (/\S+=/.test(str.slice(lineStart, offset))) return true;
  return false;
}

function buildSegments(text) {
  // 全エントリを長さ降順で並べる（非TARGET_CATSも含む）
  const allSorted = [...vocab].sort((a, b) => b.o.length - a.o.length);

  // パス1: 全登録語で領域を確保（長い語優先）
  // 翻訳のない語・対象外カテゴリの語も領域を主張し、サブワードの誤マッチを防ぐ
  const claimed = [];
  allSorted.forEach(v => {
    const esc = v.o.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pat = new RegExp('(?<![A-Za-z0-9_.-])' + esc + '(?![A-Za-z0-9_.-])', 'gi');
    let m;
    while ((m = pat.exec(text)) !== null) {
      if (!isProtected(text, m.index, m[0].length)) {
        const ov = claimed.some(r => m.index < r.end && m.index + m[0].length > r.start);
        if (!ov) claimed.push({ start: m.index, end: m.index + m[0].length, orig: m[0], v });
      }
    }
  });

  // パス2: TARGET_CATSかつ翻訳あり の領域のみ置換
  const reps = claimed
    .filter(c => TARGET_CATS.includes(c.v.cat) && (c.v.p1 || c.v.p2 || c.v.p3))
    .sort((a, b) => a.start - b.start);

  const segs = [];
  let cur = 0;
  reps.forEach(r => {
    if (cur < r.start) segs.push({ text: text.slice(cur, r.start), isReplaced: false });
    segs.push({ text: r.v.p1 || r.v.p2 || r.v.p3, isReplaced: true, orig: r.orig, vocabId: r.v.id });
    cur = r.end;
  });
  if (cur < text.length) segs.push({ text: text.slice(cur), isReplaced: false });
  return { segs, count: reps.length };
}

async function convert() {
  const text = document.getElementById('inp').value;
  if (!text.trim()) return;

  const lines = text.split('\n');
  lineData = [];
  let total = 0;

  // use_countを更新
  const countMap = {};
  lines.forEach(line => {
    const { segs, count } = buildSegments(line);
    lineData.push({ orig: line, segs });
    total += count;
    segs.filter(s => s.isReplaced).forEach(s => {
      const v = vocab.find(v => v.id === s.vocabId);
      if (v) countMap[v.o] = (countMap[v.o] || 0) + 1;
    });
  });

  // use_countをサーバーに送信
  for (const [original] of Object.entries(countMap)) {
    incrementCount(original);
  }

  renderCompare();
  document.getElementById('rep-count').textContent = total ? `— ${total}語` : '';
  document.getElementById('summary').textContent = total ? `${total}語置き換え済み` : '置き換えなし';
}

// ── 描画 ─────────────────────────────────────────────

function renderCompare() {
  const wrap = document.getElementById('compare');
  wrap.innerHTML = '';
  lineData.forEach(({ orig, segs }, li) => {
    const row = document.createElement('div');
    row.className = 'row';

    const left = document.createElement('div');
    left.className = 'cell cell-in';
    left.textContent = orig || '\u00a0';

    const right = document.createElement('div');
    right.className = 'cell cell-out';

    if (!segs.length || (segs.length === 1 && !segs[0].isReplaced)) {
      right.textContent = segs[0]?.text || '\u00a0';
    } else {
      segs.forEach((seg, si) => {
        if (!seg.isReplaced) {
          right.appendChild(document.createTextNode(seg.text));
        } else {
          const span = document.createElement('span');
          span.className = 'hl';
          span.textContent = seg.text;
          span.title = `元: ${seg.orig}`;
          span.addEventListener('click', e => { e.stopPropagation(); showPopup(span, li, si); });
          right.appendChild(span);
        }
      });
    }

    row.appendChild(left);
    row.appendChild(right);
    wrap.appendChild(row);
  });
}

function renderList(filter = '') {
  let items = [...vocab];

  items.sort(sortBy === 'freq'
    ? (a, b) => b.n - a.n
    : (a, b) => a.id - b.id);

  if (catFilter === -1) {
    items = items.filter(v => !TARGET_CATS.includes(v.cat));
  } else if (catFilter > 0) {
    items = items.filter(v => v.cat === catFilter);
  }

  const filtered = filter
    ? items.filter(v =>
        v.o.toLowerCase().includes(filter.toLowerCase()) ||
        v.p1.toLowerCase().includes(filter.toLowerCase()))
    : items;

  document.getElementById('cnt').textContent = `(${filtered.length}/${vocab.length})`;
  const list = document.getElementById('vlist');

  if (!filter) {
    list.innerHTML = '<div class="vlist-empty">検索して絞り込み</div>';
    return;
  }

  list.innerHTML = '';
  filtered.forEach(v => {
    const isT = TARGET_CATS.includes(v.cat);
    const el = document.createElement('div');
    el.className = 'vi';
    el.style.opacity = isT ? '1' : '0.4';

    const vo = document.createElement('span');
    vo.className = 'vo'; vo.title = v.o; vo.textContent = v.o;

    const arrow = document.createElement('span');
    arrow.style.cssText = 'color:#555;font-size:10px;';
    arrow.textContent = '→';

    const vp = document.createElement('span');
    vp.className = 'vp'; vp.title = v.p1; vp.textContent = v.p1;

    const vc = document.createElement('span');
    vc.className = 'vc'; vc.textContent = v.n;

    const vd = document.createElement('button');
    vd.className = 'vd'; vd.textContent = '×';
    vd.onclick = () => delV(v.id);

    el.append(vo, arrow, vp, vc, vd);
    list.appendChild(el);
  });
}

function toggleSort() {
  sortBy = sortBy === 'freq' ? 'id' : 'freq';
  document.getElementById('btn-sort').textContent = sortBy === 'freq' ? '頻度' : '登録順';
  renderList(document.getElementById('search-input').value);
}

function onCatFilter(val) {
  catFilter = parseInt(val);
  renderList(document.getElementById('search-input').value);
}

// ── ポップアップ ─────────────────────────────────────

async function showPopup(el, li, si) {
  popTarget = { el, li, si };
  const seg = lineData[li].segs[si];
  let v = vocab.find(vv => vv.id === seg.vocabId);

  document.getElementById('pop-orig').textContent = `元: ${seg.orig}`;

  const popup = document.getElementById('popup');
  const rect = el.getBoundingClientRect();
  popup.style.left = rect.left + 'px';
  popup.style.top = (rect.bottom + 4) + 'px';
  popup.classList.add('show');

  const items = document.getElementById('pop-items');

  if (v && (!v.p1 || !v.p2)) {
    items.innerHTML = '<div class="pop-loading">生成中...</div>';
    try {
      const res = await fetch('/vocab/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word: seg.orig })
      });
      const gen = await res.json();
      const newP1 = v.p1 || gen.p1 || '';
      const newP2 = v.p2 || gen.p2 || '';
      const newP3 = v.p3;
      if (newP1 !== v.p1 || newP2 !== v.p2) {
        const cat = v.cat === 1 ? inferCat(v.o) : v.cat;
        await upsertVocab(v.o, newP1, newP2, newP3, cat);
        await loadVocab();
        v = vocab.find(vv => vv.id === seg.vocabId);
      }
    } catch (e) { /* キーなし or ネットワークエラー → スキップ */ }
  }

  renderPopupItems(seg, v);
}

function renderPopupItems(seg, v) {
  const cands = [
    { label: v?.p1 || '', badge: '日本語1' },
    { label: v?.p2 || '', badge: 'カタカナ' },
    { label: v?.p3 || '', badge: '日本語2' },
  ].filter(c => c.label);

  const items = document.getElementById('pop-items');
  items.innerHTML = '';

  cands.forEach(c => {
    const d = document.createElement('div');
    d.className = 'pop-item';
    const cur = c.label === seg.text;

    const lbl = document.createElement('span');
    lbl.style.flex = '1';
    if (cur) lbl.style.color = '#6db88a';
    lbl.textContent = c.label;

    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = c.badge;

    d.append(lbl, badge);
    if (cur) {
      const chk = document.createElement('span');
      chk.style.cssText = 'color:#6db88a;font-size:10px;';
      chk.textContent = '✓';
      d.appendChild(chk);
    }
    d.addEventListener('click', () => selectCand(c.label));
    items.appendChild(d);
  });

  const custom = document.createElement('div');
  custom.className = 'pop-item';

  const customBadge = document.createElement('span');
  customBadge.className = 'badge';
  customBadge.style.flex = '0 0 auto';
  customBadge.textContent = '自分で設定';

  const customInput = document.createElement('input');
  customInput.type = 'text';
  customInput.id = 'custom-input';
  customInput.placeholder = '入力して確定';
  customInput.style.cssText = 'flex:1;background:#181818;border:1px solid #333;color:#eee;font-family:monospace;font-size:12px;padding:3px 6px;outline:none;margin:0 4px;';
  customInput.addEventListener('click', e => e.stopPropagation());

  const customBtn = document.createElement('button');
  customBtn.textContent = '確定';
  customBtn.style.cssText = 'font-size:10px;padding:3px 8px;';
  customBtn.addEventListener('click', applyCustom);

  custom.append(customBadge, customInput, customBtn);
  items.appendChild(custom);
}

async function selectCand(label) {
  if (!popTarget) return;
  const { el, li, si } = popTarget;
  lineData[li].segs[si].text = label;
  el.textContent = label;

  const seg = lineData[li].segs[si];
  const v = vocab.find(v => v.id === seg.vocabId);
  if (v && label !== v.p1) {
    // 選択した語をp1に昇格、残りを順に詰める
    const others = [v.p1, v.p2, v.p3].filter(p => p && p !== label);
    await upsertVocab(v.o, label, others[0] || '', others[1] || '', v.cat);
  }
  closePopup();
}

function applyCustom() {
  const val = document.getElementById('custom-input')?.value.trim();
  if (!val || !popTarget) return;
  selectCand(val);
}

function popRevert() {
  if (!popTarget) return;
  const { li, si } = popTarget;
  const seg = lineData[li].segs[si];
  seg.text = seg.orig;
  seg.isReplaced = false;
  renderCompare();
  closePopup();
}

function closePopup() {
  document.getElementById('popup').classList.remove('show');
  popTarget = null;
}

// ── 語彙追加フォーム ──────────────────────────────────

async function addVocabForm() {
  const o = document.getElementById('orig').value.trim();
  const p1 = document.getElementById('pref1').value.trim();
  const p2 = document.getElementById('pref2').value.trim();
  const p3 = document.getElementById('pref3').value.trim();
  const cat = parseInt(document.getElementById('cat').value);
  if (!o) return;
  await upsertVocab(o, p1, p2, p3, cat);
  ['orig', 'pref1', 'pref2', 'pref3'].forEach(id => document.getElementById(id).value = '');
  flashRegistered();
}

function flashRegistered() {
  ['btn-add', 'btn-add-footer'].forEach(id => {
    const btn = document.getElementById(id);
    if (!btn) return;
    const orig = btn.textContent;
    btn.textContent = '✓ 登録済み';
    btn.style.borderColor = '#4a7c59';
    btn.style.color = '#8de0a8';
    setTimeout(() => {
      btn.textContent = orig;
      btn.style.borderColor = '';
      btn.style.color = '';
    }, 1500);
  });
}

async function delV(id) {
  await deleteVocab(id);
}

// ── 検索 ─────────────────────────────────────────────

function onSearch(e) {
  renderList(e.target.value);
  document.getElementById('search-clear').style.display = e.target.value ? 'block' : 'none';
}

function clearSearch() {
  document.getElementById('search-input').value = '';
  document.getElementById('search-clear').style.display = 'none';
  renderList();
}

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

// ── クイック登録 ─────────────────────────────────────

let quickWord = '';

function handleTextSelection() {
  const sel = window.getSelection();
  const text = sel?.toString().trim() || '';
  hideQuickAdd();
  if (!text || text.includes('\n') || text.length > 80) return;
  if (sel.rangeCount === 0) return;
  const range = sel.getRangeAt(0);
  if (!document.getElementById('compare').contains(range.commonAncestorContainer)) return;

  quickWord = text;
  const rect = range.getBoundingClientRect();
  const qa = document.getElementById('quick-add');
  document.querySelector('#quick-add .qa-word').textContent = text;
  const top = rect.top - 36;
  qa.style.left = rect.left + 'px';
  qa.style.top = (top < 4 ? rect.bottom + 4 : top) + 'px';
  qa.classList.add('show');
}

function hideQuickAdd() {
  document.getElementById('quick-add').classList.remove('show');
  quickWord = '';
}

async function quickAddToForm() {
  if (!quickWord) return;
  const word = quickWord;
  hideQuickAdd();
  document.getElementById('orig').value = word;
  document.getElementById('cat').value = inferCat(word);
  document.getElementById('pref1').value = '生成中...';
  document.getElementById('pref2').value = '';
  document.getElementById('pref3').value = '';

  try {
    const res = await fetch('/vocab/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word })
    });
    const gen = await res.json();
    document.getElementById('pref1').value = gen.p1 || '';
    document.getElementById('pref2').value = gen.p2 || '';
  } catch (e) {
    document.getElementById('pref1').value = '';
  }
  document.getElementById('pref1').focus();
}

// ── 初期化 ────────────────────────────────────────────

document.addEventListener('click', e => {
  closePopup();
  if (!document.getElementById('quick-add').contains(e.target)) hideQuickAdd();
});
document.addEventListener('DOMContentLoaded', () => {
  loadVocab();
  document.getElementById('search-clear').style.display = 'none';
  document.getElementById('orig').addEventListener('input', e => {
    document.getElementById('cat').value = inferCat(e.target.value.trim());
  });
  document.getElementById('compare').addEventListener('mouseup', handleTextSelection);
});
