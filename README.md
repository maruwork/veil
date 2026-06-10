# VEIL — Vocabulary Engine for Individual Language

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](shared/runtime/veil-sync.py)

---

## VEILとは

VEIL は、AI-assisted technical writing のための terminology guardrail です。current canonical route は SQLite で、`~/.veil/rules/` は AI に読ませる markdown surface と遷移ミラーとして扱います。実務で揺れた語を拾い、正規化し、AI に読ませ、最終出力が従っているかを返答前に検査します。

AI が勝手に決めた英語や造語が混入して理解できない、直しても次のセッションでまた戻る、技術文書や説明文の語彙がぶれる。

AI 利用が日常化するほど、この問題は増えます。VEIL は static な style guide ではなく、`capture -> normalize -> sync -> lint` の運用ループで語彙統制を回します。依存ゼロ、ローカル完結です。

**current canonical route は `~/.veil/veil.db`、`~/.veil/rules/` は AI-readable markdown surface と遷移ミラーです。`CLAUDE.md` / `AGENTS.md` / `.cursorrules` / `.github/copilot-instructions.md` / `GEMINI.md` / `.aider.conf.yml` は保存先ではなく、参照明記先です。**

---

## 仕組み

```
task close / 会話区切り
        ↓
  /veil-capture（スキル）
        ↓
  AI が問題語を抽出
        ↓
  一般動詞単体を抑え、状態語・判断語・構造語・運用ラベルを優先する
        ↓
  shared/runtime/veil-normalize.py で揺れ統合と既存ルール照合を行う
        ↓
  高需要語・高影響語だけを採用する
        ↓
  ~/.veil/veil.db に記録する  ← current canonical route
        ↓
  ~/.veil/rules/{letter}.md を生成する  ← 遷移ミラー / AI-readable surface
        ↓
  shared/runtime/veil-sync.py が参照明記先を更新する
        ↓
  CLAUDE.md / AGENTS.md / .cursorrules 等に参照を明記する
        ↓
  shared/runtime/veil-lint.py で最終返答前の文章を検査する
        ↓
次回セッションから AI が統一された語彙で出力する
```

---

## 採用の進め方

VEIL は、候補語を一気に全部登録する前提では運用しない。需要が高いものから少しずつ正本へ入れる。

基本ルールは次の通り。

- 先に判別する。識別子、固有名、説明語、プロジェクト固有語、境界が曖昧な語を混ぜたまま訳語決定へ進まない
- 高需要語から採用する。頻出で困る語、VEIL運用そのものに効く基幹語を先に固める
- 迷う語はスキップする。固有名か一般語か迷う語、別訳が衝突する語、まだ困り度が低い語は急いで正本化しない
- 一度に増やしすぎない。少数の採用語を `sync` と `lint` まで通し、効きが見えてから次の束を足す

厳しく縛る場所は全部ではなく要所だけにする。

- フローは強く縛る。task close / 会話区切りで `capture` を通し、最終返答前に `lint` を通す
- 高影響語は強く縛る。禁止語、VEIL 基幹語、高需要で揺れると困る語を優先する
- 低頻度語や曖昧語は急いで縛らない。スキップする
- 自然文全体を全面統制しない。自然な言い換え、機械処理語、文脈依存語まで hard gate にしない

---

## コンポーネント

| コンポーネント | 役割 |
|-------------|------|
| `/veil-capture` スキル | task close / 会話区切りで問題語を抽出し、SQLite canonical へ記録し、ミラー生成と sync まで進める |
| `~/.veil/veil.db` | SQLite canonical route |
| `~/.veil/rules/{letter}.md` | AI-readable markdown surface / 遷移ミラー |
| `shared/runtime/veil-normalize.py` | capture 後の候補語を正規化し、既存一致 / 新規候補 の 2 グループで返す |
| `shared/runtime/veil-sync.py` | 語彙ルールの参照明記を各 AI ツール設定ファイルへ反映する |
| `shared/runtime/veil-lint.py` | 最終文章に登録済み原語が残っていないかを返答前に検査する |
| `shared/runtime/veil-status.py` | canonical / ミラー / 同期対象 / skill の状態確認とセットアップ診断を表示する |
| `shared/tools/veil-profile-audit.py` | current profile の rule 件数と legacy flat の有無を棚卸しする補助 |
| `shared/tools/veil-profile-export.py` | current profile を domain profile pack として書き出す補助 |
| `shared/tools/veil-db.py` | SQLite canonical の `init-db / import-rules / readback / upsert-rule / export-mirror` を扱う補助 |

`shared/tools/veil-db.py` は SQLite canonical route を初期化・取込・読返しし、current phase では single rule の追加更新と markdown ミラーの生成も担う support route です。

### core と profile

- VEIL core
  - `capture`
  - `normalize`
  - `sync`
  - `lint`
  - `status`
  - 判別順の骨格
- domain profile
  - `~/.veil/rules/`
  - 禁止語集合
  - 高需要語集合
  - 定義語の扱い
  - 固有名を残す基準
  - `lint` の厳格度

現在の標準プロファイルは technical writing 向けとして扱う。

---

## セットアップ

