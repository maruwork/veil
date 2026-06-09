# UI 分離 要件

## 1. 背景

- VEIL の本線は `~/.veil/rules/` を正本にした `capture -> normalize -> sync -> lint` の運用である。
- しかし現行の governance / canonical 文書では、`app.py` と `ui/` が本線 runtime と近い位置で見え、補助面が主対象に見えやすい。
- この曖昧さが UI への逸脱を誘発している。

## 2. 今回の対象

- `AGENTS.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`
- `README.md`
- `docs/veil-design.md`

## 3. 目的

- UI を VEIL の補助面として明確に分離する。
- 本線を `rules / capture / normalize / sync / lint` に固定して読めるようにする。
- delegated AI が UI を主対象に誤認しにくい入口へ直す。

## 4. 対象外

- UI 実装変更
- `app.py` の削除や移設
- `vocab.db` の廃止
- skill 本文の全面改稿

## 5. 完了条件

- `AGENTS.md` の first read / authority / stop rule で UI が補助面と分かる。
- `index/` の runtime authority で core path と UI support path の差が明文化される。
- `README` と `docs/veil-design.md` でも UI が補助面で、本線ではないことが読んですぐ分かる。
