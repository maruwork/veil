# active surface 軽量化 基本設計

## 1. 方針

- 「補助」と書いて残すのではなく、active surface から外す。
- current route, first read, authority, component table, design mainline から UI / helper DB 系を除く。
- 物理ファイルは触らず、current canonical だけを本線へ寄せる。

## 2. 具体化

### AGENTS.md

- `Current Authority` から `app.py`, `vocab.db`, `ui/`, `uijs/`, `js/` を落とす
- `VEIL Operation Loop` から `veil-audit-db.py`, `veil_audit_core.py`, `app.py`, `ui/` を落とす
- stop rule は UI を昇格させない規則だけ残す

### index/

- taxonomy / boundary / adoption packet から UI / helper DB 系を active mainline から外す
- `Read`, `Write`, `Current Shelf Classification`, `runtime-sensitive paths` も本線優先へ縮める

### canonical docs

- `README.md`
  - component table から `veil-audit-db.py`, `app.py` を外す
  - `Web UI` section を current path から外す
  - file tree から UI / app.py / manual を外す
- `docs/veil-design.md`
  - 設計方針から UI 行を外し、本線固定だけを残す
  - `app.py` 節と UI 監査表示節を current design から外す

## 3. 非変更

- 物理ファイル配置
- archive 化