Python 3.8 以上が必要です。

```bash
git clone https://github.com/fumimaruwork/veil.git
cd veil
```

### 1. 参照明記先ファイルを登録する

**この手順でスキルが参照する `~/.veil/config.json` が作成されます。スキルを使う前に必ず実行してください。**

```bash
python shared/runtime/veil-sync.py --add /path/to/CLAUDE.md
python shared/runtime/veil-sync.py --add /path/to/AGENTS.md
```

登録と同時に即時反映されます。対応ツールの例：

| ツール | 設定ファイル | マーカー形式 |
|--------|------------|------------|
| Claude Code | `CLAUDE.md` | `<!-- VEIL_START -->` |
| Codex | `AGENTS.md` | `<!-- VEIL_START -->` |
| Cursor | `.cursorrules` | `<!-- VEIL_START -->` |
| GitHub Copilot | `.github/copilot-instructions.md` | `<!-- VEIL_START -->` |
| Gemini CLI | `GEMINI.md` | `<!-- VEIL_START -->` |
| Aider | `.aider.conf.yml` | `# VEIL_START` |

`.yml` / `.yaml` / `.toml` / `.ini` / `.cfg` 拡張子のファイルは `# VEIL_START` / `# VEIL_END` マーカーを使用します。

### 2. スキルを配置する

```bash
bash install.sh
```

手動で配置する場合：

**Claude Code**

```bash
# macOS / Linux
cp skills/claude-code/veil-capture.md ~/.claude/commands/veil-capture.md
```

```powershell
# Windows (PowerShell)
Copy-Item skills\claude-code\veil-capture.md $env:USERPROFILE\.claude\commands\veil-capture.md
```

**Codex**

```bash
# macOS / Linux
cp -r skills/codex/veil-capture ~/.agents/skills/veil-capture
```

```powershell
# Windows (PowerShell)
Copy-Item -Recurse skills\codex\veil-capture $env:USERPROFILE\.agents\skills\veil-capture
```

---

## 使い方

### AIの語彙を捕捉する（メインワークフロー）

Claude Code で task close や会話区切りごとに実行：

```
/veil-capture
```

出力例：

```
- common asset（現状） → 共通資産（候補1）| コモンアセット（候補2）
- current state（現状） → 今の状態（候補1）| 現行状態（候補2）
- validator（現状） → バリデータ（候補1）| 検査器（候補2）

現状、または候補を選択してください。
```

ユーザーが選択した候補が preferred として canonical route に記録され、`~/.veil/rules/` ミラーを生成して AI ツール設定ファイルへ同期される。候補2・候補3 も alternatives として DB に記録される。

- **候補1**：推奨採用語
- **候補2**：必須表示の代替候補
- **候補3**：任意の追加候補

採用時の優先順は次を基本にする。

1. 頻出で困り度が高い語
2. VEIL運用そのものに効く基幹語
3. プロジェクト固有語
4. 低頻度語と境界が曖昧な語

4 は急いで登録せず、スキップして次回以降に判定してよい。

判別は少なくとも次の 5 方向に分ける。

1. 固有名として残す
2. 一般語として訳す
3. 定義語として固定する
4. 禁止語として落とす
5. まだ切れなければスキップする

候補語の揺れがある場合は、書き込み前に正規化用補助スクリプトを使う：

```bash
python shared/runtime/veil-normalize.py --stdin
python shared/runtime/veil-normalize.py --text "current states\ncurrent_state\nCurrent-State"
```

この補助スクリプトは以下を行う。

- 大文字小文字、ハイフン、アンダースコア、軽い単複の揺れ統合
- 正規化後クラスタごとに variant と出現回数をまとめる
- 既存 SQLite canonical / ミラーとの一致確認（`既存一致:` グループ）
- 既存一致がない語のミラー振分候補提示（`新規候補:` グループ）

出力例：

```
参照ルール: rules

既存一致:
- current state → 今の状態

新規候補:
- implementation plan x3 → i.md
```

`既存一致:` グループは照合済みとして扱い、preferred を確認する。`新規候補:` グループは `x{N}` の N が大きい語から採用検討に回す。最終判断は owner 側で行う。

VEIL 本体の製品設計は [docs/veil-product-design.md](docs/veil-product-design.md) を authority とします。設計原則は `高影響語だけ厳格に扱い、それ以外は自動採用しない` です。

外部テキスト（Codex の出力など）を解析する場合：

```
/veil-capture <対象テキストをここに貼り付け>
```

### ルールファイルの確認・編集

```
~/.veil/rules/
├── m.md    # m で始まる語のルール
├── u.md    # u で始まる語のルール
└── ...
```

各ファイルは直接編集できます。

```markdown
# u

- uncommitted → 未コミット
- untracked → 未追跡
- unstable wording → 不安定な表現
- update path → 更新経路
```

### 参照明記先を手動で更新する

```bash
python shared/runtime/veil-sync.py              # 全参照明記先を更新
python shared/runtime/veil-sync.py --list       # 登録済み一覧
python shared/runtime/veil-sync.py --add <path> # 参照明記先を追加
python shared/runtime/veil-sync.py --remove <path> # 参照明記先を解除
```

