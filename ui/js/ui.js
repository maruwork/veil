// イベントハンドラ・UI操作

let quickWord = '';

// ── 変換 ────────────────────────────────────────────────

async function convert() {
  const text = document.getElementById('inp').value;
  if (!text.trim()) return;

  const lines = text.split('\n');
  lineData = [];
  let total = 0;
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

  for (const [original] of Object.entries(countMap)) {
    incrementCount(original);
  }

  renderCompare();
  renderUnmatched();
  document.getElementById('rep-count').textContent = total ? t('repCount', total) : '';
  document.getElementById('summary').textContent = total ? t('replaced', total) : t('noReplace');
}

// ── ポップアップ ─────────────────────────────────────────

async function showPopup(el, li, si) {
  popTarget = { el, li, si };
  const seg = lineData[li].segs[si];
  let v = vocab.find(vv => vv.id === seg.vocabId);

  document.getElementById('pop-orig').textContent = `${t('popOrigLabel')}: ${seg.orig}`;

  const popup = document.getElementById('popup');
  const rect = el.getBoundingClientRect();
  popup.style.left = rect.left + 'px';
  popup.style.top = (rect.bottom + 4) + 'px';
  popup.classList.add('show');

  const items = document.getElementById('pop-items');
  if (v && (!v.p1 && !v.p2 && !v.p3)) {
    items.innerHTML = '';
    const loading = document.createElement('div');
    loading.className = 'pop-loading';
    loading.textContent = t('generating');
    items.appendChild(loading);
    try {
      const gen = await generateTranslation(seg.orig);
      const newP1 = v.p1 || gen.p1 || '';
      const newP2 = v.p2 || gen.p2 || '';
      if (newP1 !== v.p1 || newP2 !== v.p2) {
        const cat = v.cat === 1 ? inferCat(v.o) : v.cat;
        await upsertVocab(v.o, newP1, newP2, v.p3, cat);
        v = vocab.find(vv => vv.id === seg.vocabId);
      }
    } catch { /* DeepLキーなし or ネットワークエラー */ }
  }

  renderPopupItems(seg, v);
}

function closePopup() {
  document.getElementById('popup').classList.remove('show');
  popTarget = null;
}

