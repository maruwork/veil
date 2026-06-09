# VEIL-UX-001 基本設計

## 1. 配置

| コンポーネント | 配置 | 種別 |
|---|---|---|
| `shared/runtime/veil.py` | 新規作成 | mainline runtime（dispatcher + status + doctor） |

既存スクリプトはパス・動作ともに変更なし。

## 2. コンポーネント構成

```
shared/runtime/veil.py
  ├── dispatch()       # normalize / sync / lint / db を subprocess で呼ぶ
  ├── cmd_status()     # DB 件数 + mirror 状態 + sync 状態を表示
  ├── cmd_doctor()     # 環境診断を実行して OK / WARN / ERROR を表示
  └── main()           # sys.argv を解析してルーティング
```

## 3. dispatch 設計

```
veil normalize [args]  ->  python <script_dir>/veil-normalize.py [args]
veil sync [args]       ->  python <script_dir>/veil-sync.py [args]
veil lint [args]       ->  python <script_dir>/veil-lint.py [args]
veil db [args]         ->  python <tools_dir>/veil-db.py [args]
veil status            ->  cmd_status() を直接実行
veil doctor            ->  cmd_doctor() を直接実行
```

`script_dir` は `Path(__file__).parent`（`shared/runtime/`）で解決する。
`tools_dir` は `Path(__file__).parent.parent / "tools"` で解決する。

subprocess は `sys.executable` を使い、Python パスを明示して呼ぶ。

## 4. veil status 設計

```
$ python shared/runtime/veil.py status

canonical:   ~/.veil/veil.db
  rule count:  42 (必須: 18  推奨: 14  観察: 10)
mirror:      ~/.veil/rules/  (last updated: 2026-06-07 10:32)
sync targets: 2 registered
  [OK]  C:\Users\...\CLAUDE.md
  [OK]  C:\Users\...\AGENTS.md
```

- DB が存在しない場合: `canonical: not found` を表示して終了（exit 0）
- `~/.veil/config.json` が存在しない場合: `sync targets: not configured` を表示する
- rule 件数は `veil_rule_store.py` の `load_rules()` 相当で取得するか、DB を直接 sqlite3 で読む

## 5. veil doctor 設計

```
$ python shared/runtime/veil.py doctor

[OK]   ~/.veil/veil.db
[OK]   ~/.veil/rules/
[OK]   ~/.veil/config.json
[OK]   sync target: C:\Users\...\CLAUDE.md
[WARN] sync target not found: C:\Users\...\old-path\AGENTS.md
[OK]   skill: ~/.claude/commands/veil-capture.md
[WARN] skill not installed: ~/.agents/skills/veil-capture/SKILL.md
```

診断項目と判定:

| 項目 | OK | WARN | ERROR |
|---|---|---|---|
| `~/.veil/veil.db` | 存在する | - | 存在しない |
| `~/.veil/rules/` | 存在する | - | 存在しない |
| `~/.veil/config.json` | 存在する | 存在しない（設定未完了） | - |
| sync target file | ファイルが存在する | ファイルが見つからない | - |
| Claude Code skill | `~/.claude/commands/veil-capture.md` 存在 | 存在しない | - |
| Codex skill | `~/.agents/skills/veil-capture/SKILL.md` 存在 | 存在しない | - |

終了コード:
- ERROR が 1 件以上: exit 1
- WARN のみ: exit 0（異常扱いにしない）
- 全 OK: exit 0

## 6. 除外設計

- `veil capture` サブコマンドは作らない。capture はスキル（AI インタラクション）であり CLI から呼ぶ設計ではない
- `veil install` は out of scope。セットアップ手順は README に残す

## 7. テスト方針

- `veil.py` は stdlib のみで動くため、Python 3.8 環境があれば即テスト可能
- smoke test: `python shared/runtime/veil.py status` と `python shared/runtime/veil.py doctor` が exit 0 で返ること
- dispatch test: `python shared/runtime/veil.py lint --help` が veil-lint.py の help と同じ内容を返すこと

## 8. 影響範囲

| ファイル | 変更 |
|---|---|
| `shared/runtime/veil.py` | 新規作成 |
| `README.md` | `veil` コマンド説明を追記 |
| `docs/veil-design.md` | dispatcher コンポーネント追記 |
| `index/project-boundary-register.md` | `shared/runtime/veil.py` をエントリーに追加 |
| `index/project-file-taxonomy.md` | `shared/runtime/veil.py` を mainline runtime に追加 |

既存スクリプトへの変更: なし
