# VEIL 実利用 UX 合格化設計

## 1. 目的とこの設計の役割

この設計の目的は、VEIL を「内部テストが通る実装」から、実ユーザーへ
提供できる UX として判定可能にすることである。判定対象は、通常会話での
無介入、既存語の自動解決、例外の一問化、承認後の同期、失敗時の無書込み、
および実際に配布された Skill / HTML の鮮度である。

これは新しい正本を作る文書ではない。次の既存正本を、実行順・証拠・判定に
接続する設計である。

- 挙動と配布の正本: `docs/veil-design.md`
- 分類と評価の正本: `docs/veil-capture-classification.md`
- v13 の partial-natural-corpus 契約: `docs/governance/20260723-real-conversation-v13-recovery-design.md`
- 既存の実行履歴: `workspace/audit/20260721-real-conversation-ux-v6/execution.md`

v6--v12 の frozen 入力、生成物、結果、cause analysis は不変の履歴である。
この設計は、それらを修復・再実行・再利用しない。v13 の `frozen/` も
再作成・上書きしない。

## 2. 合格主張の階層

同じ「合格」という言葉で異なる事実を混ぜない。各主張は下位の主張を含むが、
上位の代替にはならない。

| 層 | 主張 | 最小証拠 | この設計での意味 |
| --- | --- | --- | --- |
| L1 | 実装契約 | focused regression、静的検査、実 core の使い捨て統合受入 | 実装が契約を満たす |
| L2 | partial 自然会話 | v13 の G4--G9 を一回ずつ閉じた証跡 | 観測済み範囲だけを検証した（任意の補助証跡） |
| L3 | 層別自然会話 UX | fresh な 7 session、4分類下限、独立二者レビュー、blind 評価 | 全4 UX 分岐を自然会話で検証した |
| L4 | 配布済み UX | L3、ブラウザ E2E、freshness `OK`、同一 revision の hosted checks | 実利用 UX として提供可能 |

L2 が成功しても L3 / L4 を主張してはならない。v13 は現在三つの `exclude`
だけを対象にした `partial-natural-corpus` であり、`observe`、`existing-match`、
`exception` は未観測である。

L2 の未完了も L3 / L4 を止めない。v13 は不変入力を持つ任意の補助証跡であり、
その独立生成者がいないことは製品完成のブロッカーではない。L3 の fresh 層別 run
が製品UXの自然会話証拠を直接担い、L4 が実配布の完成判定を担う。

## 3. ユーザーに対する完成 UX

### U1: 通常の無判断会話

入力は一時的・否定・引用・低影響の表現である。VEIL は semantic frame と
critic を検証し、`exclude` または `observe` を返す。ユーザーには VEIL 固有の
表、番号、質問、手動コマンドを表示しない。記録・DB・HTML・sync target は
変更しない。

### U2: 既存語の自動解決

入力は canonical DB の正確な既存対応を使う。VEIL は `existing-match` を返し、
ユーザーに質問しない。既存語の変更や競合が明示された場合は U4 へ移り、
`existing-match` を理由に黙殺してはならない。

### U3: 回復用ブラウザ経路

HTML は完全なテキストを AI review request としてコピーする。ローカル regex
preview は診断専用であり、ゼロ件を意味理解の証拠にしない。HTML は canonical
DB へ直接書き込まない。ロケール切替、clipboard fallback、任意の fine-tuning
導線はブラウザ E2E で検証する。

### U4: 永続決定が必要な会話

durable adoption / rename / definition / conflict / 高影響の未解決 / material critic
disagreement は `exception` である。複数件でも質問は短い一問だけである。
ユーザーが承認するまで DB、HTML、Skill、sync target は変更しない。承認後は
検証済み JSON batch を一回だけ原子的に登録し、HTML 再生成と sync を行う。
どこかで失敗した場合は、完了を主張せず、失敗段階と未完了の対象を示す。

## 4. UX 合格ゲートと判定条件

### Q0: 実装・ソース状態の準備

- 入力: 現行 source、既存 L1 テスト、browser runner、untracked を含む静的対象表。
- 完了事実: classifier / outcome / locale / DB / Skill / HTML のテスト、browser E2E、
  real-core 使い捨て統合が同一 source state で成功する。
- 不可条件: placeholder evaluator、`v4 main()` 呼出し、raw-text fallback、または
  source-state 未固定を実評価の証拠に使うこと。
- 停止: 失敗なら実会話入力の取得・freeze・生成を開始しない。必要最小の実装修正と
  regression を別タスクで完了してから Q0 を再判定する。

### Q1: v13 partial 自然会話の閉鎖（非ブロッキング）

