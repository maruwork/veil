# VEIL Normalization And Merge Basic Design

## 1. Target Position

target loop:

`capture -> normalize/merge assist -> write -> sync -> lint -> report`

今回追加する helper は `capture` と `write` の間に入る。

## 2. Option Comparison

### Option A: `veil-capture` の文書だけで正規化を指示する

- 利点: code 追加なし
- 欠点: agent 任せで再現性が弱い

### Option B: read-only helper script を追加する

- 利点: 再現可能
- 利点: existing rule merge を機械的に出せる
- 欠点: runtime script が増える

### Recommended Direction

Option B を採る。揺れ問題は運用依存にすると再発しやすいため、normalize と existing match の最小機械化を行う。

## 3. Data Design

### Input

- newline-separated candidate terms
- optional bullet prefixes

### Rule Authority

- `~/.veil/rules/*.md`
- parse format: `- original → preferred`

### Normalization

- lowercase
- `_` / `-` -> space
- collapse spaces
- simple singularize per token

### Output Cluster

- normalized key
- input variants
- status: `existing-match` / `new-candidate`
- existing original / preferred if matched
- suggested target file if new

## 4. Interface

### CLI

- `python veil-normalize.py --stdin`
- `python veil-normalize.py --text "..."`
- `python veil-normalize.py <file>`
- `python veil-normalize.py --json`
- `python veil-normalize.py --rules-dir <dir>`

### Exit

- `0`: success
- `2`: usage/read error

This helper is advisory, not fail-close.

## 5. Operations

### Trigger

- `veil-capture` が候補一覧を出した直後
- rule write 前に variant collapse を見たい時

### Authority / Non-Authority

- authority: existing rules
- non-authority: helper output, drafts, DB

## 6. Deferred Work

- fuzzy similarity
- preferred translation suggestion
- direct integration into skill execution
