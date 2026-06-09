# プロジェクト進行ルール統合監査表

**目的**: `pj-template` にある既存文書を、`プロジェクト進行ルール` に対して

- 何を担っているか
- どの層に属するか
- 今後どう扱うか

で一覧化し、再編判断を会話依存にしないようにする。

この文書は、以前の `project-progression-rule-connection-map.md` が持っていた

- 何を具体化しているか
- どこに属するか
- どう読むか

も吸収した、`pj-template` の進行ルール整理台帳として扱う。

## 0. 接続図と読む順

### 0.1 3層への割り当て

#### 完了骨格

主に次が担う。

- [project-progression-rule.md](project-progression-rule.md)
- [goal-path-checkpoint-task-design-framework.md](goal-path-checkpoint-task-design-framework.md)
- [business-workflow-spine.md](business-workflow-spine.md)

役割:

- 完成の定義
- ゴール
- 道のり
- checkpoint
- task
- 設計
- 仕事を閉じる境界

#### 進行ルール

主に次が担う。

- [project-progression-rule.md](project-progression-rule.md)
- [execution-readiness-gate-policy.md](../policies/execution-readiness-gate-policy.md)
- [task-realtime-operation-policy.md](../policies/task-realtime-operation-policy.md)
- [entry-guide-reference-separation-policy.md](../policies/entry-guide-reference-separation-policy.md)
- [agent-workflow-policy.md](../policies/agent-workflow-policy.md)

役割:

- 何の入口から読むか
- 着手前に何を確認するか
- 今どこにいるか
- current をどう持つか
- 次の 1 手をどう選ぶか
- 結果をどこへ書き戻すか

#### 認識・補正規律

主に次が担う。

- [project-progression-rule.md](project-progression-rule.md)
- [verification-and-retry-policy.md](../policies/verification-and-retry-policy.md)
- [entry-guide-reference-separation-policy.md](../policies/entry-guide-reference-separation-policy.md)
- [task-realtime-operation-policy.md](../policies/task-realtime-operation-policy.md)
- [agent-workflow-policy.md](../policies/agent-workflow-policy.md)

役割:

- 主語ずれの抑止
- 面種別の混線防止
- 未完了の放置防止
- 失敗時の停止
- 正本への再接地
- 補正後の再開

### 0.2 最初に読む順

`pj-template` を使う時は、少なくとも次の順で読む。

1. [project-progression-rule.md](project-progression-rule.md)
2. [project-progression-rule-integration-audit.md](project-progression-rule-integration-audit.md)
3. [goal-path-checkpoint-task-design-framework.md](goal-path-checkpoint-task-design-framework.md)
4. [execution-readiness-gate-policy.md](../policies/execution-readiness-gate-policy.md)

その後に必要な文書を追加で読む。

## 1. 判定区分

- `KEEP`
  - 役割が明確で、`プロジェクト進行ルール` の下位具体化としてそのまま残す
- `INTEGRATE`
  - 役割は有効だが、位置づけや本文の接続補強が必要
- `INTEGRATED`
  - 接続補強を実施済みで、次の波では重複圧縮や統合要否だけ見ればよい
- `REPLACE`
  - 新しい上位正本が主役になるため、旧位置づけのまま残さない
- `LATER`
  - 今すぐは触らず、後段で統合判断する

## 2. framework 棚

| 文書 | 主役割 | 主層 | 判定 | 理由 |
|---|---|---|---|---|
| `project-progression-rule.md` | 最上位進行ルール | 進行ルール / 認識・補正規律 | `KEEP` | 今回追加した中核正本 |
| `goal-path-checkpoint-task-design-framework.md` | 5 層分解 | 完了骨格 | `KEEP` | 上位分解の中核として有効 |
| `business-workflow-spine.md` | 設計 / 事前監査 / 実行 / 事後監査 | 完了骨格 / 進行ルール | `KEEP` | 業務骨格として独自価値がある |
| `decision-to-implementation-consistency-review.md` | 振り返りと整合 | 認識・補正規律 | `INTEGRATED` | ズレ検出、false-complete、補正対象面に特化し、context 正本再定義を持たない形へ整理済み |
| `framework-selection-guide.md` | フレームワーク選択補助 | 進行補助 | `INTEGRATED` | framework family の選定に限定し、個別 framework 本文と分離済み |
| `prompt-quality-improvement-cycle.md` | prompt / token 改善 | 非本線補助 | `INTEGRATED` | 改善サイクルに限定し、framework 選定や PS 群読解と分離済み |
| `ps-suite-guide.md` | 発見 / 測定 / 振り返り詳細 | 非本線補助 | `INTEGRATED` | PS 系 framework 群の読解と handoff に限定し、横断選定と分離済み |
| `README.md` | 棚入口 | 進行補助 | `INTEGRATED` | 読む順と最上位正本への接続を反映済み |

