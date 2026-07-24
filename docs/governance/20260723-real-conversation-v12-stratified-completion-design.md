# VEIL v12: 複数カテゴリ実会話UX評価 完了設計

## 1. 状態と目的

- 状態: `execution-ready design`。v12のsource、レビュー、入力固定化、生成、評価、結果はまだ作成していない。
- 目的: VEILの固定分類UXを、単一の`observe`例ではなく、複数の分類カテゴリを含む実会話由来のblind評価で検証する。
- 評価対象: 分類の妥当性、質問の必要性、既存語との整合、入力完全性、実v4 coreを通る採点、および失敗時の証跡分離。
- 成功は「すべてのカテゴリで正しい」と断定することではない。定義した最小カテゴリ構成を実会話で評価し、結果と限界を改変不能な証跡として残すことである。

## 2. 不変境界

1. v1からv11のsource、review、入力固定化、blind出力、結果、cause analysisは変更、再利用、再実行しない。
2. v12はfreshな実会話sessionだけを使う。過去評価で使ったsession、文面、またはそこから復元可能な断片は候補から除外する。
3. raw transcript、ユーザー識別子、ローカル絶対パス、URL、認証情報、外部貼付内容はv12成果物へ書かない。
4. 認可済みの候補源はClaude Code履歴に限る。各候補は匿名化した最小抜粋だけを扱い、外部への送信はしない。
5. v12の入力固定化は一回だけである。失敗した途中成果物は最終`frozen/`に残さず、成功した最終入力は変更しない。
6. G4からG9は順序どおりに進める。前段の受入条件を満たさない場合、後段を開始しない。これは停止ではなく、誤った証跡を作らないための明示的な分岐である。

## 3. v12の最小カテゴリ構成

v12は7 sessionを最低構成とする。同じsessionを複数カテゴリへ数えない。カテゴリ候補はG4で確定し、G5の独立二者レビューで変更され得るが、合計数とカテゴリ下限は維持する。

| 分類 | 必要数 | 実会話で満たす条件 | 評価上の確認点 |
| --- | ---: | --- | --- |
| `existing-match` | 1 | active vocabulary snapshotにある正規語を、話者がそのまま採用または確認している。別の優先語を提案していない。 | 重複作成を避け、既存語を提示する。 |
| `observe` | 2 | 一時的な呼称、単発の表現、または高影響でない定義不足の表現である。 | 観測として保持し、不要な確定質問を出さない。 |
| `exclude` | 2 | 否定、批評、報告、引用、または採用意思のない言及である。 | 語彙候補として扱わず、質問を出さない。 |
| `exception` | 2 | 持続的な採用、改名、競合、または高影響で定義が必要な表現である。 | 例外として扱い、必要な最小質問を出す。 |

カテゴリが満たせない場合の扱いは補完や創作ではない。G4は`source-gap`として終了し、欠けたカテゴリと探索範囲だけを記録する。G5以降は開始しない。

## 4. G4-v12: source eligibility とカテゴリ候補の確定

### 入力と許可範囲

- 読取り対象は、Claude Code履歴内の非VEIL会話だけである。
- 1候補につき、意味判定に必要な最小の匿名化抜粋、session fingerprint、候補分類、取得日時、匿名化手順版を作る。
- fingerprintは元のsession IDまたはパスを露出しない不可逆値とする。成果物に元ID、履歴パス、raw transcriptを書かない。
- 現行canonical snapshotを1回取得し、そのhash、bytes、作成時刻、active term一覧を固定候補として記録する。

### 候補ごとの必須検証

候補表の各行について、以下を機械検証する。

1. 匿名化後の抜粋が空でなく、PII検出規則、絶対パス、URL、credential pattern、外部貼付blockの禁止規則を通る。
2. session fingerprintが候補表内で一意である。
3. v1からv11の既知source fingerprintと一致しない。
4. 現在候補と過去sourceの間で、完全一致、片側包含、逆包含、共有12-gramのいずれも0件である。
5. category candidateが4カテゴリのいずれかであり、その根拠が匿名化抜粋だけから説明できる。
6. `existing-match`候補はsnapshotのactive termと正規化後に完全一致し、別のpreferred form提案を含まない。
7. 候補抜粋はreviewer A/B、generator、evaluatorが必要とする情報以外を含まない。

### G4受入条件と証跡

- 7行、7一意session、カテゴリ別に1/2/2/2件を満たす。
- 全候補が上記7検証を通る。
- source eligibility report、sanitized candidate corpus、prior-comparison matrix、snapshot record、validator outputをv12作業領域へ作る。
- reportには各カテゴリ数、除外数、除外理由の集計を含める。除外候補の原文は残さない。
- 受入条件を満たした時だけ、G5へ候補corpusを渡す。

### G4停止条件

