# VEIL-OP-001 Bundle

- bundle id: `VEIL-OP-001`
- bundle type: `operation`
- status: `draft`
- success subject: `~/.veil/veil.db が初期化され、veil-status.py --check が全 OK になる`

---

## 要件マッピング

| 要件 | 対応 |
|---|---|
| 管理できる | veil-status.py --check が全 OK → canonical が存在し normalize / lint / sync が DB を参照できる |

---

## 現状

```
~/.veil/
  rules/       ← mirror は 19 ファイル存在（a.md 〜 w.md）
  targets.json ← sync target 1件登録済み
  config.json  ← sync_script 記録済み
  behavior.md  ← 存在
  veil.db      ← 存在しない（← これが問題）
```

`veil-status.py --check` の現出力：

```
[ERROR] ~/.veil/veil.db
[OK]    ~/.veil/rules/
[OK]    ~/.veil/targets.json
[OK]    sync target: ...
[OK]    skill: ...
```

---

## F-01: 操作設計

### 操作順序

```bash
# 1. スキーマ初期化
python shared/tools/veil-db.py init-db --db ~/.veil/veil.db

# 2. mirror → DB 取り込み
python shared/tools/veil-db.py import-rules \
  --db ~/.veil/veil.db \
  --rules-dir ~/.veil/rules

# 3. 取り込み結果確認
python shared/tools/veil-db.py readback --db ~/.veil/veil.db --json

# 4. セットアップ確認
python shared/runtime/veil-status.py --check
```

### 読み取り対象

| ファイル | 内容 |
|---|---|
| `~/.veil/rules/a.md` 〜 `w.md` | 19 ファイル。`## 必須 / ## 推奨 / ## 観察` のレベル見出し付き mirror |

### 注意点

- `~/.veil/veil.db` は新規作成される（既存データなし → データ損失リスクなし）
- mirror のレベル見出しはそのまま DB の `level` カラムへ取り込まれる
- `export-mirror` は今回行わない（mirror が既に正本として機能しているため、上書きリスクを避ける）
- init-db は idempotent（再実行してもスキーマだけ再作成）

### リスク

| リスク | 対策 |
|---|---|
| import-rules が特定行を読み飛ばす | readback --json で件数と内容を確認する |
| 取り込み後に mirror と DB が不一致になる | T-02 の readback で 1 行抜き取り確認を行う |
| veil.db 作成後に veil-sync.py が mirror を上書きする | sync は今回実行しない |

---

## チェックポイント構成

```
CP-1 DB 初期化完了
  └── T-01: init-db + import-rules

CP-2 検証完了
  └── T-02: readback + --check 確認
```

---

## T-01: DB 初期化と rules 取り込み

1. Task ID: `T-01`
2. 親テーマ: DB 初期化
3. 親チェックポイント: CP-1
4. active bundle id: `VEIL-OP-001`
5. active bundle type: `operation`
6. 成功主語: `~/.veil/veil.db が存在し、mirror の全 rules が取り込まれている`
7. 今回やる範囲: `init-db` と `import-rules` の実行
8. 今回やらない範囲: `export-mirror`、`veil-sync.py`、mirror ファイルへの変更、既存 rules の内容変更
9. 目的: canonical route を SQLite に確立し、normalize / lint / sync が DB を参照できる状態にする
10. このタスクが必要な理由: `~/.veil/veil.db` が存在しないため veil-status.py --check が [ERROR] になっている
11. 着手条件: `~/.veil/rules/` に .md ファイルが 1 件以上存在する（現状: 19 件確認済み）
12. 入力: `~/.veil/rules/*.md`（19 ファイル）
13. 読んでよい場所: `~/.veil/rules/*.md`、`shared/tools/veil-db.py --help`
14. 書いてよい場所: `~/.veil/veil.db`（新規作成のみ）
15. 触ってはいけない場所: `~/.veil/rules/`、`~/.veil/targets.json`、`~/.veil/config.json`、`~/.veil/behavior.md`、sync 先ファイル全て
16. やること:
    1. `python shared/tools/veil-db.py init-db --db ~/.veil/veil.db` を実行する
    2. `python shared/tools/veil-db.py import-rules --db ~/.veil/veil.db --rules-dir ~/.veil/rules` を実行する
