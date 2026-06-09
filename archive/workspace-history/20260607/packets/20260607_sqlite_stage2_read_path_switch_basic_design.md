# Basic Design テンプレート準拠

**Project**: VEIL SQLite Stage 2  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. アーキテクチャ

Stage 2 は source selection を導入し、tool ごとに SQLite 読取へ段階移行する。

```text
[tool CLI]
   |
   +--> [--rules-dir] -> [Markdown parser]
   |
   +--> [--db] -> [SQLite readback helper]
```

切替順は次の通りとする。

1. `veil-profile-audit.py`
2. `veil-normalize.py`
3. `veil-lint.py`

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. lint から先に切替 | 効果が大きい | mainline 破壊リスクが高い | low |
| B. audit から先に切替 | support runtime で安全 | 直接の利用強制は弱い | high |
| C. normalize から先に切替 | capture 側に効く | audit より影響が広い | medium |

### Recommended Direction

- 推奨案:
  - `audit -> normalize -> lint`
- 採用理由:
  - support runtime から始める方が壊れにくい
- 却下した代替案:
  - lint first
  - all-at-once switch

## 2. 技術選択

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Source selection | `--db` optional argument | 明示的に SQLite source を選べる | default は current route を維持 |
| Shared DB read | `veil_rule_store.readback_rules()` | Stage 1 helper を再利用できる | summary contract 差分に注意 |
| First target | `veil-profile-audit.py` | support runtime で最小リスク | output 互換維持が必要 |

## 3. データ設計

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
| `rules` | audit source | `term_original`, `preferred`, `level`, `status`, `source_context` | Stage 1 schema をそのまま使う |

## 4. Interface 設計

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
| `veil-profile-audit.py --rules-dir` | rules dir | current summary/report | current behavior 維持 |
| `veil-profile-audit.py --db` | db path | db summary/report | DB 不在 / schema mismatch は error |
| `veil-profile-audit.py --json` | selected source | structured payload | source field を含める |

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| Stage 2 first wave は audit | accepted | support runtime first |
| default source はまだ rules-dir | accepted | current route 維持 |

## 5. Security and Operations

- Authentication / authorization:
  - なし
- Secret handling:
  - なし
- Logging and monitoring:
  - CLI stdout / stderr
- Backup / recovery:
  - rules-dir route remains available
- Performance target:
  - local audit が即時に終わること

## 6. 未決定事項

| Question | Owner | Due |
|---|---|---|
| `--db` と `--rules-dir` 同時指定時に error にするか `--db` 優先にするか | implementer | 第一波実装前 |