- 1つでもカテゴリ下限を満たせない、重複検出、匿名化失敗、または過去v1-v11との比較が0以外なら`source-gap`または`source-integrity-failure`を作る。
- その記録はv12の最終入力固定化パス外へ置く。G5-G9は開始しない。

## 5. G5-v12: 独立二者レビューとmerged corpus

### Reviewer A

- Aにはsanitized candidate corpus、固定分類方針、active vocabulary snapshotだけを渡す。
- 7行全件について、分類、preferred form、質問要否、根拠を記録する。
- Aの出力はschema、全行数、許可分類、質問契約、snapshot整合をvalidatorで検証する。

### Reviewer B

- BはAの出力、Aの結論、過去review artifact、生成物、評価結果へアクセスしない。
- Bには別名のsource snapshot matrix、同じ固定分類方針、同じactive vocabulary snapshotだけを渡す。
- Bは独自に7行全件を分類し、preferred form、質問要否、根拠を記録する。
- malformed、参照禁止違反、全行欠落、またはschema違反のB artifactは`rejected`として保存するが、merged corpusの根拠にしない。

### 統合と受入条件

1. validatorは両reviewの厳密なtop-level field集合、row field集合、型、session集合、カテゴリ、質問契約を検証する。
2. A/Bが一致した行はそのまま採用する。不一致行は、両方の根拠だけを用いた明示的なadjudicationで決める。
3. adjudicationは分類、preferred form、質問要否、理由、決定者、参照したA/B row IDを記録する。
4. merged corpusは正確に7行、7一意session、1/2/2/2カテゴリを満たす。レビュー結果がカテゴリ下限を壊す場合はG5 `requires-revision`で止め、G4からfresh候補を補充する。
5. merged corpusにはraw text、reviewerの環境情報、非匿名IDを含めない。

### G5停止条件

- B不成立、レビューschema不正、カテゴリ下限崩れ、またはmerged corpus validator不通過ならG6へ進まない。
- rejected artifactとvalidator出力は残す。A/Bの再利用による見かけ上の独立化はしない。

## 6. G6-v12: 原子的入力固定化と完全性証明

### 固定対象

最終パスは`workspace/audit/20260723-real-conversation-ux-v12/frozen/`とする。名称は既存形式との互換のためであり、本書では「入力固定化」と呼ぶ。最終パスには、少なくとも次を含める。

- sanitized merged corpus
- canonical snapshot record
- source eligibility reportとprior-comparison matrix
- A/B review、rejected review evidence、adjudication record
- generator procedure
- manifest、attestation、source-state inventory
- v12 validator、input-integrity module、atomic fixer
- v12 evaluator adapter、runtime audit、core boundary、terminal result runner、source-state module
- import対象の実v4 coreと、その正規化・採点依存コード

### 原子的手順

1. 最終`frozen/`が存在しないことを確認する。存在する場合は即拒否する。
2. 同一親ディレクトリに一意なstaging directoryを作る。
3. 固定対象をstagingへコピーし、全fileの相対path、bytes、SHA-256をmanifestへ列挙する。
4. manifestとattestationを作り、許可field集合、型、値、相互参照、hash、bytes、path、session集合、カテゴリ下限、artifact policy、source stateを自己検証する。
5. source stateは明示inventoryの順序、重複、存在、hash、bytesを検証する。untracked依存、inventory外のimport、またはroot外pathは拒否する。
6. 全検証成功後にstagingを最終`frozen/`へ一度だけrenameする。コピーではなく同一volume renameを使う。
7. 失敗時は最終`frozen/`を作らない。stagingは削除し、原因、段階、例外種別、入力hashだけを最終パス外のfailure recordへ残す。

### G6受入テスト

入力固定化を実行する前に、次を個別に通す。

- manifest/attestationの未知field、欠落field、型不正、値不正、path/hash/bytes不一致、timestamp不正、artifact policy不正、source-stateネスト不正を拒否する。
- duplicate session、カテゴリ数不一致、snapshot不一致、review/merged不一致をpreflightで拒否する。
- copy、hash、metadata作成、metadata検証、rename各段階のfailure injectionで最終`frozen/`が存在しないことを確認する。
- input validatorがラベル読取りより前に失敗することを確認する。
- 明示inventoryの重複、未列挙依存、hash変化を拒否する。

これらとfocused test、全test、untracked fileを含む対象ファイル静的検査が通った時だけ、G6の一回実行を行う。

## 7. G7-v12: blind生成を一度だけ実行

### 入力契約

generatorが読めるのは次の3入力だけである。

1. 固定化済みsanitized merged corpus
2. 固定分類方針
3. 固定active vocabulary snapshot

reviewer identity、adjudication理由、prior comparison matrix、結果dir、canonical DB、raw textへのアクセスは許可しない。generator procedureと入力hashを出力manifestへ記録する。

### 受入条件

