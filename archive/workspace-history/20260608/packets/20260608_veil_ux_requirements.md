# VEIL-UX-001 要件

## 1. 目的

VEIL の既存機能を、ユーザーが迷わずに呼べる形に整理する。
スクリプトの動作は変えない。入口だけを統一する。

## 2. 成功主語

ユーザーが `python shared/runtime/veil.py <subcommand>` 一本で全操作に入れる。
状態確認とセットアップ診断が単独コマンドで動く。

## 3. 範囲

### in scope

- `veil` 統一 CLI dispatcher の新規作成
  - 既存スクリプトへの thin dispatch
  - `veil normalize`, `veil sync`, `veil lint`, `veil db` を wrap する
- `veil status` サブコマンドの新規作成
  - canonical route の件数、mirror の存在、sync 対象状態を一覧表示する
- `veil doctor` サブコマンドの新規作成
  - DB 存在、rules/ mirror 存在、sync 対象ファイルの有効性、skill 配置を診断する

### out of scope

- 既存スクリプト (`veil-normalize.py`, `veil-sync.py`, `veil-lint.py`) の動作変更
- capture 後 auto-lint（機能追加であり整理ではない）
- DB schema 変更
- skill の内容変更

## 4. 機能要件

### F-01: dispatcher

- `python shared/runtime/veil.py normalize [args]` は `shared/runtime/veil-normalize.py [args]` と等価に動く
- `python shared/runtime/veil.py sync [args]` は `shared/runtime/veil-sync.py [args]` と等価に動く
- `python shared/runtime/veil.py lint [args]` は `shared/runtime/veil-lint.py [args]` と等価に動く
- `python shared/runtime/veil.py db [args]` は `shared/tools/veil-db.py [args]` と等価に動く
- 未知のサブコマンドはヘルプを表示して exit 1 する

### F-02: veil status

出力する項目:
- canonical DB のパスと存在有無、rule 件数（必須 / 推奨 / 観察 別）
- mirror ディレクトリのパスと最終更新日時
- sync 対象ファイルの件数と、全ファイルが最終 sync 済みかどうか

### F-03: veil doctor

診断する項目:
- `~/.veil/veil.db` の存在
- `~/.veil/rules/` の存在
- `~/.veil/config.json` の存在と sync target の登録有無
- 各 sync target ファイルの存在（ファイルが消えていたら WARN）
- Claude Code skill の配置（`~/.claude/commands/veil-capture.md`）

## 5. 非機能要件

- Python 標準ライブラリだけで動く（依存ゼロ維持）
- Python 3.8+ で動く
- Windows / macOS / Linux で動く

## 6. 前提と制約

- 既存スクリプトのパス・インターフェースは変えない
- `shared/runtime/` に配置する（mainline runtime shelf のルールに従う）
- `veil.py` というファイル名を使う（open decision: §7 参照）

## 7. オープン決定事項

| ID | 問い | 選択肢 | 現在の仮設 |
|---|---|---|---|
| OD-01 | `veil.py` の配置場所 | A: `shared/runtime/veil.py` / B: root `veil.py` | A（mainline runtime shelf） |
| OD-02 | dispatcher の実装方式 | A: subprocess 呼び出し / B: importlib 動的 import | A（シンプルで OS 依存が少ない） |
| OD-03 | `veil status` での rule 件数取得元 | A: DB 直読 / B: mirror markdown 読み | A（DB が canonical route） |

OD-01 は owner 確認が望ましい。root に置く場合はファイル taxonomy の root allowed list を更新する必要がある。

## 8. リスク

| リスク | 対応 |
|---|---|
| subprocess dispatch が Windows で path 解決できない | 実行前に絶対 path を組み立てて渡す |
| DB が存在しない環境で status が落ちる | DB 不在は skip 扱いにして診断結果に含める |
| veil-db.py が SQLite を直接読む前提で status を実装すると veil-db.py の変更に追従が必要 | veil status は `veil db readback --json` を subprocess 経由で呼ぶか、`veil_rule_store.py` を import して読む |
