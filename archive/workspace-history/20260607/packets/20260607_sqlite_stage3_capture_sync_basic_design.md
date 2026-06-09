# Basic Design

## 1. Decision

- canonical write route:
  - SQLite (`~/.veil/veil.db`)
- generated mirror:
  - `~/.veil/rules/*.md`
- sync source:
  - current phase では SQLite canonical を優先し、必要時に markdown mirror を再生成してから同期する

## 2. Runtime Shape

### 2.1 `veil_rule_store.py`

- DB helper を拡張する
- 追加する責務:
  - single rule upsert
  - db rows -> markdown mirror export

### 2.2 `veil-db.py`

- support CLI を拡張する
- 追加する subcommand:
  - `upsert-rule`
  - `export-mirror`

### 2.3 `veil-sync.py`

- DB が存在する current phase では DB canonical を優先する
- flow:
  1. DB canonical があれば markdown mirror を export
  2. mirror をまとめて base rules block を作る
  3. targets へ同期する
- DB が存在しない場合だけ rules-dir only fallback を許す

## 3. Data Contract

### 3.1 Upsert Input

- `term_original`
- `preferred`
- `level`
- optional:
  - `preferred_alt_2`
  - `preferred_alt_3`
  - `status`
  - `category_hint`
  - `note`
  - `source_context`

### 3.2 Mirror Export Rules

- file 振分:
  - `a-z` 始まりは `{letter}.md`
  - その他は `special.md`
- section:
  - `## 必須`
  - `## 推奨`
  - `## 観察`
- sort:
  - section 内は `term_normalized`, `term_original`, `id`

## 4. Skill Route

- current phase では candidate 決定後に
  1. `veil-db.py upsert-rule`
  2. `veil-db.py export-mirror`
  3. `veil-sync.py`
- file 直書きは旧 route として退ける

## 5. Rejected Alternatives

- capture skill だけを書き換え、runtime を変えない
  - rejected: canonical/write route が runtime で閉じない
- sync を DB 直読みにして markdown mirror を作らない
  - rejected: AI-readable mirror の current phase 契約を崩す

