# 仕様・レビュー・スキルポリシー

**目的**: specification-first work、independent review、reusable agent skill の移植可能なルールを定義する。

この policy は
`../frameworks/project-progression-rule.md`
のうち、主に

- `完成の定義から task / design へ落とす`
- `完了条件を明示してから実装する`
- `review 可能な形で進める`

を、仕様・レビュー・skill 抽出の面で具体化する。

この policy の役割は

- specification-first の規律
- independent review の成立条件
- reusable skill 抽出条件

までである。

framework family の選定そのものは
`../frameworks/framework-selection-guide.md`
を、review 実施後の不一致分類は
`../frameworks/decision-to-implementation-consistency-review.md`
を正本として参照する。

## 1. 複雑な実装の前に specification を作る

複雑または高リスクな作業では、実装前に specification を書く。

有用な場合は 3 層に分ける。

1. Requirements: 達成すべきことと成功判定。
2. Design: architecture、data flow、constraints、edge cases。
3. Task breakdown: 実行・検証できる implementation unit。

小さな task は短い inline spec でよい。ただし success criteria は明示する。

design spec を completion-level として扱う場合の quality rule は次を使う。

- policy: `spec-review-and-skill-policy.md`
- checklist: `../checklists/design-spec-completion-checklist.md`

### 1.1 実装先行時の設計証跡

DB write、migration、workflow 変更、contract 変更、rule 変更、構造変更、複数ファイル変更のように後から説明不能になりやすい作業では、実装前または実装と同時に最低限次を残す。

1. `purpose`
2. `impact`
3. `execution order`
4. `rollback`
5. `postcheck`

この 5 点が artifact に残らず、後から design spec を再構成できない状態では実装を進めない。

実装先行が許されるのは、最終版の design spec は未完成でも、上の 5 点が先に残り、current canon / backlog / task item から後続の設計書化へ戻せる場合だけとする。

## 2. 曖昧な goal を変換する

実装前に、曖昧な goal を測定可能な outcome に変換する。

例:

- 「きれいにする」→ naming、placement、complexity の具体基準
- 「bug を直す」→ expected behavior と regression check
- 「file を整理する」→ inventory、classification、accepted actions

## 3. Independent Review

重要な design や risky change は、independent review pass が有効である。

reviewer は次を判断できる必要がある。

- artifact または diff
- stated requirements
- verification evidence
- known risks

reviewer が変更を理解するために、会話履歴全体を読む必要があってはならない。

security-sensitive な変更では、review 前に threat model または同等の boundary note を用意してよい。特に次を含む場合は推奨する。

- DB write / migration / trigger / constraint
- credential / auth / bypass / privileged action
- external service / webhook / notification / import path
- destructive action または wrong-target risk

portable な叩き台が必要なら、次を使ってよい。

- `../checklists/security-review-checklist.md`

必要なら、project-local の boundary note / threat note を併用してよい。

## 4. Skill Extraction

同じ instruction、workflow、reference material が task をまたいで繰り返される場合、reusable skill、template、checklist、policy への抽出を検討する。

skill に step-by-step の micromanagement を詰め込みすぎない。よい skill は次を定義する。

- いつ使うか
- input と output
- key constraints
- completion criteria
- fallback behavior

security / threat-model 系の reusable asset は、vendor 固有の tool 手順ではなく、asset / boundary / abuse case / mitigation / verification の型を抽出する。

## 4.5 外部 workflow pattern の取り込み

外部 repo / skill / workflow から有用な pattern を見つけた場合、丸ごと導入せず次の順で扱う。

1. 既存ルールとの衝突確認
2. 採る部分だけを `policy / checklist / workflow` に落とす
3. 採らない部分を明示する

採用しやすいもの:

- parallel dispatch の条件
- bite-sized planning の粒度感
- verification-first の順序
- reusable skill / template packaging pattern

採用しにくいもの:

- project の current rule と競合する absolutist rule
- trivial work まで重くする mandatory approval step
- repo kernel を置き換える wholesale workflow

## 4.6 外部 tool の採用区分

外部 tool / tracker / memory / agent helper は、使う前に **どの面へ採るのか** を先に固定する。

### A. 日次運用に採る tool

project の日次運用 / current workflow / operator path に入れる場合は、単なる参考利用で止めない。

最低限、次を明示する。

1. どの phase で使うか
2. どの trigger / workflow / hook / runbook から起動するか
3. 何を authority とし、何を authority にしないか
4. fail-close / escalation / verification をどこで掛けるか

運用に採ると決めた tool は、`使ってもよい` ではなく、**どの場面で半自動または自動で使われるか** を current canonical surface から辿れる必要がある。

### B. 基盤作成に採る tool

project 基盤の build / redesign / refactor / taskification を助けるだけの tool は、日次運用 workflow に混ぜない。

この場合は、最低限次を明示する。

1. いつ使うか
2. 何のために使うか
3. 何を生成しても、それ自体は SSOT ではないこと
4. 使い終わったあと repo 正本へ何を落とすか

作成補助 tool は、`便利だから都度使う` を禁止する。繰り返し使うなら、`policy / checklist / workflow / skill` のいずれかへ昇格させるか、逆に単発支援として隔離する。

実際の採用時は、次を使う。

- checklist: target project or common shelf の external-tool adoption checklist
- template: target project or common shelf の external-tool adoption note template
- operator guide: target project 側で定義された operator guide or runbook

### B-1. build-side review helper の固定条件

作成補助 tool を build 前後の review helper として使う場合でも、次を守る。

1. changed-files scope に限定する
2. 出力は candidate / evidence であり、SSOT にしない
3. `feature-dev` や owner review を置き換えない
4. closure / hard-stop authority は既存の healthcheck / review lane に残す

`autonomous_code_inspection` の `build-preflight` / `build-review` profile はこの区分で読む。  
つまり、実装前後の差分 review を助けるが、build-side output 自体は current truth にならない。

### C. 繰り返し利用時の昇格ルール

同じ tool / pattern が task をまたいで繰り返し必要になる場合は、次のどちらかに寄せる。

1. 運用組込: trigger / hook / runbook / healthcheck まで落として半自動化する
2. 作成補助: 明示的な使用条件と completion artifact を rule 化する

どちらにも寄せず、session ごとに ad-hoc 判断で使い続ける状態を残さない。

## 5. Reusable Asset は portable に保つ

reusable asset では、明示的な例でない限り、project-specific path、credentials、role names、database assumptions を避ける。

project-specific rule に reusable principle が含まれる場合、portable version を抽出し、別 migration が承認されるまで元の project rule は残す。
