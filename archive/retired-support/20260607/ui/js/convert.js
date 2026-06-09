// テキスト変換エンジン

function inferCat(word) {
  const trimmed = (word || '').trim();
  if (!trimmed) return 7;

  if (trimmed.includes('=')) return 2;                    // key=value
  if (/[\\/]/.test(trimmed)) return 2;                    // path
  if (/\.[A-Za-z0-9]{1,8}$/.test(trimmed)) return 2;      // file-like
  if (/^[A-Z]+-\d+$/.test(trimmed)) return 2;             // LETTERS-000
  if (/^[A-Z0-9_]+$/.test(trimmed)) return 2;             // ALL_CAPS / UPPER_CASE
  if (/[A-Z]/.test(trimmed) && /[a-z]/.test(trimmed)) return 5; // mixed case

  const lowered = trimmed.replace(/[\-_]+/g, ' ').toLowerCase().trim();
  if (/^[a-z][a-z0-9 ]*$/.test(lowered)) {
    if (/[-_]/.test(trimmed)) return 7;                   // close-ish / current_state
    if (trimmed.includes(' ')) return 1;                  // lower phrase
    return 7;                                             // single word is cautious
  }
  return 7;
}

function isProtected(str, offset, matchLen) {
  const b = str[offset - 1] || '';
  const a = str[offset + matchLen] || '';
  if ('._-'.includes(b) || '._-'.includes(a)) return true;
  const pre = str.slice(0, offset);
  if ((pre.match(/`/g) || []).length % 2 === 1) return true;
  if ((pre.match(/"/g) || []).length % 2 === 1) return true;
  if (b === '=') return true;
  const lineStart = str.lastIndexOf('\n', offset - 1) + 1;
  if (/\S+=/.test(str.slice(lineStart, offset))) return true;
  return false;
}

function buildSegments(text) {
  // パス1: 全登録語で領域を確保（長さ降順・複合フレーズ優先）
  const allSorted = [...vocab].sort((a, b) => b.o.length - a.o.length);
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

  // パス2: TARGET_CATS かつ翻訳ありの領域のみ置換
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
