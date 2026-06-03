// テキスト変換エンジン

function inferCat(word) {
  if (/^[A-Z][A-Z0-9_]+$/.test(word)) return 2;   // ALL_CAPS → 固定値
  if (/^[A-Z]+-\d+$/.test(word))      return 2;   // LETTERS-000 → 固定値
  if (/[a-z][A-Z]|[A-Z]{2,}/.test(word)) return 5; // 内部大文字 → 固有名詞
  return 1;
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
