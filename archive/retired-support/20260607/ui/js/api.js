// サーバーとの通信

function showError(msg) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 4000);
}

async function loadAudit() {
  const res = await fetch(BASE + '/vocab/audit');
  if (!res.ok) throw new Error(`audit ${res.status}`);
  const payload = await res.json();
  auditMap = Object.fromEntries((payload.results || []).map(item => [item.id, item]));
  auditSummary = payload.summary || { keep: 0, review: 0, 'drop-candidate': 0 };
}

async function loadVocab() {
  const res = await fetch(BASE + '/vocab');
  if (!res.ok) {
    showError(`語彙の読み込みに失敗しました (${res.status})`);
    return;
  }
  vocab = await res.json();
  try {
    await loadAudit();
  } catch (err) {
    auditMap = {};
    auditSummary = { keep: 0, review: 0, 'drop-candidate': 0 };
    showError(`棚卸し情報の読み込みに失敗しました`);
  }
  if (typeof reconcileCurrentReview === 'function') {
    reconcileCurrentReview();
  }
  renderList(document.getElementById('search-input')?.value || '');
  if (lineData.length) reRenderCompare();
}

async function upsertVocab(original, p1, p2, p3, cat) {
  const res = await fetch(BASE + '/vocab/upsert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original, p1, p2, p3, cat })
  });
  if (!res.ok) throw new Error(`upsert ${res.status}`);
  await loadVocab();
}

async function deleteVocab(id) {
  const res = await fetch(BASE + '/vocab/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id })
  });
  if (!res.ok) throw new Error(`delete ${res.status}`);
  await loadVocab();
}

async function deleteVocabBatch(ids) {
  const res = await fetch(BASE + '/vocab/delete-batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids })
  });
  if (!res.ok) throw new Error(`delete-batch ${res.status}`);
  const payload = await res.json();
  await loadVocab();
  return payload.deleted_count || 0;
}

async function incrementCount(original) {
  const res = await fetch(BASE + '/vocab/increment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original })
  });
  if (!res.ok) console.error(`incrementCount failed: ${res.status}`);
}
