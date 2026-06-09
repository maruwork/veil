# Quality Gate

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で retention がない候補は `選別/review/判別/priority/level: ...` になる
- text smoke で retention がある候補は 2 行構成を維持する
- text smoke で low-priority branch unchanged
- JSON smoke で key contract unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