### 返答前に語彙を検査する

記録・同期した語彙を AI が実際の文章で使っているかは、`shared/runtime/veil-lint.py` で返答前に必ず検査する。

```bash
python shared/runtime/veil-lint.py <file>   # 返答文ファイルを検査
python shared/runtime/veil-lint.py --stdin  # stdin から検査
python shared/runtime/veil-lint.py --text "current state を整理した"  # 文字列を直接検査
```

- clean: 登録済み原語が文章に残っていない
- warning: 登録済み原語が文章に残っている（注意）。寄せ先を確認する
- violation: 登録済み原語が文章に残っている。preferred 語へ直して再検査する
- skip: `~/.veil/rules/` に rule がなければ異常終了しない

`warning` と `violation` では、`shared/runtime/veil-lint.py` が `直し方` と `置換例` も返す。まずその guidance に従って直し、必要なら行文全体を整える。

`veil-capture` は抽出・記録・同期、`shared/runtime/veil-lint.py` は返答前検査という役割に分けて運用する。

`lint` は prose 全体を全面統制するためではなく、登録済み高影響語と禁止語を守らせる gate として使う。

### VEIL の状態を確認する

canonical DB の rule 件数、ミラーの最終更新時刻、同期対象の状態を確認する：

```bash
python shared/runtime/veil-status.py
```

セットアップに問題がある場合は診断モードを使う：

```bash
python shared/runtime/veil-status.py --check
```

`[ERROR]` が出たら exit 1 になる。`[WARN]` のみなら exit 0 で続行できる。

### 現在の標準プロファイルを棚卸しする

`~/.veil/rules/` の rule 件数や、heading のない旧 flat rule がどれだけ残っているかは `shared/tools/veil-profile-audit.py` で見られます。

```bash
python shared/tools/veil-profile-audit.py
python shared/tools/veil-profile-audit.py --json
python shared/tools/veil-profile-audit.py --db workspace/veil_stage1_smoke.db
```

`audit`、`normalize`、`lint` はいずれも `--db` で SQLite source を読めます。`veil-normalize.py` は existing-match の返し方を維持しつつ、`source_type` と `source` でどちらの source を見たかを JSON で判別できます。`veil-lint.py` は rules-dir 互換を残したまま、`violation / warning / clean / skip` の返し方と exit code 契約を維持します。

### SQLite support route

SQLite canonical support route は `shared/tools/veil-db.py` です。workspace fixture を使う smoke では次のように確認できます。

```bash
python shared/tools/veil-db.py init-db --db workspace/veil_stage1_smoke.db
python shared/tools/veil-db.py import-rules --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_rules_fixture
python shared/tools/veil-db.py readback --db workspace/veil_stage1_smoke.db --json
python shared/tools/veil-db.py upsert-rule --db workspace/veil_stage1_smoke.db --term "current state" --preferred "今の状態"
python shared/tools/veil-db.py export-mirror --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_mirror
```

### 現在の標準プロファイルを書き出す

現在の標準プロファイルを technical writing 用の domain profile pack として切り出したい時は、`shared/tools/veil-profile-export.py` を使う。

```bash
python shared/tools/veil-profile-export.py --profile-name technical-writing-default
python shared/tools/veil-profile-export.py --profile-name finance-guardrail --domain finance --base-profile technical-writing-default
python shared/tools/veil-profile-export.py --profile-name technical-writing-default --output-dir workspace/profile-exports/custom-pack
```

既定では `workspace/profile-exports/<profile-name>/` に次を出力する。

- `*.md` rule files
- `manifest.json`

これは read-only export であり、canonical route と `~/.veil/rules/` ミラーを直接変更しない。
`manifest.json` には `domain`, `intended_use`, `base_profile` も入り、branch 元の profile 契約を残せる。

既存 pack から branch を起こす時は、base manifest を渡す。

```bash
python shared/tools/veil-profile-export.py --base-manifest workspace/profile-exports/technical-writing-default/manifest.json --profile-name medical-guardrail --domain medical
```

---

## ファイル構成

```
veil/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── install.sh                            # スキルファイルのデプロイスクリプト
├── shared/runtime/veil-normalize.py     # 候補語の正規化・統合候補確認
├── shared/runtime/veil-sync.py          # ルール同期スクリプト（コアツール）
├── shared/runtime/veil-lint.py          # 返答前語彙検査（コアツール）
├── shared/runtime/veil-status.py        # canonical / ミラー / 同期対象の状態確認
├── shared/tools/veil-profile-audit.py   # profile 棚卸し補助
├── shared/tools/veil-profile-export.py  # profile 書き出し補助
├── shared/tools/veil-db.py              # SQLite canonical support CLI
├── shared/tools/veil_rule_store.py      # SQLite schema / upsert / ミラー export shared helper
├── skills/                 # スキルテンプレート
│   ├── claude-code/
│   │   └── veil-capture.md
│   └── codex/
│       └── veil-capture/
│           └── SKILL.md
└── docs/
    └── veil-design.md      # 設計書
```

---

## ライセンス

[MIT License](LICENSE)