目的は L2 だけである。G4--G6 は完了済みの不変入力として扱う。Q1 は Q2 / Q3
の前提ではなく、実行可能な独立生成者が現れた時だけ再開する。

| 工程 | 実行者と読取境界 | 一回の書込み | 成功条件 | 失敗時 |
| --- | --- | --- | --- | --- |
| G7 | レビュー結果を未閲覧の独立生成者。procedure、frame schema、runtime input のみ読む | `generated-frames.jsonl` と attestation | 3 session、公開 envelope、各 evidence が当該 source text 内 | 生成失敗証跡として閉鎖。再生成しない |
| G8 | 結果を見ない評価者。G7 attestation を read-back 後に実行 | `results/first-run/` | 実 v4 core、3件、全 terminal gate true、DB/raw fallback 0 | `runtime-error` を terminal 保存。再実行しない |
| G9 | evidence closer | close record のみ | 観測範囲、未観測3分類、全 gate、失敗なら原因を明記 | L2 不成立として close。G7/G8 を修復目的で再実行しない |

G7 生成者は reviewer / corpus / canonical DB / 過去結果を閲覧してはならない。
現在レビュー結果を知る担当者は生成物を作らない。Q1 の `scored` は L3 / L4 の
合格ではない。

### Q2: v15 層別自然会話評価

Q1 の成否と独立に、L3 は新規の **v15評価パッケージ** で実行する。v14はfreeze
契約と実v4 core境界の不整合を発見したため、G3前に`requires-revision`として保存し、
生成・評価には使用しない。入力根拠は、
v12で既に確定したG4 source eligibilityとG5 independent A/B reviewである。
v12の`frozen/`、生成物、評価結果、cause analysisを変更・再実行・結果として再利用
してはならない。一方、`input/anonymized-source.jsonl`、Reviewer A、Reviewer B r6、
review reportは、hash付きのread-only provenanceとしてv15へ一回コピーしてよい。
この移送は新しいレビューやラベルの作成ではなく、既存の独立判断を原IDのまま保持する。

#### Q2-1: 入力・カテゴリ契約

- 正確に7一意 session。下限は `existing-match=1`、`observe=2`、`exclude=2`、
  `exception=2`。
- 一 session を複数カテゴリに数えない。候補分類は仮説であり、G5の独立レビュー
  結果が最終である。
- source はv12で承認・匿名化済みの7 sessionを用いる。raw transcript、URL、credential、
  user ID、日時、session ID はv15の最終 corpus に置かない。
- 既存すべての評価 source と session / normalized content / URL / credential pattern /
  共有12-gram が重複しないことを、保存済み比較表で示す。
- `existing-match` の候補にだけ、read-only canonical snapshot の active term を
  必要最小限で渡す。snapshot は hash、bytes、取得時刻を記録する。

#### Q2-2: 独立性とレビュー

- Reviewer A/Bの独立性はv12の確定済みartifactで立証済みである。v15はそのID、
  bytes、hashを保持して取り込む。v15担当者はreviewer ID・label・review frameを
  書き換えない。
- reviewer artifact は schema、exact evidence、outcome、question count、snapshot
  整合を機械検証する。malformed artifact は rejection evidence として保存し、
  静かに置換しない。
- 不一致は row 単位の adjudication を記録する。最終 merged corpus が 1/2/2/2 を
  下回れば `requires-revision` で止め、G4から fresh 候補を補充する。

#### Q2-3: compatible freeze、blind 生成、実 core 評価

v15は、実v4のruntime schema `{session_id, source_text, registered_terms}` と、
生成外部schema `{session_id, payload}` を分離して固定する。`registered_terms`は本番と
同じ判定文脈でありレビューラベルではない。一方、expected outcome、reviewer、review
frame、impact、question requirementはgenerator-visible inputから除外する。

- freeze: stagingでreviewed corpus、runtime input、generator procedure、generator-visible
  decision-frame source、evaluator identity、provenance、source inventoryをhash/bytes/pathで
  検証してから一回だけrenameする。
- blind generation: generatorには凍結済みのruntime input、procedure、decision-frame source
  だけを渡す。出力は正確に7個の`{session_id, payload}`、attestationはread allowlistと
  executor/process identityを含む。これはblind-inputの手続証拠であり、人格的な未見主張を
  偽装しない。
- evaluation: preflight成功前は結果ディレクトリを作らない。開始後はhash一致する実v4
  `score_prevalidated`だけを呼び、DB接続とrule-storeのDB入口をdeny hookで計測する。
  `main()`、固定結果lambda、コピーされたcore、外部canonical DBは禁止する。
