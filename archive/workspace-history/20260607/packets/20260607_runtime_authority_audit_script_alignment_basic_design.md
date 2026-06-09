# VEIL 監査 script runtime authority 整合 基本設計

Status: Draft
Date: 2026-06-07

## 1. 目的

`veil-audit-db.py` を「補助スクリプトだが root runtime authority に属する」として明示し、読み落としを防ぐ。

## 2. 境界

- 対象:
  - `AGENTS.md`
  - `index/project-file-taxonomy.md`
  - `index/project-boundary-register.md`
  - `index/project-template-adoption-packet.md`
- 非対象:
  - script 本体
  - docs 本文の機能説明

## 3. 反映方針

- `veil-audit-db.py` は root runtime code として並べる
- helper DB 監査という役割を短く添える
- 既存の runtime 並び順に自然に差し込む
