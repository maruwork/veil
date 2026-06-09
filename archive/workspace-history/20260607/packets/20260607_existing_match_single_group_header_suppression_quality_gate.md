# Quality Gate

- `rtk python -B -m py_compile veil-normalize.py` が通る
- single-group smoke で `c.md:` header が出ない
- single-group smoke で existing-match item 行末に `| c.md` が付く
- `rtk rg` で code / README / design / skills が single-group suppress 契約でそろう
