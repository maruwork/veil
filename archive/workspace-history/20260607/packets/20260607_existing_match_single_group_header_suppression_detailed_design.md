# Detailed Design

## Code

1. `veil-normalize.py` の `existing_items` grouped branch で source file 種類数を調べる
2. 1 種類だけなら `c.md:` header を出さず、各 line 末尾へ `| c.md` を付ける
3. 複数種類の時だけ grouped header を維持する

## Surface

1. `README.md` の existing-match 説明を single-group suppress 契約へ更新する
2. `docs/veil-design.md` と 2 skills も同じ契約へそろえる
3. `index/project-current-work.md` を新 bundle へ切り替える
