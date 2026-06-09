# VEIL Vocabulary Cleanup Requirements

## 1. Overview

### 目的

VEIL の active surface と tool-facing text に残っている英語混在メタ語を減らし、日本語優先の運用説明へ寄せる。

### 背景

- delegated AI 向け説明や VEIL helper の出力に `helper`, `normalize`, `lint`, `conflict` などの混在語が残っている
- これは VEIL の「英語・造語・揺れを減らす」という目的に反する

## 2. Scope

### In Scope

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `skills/claude-code/veil-capture.md`
- `skills/codex/veil-capture/SKILL.md`
- `veil-lint.py`
- `veil-normalize.py`

### Out of Scope

- `index/` の英語 governance 体系全体の全面翻訳
- 既存ファイル名やコマンド名そのものの改名

## 3. Success Criteria

- active surface の説明文から代表的な mixed jargon を除去する
- tool 出力も可能な範囲で日本語優先にする
- コマンド名だけは識別子として維持し、周辺説明を日本語化する

## 4. Replacement Direction

- helper -> 補助スクリプト / 補助出力
- normalize -> 正規化
- lint -> 検査
- conflict -> 競合
- reusable rule shelf -> 共通ルール棚
- current project state -> 現在のプロジェクト状態

## 5. Verification

- residue search
- `py_compile`
