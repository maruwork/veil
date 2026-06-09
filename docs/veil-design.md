# VEIL 設計書

runtime / support の詳細仕様。製品設計の正本は [veil-product-design.md](./veil-product-design.md) を参照。入口は [README.md](../README.md) を参照。

---

## 1. 設計方針

- **ローカル完結**: Python 標準ライブラリだけで動く
- **依存ゼロ**: `pip install` 不要
- **事前制御優先**: AI の出力後に修正するのでなく、事前に語彙ルールを読ませて出力を統一する
- **本線固定**: VEIL の主経路は `capture -> normalize -> sync -> lint` で完結する
- **主語固定**: VEIL は `AI-assisted technical writing` 向け terminology guardrail として扱う
- **要所厳格**: フローと高影響語だけを強く縛り、自然文全体は全面統制しない

---

## 2. 正本

| データ | 場所 | 役割 |
|---|---|---|
| 語彙ルール canonical route | `~/.veil/veil.db` | current canonical route |
| 語彙ルール markdown mirror | `~/.veil/rules/` | AI-readable markdown surface / transition mirror |
| 同期先リスト | `~/.veil/targets.json` | 同期対象ファイルのパス一覧 |
| sync script パス | `~/.veil/config.json` | `--add` 実行時に自動記録 |

`~/.veil/` はユーザーホームに固定。current phase では canonical route は SQLite、markdown rules は transition mirror として引き継がれる。

---

## 3. コンポーネント詳細

### 3-1. veil-capture スキル

AI との会話から英語・造語・略語を検出し、task close / 会話区切りの閉じ処理として current phase では SQLite canonical に記録し、その後 markdown mirror を更新する。

**配置場所**

| ツール | パス |
|---|---|
| Claude Code | `skills/claude-code/veil-capture.md` |
| Codex | `skills/codex/veil-capture/SKILL.md` |

**動作**

1. 会話や対象テキストから候補語を拾う
2. 一般動詞単体は抑え、状態語、判断語、構造語、運用ラベルを優先して候補語を一覧化する
3. 必要なら `shared/runtime/veil-normalize.py` で揺れ統合と既存 rule 照合を行う
4. 固有名として残す、一般語として訳す、定義語にする、禁止語にする、スキップする、のどれかへ先に判別する
5. 高需要語、高影響語、VEIL 基幹語から先に採用する
6. 低頻度語、文脈依存語、未確定の project 固有語はスキップする
7. ユーザーが採用語を決定した時点で current phase では `~/.veil/veil.db` canonical へ記録する
8. `shared/tools/veil-db.py export-mirror` 相当で `~/.veil/rules/` mirror を更新する
9. `shared/runtime/veil-sync.py` を実行して即時同期する

### 3-2. shared/runtime/veil-sync.py

SQLite canonical を優先し、必要時に `~/.veil/rules/` markdown mirror を再生成してから、各 AI ツール設定ファイルへ参照明記を反映する。

**authority**

- 読み取り: `~/.veil/veil.db`, `~/.veil/rules/*.md`, `~/.veil/targets.json`, `~/.veil/config.json`
- 書き込み: 同期先ファイル

**動作**

1. current phase で DB canonical が存在する場合は `~/.veil/rules/` mirror を再生成する
2. `~/.veil/rules/` mirror 以下の全 `.md` を読む
3. 語彙 rule と behavior 記述をまとめる
4. 登録済み同期先へ `VEIL_START` / `VEIL_END` 区間を書き込む

**コマンド**

```bash
python shared/runtime/veil-sync.py
python shared/runtime/veil-sync.py --add <path>
python shared/runtime/veil-sync.py --list
python shared/runtime/veil-sync.py --remove <path>
```

### 3-3. shared/runtime/veil-normalize.py

capture 後の候補語一覧を正規化し、既存 rule との照合結果を 2 グループで返す読み取り専用補助スクリプト。

**authority**

- 読み取り: `~/.veil/veil.db` または `~/.veil/rules/*.md`
- 非 authority: 補助出力、下書き候補一覧

**動作**

1. 小文字化、空白・ハイフン・アンダースコア揺れを吸収、軽い単複揺れを吸収
2. 正規化後クラスタごとに variant と出現回数をまとめる
3. 既存 rule があれば `既存一致` グループとして preferred と source_file を返す
4. 既存 rule がなければ `新規候補` グループとして target_file を返す

