# Basic Design テンプレート準拠

**Project**: VEIL SQLite Final Authority Transition  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. アーキテクチャ

この波では code path を変えず、authority wording を current phase に合わせる。

```text
[SQLite canonical route]
   - audit / normalize / lint can read

[rules-dir transition mirror]
   - capture / sync operational surface
   - AI-readable markdown surface
```

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A. 完全移行済みと書く | 単純 | 不正確 | low |
| B. Markdown canonical のまま書く | 互換は高い | 実装進展を隠す | low |
| C. transitional authority として書く | 正直で current state に合う | 少し長くなる | high |

### Recommended Direction

- 推奨案:
  - transitional authority wording
- 採用理由:
  - current implementation と docs のズレを最小にするため

## 2. 技術選択

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Canonical wording | SQLite route | Stage 2 実装進展に合う | full write migration は未完 |
| Operational wording | rules-dir transition mirror | capture/sync 未移行を表せる | generated artifact 完了とはまだ書かない |

## 3. データ設計

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
| `~/.veil/veil.db` / `rules` | canonical route | Stage 1 schema | read path switch 済み面が使う |
| `~/.veil/rules/*.md` | transition mirror | section-aware markdown | capture/sync の current surface |

## 4. Interface 設計

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
| docs authority wording | current implementation | accurate human explanation | hidden migration gap を残さない |

## 5. Security and Operations

- current phase explanation only

## 6. 未決定事項

| Question | Owner | Due |
|---|---|---|
| capture/sync write route をいつ SQLite 化するか | owner | next implementation wave |