- 7入力に対して正確に7出力を返す。
- session ID、分類、質問要否、質問文、preferred formのschemaを満たす。
- `exclude`は候補登録や質問を出さない。
- `existing-match`は重複候補を作らず既存語を提示する。
- `observe`は質問なし、`exception`は定義上必要な最小質問だけを出す。
- outputはASCII/UTF-8規約、path安全性、入力session集合との一致を検証する。

### 停止条件

生成開始前の入力違反は`preflight-failure`として、結果dirを作らずに記録する。生成開始後の例外は`runtime-error`としてterminal manifestへ記録する。どちらの場合も同じ入力で再生成しない。

## 8. G8-v12: 実v4 coreによる一回評価

### 実行境界

- v12 adapterは旧v4 `main()`を直接呼ばない。旧来のresult directory preflightと旧manifest形式に依存せず、v12でpreflight済みの入力を実v4 coreの採点境界へ渡す。
- adapterは結果dirを前作成してcoreと競合しない。
- 実coreはv12固定source-state inventoryに記載されたファイルだけから読み込む。偽core、固定結果lambda、placeholder adapterは受入根拠にしない。
- adapterは`runtime-started`を記録してからcoreを呼ぶ。開始前失敗と開始後失敗をterminal manifestで区別する。

### 実測監査

- canonical DB接続経路を実行禁止hookで覆い、呼ばれたら即例外かつcounterを増加させる。
- raw-text fallback経路を実行禁止hookで覆い、呼ばれたら即例外かつcounterを増加させる。
- terminal gatesは固定値ではなく、hook counter、source state before/after、schema検証、core resultから構成する。
- scored成功の必要値は`canonical_db_access_attempts = 0`、`raw_text_fallback_attempts = 0`、`source_state_before == source_state_after`である。

### 実core統合受入テスト

G8の一回実行前に、使い捨ての7行fixtureで実v4 coreを最後まで通す。以下を必須とする。

1. strict preflight、`runtime-started`、実core採点、case result、summary、scored terminal manifestが一続きで成功する。
2. DB接続試行とraw fallback試行は実経路でhookにより失敗し、counterが実測値としてterminal manifestへ残る。
3. source-state変更は評価を失敗させ、変更前後の差を残す。
4. coreのpost-start例外は`runtime-error`として残り、scored扱いにならない。
5. 10 gateは各々個別にfalseとなるfixtureを持ち、gate値の固定化を防ぐ。

### 結果と停止

本番G8は一度だけ実行し、`results/first-run/`にterminal manifest、case results、summary、runtime audit、source state before/afterを残す。`runtime-error`、`preflight-failure`、gate失敗は評価失敗証跡であり、同じv12入力の再実行理由にしない。

## 9. G9-v12: evidence close

G9は評価値を都合よく解釈する工程ではない。次の事実を相互参照可能なclose recordへまとめる。

- G4 source eligibilityのカテゴリ構成、freshness、匿名化、過去比較
- G5のA/B独立性、rejected artifact、adjudication、merged corpus検証
- G6の原子的入力固定化とmanifest/attestation/source-state検証
- G7のblind入力制約と出力完全性
- G8の実core統合、10 gate、DB/raw fallback実測、terminal state
- 分類別の件数、期待分類との差、質問数、質問の必要性、既存語重複回避、失敗または限界

close recordは「v12で観測できた範囲」を記す。7例の結果から一般的なUX品質や全カテゴリの網羅性を主張しない。release、canonical vocabulary更新、既存証跡への書換えはG9の範囲外である。

## 10. 実行開始チェックリスト

### G4開始前

- [ ] v12最小構成1/2/2/2と7一意sessionが本書どおりである。
- [ ] v1-v11の既知source fingerprint一覧を比較専用に読み込める。
- [ ] 匿名化、PII、URL、path、credential、external-paste検査が候補validatorにある。

### G6開始前

- [ ] G4 reportとG5 merged corpusが7行、1/2/2/2、全session一意である。
- [ ] 独立B artifactがvalidatorを通るか、拒否証跡と適法な代替reviewがある。
- [ ] 入力固定化のfailure injectionとstrict metadata testsが通る。

### G7開始前

- [ ] 最終`frozen/`が一度だけ原子的に作成され、自己検証済みである。
- [ ] generatorが読む3入力と禁止入力がコードとテストで固定されている。

### G8開始前

- [ ] 実v4 coreを用いる7行使い捨て統合fixtureが通る。
- [ ] DB/raw hook、post-start runtime error、source-state mutation、10 gate個別failureを実測テストで通す。

### G9開始前

- [ ] G8 terminal manifestが`scored`または`runtime-error`のいずれかで不変に存在する。
- [ ] 実行されなかった工程を成功として記載していない。

## 11. 完了判定

v12の実作業完了は、G4からG9の全受入条件を満たしてG9 close recordが作られた時だけである。任意の停止条件に入った場合の完了は、その停止点までの不変証跡と次に必要なfresh inputまたは修正範囲を明記した時だけであり、未実行工程を完了とは扱わない。
