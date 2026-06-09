# Normalize Single Word Precision Execution Report

## Summary

- `veil-normalize.py` の single-word lowercase 判定を保守的に改善した
- 名詞化 suffix を持つ単語は 1 回でも `説明語候補` へ寄る
- 同じ lowercase 単語が 2 回以上出る場合は `説明語候補` へ寄る
- 識別子候補、固有名候補の既存 path は維持した
- `README.md`、`docs/veil-design.md`、`index/project-current-work.md` を wave 2 に追従させた

## Runtime Change

### `veil-normalize.py`

- `LOWER_SINGLE_WORD_RE` を追加
- `NOUN_LIKE_SUFFIXES` を追加
- `classify_candidate_hint(term, occurrence_count=1)` に拡張
- `cluster_candidates(...)` から occurrence_count を渡すようにした

## Verification

### Syntax

```text
python -m py_compile veil-normalize.py
```

- result: PASS

### Heuristic Readback

代表語の確認:

- `verification` x1
  - `説明語候補`
  - `小文字単語で名詞化された一般語に見える`
- `normalization` x1
  - `説明語候補`
  - `小文字単語で名詞化された一般語に見える`
- `summary` x1
  - `境界が曖昧な候補`
- `summary` x2
  - `説明語候補`
  - `同じ小文字単語が複数回現れ、一般語として使われている可能性が高い`
- `GitHub` x1
  - `固有名候補`
- `status=close` x1
  - `識別子候補`

### Cluster Readback

`verification / normalization / summary / summary / close / close / GitHub / status=close` の cluster readback で:

- `normalization` と `verification` は `説明語候補 + 観察`
- `summary` と `close` は `説明語候補 + 推奨`
- `GitHub` は `固有名候補 + 観察`
- `status=close` は `識別子候補 + 観察`

## Residual

- wave 2 は閉じた
- 次の自然な tuning wave は `capture report` の軽量化、または `close` のような高頻度一般動詞をさらに保守的に扱う追加 tuning
