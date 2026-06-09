# Support Runtime Root Eviction Requirements

## Goal

root 直下の support runtime `.py` を退避し、root には current mainline runtime だけを残す。

## Scope

- `shared/tools/veil-profile-audit.py`
- `shared/tools/veil-profile-export.py`
- `shared/tools/veil-db.py`
- `shared/tools/veil_rule_store.py`
  を support shelf へ移す
- mainline import と smoke path を追従させる
- taxonomy / boundary / README / design の path を更新する

## Acceptance

1. root の `.py` は mainline と startup だけになる
2. support runtime は 1 shelf にまとまる
3. `veil-sync.py`、`veil-lint.py`、`veil-normalize.py` が新 path で動く
