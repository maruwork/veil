# UI 分離 基本設計

## 1. 方針

- 文書上の序列を変える。
- UI を「存在はするが、正本運用や本線 runtime ではない」と明記する。
- `app.py` は runtime code ではあっても、mainline authority ではなく support runtime として扱う。

## 2. 変更方針

### AGENTS.md

- `First Read` から `app.py` を外す。
- `Current Authority` を
  - `mainline authority`
  - `support runtime`
  - `support UI assets`
  に分ける。
- stop rule に「UI を主対象へ昇格させない」を追加する。

### index/

- file taxonomy / boundary register / adoption packet で
  - `veil-sync.py`
  - `veil-lint.py`
  - `veil-normalize.py`
  - `veil-audit-db.py`
  - `veil_audit_core.py`
  - `install-startup.py`
  を本線または本線補助として整理する。
- `app.py` と `ui/` は support runtime / support UI へ寄せる。

### canonical docs

- `README.md` と `docs/veil-design.md` 冒頭で
  - VEIL は UI ツールではない
  - UI は helper DB を扱う補助面
  を短く強く書く。

## 3. 非変更

- Python / JS runtime の処理
- helper DB の監査ロジック
