# Basic Design テンプレート

**使う場面**: 要求を受けて、構成と技術選択を決める時に使う。  
**差し替える所**: 層名、構成図、interface 名、関連 decision の管理方法。  
**書かないこと**: 実装タスクの細分化、今の状態の管理、project 固有の current 運用。

**Project**:
**Author**:
**Date**:
**Status**: Draft / Review / Approved

## 1. アーキテクチャ

system boundary、major components、runtime flow を書く。
task に落とせる粒度で boundary と flow が見えるように書く。
requirements の workflow と別の順番や別の主語が立つ場合は、そのまま進めず split gate として見直す。

```text
[client] -> [service] -> [storage]
```

### Option Comparison

| Option | Pros | Cons | Fit |
|---|---|---|---|
| A |  |  | high / medium / low |
| B |  |  | high / medium / low |

### Recommended Direction

- 推奨案:
- 採用理由:
- 却下した代替案:

後続 task が同じ前提で進めるよう、採用案と却下案の境界を曖昧にしない。
requirements と別の boundary や別の completion 主語になる場合は stop gate として扱う。

## 2. 技術選択

各選択が task spec の precondition / out-of-scope に渡るように書く。

| 層 | 選択 | 理由 | 制約 |
|---|---|---|---|
| Frontend |  |  |  |
| Backend |  |  |  |
| Data |  |  |  |
| Infrastructure |  |  |  |

## 3. データ設計

task / DB spec に渡す entity、field、制約を書く。

| Entity/Table | 目的 | 主要 field | 制約 |
|---|---|---|---|
|  |  |  |  |

## 4. Interface 設計

task spec の interface contract に渡せる input / output / error behavior を書く。

| Interface | Input | Output | Error Behavior |
|---|---|---|---|
|  |  |  |  |

task spec へ渡す時に input / output / error behavior のどれかが hidden なら、completion とせずに停止する。

### Related Decisions

| Decision | Status | Note |
|---|---|---|
| ADR / design note | draft / proposed / accepted |  |

## 5. Security and Operations

- Authentication / authorization:
- Secret handling:
- Logging and monitoring:
- Backup / recovery:
- Performance target:

## 6. 未決定事項

owner または due がない未決定事項は stop gate として扱う。
requirements と task spec の間で unresolved の owner や境界がずれる場合も stop gate として扱う。

| Question | Owner | Due |
|---|---|---|
|  |  |  |
