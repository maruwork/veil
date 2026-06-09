# VEIL 監査 script runtime authority 整合 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

追加済みの `veil-audit-db.py` を、入口文書と `index/` の runtime authority へ正式に反映する。

## 2. 背景

- `veil-audit-db.py` は README と設計書には入っている
- しかし `AGENTS.md`、`index/project-file-taxonomy.md`、`index/project-boundary-register.md`、採用パケット側にはまだ未反映
- runtime surface の記述がずれると、次の delegated AI が読み落とす

## 3. 今回の範囲

- `AGENTS.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`

## 4. 今回の範囲外

- 新機能追加
- script 本体の変更

## 5. 機能要件

- `First Read` に `veil-audit-db.py` を加える
- `Current Authority` の runtime 一覧へ加える
- taxonomy / boundary / adoption packet の runtime 一覧へ加える

## 6. 完了条件

- README / 設計書 / AGENTS / index の runtime surface が `veil-audit-db.py` を含んで一致している
