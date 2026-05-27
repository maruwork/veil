// 初期化

document.addEventListener('click', e => {
  closePopup();
  if (!document.getElementById('quick-add').contains(e.target)) hideQuickAdd();
});

document.addEventListener('DOMContentLoaded', () => {
  const langSel = document.getElementById('lang-select');
  if (langSel) langSel.value = currentLang;
  applyLocale();
  loadVocab();
  document.getElementById('search-clear').style.display = 'none';
  document.getElementById('orig').addEventListener('input', e => {
    document.getElementById('cat').value = inferCat(e.target.value.trim());
  });
  document.getElementById('compare').addEventListener('mouseup', handleTextSelection);
  document.getElementById('inp').addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); convert(); }
  });
});