- raw fallback: v4 kernelにfallback interfaceがないため、ゼロcounterを偽の実行証拠に
  しない。G0のdependency testでkernel境界を記録し、L3では`not-applicable-to-v4-kernel`
  と明示する。本番fallbackがある場合の評価はL4の別テストで行う。
- terminal: completed scoringにはcore gate、7 case、session set、1/2/2/2、DB zero、source
  inventory、入力hashを記録し、`passed`又は`requires-revision`を分離する。開始後の例外は
  `runtime-error`として保存し、同一packageを再実行しない。

### Q3: 配布済み UX の確認

Q2が `scored` かつすべての gate を満たした source revision だけが対象である。
HTMLとinstalled Skillの鮮度修復は、実ユーザーを旧仕様に残さないためQ0後に先行して
実施してよい。ただし、その修復はL4の最終合格を先取りしない。L4 `release-ready`
判定は、Q2の層別自然会話証跡と同一 revision でQ3を再確認した時だけに行う。

1. その revision の classifier / outcome / locale / DB / Skill / HTML / browser E2E を通す。
2. 明示承認された install / export / sync を実施し、HTMLと両Skillを生成源から更新する。
3. `veil-status --check --json` で DB、HTML、Claude Skill、Codex Skill、required target
   の全項目が `OK` であることを保存する。`STALE`、`MISSING`、`ERROR` は不合格であり、
   ファイルの存在では代替しない。
4. 同一 revision を commit / merge した後、その revision の hosted checks を確認する。
5. release verdict は Q0--Q3 の source revision、証跡 hash、結果、残余制約を一つの
   read-only JSON / Markdown record に束ねる。過去評価の成功数を寄せ集めない。

Q3 の install、sync、commit、merge、push、release はそれぞれ別の明示承認を要する。
本設計の作成自体は、これらを許可しない。

v15の実行時に必要な個別の入力 schema、read allowlist、terminal artifact schema、
focused acceptance、write scope、失敗終端は
`workspace/audit/20260724-real-conversation-ux-v15/goal-register.md` を規範とする。
この文書の抽象的なQ2表現と競合する場合は、同 register のより狭い境界を優先する。

## 5. 判定レコードの詳細設計

`workspace/audit/<successor-run>/close/ux-release-verdict.json` は Q3 の最終判定だけに
用いる。必須 field は次である。

```json
{
  "contract_version": "1",
  "source_revision": "immutable source identity",
  "verdict": "release-ready | requires-revision | evidence-incomplete",
  "claims": {
    "implementation_contract": false,
    "partial_natural_corpus": false,
    "stratified_natural_corpus": false,
    "delivered_ux": false
  },
  "evidence": {
    "q0": [], "q1": [], "q2": [], "q3": []
  },
  "category_counts": {
    "existing-match": 0, "observe": 0, "exclude": 0, "exception": 0
  },
  "delivery_status": [],
  "limitations": [],
  "created_at": "UTC ISO-8601"
}
```

`release-ready` は `claims` の全値が true、カテゴリが 1/2/2/2、delivery status の
required 項目が全て `OK`、かつ hosted check が同一 revision で成功した場合だけに
限る。Q1の partial 証拠は `partial_natural_corpus` のみを true にできる。

## 6. 実行順と権限境界

1. Q0を current source state で確認する。
2. v12 G4/G5の確定済み匿名化sourceとA/B r6をv15へprovenance付きで一回移送する。
3. v15 G0--G6を順序どおりに実行する。
4. Q3の install / sync / Git / hosted check は、Q2 成功後の個別承認で実行する。
5. Q1は未閲覧の独立生成者が利用可能な場合だけ並行ではなく別系統で閉じる。

どの段階でも、前工程の不成立、独立性喪失、source-state変化、schema不正、または
一回限り操作後の failure は「修復のための再実行」ではない。事実を immutable evidence
として close し、必要なら新しい recovery design と fresh input を作る。

## 7. この時点の開始可能性

- Q0: 2026-07-24時点の full pytest、静的検査、browser E2E は成功証跡がある。しかし
  L4では、G6が選んだ同一 source revision に対して全てを再取得する。
- Q1: v13 G7の実行待ちだが、L3/L4を止めない補助証跡である。
- Q2: v12 G4/G5のprovenance移送後、v15 G0--G6を完成の主経路とする。v14は
  生成・評価を開始せず`requires-revision`として保存済みである。
- Q3: HTMLと両 installed Skill の freshness は `OK` の成功証跡がある。ただし、L4の
  same-revision 判定ではなく、G6で再確認するまで `release-ready` にはしない。

この設計の完了条件は、Q0--Q3の境界・成果物・停止条件・権限が一意に定まり、
`execution.md` が現行のv13運用状態とこの上位計画を矛盾なく参照することである。
