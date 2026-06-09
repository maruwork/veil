# Basic Design テンプレート準拠

**Project**: VEIL SQLite Stage 2 Normalize Wave  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. アーキテクチャ

`veil-normalize.py` は candidate cluster logic を維持し、rule index loading だけ source selectable にする。

```text
[candidate lines]
      |
      v
[cluster_candidates]
      ^
      |
 [rules-dir loader] or [db loader]
```

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. normalize 内で db query 直書き | 早い | helper 再利用が弱い | medium |
| B. `veil_rule_store.py` に db index helper を足す | shared logic を寄せられる | helper 追加が必要 | high |

### Recommended Direction

- 推奨案:
  - shared helper 経由の db index load
- 採用理由:
  - future lint wave でも再利用しやすい
- 却下した代替案:
  - normalize file 内でのみ db row を整形する

## 2. 技術選択

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Source selection | `--db` optional argument | audit wave と揃う | default は rules-dir |
| DB row adaptation | `veil_rule_store` helper | row -> normalize index 変換を再利用 | `source_file` contract を保守的に保つ |
| Conflict handling | db source では empty conflict 可 | Stage 2 wave の主目的は source switch | full conflict parity は後続でもよい |

## 3. データ設計

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
| `rules` | normalize existing-match source | `term_original`, `term_normalized`, `preferred`, `level`, `source_context` | Stage 1 schema を利用 |

## 4. Interface 設計

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
| `veil-normalize.py --rules-dir` | candidates + rules dir | current payload | current behavior 維持 |
| `veil-normalize.py --db` | candidates + db path | same payload shape | db 不在 / schema mismatch は error |
| JSON payload | source info + conflicts + results | existing-match/new-candidate | key drift を起こさない |

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| normalize wave は audit の次 | accepted | Stage 2 order fixed |
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
  - local candidate normalization が即時に終わること

## 6. 未決定事項

| Question | Owner | Due |
|---|---|---|
| db source の conflict parity を Stage 2 wave で追うか後回しにするか | implementer | lint wave 前 |