**出力フォーマット（テキスト）**

```
参照ルール: rules

既存一致:
- current state → 今の状態

新規候補:
- implementation plan x3 → i.md
```

**コマンド**

```bash
python shared/runtime/veil-normalize.py --stdin
python shared/runtime/veil-normalize.py --text "current state"
python shared/runtime/veil-normalize.py --json
```

### 3-4. shared/runtime/veil-lint.py

最終文章に登録済み原語が残っていないかを返答前 gate として検査する。

**authority**

- 読み取り: `~/.veil/veil.db` または `~/.veil/rules/*.md`
- 非 authority: capture report, 一時下書き

**動作**

1. SQLite canonical または `~/.veil/rules/*.md` mirror から `- original → preferred` 形式の rule を読む
2. 入力文を走査する
3. 登録済み原語が残っていたら違反候補として返す
4. inline code や code block は対象外にする
5. 登録済みルールの違反を fail-close として返す
6. violation には `直し方` と first-hit の `置換例` を返す

**コマンド**

```bash
python shared/runtime/veil-lint.py <file>
python shared/runtime/veil-lint.py --stdin
python shared/runtime/veil-lint.py --text "current state を整理した"
python shared/runtime/veil-lint.py --json
```

### 3-5. shared/runtime/veil-status.py

VEIL の状態確認とセットアップ診断を返す。引数なしで状態サマリー、`--check` でセットアップ診断を表示する。

**authority**

- 読み取り: `~/.veil/veil.db`, `~/.veil/rules/`, `~/.veil/targets.json`, skill ファイル
- 書き込み: なし

**動作（引数なし）**

1. canonical DB の存在と rule 件数を表示する
2. mirror の最終更新時刻を表示する
3. sync targets の登録数と存在確認を表示する
4. 常に exit 0

**動作（--check）**

1. DB, rules/, targets.json, 各 sync target, skill ファイルの存在を確認する
2. 各項目を `[OK]` / `[WARN]` / `[ERROR]` で返す
3. ERROR が 1 件以上なら exit 1、それ以外は exit 0

**コマンド**

```bash
python shared/runtime/veil-status.py
python shared/runtime/veil-status.py --check
python shared/runtime/veil-status.py --json
```

### 3-6. profile support tools

`shared/tools/veil-profile-audit.py`、`shared/tools/veil-profile-export.py`、`shared/tools/veil-db.py`、`shared/tools/veil_rule_store.py` は mainline runtime ではなく support runtime である。`shared/tools/veil-db.py` と `shared/tools/veil_rule_store.py` は SQLite canonical の schema / import / readback / upsert / mirror export を補助し、Stage 2 では `shared/tools/veil-profile-audit.py`、`shared/runtime/veil-normalize.py`、`shared/runtime/veil-lint.py` が `--db` で SQLite source を読める。

**authority**

- 読み取り: `~/.veil/veil.db`, `~/.veil/rules/*.md`
- 書き込み:
  - `shared/tools/veil-profile-audit.py`: なし
  - `shared/tools/veil-profile-export.py`: export output dir のみ
  - `shared/tools/veil-db.py`: 指定した SQLite DB path、指定した mirror directory
  - `shared/tools/veil_rule_store.py`: helper として SQLite DB / mirror directory を扱う

**用途**

1. `shared/tools/veil-profile-audit.py`
   - level 分布と legacy flat rule の有無を可視化する
   - Stage 2 第一波では `--db` による SQLite source 読取もできる
2. `shared/runtime/veil-normalize.py`
   - Stage 2 次波では `--db` による SQLite source 読取もできる
3. `shared/runtime/veil-lint.py`
   - Stage 2 最終波では `--db` による SQLite source 読取もできる
4. `shared/tools/veil-profile-export.py`
   - current default profile を section-aware のまま domain profile pack として書き出す
5. `shared/tools/veil-db.py`
   - SQLite canonical の `init-db / import-rules / readback / upsert-rule / export-mirror` を行う

**コマンド**

