# Support Runtime Root Eviction Basic Design

## Placement

- existing shelf:
  - `shared/tools/`

## Move Set

- `shared/tools/veil-profile-audit.py`
- `shared/tools/veil-profile-export.py`
- `shared/tools/veil-db.py`
- `shared/tools/veil_rule_store.py`

## Keep In Root

- `veil-sync.py`
- `veil-lint.py`
- `veil-normalize.py`
- `install-startup.py`

## Compatibility

- mainline runtime は `shared/tools/` 配下の helper を import する
- smoke と docs は new path を参照する
