// サーバーとの通信

async function loadVocab() {
  const res = await fetch(BASE + '/vocab?lang=' + currentLang);
  vocab = await res.json();
  renderList(document.getElementById('search-input')?.value || '');
  if (lineData.length) reRenderCompare();
}

async function upsertVocab(original, p1, p2, p3, cat) {
  await fetch(BASE + '/vocab/upsert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original, p1, p2, p3, cat, lang: currentLang })
  });
  await loadVocab();
}

async function deleteVocab(id) {
  await fetch(BASE + '/vocab/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, lang: currentLang })
  });
  await loadVocab();
}

async function incrementCount(original) {
  await fetch(BASE + '/vocab/increment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ original, lang: currentLang })
  });
}

async function generateTranslation(word) {
  try {
    const res = await fetch(BASE + '/vocab/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word, lang: currentLang })
    });
    return await res.json();
  } catch {
    return { p1: '', p2: '', p3: '' };
  }
}
