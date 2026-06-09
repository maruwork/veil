# active surface 軽量化 実装計画

## 1. 編集対象

- `AGENTS.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`
- `README.md`
- `docs/veil-design.md`

## 2. 検証

- `rtk rg` で `app.py`, `ui/`, `manual.html`, `vocab.db`, `veil-audit-db.py`, `veil_audit_core.py` の current 記述がどこまで減ったか確認する
- 本線として `veil-capture`, `veil-normalize.py`, `veil-sync.py`, `veil-lint.py`, `~/.veil/rules/` が前面に出ていることを確認する
