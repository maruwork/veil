# 共通テンプレート

project をまたいで使える文書雛形を置く。

template 全体の分け方、切り出し単位、project 側に残す版のルールは
[PJ Template README](../README.md)
と各 template 冒頭の用途説明を正本として読む。

本文は日本語正本とする。`Status`、`ID`、`PASS / FAIL`、schema key、external tool と連動する field name は英語のまま維持してよい。

ただし、英語はそのまま置くだけでよいわけではない。共通テンプレートでは次を守る。

- 単なる説明語なら、日本語またはカタカナで書く
- `ACTIVE` / `DONE` / `PASS` / `FAIL` のような固定値は、`status 値` / `verdict 値` のように種別を添えて書く
- ``field_name`` / ``variable_name`` のようなコード上の語は、``backticks`` で囲み、field 名または変数名だと明示する
- command / option / policy 名も、その種別を添える

目的は翻訳ではなく、英語ラベルを見た時に**それが説明語なのか、固定値なのか、コード名なのか**を一目で分かるようにすること。

## 入口で前に出す雛形

- project 構造整理
  - [project-structure-governance-starter-pack.md](./project-structure-governance-starter-pack.md)
  - [project-file-taxonomy-template.md](./project-file-taxonomy-template.md)
  - [project-boundary-register-template.md](./project-boundary-register-template.md)
  - [project-workspace-and-artifact-policy-template.md](./project-workspace-and-artifact-policy-template.md)
- 入口
  - [navigation-template.md](./navigation-template.md)
- 導入
  - [project-template-adoption-packet-template.md](./project-template-adoption-packet-template.md)
- 設計
  - [requirements-template.md](./requirements-template.md)
  - [basic-design-template.md](./basic-design-template.md)
  - [implementation-plan-template.md](./implementation-plan-template.md)
- 判定
  - [decision-packet-template.md](./decision-packet-template.md)
  - [evaluation-verdict-template.md](./evaluation-verdict-template.md)
- task
  - [task-spec-template.md](./task-spec-template.md)
  - [task-checklist-template.md](./task-checklist-template.md)

この棚には他にも雛形があるが、入口では上の本体だけを見せ、残りは必要時だけ開く。

## 保管資産として残す雛形

- 統合済み・削除済みの細目は入口 README に抱え込まず、必要時だけ履歴と監査記録で確認する

これらは他案件へ持ち出せる雛形である。project 固有の元文書は、共通雛形へ移植できる部分だけを抜き出し、元の棚に project 固有の正本として残す。

## 他案件で最初に使う入口順
先に
`../frameworks/project-progression-rule.md`
へ戻り、

- `current ownership`
- `restart aid`
- `publication mode`
- `structure weight`
- `runtime placement`

の分岐条件を先に決める。
そのうえで次の 3 択から今の主語に直接効く 1 本だけを選ぶ。

1. project 構造整理から入るなら
   - [project-structure-governance-starter-pack.md](./project-structure-governance-starter-pack.md)
2. project の入口と案内文を作るなら
   - [navigation-template.md](./navigation-template.md)
3. task / design / audit の文書雛形が必要なら
   - 必要な template だけを開く

template 棚を一覧から順に読む必要はない。
迷ったら `../README.md` に戻る。

## そのまま使うもの / 差し替えるもの

- そのまま使うもの
  - template の章構成
  - 記入観点
  - owner judgment を残す位置
- project ごとに差し替えるもの
  - path
  - 今の状態を見るファイル名
  - validator / healthcheck / command 名
  - project 固有の shelf 名
