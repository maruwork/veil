# Quality Gate

- `rtk python -m py_compile veil-normalize.py`
- text smoke で retention がある non-low-priority `new-candidate` が `選別/review/保留: ...` になる
- text smoke で retention がない場合は `選別/review: ...` が維持される
- text smoke で `判別` 独立行が維持される
- text smoke で low-priority branch unchanged
- JSON smoke で key contract unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
