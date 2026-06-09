# Basic Design

## 1. Decision

- `veil-lint.py` の core 判定は変えない
- 追加するのは report layer の fix guidance

## 2. Guidance Contract

### 2.1 Rule Level Guidance

各 result item に次を追加する。

- `suggested_preferred`
- `suggested_action`

`suggested_action` は基本的に:

- `"{original} を {preferred} へ直す"`

### 2.2 Hit Level Guidance

各 hit に次を追加する。

- `suggested_replacement`
- `suggested_line_preview`

`suggested_line_preview` は、line 全体を無理に自動置換せず、最初の `match` を `preferred` へ置き換えた preview とする。

## 3. Text Output

- item line:
  - `- [必須] current state -> 今の状態 ...`
- follow line:
  - `  直し方: current state を 今の状態 へ直す`
- first preview line:
  - `  置換例: ...`

## 4. JSON Output

- top-level status は維持
- each item:
  - `suggested_preferred`
  - `suggested_action`
- each hit:
  - `suggested_replacement`
  - `suggested_line_preview`

## 5. Rejected Alternatives

- 自動修正そのものを入れる
  - rejected: まずは gate の直しやすさ改善が先
- normalize と lint を同時に再設計する
  - rejected: scope が広がりすぎる