## 3. policies 棚

| 文書 | 主役割 | 主層 | 判定 | 理由 |
|---|---|---|---|---|
| `execution-readiness-gate-policy.md` | 着手前 gate | 進行ルール | `KEEP` | 最重要の具体化文書 |
| `task-realtime-operation-policy.md` | current 正本運用 | 進行ルール / 認識・補正規律 | `KEEP` | 記憶依存防止の中核 |
| `entry-guide-reference-separation-policy.md` | 入口分離 | 進行ルール / 認識・補正規律 | `KEEP` | 面種別混線防止に必須 |
| `verification-and-retry-policy.md` | 検証と retry | 認識・補正規律 | `KEEP` | 完了証拠と retry 規律に必須 |
| `agent-workflow-policy.md` | agent 作業運用 | 進行ルール / 認識・補正規律 | `INTEGRATED` | 次の 1 手、限定実行、継続判定との関係を追記済み |
| `context-management-policy.md` | context 管理 | 認識・補正規律 | `INTEGRATED` | 再接地、current、入口混線防止に特化し、不一致分類 review は別 framework へ分離済み |
| `diff-ownership-and-wave-close-policy.md` | dirty state / wave close | 進行補助 | `INTEGRATED` | bounded 進行と停止条件の関係を追記済み |
| `file-operation-policy.md` | file 操作境界 | 進行補助 | `KEEP` | 実行制約として独立価値がある |
| `naming-and-shelf-policy.md` | 命名と棚配置 | 進行補助 | `KEEP` | 表記揺れ抑制に寄与 |
| `project-template-installation-gate-policy.md` | template 導入 gate | 進行補助 | `KEEP` | template 適用時に必要 |
| `project-template-adoption-completion-policy.md` | template 適用完了条件 | 完了骨格 / 進行補助 | `INTEGRATED` | 完成定義、完了条件、入口判定との関係を追記済み |
| `project-publication-responsibility-policy.md` | 公開責務分担 | プロジェクト固有派生補助 | `KEEP` | 公開案件固有の重要 rule |
| `spec-review-and-skill-policy.md` | spec / skill 扱い | 進行補助 | `INTEGRATED` | specification-first、independent review、skill 抽出に限定し、選定・不一致分類と分離済み |
| `token-optimization-policy.md` | token 最適化 | 非本線補助 | `INTEGRATED` | source-first と正本非代替の関係を追記済み |
| `README.md` | 棚入口 | 進行補助 | `INTEGRATED` | 最上位正本への読む順を追記済み |

## 4. checklist 棚

| 文書 | 主役割 | 主層 | 判定 | 理由 |
|---|---|---|---|---|
| `implementation-audit-checklist.md` | 実装後監査 | 進行ルール / 認識・補正規律 | `KEEP` | 完了証拠確認に直接使える |
| `design-spec-completion-checklist.md` | design spec 完了監査 | 完了骨格 / 進行ルール | `KEEP` | completion-level spec 判定に有効 |
| `ai-agent-runtime-bootstrap-checklist.md` | AI 作業環境立ち上げ | 進行補助 | `KEEP` | 新規プロジェクト開始時に有効 |
| `security-review-checklist.md` | security 観点監査 | 進行補助 | `INTEGRATED` | 最上位ルールの検証・停止条件・書き戻しとの関係を追記済み |
| `unit-test-checklist.md` | unit test 観点 | 進行補助 | `INTEGRATED` | 最上位ルールの検証・完了条件・書き戻しとの関係を追記済み |
| `integration-test-checklist.md` | integration test 観点 | 進行補助 | `INTEGRATED` | 最上位ルールの checkpoint・検証・書き戻しとの関係を追記済み |
| `README.md` | 棚入口 | 進行補助 | `INTEGRATED` | 最上位正本と監査表への接続を追記済み |

