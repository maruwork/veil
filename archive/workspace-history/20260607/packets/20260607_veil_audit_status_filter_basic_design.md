# VEIL audit status filter 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 判定結果の後段で絞る
- `audit_status()` のロジックは極力変えない
- 使い方は「まず drop-candidate、次に review」の順で読む運用に寄せる

## 2. 実装方針

### 2.1 CLI

- `argparse` に `--status` を `append` + `choices` で追加する
- choices は `keep`, `review`, `drop-candidate`

### 2.2 フィルタ

- `audit_rows()` 後に status 一致で絞る
- 指定なしなら全件維持

### 2.3 出力

- text: 絞り込み後の集計と一覧を表示
- json: `filters.statuses` を payload に含める

## 3. 文書反映

- README
  - helper DB 見直し時の使い方に filter 例を追加
- docs/veil-design.md
  - CLI 例へ `--status` を追加
- docs/manual.html
  - 監査補助の例に `drop-candidate` / `review` 絞り込みを追加

## 4. 検証方針

- py_compile
- 仮 DB で `drop-candidate` のみ / `review` のみ / 複数指定なし を確認
