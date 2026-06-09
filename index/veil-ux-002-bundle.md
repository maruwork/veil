# VEIL-UX-002 Bundle

- bundle id: `VEIL-UX-002`
- bundle type: `mainline`
- status: `active`
- success subject: `normalize 実行後に迷わず判断できる。おかしい時とセットアップ時に状態を確認できる`

---

## 要件マッピング

| 要件 | 対応機能 | ギャップ → タスク |
|---|---|---|
| ルール通り語句を摘出する | normalize 補助 | 旧ロジック残存 → T-01 |
| かんたんに登録できる | upsert-rule（済） | なし |
| 管理できる | ツール不在 | 状態・セットアップ確認 → T-02 |
| AI が必ず守る | lint / sync（済） | docs が旧設計を記述 → T-04 |

---

## F-01: normalize シンプル化

### 削除する関数

- `classify_candidate_hint()`
- `suggest_level()`
- `suggest_selection_hint()`
- `suggest_retention_hint()`
- `suggest_shortlist_hint()`
- `priority_hint()`
- `is_general_verb_family()`
- `general_verb_family_forms()`

### 削除する定数

- `TICKET_ID_RE`
- `ALL_CAPS_RE`
- `LOWER_PHRASE_RE`
- `LOWER_SINGLE_WORD_RE`
- `NOUN_LIKE_SUFFIXES`
- `GENERAL_VERB_LIKE_WORDS`

### 残す関数

| 関数 | 理由 |
|---|---|
| `cluster_candidates()` | 骨格は残す。hints 関連の呼び出しを除去して簡略化 |
| `target_file_for()` | 新規候補の書き先ファイルを示す |
| `load_rule_index_for_source()` | 既存ルールとの照合 |
| `parse_candidate_lines()` | 入力パース |
| `print_text_result()` | 出力（新フォーマットで書き直す） |
| `compact_source_label()` | ソース表示の整形 |
| `print_conflicts()` | 競合警告 |

### cluster_candidates() 簡略後の返値

```python
{
  "normalized": str,
  "status": "existing-match" | "new-candidate",
  "occurrence_count": int,
  "representative": str,
  "variants": [str],
  # existing-match のみ
  "preferred": str,
  "source_file": str,
  # new-candidate のみ
  "target_file": str,
}
```

### 新しいテキスト出力フォーマット

```
参照ルール: rules

既存一致:
- current state → 今の状態
- implementation → 実装

新規候補:
- implementation plan x3 → i.md
- current phase → c.md
- close x2 → special.md
```

- グループが空の場合はそのグループを表示しない
- `x{count}` は occurrence_count > 1 の時だけ付ける

### 新しい JSON 出力フォーマット

```json
{
  "source_type": "db",
  "source": "...",
  "candidate_count": 6,
  "existing": [
    {
      "normalized": "current state",
      "preferred": "今の状態",
      "source_file": "c.md",
      "occurrence_count": 1,
      "variants": ["current state"]
    }
  ],
  "new": [
    {
      "normalized": "implementation plan",
      "representative": "implementation plan",
      "occurrence_count": 3,
      "target_file": "i.md",
      "variants": ["implementation plan", "Implementation Plan"]
    }
  ]
}
```

---

## F-02/F-03: veil-status.py

### 決定事項

- 実装先: `shared/runtime/veil-status.py`（新規作成）
- F-02（状態確認）と F-03（セットアップ確認）を 1 スクリプトに統合する
- 引数なし = F-02（状態表示）、`--check` = F-03（セットアップ診断）

### コマンド

```bash
python shared/runtime/veil-status.py
python shared/runtime/veil-status.py --check
python shared/runtime/veil-status.py --db ~/.veil/veil.db
python shared/runtime/veil-status.py --json
```

### F-02: 引数なし時の出力

```
canonical:   ~/.veil/veil.db
  rule count:  42
mirror:      ~/.veil/rules/  (last updated: 2026-06-07 10:32)
sync targets: 2 registered
  [OK]   C:\Users\...\CLAUDE.md
  [MISS] C:\Users\...\old-path\AGENTS.md
```

- DB 不在: `canonical: not found`
- config.json 不在: `sync targets: not configured`
- 常に exit 0

### F-03: --check 時の出力