async function selectCand(label) {
  if (!popTarget) return;
  const { el, li, si } = popTarget;
  lineData[li].segs[si].text = label;
  el.textContent = label;

  const seg = lineData[li].segs[si];
  const v = vocab.find(v => v.id === seg.vocabId);
  if (v && label !== v.p1) {
    const others = [v.p1, v.p2, v.p3].filter(p => p && p !== label).slice(0, 2);
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

async function popExclude() {
  if (!popTarget) return;
  const seg = lineData[popTarget.li].segs[popTarget.si];
  const v = vocab.find(v => v.id === seg.vocabId);
  if (v) await upsertVocab(v.o, v.p1, v.p2, v.p3, 2);
  closePopup();
}

// ── 語彙追加フォーム ──────────────────────────────────────

async function addVocabForm() {
  const o = document.getElementById('orig').value.trim();
  if (!o) return;
  const p1 = document.getElementById('pref1').value.trim();
  const p2 = document.getElementById('pref2').value.trim();
  const p3 = document.getElementById('pref3').value.trim();
  const cat = parseInt(document.getElementById('cat').value);
  await upsertVocab(o, p1, p2, p3, cat);
  ['orig', 'pref1', 'pref2', 'pref3'].forEach(id => document.getElementById(id).value = '');
  flashRegistered();
}

function flashRegistered() {
  ['btn-add', 'btn-add-footer'].forEach(id => {
    const btn = document.getElementById(id);
    if (!btn) return;
    const orig = btn.textContent;
    btn.textContent = t('flashDone');
    btn.classList.add('btn-flash');
    setTimeout(() => {
      btn.textContent = orig;
      btn.classList.remove('btn-flash');
    }, 1500);
  });
}

// ── 検索 ─────────────────────────────────────────────────

function onSearch(e) {
  renderList(e.target.value);
  document.getElementById('search-clear').style.display = e.target.value ? 'block' : 'none';
}

function clearSearch() {
  document.getElementById('search-input').value = '';
  document.getElementById('search-clear').style.display = 'none';
  renderList();
}

function toggleSort() {
  sortBy = sortBy === 'freq' ? 'id' : 'freq';
  document.getElementById('btn-sort').textContent = sortBy === 'freq' ? t('sortFreq') : t('sortId');
  renderList(document.getElementById('search-input').value);
}

function onCatFilter(val) {
  catFilter = parseInt(val);
  renderList(document.getElementById('search-input').value);
}

// ── エクスポート / インポート ──────────────────────────────

function exportVocab() {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const blob = new Blob([JSON.stringify(vocab, null, 2)], { type: 'application/json' });
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
  let entries;
  try {
    entries = JSON.parse(await file.text());
    if (!Array.isArray(entries)) throw new Error();
  } catch {
    alert(t('importError'));
    e.target.value = '';
    return;
  }
  for (const v of entries) {
    if (!v.o) continue;
    await upsertVocab(v.o, v.p1 || '', v.p2 || '', v.p3 || '', v.cat || 1);
  }
  e.target.value = '';
}

// ── クイック登録 ──────────────────────────────────────────

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

async function fillAddForm(word) {
  document.getElementById('orig').value = word;
  document.getElementById('cat').value = inferCat(word);
  document.getElementById('pref1').value = t('generating');
  document.getElementById('pref2').value = '';
  document.getElementById('pref3').value = '';
  try {
    const gen = await generateTranslation(word);
    document.getElementById('pref1').value = gen.p1 || '';
    document.getElementById('pref2').value = gen.p2 || '';
  } catch {
    document.getElementById('pref1').value = '';
  }
  document.getElementById('pref1').focus();
}

async function quickAddToForm() {
  if (!quickWord) return;
  const word = quickWord;
  hideQuickAdd();
  await fillAddForm(word);
}

// ── ロケール適用 ──────────────────────────────────────────

function applyLocale() {
  const setText = (id, key) => { const el = document.getElementById(id); if (el) el.textContent = t(key); };
  const setPh   = (id, key) => { const el = document.getElementById(id); if (el) el.placeholder  = t(key); };

  setText('header-subtitle', 'subtitle');
  setPh('inp', 'inputPh');
  document.getElementById('col-hd-in').textContent = t('colIn');
  const fc = (id, text) => { const n = document.getElementById(id); if (n?.firstChild) n.firstChild.textContent = text; };
  fc('col-hd-out', t('colOut') + ' ');

  setText('lbl-add', 'sectionAdd');
  setPh('orig',  'origPh');
  setPh('pref1', 'p1Ph');
  setPh('pref2', 'p2Ph');
  setPh('pref3', 'p3Ph');
  const catMap = { '1': 'cat1', '5': 'cat5', '6': 'cat6', '7': 'cat7' };
  Array.from(document.getElementById('cat').options).forEach(o => { if (catMap[o.value]) o.text = t(catMap[o.value]); });
  setText('btn-add', 'btnAdd');

  fc('lbl-unmatched', t('sectionUnmatched') + ' ');
  fc('lbl-vocab',     t('sectionVocab') + ' ');
  const cfMap = { '0': 'catAll', '1': 'cat1', '5': 'cat5', '6': 'cat6', '7': 'cat7', '-1': 'catExcluded' };
  Array.from(document.getElementById('cat-filter').options).forEach(o => { if (cfMap[o.value]) o.text = t(cfMap[o.value]); });
  setPh('search-input', 'searchPh');
  document.getElementById('btn-sort').textContent = sortBy === 'freq' ? t('sortFreq') : t('sortId');

  setText('btn-convert',    'btnConvert');
  setText('btn-add-footer', 'btnRegister');

  setText('pop-title',        'popTitle');
  setText('pop-revert-text',  'popRevert');
  setText('pop-exclude-text', 'popExclude');

  setText('btn-quick-add', 'quickAddBtn');
}