17. 期待する出力: import-rules の完了メッセージ。エラーなし
18. 合格条件:
    - `~/.veil/veil.db` が存在する
    - import-rules がエラーなく完了する
19. 失敗条件: import-rules がエラーを出す、または `~/.veil/veil.db` が作成されない
20. 停止条件: import-rules が特定の rules を読み飛ばすエラーを出した場合（T-02 に差し戻す前に停止）
21. 差し戻し条件: T-02 の readback で件数が明らかに少ない場合
22. 人判断へ上げる条件: import-rules がレベル見出しを正しく解釈できない形式の rules ファイルを発見した場合
23. 証拠: init-db と import-rules の実行ログ
24. 結果の記録先: `index/project-current-work.md`（CP-1 通過として記録）
25. 最終判定者: owner

---

## T-02: 検証

1. Task ID: `T-02`
2. 親テーマ: 検証
3. 親チェックポイント: CP-2
4. active bundle id: `VEIL-OP-001`
5. active bundle type: `operation`
6. 成功主語: `readback が rules を返し、--check が全 OK になる`
7. 今回やる範囲: `readback --json` での件数確認、`veil-status.py --check` での全 OK 確認
8. 今回やらない範囲: DB の内容修正、mirror の変更
9. 目的: T-01 の取り込みが正しく完了したことを証拠で確認する
10. このタスクが必要な理由: DB write は可逆性が低いため、取り込み結果を確認して完了とする
11. 着手条件: T-01 完了、`~/.veil/veil.db` が存在する
12. 入力: `~/.veil/veil.db`
13. 読んでよい場所: `~/.veil/veil.db`（readback 経由）
14. 書いてよい場所: `index/project-current-work.md`（結果記録のみ）
15. 触ってはいけない場所: `~/.veil/veil.db`（readback は read-only）、`~/.veil/rules/`、その他全て
16. やること:
    1. `python shared/tools/veil-db.py readback --db ~/.veil/veil.db --json` を実行して件数と内容を確認する
    2. mirror の既知 rule（例: `current state → 今の状態`）が DB に存在することを確認する
    3. `python shared/runtime/veil-status.py --check` を実行して全 OK を確認する
    4. `python shared/runtime/veil-status.py` で rule count が 0 より大きいことを確認する
17. 期待する出力: readback が 1 件以上返す。`--check` が全 `[OK]`、exit 0
18. 合格条件:
    - `readback --json` が 1 件以上の rules を返す
    - `current state` が DB に存在し preferred が `今の状態` である
    - `veil-status.py --check` が全 `[OK]`、exit 0
    - `veil-status.py` の rule count が 0 より大きい
19. 失敗条件: 上記合格条件のいずれかを満たさない
20. 停止条件: readback が 0 件を返した場合（T-01 に差し戻し）
21. 差し戻し条件: `current state` が DB に存在しない場合（import-rules の読み取りに問題あり）
22. 人判断へ上げる条件: mirror の件数と DB の件数に大きな乖離がある場合
23. 証拠: readback --json の出力、veil-status.py --check の出力
24. 結果の記録先: `index/project-current-work.md`（bundle complete として記録）
25. 最終判定者: owner

---

## トレーサビリティ

| 要件 | タスク |
|---|---|
| 管理できる（DB が存在して --check が全 OK） | T-01 → T-02 |

---

## 巻き戻し手段

- `~/.veil/veil.db` を削除すれば初期化前の状態に完全に戻る
- mirror は変更しないため、mirror を source とした運用は継続できる
