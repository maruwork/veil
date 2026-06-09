# Project File Taxonomy Template

**使う場面**: file type ごとの置き場を決める時に使う。  
**差し替える所**: 棚名、file type 名、例示 path、例外の扱い。  
**書かないこと**: 日々の current 管理、実装 task の細部、project 固有の current 正本再定義。

> **用途**:
> project 固有の file / folder 構成を「file type -> shelf」の matrix として固定するための reusable template。
> source-project 固有の棚名は持ち込まず、どの project でも最初に棚を決められる最小構成にする。

**role**: placement matrix — file type → shelf の対応を埋める
**project_id**: `project_xxx`
**status**: Draft / Approved
**companion rulebook**: [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md) — shelf class 定義・workspace rules・cleanup procedure
**companion policies**:
- `../policies/entry-guide-reference-separation-policy.md`
- `../policies/file-operation-policy.md`
- `../policies/naming-and-shelf-policy.md`

---

## 1. Purpose

- file を作る前に shelf を決める
- current canonical / support / generated / archive を混線させない
- repo が成長しても dumping ground を作らない

この template は `file type をどこへ置くか` を決めるためのものであり、

- 棚そのものが今の正本かどうか
- workspace / generated / archive の retention rule
- project 全体の入口や読む順

を単独で確定する文書ではない。

## 2. Entry Rule

- 初見の reader / agent が最初に読む入口を 1 つ決める
  - `{example only: README.md / index.md / docs/README.md}`
- entry file は「何を見る project か」「今どこを見るか」「正本はどこか」「どの guide に進むか」だけを答える薄い surface に保つ
- taxonomy は current work board ではなく placement matrix だと明記する
- front current surface を最小セットで決める
  - `{example only: README.md -> current-overview.md -> execution-board.md}`

## 2.1 Entry / Guide / Reference Split

- entry / guide / reference の 3 役を分ける
- guide は 3 本までを原則とする
  - `{example only: guide-first-read.md / guide-current-work.md / guide-runtime.md}`
- reference shelf には inventory / generated index / backlog catalog を置く
- reference file には `current authoritative source ではない` 注記と current への戻り先を必ず書く
- README が長いだけで機械的に割らず、role conflict がある時だけ分離する

## 3. Placement Matrix

| file type | canonical shelf | examples | notes / enforcement |
|---|---|---|---|
| `current canonical docs` | `{path}` | `{files}` | `{notes}` |
| `governance / policy` | `{path}` | `{files}` | `{notes}` |
| `design / architecture` | `{path}` | `{files}` | `{notes}` |
| `task / work tracking` | `{path}` | `{files}` | `{notes}` |
| `runtime / tool code` | `{path}` | `{files}` | `{notes}` |
| `library / shared code` | `{path}` | `{files}` | `{notes}` |
| `tests` | `{path}` | `{files}` | `{notes}` |
| `config / schema` | `{path}` | `{files}` | `{notes}` |
| `templates / reusable assets` | `{path}` | `{files}` | `{notes}` |
| `workspace / scratch` | `{path}` | `{files}` | `{notes}` |
| `generated reports` | `{path}` | `{files}` | `{notes}` |
| `archive / historical` | `{path}` | `{files}` | `{notes}` |
| `entry / guide surface` | `{path}` | `{files}` | `{single entry / guide max 3 / no inventory}` |
| `reference shelf` | `{path}` | `{files}` | `{non-authority note / redirect to current canonical}` |
| `hidden active tools / ignored assets` | `{path}` | `{files}` | `{manifest / visibility rule}` |
| `visible support document` | `{path}` | `{files}` | `{non-authority note / redirect to current surface}` |
| `runtime / agent residue` | `{path}` | `{files}` | `{cleanup or retention rule}` |
| `reserved-empty shelf` | `{path}` | `{files}` | `{why it exists / no ad hoc write}` |
| `repo-external intake` | `{path or none}` | `{files}` | `{notes}` |

## 4. Placement Decision Order

1. 既存 matrix に該当する row があるか確認する
2. 既存 shelf で role を説明できるなら、新しい folder を作らない
3. 該当 row がない場合だけ、新しい file type を追加する
4. 暫定置きが必要なら declared workspace を使う
5. scratch を canonical へ昇格する時は review と placement decision を通す

## 5. Canonical Separation Rule

shelf class の定義は [`project-structure-governance-starter-pack.md`（rulebook）cleanup procedure 章](./project-structure-governance-starter-pack.md) を正本とする。

本 taxonomy では次の 5 区分を少なくとも確保する。

- current canonical
- support
- generated
- historical
- external intake

同じ意味の file を複数 shelf に散在させない。

front current surface と visible support document は分ける。

- front current surface
  - current progress / active branch / completion posture を最初に読む面
- visible support document
  - file picker / docs root で目立つが、current progress の正本ではない補助文書

## 6. Root Rule

- root に置いてよい file を明示する
- root exception は最小限にする
- 新規 root file は原則禁止にする
- root や docs root で目立つ support document は、front current surface に昇格させない

## 7. Workspace Rule

- active workspace は 1 つに寄せる
- generated output は canonical shelf と混ぜない
- hidden active tool が workspace 外や ignore 配下にある場合は visibility rule を書く
- compatibility 用の legacy workspace がある場合は:
  - new write target にしない
  - 何の caller がまだ依存しているかを書く

## 8. Archive Rule

- delete より archive を優先する
- archive file が active topology を離れた理由を残す
- active shelf と archive shelf を混在させない

## 9. Follow-Up Surfaces

file role または location が変わったら、少なくとも次を更新する。

- taxonomy
- entry index / navigation
- boundary or disposition register
- caller / config / generator reference

## 10. Completion Rule

この taxonomy は、少なくとも次が揃って初めて完了とみなす。

- entry file
- entry / guide / reference split rule
- placement matrix
- boundary / disposition register
- workspace / archive rule
- hidden active asset visibility rule
- front current surface rule
- visible support document rule
- reserved-empty / runtime residue の扱い

## 11. Local Notes

- `{project-specific exceptions}`
- `{enforcement hooks or scripts}`
- `{known residual shelves}`