```
[OK]   ~/.veil/veil.db
[OK]   ~/.veil/rules/
[OK]   ~/.veil/config.json
[OK]   sync target: C:\Users\...\CLAUDE.md
[WARN] sync target not found: C:\Users\...\old-path\AGENTS.md
[OK]   skill: ~/.claude/commands/veil-capture.md
[WARN] skill not installed: ~/.codex/skills/veil-capture/SKILL.md
```

- ERROR が 1 件以上: exit 1
- WARN のみ / 全 OK: exit 0

### 読み取り先

| 情報 | 取得元 |
|---|---|
| rule 件数 | `veil_rule_store.readback_rules(db_path)` |
| mirror 最終更新 | `~/.veil/rules/` ディレクトリの最終更新時刻 |
| sync targets | `~/.veil/config.json` の `targets` キー |
| skill 配置 | `~/.claude/commands/veil-capture.md`、`~/.codex/skills/veil-capture/SKILL.md` |

---

## T-04 docs 書き戻し対象

| ファイル | 更新内容 |
|---|---|
| `docs/veil-design.md` | §3-3 normalize 新フォーマット、§3-4 lint レベル記述削除、§4 mirror フォーマット更新、§5 rule 3層 削除、§7 core/profile 更新、§8 検査運用 更新、veil-status.py 追加 |
| `docs/veil-product-design.md` | §4.4 lint レベル記述削除、§5.3 owner override レベル記述削除、§7 Rule Levels 削除 |
| `README.md` | normalize 出力フォーマット変更、veil-status.py 使い方追加 |
| `AGENTS.md` | normalize 動作説明の更新 |
| `index/project-current-work.md` | bundle を complete に更新 |

---

## チェックポイント構成

```
CP-1 normalize シンプル化
  └── T-01: veil-normalize.py 改修

CP-2 管理ツール新設
  └── T-02: veil-status.py 新設

CP-3 検証・書き戻し
  ├── T-03: smoke verify
  └── T-04: docs / governance 書き戻し
```

---

## T-01: veil-normalize.py 改修

1. Task ID: `T-01`
2. 親テーマ: normalize 出力シンプル化
3. 親チェックポイント: CP-1
4. active bundle id: `VEIL-UX-002`
5. active bundle type: `mainline`
6. 成功主語: `veil-normalize.py が 既存一致 / 新規候補 の 2 グループだけを返す`
7. 今回やる範囲: §F-01 の削除リストにある関数・定数の削除、`cluster_candidates()` の hints 除去、`print_text_result()` 新フォーマット実装、JSON 出力の新フォーマット実装
8. 今回やらない範囲: `target_file_for()`、`load_rule_index_for_source()`、`parse_candidate_lines()`、`--db` / `--rules-dir` オプションへの変更
9. 目的: normalize 出力の複雑さを取り除き、candidate を迷わず判断できるようにする
10. このタスクが必要な理由: 「ルール通り語句を摘出する」という要件 1 を妨げる旧ロジックが残存しているため
11. 着手条件: `index/veil-ux-002-bundle.md` が index/ にある
12. 入力: `shared/runtime/veil-normalize.py`（現行ファイル）
13. 読んでよい場所: `index/veil-ux-002-bundle.md`、`shared/tools/veil_rule_store.py`、`shared/runtime/veil-normalize.py`
14. 書いてよい場所: `shared/runtime/veil-normalize.py` のみ
15. 触ってはいけない場所: `target_file_for()`、`load_rule_index_for_source()`、`parse_candidate_lines()`、`--db` / `--rules-dir` オプション、他ファイル全て
16. やること:
    1. §削除する関数・定数 をすべて削除する
    2. `cluster_candidates()` から hints 関連の呼び出しを除去し、返値を §簡略後の返値 に合わせる
    3. `print_text_result()` を新フォーマットで書き直す
    4. `main()` の JSON 出力を新フォーマットに合わせる
17. 期待する出力: 2グループ（既存一致 / 新規候補）のみ返す veil-normalize.py
18. 合格条件:
    - `python shared/runtime/veil-normalize.py --text "current state"` で既存一致グループに current state が出る
    - `python shared/runtime/veil-normalize.py --text "implementation plan"` で新規候補グループに出る
    - `--json` の出力に hints 関連フィールドが含まれない
    - §削除する関数・定数 がファイルに 1 件も残っていない
