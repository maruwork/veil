# Quality Gate

- `rtk python -m py_compile veil-normalize.py`
- text smoke で non-low-priority `new-candidate` が `選別/review: ... | ... | ...` になる
- text smoke で `判別` 独立行が維持される
- text smoke で low-priority branch unchanged
- JSON smoke で key contract unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
