# VEIL Guardrail Mainline Reinforcement Task Design

## 1. Parent Theme

- workstream: VEIL guardrail mainline reinforcement
- objective: `capture` と `lint` を workflow gate 化し、rule 3 層と core / profile 境界を canonical に固定する
- parent requirements:
  - `workspace/20260607_veil_guardrail_mainline_reinforcement_requirements.md`
- parent basic design:
  - `workspace/20260607_veil_guardrail_mainline_reinforcement_basic_design.md`
- parent implementation plan:
  - `workspace/20260607_veil_guardrail_mainline_reinforcement_implementation_plan.md`

## 2. Parent Checkpoints

### CP-1 主語固定

- VEIL の説明主語が `AI-assisted technical writing terminology guardrail` に固定される

### CP-2 mainline gate 固定

- `capture` が閉じ処理、`lint` が返答前 gate として読める

### CP-3 rule 3 層固定

- `必須 / 推奨 / 観察` の違いが fail / warning / observe と対応する

### CP-4 core / profile 境界固定

- 共通 engine と domain 差し替え面が分離して説明される

### CP-5 surface 整合確認

- `AGENTS.md`, `README.md`, `docs/veil-design.md`, `skills/*` で矛盾がない

## 3. Dependency and Sequencing

- Task A は先頭固定
- Task B は Task A 完了後に着手
- Task C は Task A と Task B の文脈を前提に着手
- Task D は Task A-C の表現を受けて境界整理を行う
- Task E は A-D 完了後の verify task
- Task F は Task E 合格後にだけ着手

## 4. Shared Protected Boundaries