19. 失敗条件: 削除対象の関数・定数が 1 件でも残っている、または既存照合が動かない
20. 停止条件: `load_rule_index_for_source()` や `parse_candidate_lines()` を変更する必要が出てきた場合（スコープ外判断が必要）
21. 差し戻し条件: 合格条件を 1 つでも満たさない場合
22. 人判断へ上げる条件: 削除対象外の関数に hints 呼び出しが混在していて除去の可否が判断できない場合
23. 証拠: `--text "current state"` と `--text "implementation plan"` の実行結果、`--json` の出力
24. 結果の記録先: `index/project-current-work.md`（CP-1 通過として記録）
25. 最終判定者: owner

---

## T-02: veil-status.py 新設

1. Task ID: `T-02`
2. 親テーマ: 管理ツール新設
3. 親チェックポイント: CP-2
4. active bundle id: `VEIL-UX-002`
5. active bundle type: `mainline`
6. 成功主語: `veil-status.py が状態確認とセットアップ確認を返す`
7. 今回やる範囲: `shared/runtime/veil-status.py` の新規作成（F-02 引数なし、F-03 `--check`、`--json` 対応）
8. 今回やらない範囲: 既存スクリプトへの変更、veil-sync.py への変更、skill ファイルへの変更
9. 目的: 「管理できる」という要件 3 を満たす状態・セットアップ確認手段を作る
10. このタスクが必要な理由: 現状、rule 件数・mirror 状態・sync targets・skill 配置を一覧確認できる手段がないため
11. 着手条件: `index/veil-ux-002-bundle.md` が index/ にある（T-01 とは独立して着手可）
12. 入力: なし（新規ファイル）
13. 読んでよい場所: `index/veil-ux-002-bundle.md` §F-02/F-03、`shared/tools/veil_rule_store.py`（readback_rules のみ参照）
14. 書いてよい場所: `shared/runtime/veil-status.py`（新規作成のみ）
15. 触ってはいけない場所: `veil_rule_store.py`、その他既存スクリプト全て
16. やること:
    1. `parse_args()` — `--check`、`--db`、`--json` オプションを定義する
    2. `collect_status(db_path)` — F-02 の各情報（rule 件数・mirror 最終更新・sync targets 存在確認）を収集して dict で返す
    3. `collect_setup(db_path)` — F-03 の各項目（DB / rules/ / config.json / sync targets / skill）を確認して OK/WARN/ERROR で返す
    4. `print_status(payload)` / `print_setup(payload)` — テキスト出力
    5. exit code: `--check` 時のみ ERROR が 1 件以上で exit 1、それ以外は exit 0
17. 期待する出力: F-02 は状態サマリー、F-03 は OK/WARN/ERROR の項目別診断
18. 合格条件:
    - DB あり環境（`~/.veil/veil.db`）で rule 件数が正しく表示される
    - DB なし環境で `canonical: not found` が表示されて exit 0 する
    - `--check` で全 OK のとき exit 0
    - `--check` で DB 不在のとき ERROR が出て exit 1
    - skill 未配置のとき WARN が出て exit 0
19. 失敗条件: 上記合格条件のいずれかを満たさない
20. 停止条件: `~/.veil/config.json` の実際の schema が設計と異なる場合（要確認）
21. 差し戻し条件: 合格条件を 1 つでも満たさない場合
22. 人判断へ上げる条件: `~/.veil/config.json` に `targets` キー以外の構造が使われていて読み方が不明な場合
23. 証拠: DB あり/なし両環境、`--check` 正常・異常の実行結果
24. 結果の記録先: `index/project-current-work.md`（CP-2 通過として記録）
25. 最終判定者: owner

---

## T-03: smoke verify

