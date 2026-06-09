# VEIL seed 語彙整合 基本設計

Status: Draft
Date: 2026-06-07

## 1. 目的

新規 DB に最初から入る語彙を、今の VEIL 運用方針に沿った控えめな集合へ寄せる。

## 2. 境界

- 対象:
  - `app.py`
  - `docs/manual.html`
  - `docs/veil-design.md`
  - 必要なら `README.md`
- 非対象:
  - 既存 `vocab.db` の書き換え
  - `~/.veil/rules/`

## 3. 主要設計

### 3.1 seed は helper bootstrap として扱う

seed は helper DB の最初の足場にすぎず、広い辞書ではない。

### 3.2 phrase 優先・高確度優先

残す seed は、なるべく

- AI 運用でよく困る
- 意味が安定している
- 日本語化の方向が大きく揺れない
- phrase として使える

ものを優先する。

### 3.3 外す方向

- 単語単体で用途が広い
- `project 固有` すぎる
- 訳語が不自然
- UI の新しい慎重側判定と逆向き

## 4. 却下する案

- seed を完全に空にする
  - helper としての出発点が消えるため不採用
- 旧 seed をそのまま残して category だけ変える
  - 初期ノイズが減らないため不採用
