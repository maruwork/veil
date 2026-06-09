// DOM描画

function fmtCount(n) {
  if (n >= 1000) return Math.round(n / 1000) + 'k';
  return String(n);
}

function auditLabel(status) {
  if (status === 'keep') return t('auditKeep');
  if (status === 'review') return t('auditReview');
  if (status === 'drop-candidate') return t('auditDrop');
  return '';
}

function auditTooltip(audit) {
  if (!audit) return '';
  const parts = [
    `監査: ${auditLabel(audit.status)}`,
    `次: ${audit.suggested_action}`,
  ];
  if (audit.review_focus?.length) parts.push(`焦点: ${audit.review_focus.join(' / ')}`);
  if (audit.reasons?.length) parts.push(`理由: ${audit.reasons.join(' / ')}`);
  return parts.join('\n');
}

function auditInlineHint(audit) {
  if (!audit || audit.status === 'keep') return '';
  if (audit.status === 'drop-candidate') {
    return audit.review_focus?.[0] || audit.suggested_action || '';
  }
  if (audit.status === 'review') {
    return (audit.review_focus || []).slice(0, 2).join(' / ');
  }
  return '';
}

function renderAuditSummary() {
  const el = document.getElementById('audit-summary');
  if (!el) return;
  const keep = auditSummary.keep || 0;
  const review = auditSummary.review || 0;
  const drop = auditSummary['drop-candidate'] || 0;
  const total = keep + review + drop;
  el.textContent = total ? t('auditSummary', keep, review, drop) : t('auditNone');
  const reviewBtn = document.getElementById('btn-review-next');
  if (reviewBtn) {
    reviewBtn.textContent = t('reviewNext', review);
    reviewBtn.disabled = review === 0;
    reviewBtn.title = t('reviewNextTitle', review);
  }
  const bulk = document.getElementById('btn-drop-bulk');
  if (bulk) {
    bulk.textContent = t('bulkDrop', drop);
    bulk.disabled = drop === 0;
    bulk.title = drop ? t('bulkDropConfirm', drop, t('auditDrop')) : t('bulkDrop', drop);
  }
}

function reRenderCompare() {
  let total = 0;
  lineData = lineData.map(({ orig }) => {
    const { segs, count } = buildSegments(orig);
    total += count;
    return { orig, segs };
  });
  renderCompare();
  renderUnmatched();
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
  renderAuditSummary();
  let items = [...vocab];

  const auditPriority = { 'drop-candidate': 0, review: 1, keep: 2 };
  items.sort((a, b) => {
    if (sortBy === 'freq') return b.n - a.n;
    if (sortBy === 'id') return a.id - b.id;
    const aAudit = auditMap[a.id]?.status;
    const bAudit = auditMap[b.id]?.status;
    const ap = aAudit in auditPriority ? auditPriority[aAudit] : 3;
    const bp = bAudit in auditPriority ? auditPriority[bAudit] : 3;
    if (ap !== bp) return ap - bp;
    if (a.n !== b.n) return a.n - b.n;
    return a.id - b.id;
  });

  if (catFilter === -1) {
    items = items.filter(v => !TARGET_CATS.includes(v.cat));
  } else if (catFilter > 0) {
    items = items.filter(v => v.cat === catFilter);
  }
  if (auditFilter !== 'all') {
    items = items.filter(v => auditMap[v.id]?.status === auditFilter);
  }

  const filtered = filter
    ? items.filter(v => {
        const q = filter.toLowerCase();
        return v.o.toLowerCase().includes(q) ||
               (v.p1 || '').toLowerCase().includes(q) ||
               (v.p2 || '').toLowerCase().includes(q) ||
               (v.p3 || '').toLowerCase().includes(q);
      })
    : items;

  document.getElementById('cnt').textContent = `(${filtered.length}/${vocab.length})`;
  const list = document.getElementById('vlist');
  list.innerHTML = '';

  filtered.slice(0, DISPLAY_LIMIT).forEach(v => {
    const isT = TARGET_CATS.includes(v.cat);
    const trans = v.p1 || v.p2 || v.p3;
    const noTrans = isT && !trans;
    const audit = auditMap[v.id];
    const el = document.createElement('div');
    el.className = 'vi';
    el.classList.toggle('vi-inactive', !(isT && !noTrans));
    el.classList.toggle('vi-current-review', currentReviewId === v.id);

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

    el.append(vo, arrow, vp);
    if (audit) {
      const ab = document.createElement('span');
      ab.className = `audit-badge audit-${audit.status}`;
      ab.textContent = auditLabel(audit.status);
      ab.title = auditTooltip(audit);
      el.appendChild(ab);
    }
    el.append(vc, vd);

    const hint = auditInlineHint(audit);
    if (hint) {
      const ah = document.createElement('div');
      ah.className = `audit-hint audit-hint-${audit.status}`;
      ah.textContent = hint;
      ah.title = auditTooltip(audit);
      el.appendChild(ah);
    }
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