1. Task ID: `T-03`
2. 親テーマ: 検証
3. 親チェックポイント: CP-3
4. active bundle id: `VEIL-UX-002`
5. active bundle type: `mainline`
6. 成功主語: `T-01 と T-02 の成果が実環境で期待通りに動く`
7. 今回やる範囲: normalize と veil-status.py の動作確認
8. 今回やらない範囲: docs 更新、コード修正（修正が必要なら T-01/T-02 に差し戻す）
9. 目的: CP-3 通過前に実装の合格を証拠で確認する
10. このタスクが必要な理由: T-01/T-02 の合格条件を実行ログで証拠化するため
11. 着手条件: T-01 と T-02 の両方が完了している
12. 入力: 実装済み `veil-normalize.py`、`veil-status.py`、`~/.veil/veil.db`
13. 読んでよい場所: `index/veil-ux-002-bundle.md` §T-01 合格条件、§T-02 合格条件
14. 書いてよい場所: `index/project-current-work.md`（結果記録のみ）
15. 触ってはいけない場所: `veil-normalize.py`、`veil-status.py`（smoke 中に修正しない）
16. やること:
    1. `python shared/runtime/veil-normalize.py --text "current state"` を実行して既存一致グループを確認する
    2. `python shared/runtime/veil-normalize.py --text "implementation plan"` を実行して新規候補グループを確認する
    3. `python shared/runtime/veil-normalize.py --json --text "current state"` で JSON フォーマットを確認する
    4. `python shared/runtime/veil-status.py` で状態表示を確認する
    5. `python shared/runtime/veil-status.py --check` でセットアップ診断を確認する
17. 期待する出力: 各コマンドが §合格条件 を満たす実行ログ
18. 合格条件: T-01 と T-02 の合格条件を全て満たす実行ログが得られている
19. 失敗条件: いずれかのコマンドが期待と異なる出力を返す
20. 停止条件: smoke 中に修正が必要な箇所を発見した場合（修正は T-01/T-02 に差し戻す）
21. 差し戻し条件: 実行ログが合格条件を満たさない場合は T-01 または T-02 に差し戻す
22. 人判断へ上げる条件: DB が存在せず smoke が実行できない場合
23. 証拠: 実行ログ全件
24. 結果の記録先: `index/project-current-work.md`（CP-3 前半通過として記録）
25. 最終判定者: owner

---

## T-04: docs / governance 書き戻し

1. Task ID: `T-04`
2. 親テーマ: docs 整合
3. 親チェックポイント: CP-3
4. active bundle id: `VEIL-UX-002`
5. active bundle type: `mainline`
6. 成功主語: `全ドキュメントが現行実装と矛盾しない`
7. 今回やる範囲: §T-04 docs 書き戻し対象 に列挙した 5 ファイルの更新
8. 今回やらない範囲: runtime コードの変更、新機能追加
9. 目的: 「AI が必ず守る」という要件 4 を満たすために、AI が読む docs を現行実装と一致させる
10. このタスクが必要な理由: docs に旧設計（level system、旧 normalize 出力）が残っており AI が誤読する
11. 着手条件: T-03 smoke verify 完了
12. 入力: 実装済みの `veil-normalize.py`、`veil-status.py`、現行の各 docs ファイル
13. 読んでよい場所: `index/veil-ux-002-bundle.md`、実装済みスクリプト（動作確認のため）
14. 書いてよい場所: §T-04 docs 書き戻し対象 に列挙した 5 ファイルのみ
15. 触ってはいけない場所: runtime スクリプト、`index/veil-ux-002-bundle.md`、`common/`
16. やること: §T-04 docs 書き戻し対象 の各ファイルを現行実装に合わせて更新する
17. 期待する出力: docs が現行実装と矛盾しない状態
18. 合格条件: §T-04 docs 書き戻し対象 の全ファイルが現行実装を正しく記述している
19. 失敗条件: 更新後の docs に現行実装と矛盾する記述が 1 件でも残っている
20. 停止条件: docs の更新が runtime コードの変更を要求する場合（設計の矛盾として人判断へ上げる）
21. 差し戻し条件: 更新後に owner が矛盾を指摘した場合
22. 人判断へ上げる条件: docs と実装の間に仕様上の矛盾を発見した場合
23. 証拠: 更新後の各ファイルの差分
24. 結果の記録先: `index/project-current-work.md`（bundle complete として記録）
25. 最終判定者: owner

---

## トレーサビリティ

| 要件 | タスク |
|---|---|
| ルール通り語句を摘出する | T-01 |
| 管理できる | T-02 |
| smoke test | T-03 |
| AI が必ず守る（docs 整合） | T-04 |
