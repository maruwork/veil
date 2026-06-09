# VEIL Operation Loop Hardening Basic Design

## 1. Architecture

### Current Loop

`capture -> rules write -> sync`

問題は、sync 後に「AI 出力が本当に語彙ルールを守ったか」を見る検査面が存在しないこと。

### Target Loop

`capture -> rules write -> sync -> lint -> report`

- `veil-capture`
  - 候補抽出
  - 正規化
  - 候補決定
  - 既存照合
  - `~/.veil/rules/` 書き込み
  - `veil-sync.py` 実行
- `veil-lint.py`
  - 最終 prose を `~/.veil/rules/` に照らして検査
  - 登録済み原語が残っていれば fail-close

## 2. Option Comparison

### Option A: `veil-sync.py` に lint 機能を混ぜる

- 利点: script 数が増えない
- 欠点: sync と verify の責務が混ざる

### Option B: `veil-lint.py` を別 script として追加する

- 利点: phase 分離が明確
- 利点: `common` の verify phase に直接対応しやすい
- 欠点: runtime script が 1 つ増える

### Recommended Direction

Option B を採る。VEIL の弱点は「同期できるのに使われない」ことであり、これは sync ではなく verify の問題だからである。

## 3. Data Design

### Authority

- 読み authority: `~/.veil/rules/*.md`
- 非 authority: `vocab.db`, `workspace/`, AI の一時出力

### Rule Parse

- 入力形式: `- original → preferred`
- 許容揺れ:
  - `->`
  - `→`
  - preferred 側の候補列挙
- lint は preferred の先頭要素だけを推奨語として使う

## 4. Interface Design

### CLI

- `python veil-lint.py <file>`
- `python veil-lint.py --stdin`
- `python veil-lint.py --text "<text>"`
- `python veil-lint.py --json`

### Exit Codes

- `0`: clean または lint 対象 rule なし
- `1`: violation あり
- `2`: usage / read error

### Output

- text mode:
  - summary
  - rule ごとの hit count
  - line number
  - suggested preferred
- json mode:
  - machine-readable result

## 5. Protection Rules

- fenced code block は検査対象外
- inline code は検査対象外
- prose は検査対象

この保護は「コードや path の英語表記まで違反扱いしない」ための最小保護である。

## 6. Operations Design

### Trigger

- VEIL 語彙を守るべき日本語 prose を返す前
- 特に capture / sync 後の closing report、設計説明、変更報告

### Fail-Close

- lint violation が出たら、そのまま完了扱いしない
- prose を直して再 lint する
- 原語を意図的に残す必要がある場合だけ説明付きで許容する

### Deferred Work

- normalize/merge 支援は次 wave
- capture trigger 自動化も次 wave
