# Project Boundary Register Template

**使う場面**: 棚ごとの class と disposition を登録する時に使う。  
**差し替える所**: 棚名、class 名、disposition、根拠の置き方。  
**書かないこと**: 実装 plan 本文、今の状態の正本、project 固有の current 運用。

> **用途**:
> 棚ごとの扱いを固定し、「そこが今の正本かどうか」を一意に読むための再利用 template。

> **読み方**: このファイルは記入用 register。棚の種類、workspace の扱い、片づけ手順は [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md) の cleanup procedure 章で読む。

**project_id**: `project_xxx`
**status**: Draft / Approved
**paired taxonomy**: `project-file-taxonomy-template.md`
**rulebook**: `project-structure-governance-starter-pack.md`

---

## 1. Purpose

- 棚ごとの意味を固定する
- 今の正本と補助 / 生成物 / 履歴を混同しない
- 「docs は全部今の正本」といった誤読を防ぐ

この template は `各棚の class と今の正本性` を登録するためのものであり、

- file type ごとの置き場所決定
- workspace / generated / archive の retention rule
- project 全体の入口や読む順

を単独で確定する文書ではない。

## 2. Register

| shelf | class | 今の正本か | role | notes |
|---|---|---|---|---|
| `{path}` | `current canonical` / `support` / `generated` / `historical` / `external` / `reserved-empty` | `yes/no` | `{role}` | `{notes}` |
| `{path}` | `current canonical` / `support` / `generated` / `historical` / `external` / `reserved-empty` | `yes/no` | `{role}` | `{notes}` |
| `{path}` | `current canonical` / `support` / `generated` / `historical` / `external` / `reserved-empty` | `yes/no` | `{role}` | `{notes}` |

## 3. Reading Rules

shelf class の定義は [`project-structure-governance-starter-pack.md` cleanup procedure 章](./project-structure-governance-starter-pack.md) を参照。

各棚の class は §2 Register の `class` column に記入する。class の候補値: `current canonical` / `front current surface` / `support` / `visible support` / `generated` / `historical` / `external` / `reserved-empty`

## 4. Minimum Required Shelves

少なくとも次は register に載せる。

- entry / index shelf
- current task or work shelf
- governance / policy shelf
- design shelf
- runtime / code shelf
- workspace / generated shelf
- archive / historical shelf
- front current surface
- hidden active or ignored shelf
- 実行後や agent 作業後の残り物を置く棚
- reserved-empty shelf が存在するならその shelf

## 5. Boundary Questions

各 shelf について最低限これを答える。

- ここは今の正本か
- 何のための棚か
- 何を置いてはいけないか
- 何を読む前提の reader / agent がいるか
- front current surface に置いてよいか
- visible support として残すなら、どの今の状態の入口へ戻すか

## 6. Completion Rule

- taxonomy と register が同じ棚構造を読める
- entry file と register が矛盾しない
- generated / archive / support が今の正本と混線しない
- front current surface が support / visible support と混線しない
- reserved-empty shelf がある場合、notes に `no ad hoc write` がある
- hidden active asset がある場合、visibility / manifest 導線が notes にある

## 7. Local Exceptions

- `{exception keep shelves}`
- `{old-reference shelves}`
- `{external authority shelves}`
