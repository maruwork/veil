// DOM描画

function fmtCount(n) {
  if (n >= 1000) return Math.round(n / 1000) + 'k';
  return String(n);
}

function reRenderCompare() {
  let total = 0;
  lineData = lineData.map(({ orig }) => {
    const { segs, count } = buildSegments(orig);
    total += count;
    return { orig, segs };
  });
  renderCompare();
  document.getElementById('rep-count').textContent = total ? t('repCount', total) : '';
  document.getElementById('summary').textContent = total ? t('replaced', total) : t('noReplace');
}

function renderCompare() {
  const wrap = document.getElementById('compare');
  wrap.innerHTML = '';
  lineData.forEach(({ orig, segs }, li) => {
    const row = document.createElement('div');
    row.className = 'row';

    const left = document.createElement('div');
    left.className = 'cell cell-in';
    left.textContent = orig || ' ';

    const right = document.createElement('div');
    right.className = 'cell cell-out';

    if (!segs.length || (segs.length === 1 && !segs[0].isReplaced)) {
      right.textContent = segs[0]?.text || ' ';
    } else {
      segs.forEach((seg, si) => {
        if (!seg.isReplaced) {
          right.appendChild(document.createTextNode(seg.text));
        } else {
          const span = document.createElement('span');
          span.className = 'hl';
          span.textContent = seg.text;
          span.title = t('origTooltip', seg.orig);
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
  list.innerHTML = '';

  filtered.slice(0, DISPLAY_LIMIT).forEach(v => {
    const isT = TARGET_CATS.includes(v.cat);
    const trans = v.p1 || v.p2 || v.p3;
    const noTrans = isT && !trans;
    const el = document.createElement('div');
    el.className = 'vi';
    el.classList.toggle('vi-inactive', !(isT && !noTrans));

    const vo = document.createElement('span');
    vo.className = 'vo'; vo.title = v.o; vo.textContent = v.o;

    const arrow = document.createElement('span');
    arrow.className = 'vi-arrow';
    arrow.textContent = '→';

    const vp = document.createElement('span');
    vp.className = 'vp';
    if (noTrans) {
      vp.classList.add('vp-empty');
      vp.textContent = t('noTrans');
    } else {
      vp.title = trans;
      vp.textContent = trans;
    }

    const vc = document.createElement('span');
    vc.className = 'vc'; vc.textContent = fmtCount(v.n);

    const vd = document.createElement('button');
    vd.className = 'vd'; vd.textContent = '×';
    vd.onclick = () => deleteVocab(v.id);

    el.append(vo, arrow, vp, vc, vd);
    list.appendChild(el);
  });

  if (filtered.length > DISPLAY_LIMIT) {
    const more = document.createElement('div');
    more.className = 'vocab-more';
    more.textContent = t('otherItems', filtered.length - DISPLAY_LIMIT);
    list.appendChild(more);
  }
}

function renderUnmatched() {
  const vocabSet = new Set(vocab.map(v => v.o.toLowerCase()));
  const wordCount = {};

  lineData.forEach(({ segs }) => {
    segs.filter(s => !s.isReplaced).forEach(s => {
      (s.text.match(/[A-Za-z]{3,}/g) || []).forEach(w => {
        const key = w.toLowerCase();
        if (!STOP_WORDS.has(key) && !vocabSet.has(key)) {
          wordCount[w] = (wordCount[w] || 0) + 1;
        }
      });
    });
  });

  const sorted = Object.entries(wordCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const section = document.getElementById('unmatched-section');
  const hrEl = document.getElementById('hr-unmatched');
  if (!sorted.length) {
    section.style.display = hrEl.style.display = 'none';
    return;
  }

  section.style.display = hrEl.style.display = '';
  document.getElementById('unmatched-cnt').textContent = `(${sorted.length})`;

  const list = document.getElementById('unmatched-list');
  list.innerHTML = '';
  sorted.forEach(([word, count]) => {
    const chip = document.createElement('div');
    chip.className = 'unmatched-chip';
    const wSpan = document.createElement('span');
    wSpan.textContent = word;
    const cSpan = document.createElement('span');
    cSpan.className = 'chip-cnt';
    cSpan.textContent = `×${count}`;
    chip.append(wSpan, cSpan);
    chip.addEventListener('click', () => fillAddForm(word));
    list.appendChild(chip);
  });
}

function renderPopupItems(seg, v) {
  const cands = [
    { label: v?.p1 || '', badge: t('p1Badge') },
    { label: v?.p2 || '', badge: t('p2Badge') },
    { label: v?.p3 || '', badge: t('p3Badge') },
  ].filter(c => c.label);

  const items = document.getElementById('pop-items');
  items.innerHTML = '';

  cands.forEach(c => {
    const d = document.createElement('div');
    d.className = 'pop-item';
    const cur = c.label === seg.text;

    const lbl = document.createElement('span');
    lbl.className = 'pop-cand-label' + (cur ? ' active' : '');
    lbl.textContent = c.label;

    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = c.badge;

    d.append(lbl, badge);
    if (cur) {
      const chk = document.createElement('span');
      chk.className = 'pop-cand-check';
      chk.textContent = '✓';
      d.appendChild(chk);
    }
    d.addEventListener('click', () => selectCand(c.label));
    items.appendChild(d);
  });

  const custom = document.createElement('div');
  custom.className = 'pop-item';

  const customBadge = document.createElement('span');
  customBadge.className = 'badge pop-custom-badge';
  customBadge.textContent = t('popCustom');

  const customInput = document.createElement('input');
  customInput.type = 'text';
  customInput.id = 'custom-input';
  customInput.placeholder = t('popCustomPh');
  customInput.addEventListener('click', e => e.stopPropagation());

  const customBtn = document.createElement('button');
  customBtn.className = 'pop-custom-btn';
  customBtn.textContent = t('popConfirm');
  customBtn.addEventListener('click', applyCustom);

  custom.append(customBadge, customInput, customBtn);
  items.appendChild(custom);
}

