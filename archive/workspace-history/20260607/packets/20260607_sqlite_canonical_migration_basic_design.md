# Basic Design テンプレート準拠

**Project**: VEIL SQLite Canonical Migration  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. アーキテクチャ

VEIL の mainline は、`SQLite 正本` と `Markdown 生成物` の 2 面に分ける。

```text
[capture / normalize / lint / audit]
                |
                v
        [SQLite canonical]
                |
                v
      [Markdown generated mirror]
                |
                v
     [AI instruction surfaces via sync]
```

この構成では、

- machine-readable authority は SQLite に一本化する
- AI に読ませる text surface は Markdown に残す
- delegated AI は file browse ではなく query / generated surface を使う

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. Markdown 正本継続 | 現在互換が高い | query / review / stats / queue に弱い | low |
| B. JSON 正本 | 構造化できる、読みやすい | 更新競合、検索、集計、将来拡張で弱い | medium |
| C. SQLite 正本 + Markdown 生成物 | query、集計、state、将来拡張に強い | 初回移行設計が必要 | high |

### Recommended Direction

- 推奨案:
  - `SQLite 正本 + Markdown 生成物`
- 採用理由:
  - VEIL の今後の課題が file browse ではなく queue / lint / audit / tuning 強化だから
- 却下した代替案:
  - Markdown 長期正本維持
  - JSON 単独正本

## 2. 技術選択

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Runtime | Python stdlib `sqlite3` | 追加依存なしで扱える | current scripts も Python 前提 |
| Data | `~/.veil/veil.db` | rules を 1 DB に集約できる | outside-workspace path への write は実装時 approval boundary に注意 |
| Generated Text | `~/.veil/rules/*.md` | AI に読ませる surface を維持できる | canonical ではなく generated と明示する |
| Migration | staged coexistence | mainline を壊さず切替できる | 一括置換は禁止 |

## 3. データ設計

Stage 1 minimum viable canonical は `rules` table を中心にする。

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
| `rules` | 語彙 rule 正本 | `id`, `term_original`, `term_normalized`, `preferred`, `preferred_alt_2`, `preferred_alt_3`, `level`, `status`, `category_hint`, `note`, `source_context`, `created_at`, `updated_at` | `level` は `required / recommended / observe` 相当、`term_original` は not null、`status` は active 前提 |

補足:

- Stage 1 では table を増やしすぎない
- `capture_count`、`lint_hit_count`、`review_flag`、`demotion_candidate` は future columns 候補に留める
- generated Markdown は DB から再生成可能な情報だけを持つ

## 4. Interface 設計

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
| Markdown import route | `~/.veil/rules/*.md` | SQLite `rules` rows | malformed line / duplicate authority は warning or stop を定義する |
| SQLite read route | DB path, query filters | normalized rows / lint matching rows / audit rows | DB 不在・schema mismatch は明示 error |
| Markdown generation route | SQLite rows | section-aware `*.md` files | DB はあるが生成不能なら sync 前に停止 |
| Sync route | generated `*.md` + target config | AI instruction surface 更新 | generated route 未完了なら sync しない |

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| SQLite を canonical にする | accepted | `workspace/20260607_sqlite_canonical_migration_decision_note.md` |
| Markdown は generated artifact にする | accepted | Stage 4 で docs authority も更新 |
| branch-first は current mainline から外す | accepted | `index/project-current-work.md` に反映済み |

## 5. Security and Operations

- Authentication / authorization:
  - なし。local-only DB を想定
- Secret handling:
  - なし
- Logging and monitoring:
  - Stage 1 は smoke evidence を `workspace/` に残す
- Backup / recovery:
  - 移行前 Markdown を source backup として残す
- Performance target:
  - local CLI read/write が即時に終わる範囲

## 6. 未決定事項

| Question | Owner | Due |
|---|---|---|
| DB path を `~/.veil/veil.db` に固定するか | owner | Stage 1 着手前 |
| generated Markdown を `veil-sync.py` 内で作るか、support script 分離にするか | implementer | Stage 1 packet 完了時 |
| `rules` table の unique 制約を `term_original` に置くか `term_normalized` に置くか | implementer | schema task 実装前 |
