# Project Template Adoption Packet Template

**使う場面**: `pj-template` を個別 project に導入し、その project で AI がどこまで安全に進めてよいかを固定する時に使う。  
**差し替える所**: project 名、入口、governance 棚、read/write/no-touch 境界、既存の local rule 名。  
**書かないこと**: 実装タスクの詳細、archive / delete の最終判定、project 固有の日々の current 運用ログ。

**project_id**: `project_xxx`
**status**: Draft / Approved
**shared_template_source**: `{shared template source path or identifier}`
**owner**: `{owner}`

---

## 1. Purpose

- この project に `pj-template` をどう適用するかを固定する
- AI が読んでよい場所、書いてよい場所、止まる条件を固定する
- local canonical と shared template を混ぜない

この packet は、project 固有ルールを最初に定義する文書ではない。
まず
`../frameworks/project-progression-rule.md`
を上位正本として受け、その project で

- どの入口から読むか
- どこへ書き戻すか
- 何が owner-only decision か

を project 側へ落とすために使う。

## 2. Reading Route

最初に読む順を project 用に固定する。

1. `{project entry path}`
2. `{current canonical path / none}`
3. `{governance or rule SSOT path}`
4. `{runtime / code surface path / none}`
5. `{this packet path}`

この Reading Route は、`プロジェクト進行ルール` の

- `入口判定`
- `current`
- `書き戻し`

を project-local に具体化したものとして扱う。

### 2.1 Entry Split

- 全体理解の入口:
  - `{path}`
- 現在作業の入口:
  - `{path}`
- 設計の入口:
  - `{path}`
- 実行面の入口:
  - `{path}`

## 3. Governance Shelf

- governance shelf:
  - `{path}`
- governance shelf entry:
  - `{README path}`
- installed packet:
  - `{packet path}`

## 3.5 Template Branch Decisions

- current ownership:
  - `{local-current / no-local-current / no-current-canonical}`
- restart aid:
  - `{restart-aid-present / restart-aid-none}`
- publication mode:
  - `{publication-planned / publication-not-planned}`
- structure weight:
  - `{lightweight / standard / extended}`
- runtime placement:
  - `{runtime-local / runtime-downstream / runtime-none}`

この項目は `型名` を付けるためではなく、
template 側で吸収する可変条件を先に固定するために書く。
project 固有 rule を増やす前に、まずここへ落とす。

### 3.6 Branch Consequence Record

- current ownership consequence:
  - `{local current path / downstream current path / none}`
- restart aid consequence:
  - `{restart aid path / none}`
- publication consequence:
  - `{publication responsibility path / none}`
- runtime consequence:
  - `{local runtime-sensitive path / downstream runtime authority path / none}`

次を満たさない記入は無効とする。

- `current ownership = local-current`
  - local current path が必要
- `current ownership = no-local-current`
  - local current path は `none`
  - downstream current path が必要
- `current ownership = no-current-canonical`
  - local current path は `none`
  - downstream current path も `none`
  - project entry path が必要
- `restart aid = restart-aid-present`
  - restart aid path が必要
- `restart aid = restart-aid-none`
  - restart aid path は `none`
- `publication mode = publication-planned`
  - publication responsibility path が必要
- `runtime placement = runtime-local`
  - local runtime-sensitive path が必要
- `runtime placement = runtime-downstream`
  - downstream runtime authority path が必要
- `runtime placement = runtime-none`
  - local runtime-sensitive path も downstream runtime authority path も `none`

### 3.7 Rule Ownership Split

- shared progression rule が決めること:
  - `{paths or bullets}`
- template-side branches が決めること:
  - `{paths or bullets}`
- truly project-specific として残すこと:
  - `{paths or bullets}`

### 3.8 Bundle Adoption

- bundle declaration surface:
  - `{path}`
- continue check surface:
  - `{path}`
- close / residual split adoption:
  - `{yes/no + note}`
- template version status:
  - `{legacy-template / upgraded-template / not-applicable-yet}`

## 4. Read / Write / No-Touch Boundary

### Read

- `{paths}`

### Write

- `{governance paths}`
- `{allowed companion paths if any}`

### No-Touch

- `{archive paths}`
- `{runtime-sensitive or generated-sensitive paths}`
- `{external or hidden paths}`

## 5. Current Shelf Classification

- current canonical:
  - `{paths or none}`
- no-local-current:
  - `{yes/no + reason}`
- no-current-canonical:
  - `{yes/no + reason}`
- restart aid / handoff only:
  - `{paths or none}`
- support:
  - `{paths}`
- generated / workspace:
  - `{paths}`
- historical / archive:
  - `{paths}`
- hidden active or ignored assets:
  - `{paths or none}`

`restart aid / handoff only` に置く面は、session 再開時の補助には使ってよいが、current canonical の代替にはしない。

`no-local-current: yes` の project は、この shelf 自体が project-local current を持たないことを意味する。
この場合は、

- current canonical を `none`
- restart aid / handoff only を `none` または補助面だけ
- downstream / operator / integration 側の current 正本

を明示する。

つまり、共通棚、template 棚、library 棚、packaging 棚のように `project-local current` を自棚へ持たない形を明示的に許可する。

`no-current-canonical: yes` の project は、daily current を持たない静的 project を意味する。
この場合は、

- current canonical を `none`
- downstream / operator / integration 側 current も `none`
- restart aid / handoff only を `none`
- project entry path と正式文書の入口

を明示する。

## 6. Runtime And Caller-Sensitive Paths

- runtime-sensitive paths:
  - `{paths}`
- caller-sensitive rename / move prohibited:
  - `{yes/no + notes}`
- generated output that may still be consumed:
  - `{paths or none}`

## 7. Expected Local Deliverables

導入後に project 側へ置く標準面を宣言する。

- `README.md` or local entry route
- `project-file-taxonomy.md`
- `project-boundary-register.md`
- `project-workspace-and-artifact-policy.md`

既存の local equivalent がある場合は、その path と関係を明記する。

## 8. Output And Reporting

- output file:
  - `{summary path}`
- unresolved points file:
  - `{path}`
- latest result wording:
  - `{rule}`

最低限残す reporting 項目:

- `active bundle id`
- `active bundle type`
- `成功主語`
- `現在地`
- `今回の 1 手`
- `完了条件`
- `強い証拠`
- `停止理由`
- `次の 1 手`
- `書き戻し先`

If GitHub public release is planned, this packet must also record the project's publication-readiness asset status and the publication responsibility split defined by `project-publication-responsibility-policy.md`.

## 8.5 Project-Specific Exception Register

template 側で吸えず、project 固有へ残すものだけを書く。

| 例外名 | template で吸えなかった理由 | 該当 branch decisions | owner 判断の有無 | 残す場所 |
|---|---|---|---|---|
|  |  |  |  |  |

この表を埋めずに project 固有 rule を増やしてはならない。

## 9. Owner-Only Decisions

- final canonical versus historical classification
- archive / restore / delete
- hidden active asset keep versus expose versus retire
- caller-sensitive rename / move / delete
- project entry replacement if current route is unclear

## 10. Stop Conditions

- current canonical route is unclear
- archive と active work が混ざっていて local rule がない
- hidden active asset が疑われる
- generated artifact の caller 関係が不明
- 新しい棚を作るが placement rule がない

## 11. Completion Rule

- project reading route is explicit
- governance shelf and packet path are explicit
- read / write / no-touch boundary is explicit
- current / support / generated / archive handling is explicit
- runtime-sensitive paths are explicit
- owner-only decisions remain owner-only
- shared / template / project-specific split is explicit
- branch consequences are explicit
- project-specific exceptions are justified and recorded