## 5. 現時点の結論

### 5.1 置換対象は限定的

現時点で `REPLACE` と言えるのは、主に `project-progression-rule.md` を入れたことで

- 以前は暗黙に散っていた最上位ルールの位置

だけである。

つまり、既存文書を大量廃止する段階ではない。

### 5.2 多くは `KEEP` か `INTEGRATED`

既存文書の大半は役割が残っている。

問題は、内容が無価値なことではなく、

- 最上位ルールとの接続が明示されていない
- どの層に属するかが曖昧
- 入口から見た読む順がぶれている

ことである。

第一波では、この `接続が明示されていない` 問題を優先して補強した。

### 5.3 template 側で固定した分岐条件

`型名` を増やすより先に、
template 側で吸収すべき分岐条件を固定する方が正しいと確認できた。

現時点で確定している分岐条件は次のとおり。

1. `current ownership`
   - `local-current`
   - `no-local-current`
   - `no-current-canonical`
2. `restart aid`
   - `restart-aid-present`
   - `restart-aid-none`
3. `publication mode`
   - `publication-planned`
   - `publication-not-planned`
4. `structure weight`
   - `lightweight`
   - `standard`
   - `extended`
5. `runtime placement`
   - `runtime-local`
   - `runtime-downstream`
   - `runtime-none`

project ごとの差は、まずこの分岐条件へ落とす。
分岐条件で吸収できる差を、すぐに `別型` や `project 固有例外` として増やさない。

### 5.4 代表的な分岐の組み合わせ

分岐条件の組み合わせとして、少なくとも次の代表例が確認できている。

1. `local-current / restart-aid-present / runtime-local`
   - local current を自棚に持つ
   - restart aid はあるが canonical current の代替にはしない
   - runtime 実体を local に持つ
   - `Do Not Start From` のような否定ルールを併用しやすい
2. `no-local-current / restart-aid-none / runtime-downstream`
   - local current は持たない
   - downstream current や runtime authority へ戻る
   - 共通棚として entry / runtime / contract を持ちやすい
3. `no-local-current / restart-aid-present / runtime-local`
   - local current は持たない
   - restart aid は持つ
   - runtime 実体は local にある
   - DB 正本や handover 表示のように authority 面を分けやすい
4. `local-current / restart-aid-none / runtime-local`
   - local current を持つ
   - restart aid は持たない
   - runtime 実体を local に持つ
   - product README と構造 index のような複数入口を併用しやすい
5. `no-current-canonical / restart-aid-none / runtime-none`
   - daily current を持たない
   - restart aid も持たない
   - static guide / artifact / schema shelf として扱う

現時点の template は、`daily current を持つ project`、`downstream current へ戻る project`、
`daily current 自体を持たない静的 project` をどれも表現できるところまで到達したとみなす。

### 5.5 運用監査と経緯の戻り先

次は、この framework 本体ではなく `reference` 側の監査・経緯記録として扱う。

- 一次完成の時点判定
- 実案件横断の観察結果
- 残件の設計固定
- enforcement upgrade の観察メモ
- その波で触った具体ファイル一覧

参照先:

- [../../refernce/pj-template-progression-rule-audit-history-20260608.md](../../refernce/pj-template-progression-rule-audit-history-20260608.md)

## 6. この文書の役割

この文書は、`pj-template` 本体に残すべき次だけを持つ。

1. 接続図
2. 読む順
3. 各棚文書の役割整理
4. template 側で固定した分岐条件
5. 代表的な分岐の組み合わせ

実案件の観察ログ、時点判定、upgrade 計画、修正対象一覧は `reference` 側で読む。