### Read Allowed Commonly

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-template-adoption-packet.md`
- `workspace/reference/20260607_veil_public_release_deep_research.md`
- parent packet 3 本

### Write Allowed Commonly

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- 必要時のみ `index/project-file-taxonomy.md`
- 必要時のみ `index/project-boundary-register.md`
- 必要時のみ `index/project-template-adoption-packet.md`
- `workspace/20260607_veil_guardrail_mainline_reinforcement_*.md`

### Must Not Touch in This Wave

- `app.py`
- `ui/`
- `uijs/`
- `js/`
- `docs/manual.html`
- `veil-audit-db.py`
- `veil_audit_core.py`
- `vocab.db`
- `~/.veil/rules/` の実データ
- archive / hidden helper shelves

## 5. Task Designs

### Task ID: T-A

- 親テーマ:
  - VEIL guardrail mainline reinforcement
- 親チェックポイント:
  - CP-1 主語固定
- 目的:
  - VEIL の説明主語を broad tool から `AI-assisted technical writing terminology guardrail` へ固定する
- このタスクが必要な理由:
  - 主語が広いままだと、VEIL の本線と公開価値がぶれ、補助面や一般用途へ拡散する
- 着手条件:
  - parent requirements / basic design / implementation plan を読了している
  - current `README.md`, `docs/veil-design.md`, `AGENTS.md` の主語表現を確認済みである
- 入力:
  - deep research の positioning 結論
  - current canonical docs の主語表現
- 読んでよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - `AGENTS.md`
  - `workspace/reference/20260607_veil_public_release_deep_research.md`
  - parent packet 3 本
- 書いてよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - `AGENTS.md`
- 触ってはいけない場所:
  - runtime scripts
  - UI / helper DB 系
  - `~/.veil/rules/`
- やること:
  - VEIL の target を technical writing / product documentation / regulated prose 向けの guardrail に寄せる
  - `AI ガバナンス全般`, `翻訳ツール`, `なんでも直す writing assistant` に見える表現を落とす
  - `mainline` の主語が `rules / capture / normalize / sync / lint` に乗るように説明を短く組み直す
- 期待する出力:
  - 3 surface で同じ主語が読める canonical wording
- 合格条件:
  - `README.md`, `docs/veil-design.md`, `AGENTS.md` のいずれでも VEIL の主語が broad tool ではなく guardrail になっている
  - 説明が UI / helper DB を前提にしない
- 失敗条件:
  - broad AI governance や general writer tool に読める表現が残る
  - technical writing 以外へ無制限に広げる文言が残る
- 停止条件:
  - current canonical 間で既存の target 定義が衝突していて先に裁定が必要
- 差し戻し条件:
  - 技術文書向けに固定した結果、既存 mainline 説明と意味が食い違う
- 人判断へ上げる条件:
  - regulated content まで current default target に含めるかが曖昧な場合
- 証拠:
  - `rtk rg` による `technical writing`, `guardrail`, `AI ガバナンス全般`, `翻訳ツール` 残存確認
- 結果の記録先:
  - updated canonical docs
  - final report
- 最終判定者:
  - project operator
- referenced design sections:
  - requirements: `1. Overview`, `2. Scope`, `3. Success Criteria`
  - basic design: `1. Architecture`, `6. Documentation Design`
- dependencies and blockers:
  - blocker: target market wording の未裁定
- target files/components:
  - `README.md`, `docs/veil-design.md`, `AGENTS.md`
- acceptance criteria:
  - CP-1 を満たす
- test / evidence mapping:
  - text search and cross-surface wording comparison
- explicit out-of-scope items:
  - script 実装変更
  - domain profile の physical layout

### Task ID: T-B

- 親テーマ:
  - VEIL guardrail mainline reinforcement
- 親チェックポイント:
  - CP-2 mainline gate 固定
- 目的:
  - `capture` を閉じ処理、`lint` を返答前必須 gate として canonical に固定する
- このタスクが必要な理由:
  - VEIL の差別化と実効性は `capture + lint gate` に集中している
- 着手条件:
  - T-A が完了している
  - current mainline description と skill 手順を読み直している
- 入力:
  - current `README.md`
  - current `docs/veil-design.md`
  - 2 つの `veil-capture` skill
- 読んでよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
  - parent packet 3 本
- 書いてよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
- 触ってはいけない場所:
  - `veil-lint.py` 実装仕様
  - `veil-normalize.py` 実装仕様
  - UI / helper DB 系
- やること:
  - `capture` を task close / 会話区切り / closing report 前の閉じ処理として記述する
  - `lint` を最終日本語 prose 前の必須 gate として記述する
  - capture report 自体は lint 対象外、main task prose のみ対象とする境界を保つ
  - gate を通らない close を完了扱いしない方針を明記する
- 期待する出力:
  - mainline gate と trigger が読める一貫した説明
- 合格条件:
  - 4 surface すべてで `capture` と `lint` の trigger が矛盾なく読める
  - `capture` が optional helper としてではなく close flow として読める
  - `lint` が pre-response gate として読める
- 失敗条件:
  - `capture` や `lint` が任意実行に見える
  - skill と canonical docs で trigger が違う
- 停止条件:
  - current skill wording が実運用と materially 衝突し、その場で裁定できない
- 差し戻し条件:
  - gate 強化により current docs と skill の責務境界が崩れる
- 人判断へ上げる条件:
  - どの会話区切りを capture 必須 trigger とみなすか曖昧な場合
- 証拠:
  - `rtk rg` による `task close`, `会話区切り`, `返答前`, `lint`, `capture` の surface 一致確認
- 結果の記録先:
  - updated canonical docs and skills
- 最終判定者:
  - project operator
- referenced design sections:
  - requirements: `4. Functional Requirements`
  - basic design: `1. Architecture`, `5. Operations Design`, `6. Documentation Design`
- dependencies and blockers:
  - dependency: T-A
  - blocker: trigger wording の未裁定
- target files/components:
  - `README.md`, `docs/veil-design.md`, `skills/codex/veil-capture/SKILL.md`, `skills/claude-code/veil-capture.md`
- acceptance criteria:
  - CP-2 を満たす
- test / evidence mapping:
  - text search and manual cross-read
- explicit out-of-scope items:
  - trigger 自動化実装
  - lint の runtime hook

### Task ID: T-C

- 親テーマ:
  - VEIL guardrail mainline reinforcement
- 親チェックポイント:
  - CP-3 rule 3 層固定
- 目的:
  - `必須 / 推奨 / 観察` を rule governance として明記し、過剰統制を避ける
- このタスクが必要な理由:
  - 全語彙 hard gate を避けつつ、高影響語だけは強く縛るため
- 着手条件:
  - T-A, T-B が完了している
  - current rule explanation を読み直している
- 入力:
  - deep research の過剰統制リスク
  - current README / design の rule 説明
- 読んでよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - `workspace/reference/20260607_veil_public_release_deep_research.md`
  - parent packet 3 本
- 書いてよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - 必要なら `AGENTS.md` の operation loop 節
- 触ってはいけない場所:
  - `~/.veil/rules/` format 実データ
  - `veil-lint.py` / `veil-normalize.py` 実装
- やること:
  - `必須 / 推奨 / 観察` の定義を書く
  - `必須 = fail-close`, `推奨 = warning`, `観察 = capture / normalize / observe only` を結び付ける
  - 厳格統制対象を `禁止語`, `VEIL基幹語`, `high-demand / high-impact 語` に寄せる
  - 緩く扱う対象を `低頻度語`, `文脈依存語`, `未確定 project 固有語`, `機械処理語` に寄せる
  - 現 wave は logical layering のみで physical format 変更はしない、と明記する
- 期待する出力:
  - level semantics が理解できる canonical explanation
- 合格条件:
  - `README.md` と `docs/veil-design.md` に 3 層が明示されている
  - `fail / warning / observe` の差が説明されている
  - 全面統制ではないことが明記されている
- 失敗条件:
  - 3 層が名前だけで、運用差が不明
  - `必須` と `推奨` の違いが曖昧
- 停止条件:
  - current rule file format と level semantics が衝突し、文書化だけでも誤解を生む
- 差し戻し条件:
  - warning / observe の説明が現行 lint 実装と矛盾しすぎる
- 人判断へ上げる条件:
  - `VEIL基幹語` の current default 範囲を今ここで固定できない場合
- 証拠:
  - `rtk rg` による `必須`, `推奨`, `観察`, `fail`, `warning`, `observe` の surface 確認
- 結果の記録先:
  - updated canonical docs
- 最終判定者:
  - project operator
- referenced design sections:
  - requirements: `4. Functional Requirements`, `6. Risks`
  - basic design: `2. Control Model`
- dependencies and blockers:
  - dependency: T-A, T-B
  - blocker: level を current docs だけでどう表すか
- target files/components:
  - `README.md`, `docs/veil-design.md`, optional `AGENTS.md`
- acceptance criteria:
  - CP-3 を満たす
- test / evidence mapping:
  - text search and operator readback
- explicit out-of-scope items:
  - level の physical encoding
  - lint 実装変更

### Task ID: T-D

- 親テーマ:
  - VEIL guardrail mainline reinforcement
- 親チェックポイント:
  - CP-4 core / profile 境界固定
- 目的:
  - VEIL core と domain profile の責務境界を current canonical に固定する
- このタスクが必要な理由:
  - 業界別適用可能性を見せつつ、現行 default profile の主語を曖昧にしないため
- 着手条件:
  - T-A, T-B, T-C が完了している
- 入力:
  - current canonical docs
  - deep research の市場整理
  - parent packet 3 本
- 読んでよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - `AGENTS.md`
  - 必要時のみ `index/project-file-taxonomy.md`
  - 必要時のみ `index/project-boundary-register.md`
  - 必要時のみ `index/project-template-adoption-packet.md`
- 書いてよい場所:
  - `README.md`
  - `docs/veil-design.md`
  - `AGENTS.md`
  - 必要時のみ `index/` 3 面
- 触ってはいけない場所:
  - profile の physical implementation
  - runtime script responsibilities
  - retired support surface
- やること:
  - core に属するものを固定する
  - profile に属するものを固定する
  - current default profile を technical writing profile として説明する
  - 将来の業界別 profile は follow-up wave で扱うと明記する
  - 必要なら governance 上の active surface 表記を最小修正する
- 期待する出力:
  - `core + current default profile` 構造が読める canonical wording
- 合格条件:
  - `README.md`, `docs/veil-design.md`, `AGENTS.md` で core / profile の境界が一致する
  - profile を入れても UI / helper DB が mainline に戻らない
- 失敗条件:
  - profile 概念が broad expansion に読める
  - core と profile の責務が混ざる
- 停止条件:
  - governance 側の current authority と境界定義が食い違い、先に index 裁定が必要
- 差し戻し条件:
  - current default profile を technical writing と書くことで既存主語と衝突する
- 人判断へ上げる条件:
  - regulated profile を current default に含めるか分岐が必要な場合
- 証拠:
  - `rtk rg` による `core`, `profile`, `technical writing profile`, `default profile` 確認
- 結果の記録先:
  - updated canonical docs and optional index updates
- 最終判定者:
  - project operator
- referenced design sections:
  - requirements: `2. Scope`, `4. Functional Requirements`
  - basic design: `3. Core and Profile Separation`, `6. Documentation Design`
- dependencies and blockers:
  - dependency: T-A, T-B, T-C
  - blocker: default profile wording の未裁定
- target files/components:
  - `README.md`, `docs/veil-design.md`, `AGENTS.md`, optional `index/*`
- acceptance criteria:
  - CP-4 を満たす
- test / evidence mapping:
  - text search and cross-surface wording comparison
- explicit out-of-scope items:
  - domain profile directory layout
  - profile switching implementation

### Task ID: T-E

- 親テーマ:
  - VEIL guardrail mainline reinforcement
- 親チェックポイント:
  - CP-5 surface 整合確認
- 目的:
  - A-D の反映後、surface 整合と補助残骸の非再混入を検証する
- このタスクが必要な理由:
  - 文書改定 wave は実装変更より、surface 間のズレ再発が主リスクになる
- 着手条件:
  - T-A から T-D が完了している
- 入力:
  - updated canonical docs
- 読んでよい場所:
  - `AGENTS.md`
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
  - 必要時のみ `index/` 3 面
- 書いてよい場所:
  - current task design packet の follow-up note
  - 必要なら上記文書の軽微修正
- 触ってはいけない場所:
  - runtime scripts
  - retired support surface
- やること:
  - text search で key phrase を確認する
  - UI / helper DB の再混入がないか確認する
  - task close / lint gate / 3 層 / core-profile が 5 surface で揃うか確認する
  - ズレがあればその場で additive 修正する
- 期待する出力:
  - evidence-backed surface verification result
- 合格条件:
  - CP-5 を満たす
  - 残るズレがあれば residual risk として明示されている
- 失敗条件:
  - 主要 surface 間で trigger, target, strictness の記述が矛盾する
- 停止条件:
  - 複数 surface で意味差が大きく、追加裁定なしに統一できない
- 差し戻し条件:
  - verify 中に T-A から T-D の前提が崩れる
- 人判断へ上げる条件:
  - wording を合わせると別の既存 rule と衝突する場合
- 証拠:
  - `rtk rg` 結果
  - manual cross-read summary
- 結果の記録先:
  - final report
- 最終判定者:
  - project operator
- referenced design sections:
  - implementation plan: `7. Acceptance Mapping`, `8. Verification Plan`
- dependencies and blockers:
  - dependency: T-A, T-B, T-C, T-D
- target files/components:
  - `AGENTS.md`, `README.md`, `docs/veil-design.md`, `skills/*`, optional `index/*`
- acceptance criteria:
  - CP-5 を満たす
- test / evidence mapping:
  - `rtk rg` and cross-surface review
- explicit out-of-scope items:
  - new implementation wave execution

### Task ID: T-F

- 親テーマ:
  - VEIL guardrail mainline reinforcement
- 親チェックポイント:
  - CP-5 surface 整合確認後の次動作確定
- 目的:
  - 次 wave を `implementation` へ進めるための follow-up packet を起こすか、残課題を deferred に送るかを固定する
- このタスクが必要な理由:
  - `common` の close では、次 action を曖昧にしない必要がある
- 着手条件:
  - T-E が合格している
- 入力:
  - T-E の verify 結果
  - remaining deferred design questions
- 読んでよい場所:
  - parent packet 3 本
  - current task design packet
- 書いてよい場所:
  - `workspace/` の follow-up packet
- 触ってはいけない場所:
  - canonical docs の再改定
  - runtime scripts
- やること:
  - next wave を `rule 3 層 physical format`, `lint fail/warning/observe`, `default profile migration` のどれにするか決める
  - その wave の packet を separate workstream として起こすか、deferred list に残す
- 期待する出力:
  - next workstream decision
- 合格条件:
  - この wave の close 後に次の入口が曖昧でない
- 失敗条件:
  - verify を終えても次 wave が未定のまま
- 停止条件:
  - T-E で重大不整合が残り、next wave を切る前に再設計が必要
- 差し戻し条件:
  - T-E の残課題が current wave へ戻すべき内容だった場合
- 人判断へ上げる条件:
  - 次 wave の優先順位が複数案で同程度に競合する場合
- 証拠:
  - follow-up packet or deferred decision note
- 結果の記録先:
  - `workspace/`
- 最終判定者:
  - project operator
- referenced design sections:
  - implementation plan: `11. Follow-up Waves`
- dependencies and blockers:
  - dependency: T-E
- target files/components:
  - `workspace/`
- acceptance criteria:
  - next action visibility
- test / evidence mapping:
  - presence of follow-up packet or explicit defer note
- explicit out-of-scope items:
  - follow-up implementation itself

## 6. Review Trigger Check

- referenced design docs:
  - 3 (`requirements`, `basic design`, `implementation plan`)
- implementation files in current wave:
  - 5-8 想定
- dependency blockers:
  - wording 裁定が最大 3 系統

超過していないため、この粒度の task split を維持する。
