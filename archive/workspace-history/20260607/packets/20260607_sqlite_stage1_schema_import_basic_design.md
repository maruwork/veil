# Basic Design テンプレート準拠

**Project**: VEIL SQLite Stage 1  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. アーキテクチャ

Stage 1 は current Markdown runtime を残したまま、SQLite support route を追加する。

```text
[rules/*.md]
     |
     v
[markdown parser helper]
     |
     v
[sqlite init/import/readback module]
     |
     v
[smoke CLI]
```

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. 既存 script ごとに個別 import 実装 | 早い | parser drift が起きる | low |
| B. shared module を作って Stage 1 CLI から使う | 今後再利用できる | module 追加が必要 | high |

### Recommended Direction

- 推奨案:
  - shared module + Stage 1 CLI
- 採用理由:
  - Stage 2 で lint/normalize/audit 側へ再利用しやすい
- 却下した代替案:
  - 各 script の中に SQLite import を散らす

## 2. 技術選択

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Shared logic | `veil_rule_store.py` | schema / import / readback を集約できる | current scripts から段階利用する |
| CLI entry | `veil-db.py` | init/import/readback を 1 入口で扱える | Stage 1 では support route に留める |
| Data | SQLite `rules` table | canonical 候補の最小構造 | current runtime はまだ読まない |
| Smoke | workspace fixture + workspace DB | sandbox 内で検証可能 | home dir write を不要にする |

## 3. データ設計

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
| `rules` | Stage 1 canonical candidate rows | `id`, `term_original`, `term_normalized`, `preferred`, `preferred_alt_2`, `preferred_alt_3`, `level`, `status`, `category_hint`, `note`, `source_context`, `created_at`, `updated_at` | `term_original` not null, `preferred` not null, `level` not null |

補足:

- Stage 1 では unique 制約は conservative に置く
- import source file と source line を `source_context` に含めてもよい
- `status` は `active` 固定でよい

## 4. Interface 設計

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
| `init-db` | db path | schema 作成済み DB | write 失敗で non-zero |
| `import-rules` | db path, rules dir | imported row count, conflicts, warnings | rules dir 不在 or read 失敗で non-zero |
| `readback` | db path, optional level | rows / counts | DB 不在 or schema mismatch で non-zero |

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| current runtime は Stage 1 で切り替えない | accepted | non-breaking を優先 |
| shared module を先に作る | accepted | parser drift を防ぐ |

## 5. Security and Operations

- Authentication / authorization:
  - なし
- Secret handling:
  - なし
- Logging and monitoring:
  - CLI stdout / stderr と `workspace` evidence
- Backup / recovery:
  - import source は Markdown rules fixture
- Performance target:
  - local single-user CLI として十分軽いこと

## 6. 未決定事項

| Question | Owner | Due |
|---|---|---|
| `term_normalized` unique を Stage 1 で付けるか | implementer | 実装前 |
| `source_context` の粒度を file 名までにするか line まで持つか | implementer | 実装前 |
