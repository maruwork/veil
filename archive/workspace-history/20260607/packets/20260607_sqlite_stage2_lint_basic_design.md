# Basic Design テンプレート準拠

**Project**: VEIL SQLite Stage 2 Lint Wave  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. アーキテクチャ

`veil-lint.py` は text masking と hit detection を維持し、rule loading だけ source selectable にする。

```text
[input text]
    |
    v
[mask protected segments]
    |
    v
[build patterns from rules-dir or db source]
    |
    v
[violations / warnings / clean]
```

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. lint 内で db query 直書き | 実装は早い | source helper が散る | medium |
| B. `veil_rule_store.py` に db rule loader を足す | source adaptation を再利用できる | helper 追加が必要 | high |

### Recommended Direction

- 推奨案:
  - shared db rule loader + lint source selection
- 採用理由:
  - audit / normalize と source selection pattern をそろえるため
- 却下した代替案:
  - lint file 内でのみ db row を整形する

## 2. 技術選択

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Source selection | `--db` optional argument | current route を壊さない | default は rules-dir |
| DB rule adaptation | `veil_rule_store` helper | level/preferred/source を shared 化できる | lint 用 field を満たす必要がある |
| Output | current text/json contract 維持 | user facing drift を減らす | source info は追加のみ |

## 3. データ設計

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
| `rules` | lint source | `term_original`, `preferred`, `level` | Stage 1 schema を利用 |

## 4. Interface 設計

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
| `veil-lint.py --rules-dir` | text + rules dir | current payload | current behavior 維持 |
| `veil-lint.py --db` | text + db path | same payload shape | db 不在 / schema mismatch は skip or error |
| JSON payload | source info + violations/warnings | current keys | key drift を起こさない |

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| lint wave は normalize の次 | accepted | Stage 2 order fixed |
| default source remains rules-dir | accepted | mainline safety |

## 5. Security and Operations

- Authentication / authorization:
  - なし
- Secret handling:
  - なし
- Logging and monitoring:
  - CLI output
- Backup / recovery:
  - rules-dir route remains
- Performance target:
  - local lint が即時に終わること

## 6. 未決定事項

| Question | Owner | Due |
|---|---|---|
| empty db を skip とするか clean とするか | implementer | 実装前 |
