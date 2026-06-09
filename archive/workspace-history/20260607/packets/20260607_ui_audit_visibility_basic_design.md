# VEIL UI audit visibility 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 監査ロジックは shared helper に寄せて CLI と UI で共用する
- UI は「見る・絞る」までに留め、削除や更新は既存の delete / upsert 導線を使う

## 2. 実装方針

### 2.1 shared helper

- 新規 `veil-audit-core.py`
- `audit_rows()`
- `filter_results()`
- `VALID_STATUSES`
- 行動指針生成

`veil-audit-db.py` と `app.py` はこれを使う。

### 2.2 app API

- `GET /vocab/audit`
- レスポンス:
  - `summary`
  - `results`
- query:
  - `status=review`
  - `status=drop-candidate`

### 2.3 UI

- state
  - `auditMap`
  - `auditSummary`
  - `auditFilter`
- render
  - 語彙行へ status badge
  - tooltip に `次アクション` / `見直し焦点`
  - filter 反映
  - summary 反映
- html
  - audit summary 表示領域
  - audit filter select
- locale
  - status 名と audit filter 文言

## 3. 文書反映

- README
  - UI で audit status を見られること
- docs/veil-design.md
  - `/vocab/audit` を API 一覧へ追加
- docs/manual.html
  - 語彙一覧に audit badge / filter が出る説明を追加

## 4. 検証方針

- py_compile
- API smoke
- UI の簡易 smoke
- 文書整合確認
