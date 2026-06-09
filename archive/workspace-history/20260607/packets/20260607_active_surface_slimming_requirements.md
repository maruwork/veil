# active surface 軽量化 要件

## 1. 背景

- VEIL の本線は `rules / capture / normalize / sync / lint` で完結する。
- `app.py`, `ui/`, `docs/manual.html`, `vocab.db`, `veil-audit-db.py`, `veil_audit_core.py` は UI / helper DB 系であり、本線理解の妨げになっている。
- 次に進む前に、active surface から UI 系を外し、全体を軽く見やすくする必要がある。

## 2. 今回の対象

- `AGENTS.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`
- `README.md`
- `docs/veil-design.md`

## 3. 方針

- UI / helper DB 系を current active surface から外す。
- 本線は `~/.veil/rules/`, `veil-capture`, `veil-normalize.py`, `veil-sync.py`, `veil-lint.py` に絞る。
- UI / helper DB 系の物理削除や archive 移動は今回は行わない。
- まず「読んだ時に存在しないものとして扱える」状態まで文書と governance を軽量化する。

## 4. 対象外

- `app.py`, `ui/`, `docs/manual.html` の物理削除
- archive 移動
- runtime code の削除

## 5. 完了条件

- `AGENTS.md` の first read / authority / operation loop に UI / helper DB 系が出ない。
- `index/` で UI / helper DB 系が active mainline として見えない。
- `README.md` と `docs/veil-design.md` が本線説明だけで読める。
- UI / helper DB の存在説明は current path から外れ、必要なら「現役外」と分かる最小限の扱いに留まる。
