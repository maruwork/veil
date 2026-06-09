# VEIL 直近修正案の再構成メモ

作成日: 2026-06-07

## 目的

直近で詰めていた VEIL の修正案が正式な記録として残っていない前提で、現作業ツリー差分と直近コミットから意図を再構成する。

## 再構成に使った根拠

- 現作業ツリー差分
  - `README.md`
  - `docs/veil-design.md`
  - `docs/manual.html`
  - `app.py`
  - `veil-sync.py`
  - `install-startup.py`
  - `skills/claude-code/veil-capture.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `CLAUDE.md`
  - `CHANGELOG.md`
- 直近コミット
  - `35fe44fe8067a47d4c5e9958f3bd3001606cd128`
    - `feat: veil-capture をゲート付き11段階手順に刷新`
  - `8839c5024d259a9657bd160b58e8ce8aaf6a6276`
    - `docs: CLAUDE.md に造語・短縮英語禁止ルールを追加`
  - `397cc7e76fdeaca65b96db794cc100ff526f4ed3`
    - `feat: veil-sync に行動ルール(behavior.md)の同期を追加`

## ほぼ確実に進めていた修正テーマ

### 1. 正本を `~/.veil/rules/` へ寄せる

直近の未記録差分は、VEIL の正本を SQLite や `app.py` 側ではなく `~/.veil/rules/` に明確に寄せる方向で揃っている。

差分上の兆候:

- `README.md`
  - Web UI を「補助機能」と明記
  - `veil-sync.py` は `~/.veil/rules/` と `behavior.md` だけを同期すると説明
- `docs/manual.html`
  - 正本データを `~/.veil/rules/` と記述
  - `vocab.db` を補助データに格下げ
- `docs/veil-design.md`
  - `~/.veil/rules/` を正本として説明

### 2. `veil-sync.py` から VEIL サーバー依存を外す

未記録差分の中心はこれ。

意図:

- `app.py` 起動状態に依存せず同期できるようにする
- 同期対象を `~/.veil/rules/*.md` と `~/.veil/behavior.md` に限定する
- 参照明記先への反映機能を `veil-sync.py` 単体で完結させる

差分上の具体:

- `veil-sync.py`
  - `urllib.request` 削除
  - `VEIL_URL = "http://127.0.0.1:8080/vocab/prompt"` 削除
  - `fetch_vocab()` 削除
  - `--stdin` モード削除
  - `behavior.md` を組み込む同期へ整理
- `CHANGELOG.md`
  - `veil-sync.py` を rules-only 同期へ整理した記述を追加

### 3. `app.py` の自動同期責務を廃止する

意図:

- `app.py` はローカルUIに限定する
- 語彙DB変更をフックして参照明記先まで自動反映する責務を外す

差分上の具体:

- `trigger_sync()` 削除
- `SYNC_SCRIPT` / `SYNC_LOG` 削除
- `/vocab/prompt` エンドポイント削除
- upsert/delete 後の `trigger_sync()` 呼び出し削除

### 4. `veil-capture` スキルの終端条件を新設計へ合わせる

意図:

- スキルの完了条件を「VEIL サーバー接続確認」ではなく「`veil-sync.py` 実行結果確認」へ寄せる
- 正本の更新と同期確認を重視する

差分上の具体:

- `skills/claude-code/veil-capture.md`
- `skills/codex/veil-capture/SKILL.md`

いずれも:

- VEIL サーバー未接続確認の文脈を削除
- 「base rules のみ同期」の条件を削除
- 完了条件を単純化

### 5. ドキュメント全体を新運用へ再整列する

意図:

- VEIL の主役を `app.py` から `veil-capture` + `~/.veil/rules/` + `veil-sync.py` に置き直す
- Web UI は補助、同期は手動実行という運用へ合わせる

差分上の具体:

- `README.md`
  - UI をメインワークフローから外す
- `docs/manual.html`
  - 自動同期説明を手動同期説明へ変更
- `docs/veil-design.md`
  - `/vocab/prompt` と `--stdin` の記述を削除
- `install-startup.py`
  - `sync-error.log` 表示削除

## 直近コミットとの流れ

履歴として見える流れは次の通り。

1. `veil-capture` を厳格なゲート手順へ刷新
2. `CLAUDE.md` に造語・短縮英語禁止を追加
3. `veil-sync.py` に `behavior.md` 同期を追加
4. その次の未記録ワークとして
   - `veil-sync.py` の rules-only 化
   - `app.py` の自動同期撤去
   - README / 設計書 / マニュアル / スキルの追従
   をまとめて進めていた可能性が高い

## まだ記録されていない論点

未記録差分の意図はかなり明確だが、完全には閉じていない論点も残る。

### 1. `vocab.db` の置き場

ガバナンス文書では `shared/vocab.db` 扱いが残っている一方、実装は repo 直下の `vocab.db` を使っている。

- `index/project-template-adoption-packet.md`
- `index/project-file-taxonomy.md`
- `app.py`

このため、次のどちらかを選んで統一する必要がある。

- 実装を `shared/vocab.db` に寄せる
- ガバナンス文書を repo 直下 `vocab.db` に寄せる

### 2. `docs/manual.html` の旧多言語残骸

`/docs/manual/en.html` などへのリンクと「現在の言語ペア」という記述が残っている。
現行実装と整合しないため、旧仕様の名残として整理対象。

### 3. `docs/veil-design.md` と UI 実装の細部不一致

設計書では「実変換は候補1だけ」という読み方になるが、`ui/js/convert.js` では `p1` が空なら `p2` / `p3` にフォールバックする。

ここは次のどちらかを選んで揃える必要がある。

- 実装を `p1` のみに厳格化する
- 設計書をフォールバック実装に合わせる

## いま最も自然な復元結論

直近で詰めていた未記録修正案は、要約すると次の一文に集約できる。

`VEIL の正本を ~/.veil/rules に固定し、veil-sync.py を app.py 非依存の同期器へ整理し、Web UI は補助機能へ位置付け直す。`

## 次に記録化すべき内容

正式に残すなら、少なくとも次を canonical 側へ反映する必要がある。

1. この再構成内容を前提に、何を採用し何を保留にするかの決定
2. `vocab.db` の authority と配置
3. `docs/manual.html` の旧仕様掃除
4. `docs/veil-design.md` と `ui/js/convert.js` の整合

