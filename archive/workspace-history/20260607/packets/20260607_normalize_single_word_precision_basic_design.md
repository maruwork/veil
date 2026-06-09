# Basic Design

## 1. Decision

- `classify_candidate_hint()` を全面変更せず、single-word lowercase path だけを保守的に拡張する

## 2. Heuristic

### 2.1 Positive Signals

- lowercase 単語
- 長さが一定以上
- 名詞化 suffix を持つ
  - `tion`, `sion`, `ment`, `ness`, `ity`, `ance`, `ence`, `ship`
- または occurrence_count が 2 以上

### 2.2 Conservative Guard

- `=`、path、拡張子、ticket id、ALL_CAPS、mixed-case は既存優先
- suffix を持たず occurrence_count も低い単語は従来どおり `境界が曖昧`

## 3. Output Contract

- existing JSON/text shape は維持
- `classification_hint` と `classification_reason` だけが改善される

## 4. Rejected Alternatives

- dictionary based classification
  - rejected: local rule が増えすぎる
- broad NLP scoring
  - rejected: VEIL の依存ゼロ方針に合わない

