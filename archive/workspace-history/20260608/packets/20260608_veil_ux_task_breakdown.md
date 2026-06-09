# VEIL-UX-001 タスク分割

## チェックポイント構成

```
CP-1 設計確定
  └── T-01: 要件・基本設計レビュー（owner 確認）
CP-2 dispatcher 実装
  └── T-02: shared/runtime/veil.py（dispatch + main）実装
CP-3 status / doctor 実装
  ├── T-03: veil status 実装
  └── T-04: veil doctor 実装
CP-4 検証・書き戻し
  ├── T-05: smoke verify
  └── T-06: doc / governance 書き戻し
```

---

## T-01: 設計確定

- 親 CP: CP-1
- 目的: 実装前に要件と設計の open decision を owner に確認する
- 着手条件: requirements と basic design が workspace/ にある
- 確認事項:
  - OD-01: `veil.py` は `shared/runtime/` に置く（root には置かない）でよいか
  - OD-02: dispatch は subprocess 呼び出しでよいか
  - OD-03: rule 件数取得は sqlite3 直読みでよいか
- 合格条件: owner が上記 3 点を確認済みである
- 最終判定者: owner

---

## T-02: dispatcher 実装

- 親 CP: CP-2
- 着手条件: T-01 完了
- 読む場所: `workspace/20260608_veil_ux_basic_design.md` §3
- 書く場所: `shared/runtime/veil.py`（新規）
- 触ってはいけない場所: 既存スクリプト全て、`index/`, `common/`
- やること:
  1. `shared/runtime/veil.py` を新規作成する
  2. `main()` で `sys.argv[1]` を読み、サブコマンドにルーティングする
  3. `normalize / sync / lint / db` は `subprocess.run()` + `sys.executable` で dispatch する
  4. 未知サブコマンドはヘルプを表示して exit 1 する
- 合格条件:
  - `python shared/runtime/veil.py normalize --help` が veil-normalize.py の help を返す
  - `python shared/runtime/veil.py lint --help` が veil-lint.py の help を返す
  - 未知コマンドで exit 1 する
- 証拠: コマンド実行結果

---

## T-03: veil status 実装

- 親 CP: CP-3
- 着手条件: T-02 完了
- 読む場所: `workspace/20260608_veil_ux_basic_design.md` §4、`shared/tools/veil_rule_store.py`
- 書く場所: `shared/runtime/veil.py` に `cmd_status()` を追加
- やること:
  1. `~/.veil/veil.db` を sqlite3 で読み、rule 件数を level 別に集計する
  2. `~/.veil/rules/` の最終更新日時を取得する
  3. `~/.veil/config.json` から sync targets を読み、各ファイルの存在を確認する
  4. 結果を整形して stdout に出力する
- 合格条件:
  - DB あり環境で rule 件数が正しく表示される
  - DB なし環境で `not found` 表示されて exit 0 する
- 証拠: 実行結果スクリーンショットまたはコマンド出力

---

## T-04: veil doctor 実装

- 親 CP: CP-3
- 着手条件: T-02 完了（T-03 と並行可）
- 読む場所: `workspace/20260608_veil_ux_basic_design.md` §5
- 書く場所: `shared/runtime/veil.py` に `cmd_doctor()` を追加
- やること:
  1. `~/.veil/veil.db`, `~/.veil/rules/`, `~/.veil/config.json` の存在を確認する
  2. config.json から sync targets を読み、各ファイルの存在を確認する
  3. Claude Code skill (`~/.claude/commands/veil-capture.md`) の存在を確認する
  4. Codex skill (`~/.agents/skills/veil-capture/SKILL.md`) の存在を確認する
  5. 結果を `[OK] / [WARN] / [ERROR]` 形式で出力する
  6. ERROR があれば exit 1 する
- 合格条件:
  - 正常環境で全 OK が出て exit 0 する
  - skill 未配置環境で WARN が出て exit 0 する
  - DB 不在環境で ERROR が出て exit 1 する
- 証拠: 実行結果

---

## T-05: smoke verify

- 親 CP: CP-4
- 着手条件: T-03, T-04 完了
- やること:
  1. `python shared/runtime/veil.py status` が正常終了する
  2. `python shared/runtime/veil.py doctor` が正常終了する（WARN は許容）
  3. `python shared/runtime/veil.py normalize --stdin` が veil-normalize.py と同じ動作をする
  4. `python shared/runtime/veil.py lint --text "test"` が veil-lint.py と同じ動作をする
- 合格条件: 上記 4 コマンド全て期待通りに動く
- 証拠: コマンド実行ログ

---

## T-06: doc / governance 書き戻し

- 親 CP: CP-4
- 着手条件: T-05 完了
- 書く場所:
  - `README.md`: `veil status`, `veil doctor`, dispatcher の使い方を追記
  - `docs/veil-design.md`: dispatcher コンポーネントを追記
  - `index/project-boundary-register.md`: `shared/runtime/veil.py` を追加
  - `index/project-file-taxonomy.md`: `shared/runtime/veil.py` を mainline runtime に追加
  - `index/project-current-work.md`: bundle を complete に更新
- 合格条件: 上記全ファイルが最新状態を反映している
- 最終判定者: owner

---

## トレーサビリティ

| 要件 | 設計 | タスク |
|---|---|---|
| F-01 dispatcher | §3 dispatch 設計 | T-02 |
| F-02 veil status | §4 veil status 設計 | T-03 |
| F-03 veil doctor | §5 veil doctor 設計 | T-04 |
| smoke test | §7 テスト方針 | T-05 |
| doc 更新 | §8 影響範囲 | T-06 |