```bash
python shared/tools/veil-profile-audit.py
python shared/tools/veil-profile-audit.py --db workspace/veil_stage1_smoke.db
python shared/runtime/veil-normalize.py --text "current state" --db workspace/veil_stage1_smoke.db --json
python shared/runtime/veil-lint.py --text "current state" --db workspace/veil_stage1_smoke.db
python shared/tools/veil-db.py init-db --db workspace/veil_stage1_smoke.db
python shared/tools/veil-db.py import-rules --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_rules_fixture
python shared/tools/veil-db.py readback --db workspace/veil_stage1_smoke.db --json
python shared/tools/veil-db.py upsert-rule --db workspace/veil_stage1_smoke.db --term "current state" --preferred "今の状態"
python shared/tools/veil-db.py export-mirror --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_mirror
```

### 3-7. package import 構造

`shared/__init__.py`、`shared/runtime/__init__.py`、`shared/tools/__init__.py` は空ファイルだが意図的に存在する。`from shared.tools.veil_rule_store import ...` という package import パスを有効にするためであり、project root を `sys.path` に追加した上で `try: from shared.tools... except ModuleNotFoundError: from veil_rule_store...` の fallback pattern が正常に動くために必要である。削除しないこと。

---

## 4. データ形式

rule は次のように持つ。

```md
# c

- current state → 今の状態
- current issue → 現在の課題
```

新規追加時は preferred を確定し、canonical DB へ記録してから mirror を再生成する。

候補の意味は次の通り。

| 項目 | 意味 |
|---|---|
| p1 | 採用語。canonical route に入り、current phase では mirror と同期対象にもなる |
| p2 | 候補2。保持されるが同期対象外 |
| p3 | 候補3。保持されるが同期対象外 |

AI ツール設定ファイルへ同期されるのは候補1だけです。

---

## 5. 判別順

capture 後の候補は、少なくとも次の順で判別する。

1. 固有名として残す
2. 一般語として訳す
3. 定義語にする
4. 禁止語にする
5. スキップする

この判別補助は最終判定ではなく、先に見る順を決めるための補助である。

統制を弱める対象は次とする。

- 低頻度語
- 文脈依存が強い語
- 未確定の project 固有語
- コード識別子、ファイル名、path、CLI option などの機械処理語

---

## 6. core と profile

### VEIL core

- `veil-capture`
- `shared/runtime/veil-normalize.py`
- `shared/runtime/veil-sync.py`
- `shared/runtime/veil-lint.py`
- `shared/runtime/veil-status.py`
- `capture -> normalize -> sync -> lint` の運用骨格
- 判別順の骨格

### domain profile

- `~/.veil/veil.db`
- `~/.veil/rules/` mirror
- 禁止語集合
- 高需要語集合
- 定義語の扱い
- 固有名を残す基準
- `lint` 厳格度

現在の default profile は technical writing 向けとする。

current default profile を repo 外や別 bundle に切り出す時は、`shared/tools/veil-profile-export.py` で profile pack を作る。これは domain profile 分離のための support route であり、mainline の `capture -> normalize -> sync -> lint` 自体は変えない。

export manifest には `domain`, `intended_use`, `base_profile` を残し、technical writing default から業界別 profile へ分岐する時の最小契約とする。

---

## 7. 検査運用

- task close / 会話区切りで capture する
- 記録したら同期する
- 同期したら最終返答前に lint する
- lint 違反が出たら直して再検査する
- 原語を意図的に残す場合だけ理由を添えて許容する

capture では、採用語の選択肢を `- term（現状） → 候補1（候補1）| 候補2（候補2）` の形式で提示し、ユーザー選択後に canonical へ記録して `同期` まで完了する。

normalize の `既存一致:` グループは照合済みとして扱い、preferred を確認する。`新規候補:` グループは `x{N}` の N が大きい語から採用検討に回す。

現状確認は `shared/runtime/veil-status.py` を使う。セットアップ問題が疑われる場合は `--check` を実行する。

current default profile の棚卸しには `shared/tools/veil-profile-audit.py` を使う。これは read-only で、level 分布と legacy flat rule の残りを可視化する補助である。

domain profile を別配布単位として扱いたい場合は、`shared/tools/veil-profile-export.py` で current default profile を pack 化してから tuning や分岐を行う。
