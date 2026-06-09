# VEIL Consistency Recovery Basic Design

Project: VEIL current consistency recovery
Author: Codex
Date: 2026-06-07
Status: Draft

## 1. アーキテクチャ

今回の作業は新機能追加ではなく、current VEIL の説明面と governance 面を現行実装へ再整列する workstream とする。

```text
[runtime truth: app.py / veil-sync.py / ui/js/convert.js]
        ->
[current docs: README.md / docs/veil-design.md / docs/manual.html]
        ->
[governance docs: index/*]
        ->
[workspace design artifacts]
```

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. docs / governance を現行実装へ寄せる | 低リスク、早い、現行挙動を壊さない | 実装の癖も説明する必要がある | high |
| B. 実装を docs に合わせて直す | 仕様が美しくなる可能性がある | 影響が広い、意図せぬ回帰が起きうる | medium |

### Recommended Direction

- 推奨案:
  - A. docs / governance を現行実装へ寄せる
- 採用理由:
  - 今回の主題は obsolete 残骸除去と整合回復であり、新たな runtime redesign ではない
  - 既存挙動の破壊を避けられる
- 却下した代替案:
  - `p1` strict-only へ実装変更する案
  - `vocab.db` をただちに `shared/` へ移設する案

## 2. 技術選択

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Docs | Markdown / HTML manual 更新 | current VEIL の説明責務 | obsolete と historical を分ける |
| Governance | `index/` 更新 | authority を project-local に明示する | `common/` を scratch 化しない |
| Runtime | 最小変更または無変更 | 挙動破壊を避ける | docs と一致させる範囲に限定 |

## 3. データ設計

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
| `vocab.db` | Web UI 補助データ | `original`, `p1`, `p2`, `p3`, `cat` | 正本ではない |
| `~/.veil/rules/*.md` | 語彙ルール正本 | `- original -> preferred` | current canonical outside repo |
| `~/.veil/behavior.md` | behavior overlay | free-form text | `veil-sync.py` に統合される |

## 4. Interface 設計

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
| `veil-sync.py` | `rules/*.md`, `behavior.md`, target file list | target files with VEIL block | target missing は skip |
| `app.py` `/manual` | none | current manual HTML | file missing は 404 |
| `ui/js/convert.js` `buildSegments()` | current text + vocab entries | replacement segments | protected area は skip |

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| `vocab.db` を補助データとして扱う | proposed | current implementation に一致 |
| old multilingual links を active surface から除去する | proposed | user directive |
| `p1` fallback は docs 側で説明整合する | proposed | runtime redesign は別 task |

## 5. Security and Operations

- Authentication / authorization:
  - 変更なし
- Secret handling:
  - 変更なし
- Logging and monitoring:
  - 変更なし
- Backup / recovery:
  - `workspace/` に設計記録を残す
- Performance target:
  - 影響なし

## 6. 未決定事項

| Question | Owner | Due |
|---|---|---|
| 将来 `vocab.db` を `shared/` へ移すか | owner | later |
| `p1` strict-only へ runtime を寄せるか | owner | later |

