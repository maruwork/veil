# VEIL Guardrail Mainline Reinforcement Implementation Plan

## 1. Packet Minimum Fields

- workstream: VEIL guardrail mainline reinforcement
- objective: `capture` と `lint` を workflow gate 化し、rule 3 層と core/profile 境界を固定する
- authority kept: `~/.veil/rules/`, `README.md`, `docs/veil-design.md`, `AGENTS.md`, `skills/`
- excluded for this wave: UI, helper DB, archive, physical profile expansion

## 2. Implementation Decision Record

- VEIL の主語を `AI-assisted technical writing terminology guardrail` に固定する
- フローの厳格化を先にやり、全語彙の厳格化はしない
- rule strictness を `必須 / 推奨 / 観察` に分ける
- current default profile を technical writing profile と見なす
- domain profile 実装は後続 wave とし、この wave では境界定義に留める

## 3. Checkpoints

1. VEIL の主語と target market を固定する
2. mainline gate を `capture close` と `pre-response lint` に固定する
3. rule strictness 3 層を定義する
4. core / profile 分離を定義する
5. canonical docs と skills に反映する
6. surface 整合を verify する

## 4. Tasks

### Task A: Canonical Positioning Rewrite

- `README.md`
- `docs/veil-design.md`
- `AGENTS.md`

目的:

- VEIL の主語を broad tool から technical writing guardrail へ固定する

### Task B: Mainline Gate Rewrite

- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`

目的:

- `capture` の閉じ処理化
- `lint` の返答前必須 gate 化

### Task C: Rule Layer Design Rewrite

- `README.md`
- `docs/veil-design.md`
- 必要なら `veil-lint.py` / `veil-normalize.py` の follow-up note

目的:

- `必須 / 推奨 / 観察` を current rule governance として明記する

### Task D: Core / Profile Boundary Rewrite

- `README.md`
- `docs/veil-design.md`
- `AGENTS.md`
- `index/` の必要面

目的:

- 共通エンジンと業界別差し替え面を分ける

## 5. Files

### New

- `workspace/20260607_veil_guardrail_mainline_reinforcement_requirements.md`
- `workspace/20260607_veil_guardrail_mainline_reinforcement_basic_design.md`
- `workspace/20260607_veil_guardrail_mainline_reinforcement_implementation_plan.md`
- `workspace/20260607_veil_guardrail_mainline_reinforcement_task_design.md`

### Update

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- 必要なら `index/project-file-taxonomy.md`
- 必要なら `index/project-boundary-register.md`
- 必要なら `index/project-template-adoption-packet.md`

## 6. Execution Order

1. packet を作成する
2. task-design を Task A-F まで分解する
3. canonical docs で VEIL の主語を固定する
4. skills と設計書で gate と判別順を固定する
5. rule 3 層と core/profile を文書化する
6. `rg` で surface 整合を確認する
7. follow-up 実装 wave を separate packet として起こす

## 7. Acceptance Mapping

- target 固定 -> `README.md`, `docs/veil-design.md`, `AGENTS.md`
- `capture` / `lint` gate 固定 -> `README.md`, `docs/veil-design.md`, `skills/*/veil-capture*`
- rule 3 層 -> `README.md`, `docs/veil-design.md`
- core/profile 分離 -> `README.md`, `docs/veil-design.md`, `AGENTS.md`

## 8. Verification Plan

- `rtk rg` で `technical writing`, `guardrail`, `必須`, `推奨`, `観察`, `profile`, `capture`, `lint` を検索する
- `README.md`, `docs/veil-design.md`, `AGENTS.md`, `skills/*` の surface が同じ主語で読めることを確認する
- UI / helper DB の再混入がないことを確認する

## 9. Risks

- rule 3 層を文書だけ先行で入れると、実装との差が一時的に広がる
- profile 概念を早く入れすぎると、現行 default profile の境界が逆に曖昧になる
- `capture` 必須化の説明が強すぎると、現行 skill 利用負荷が高く見える

## 10. Stop Conditions

- current `~/.veil/rules/` format と rule 3 層設計が根本衝突する
- current mainline script の責務を読まずに level semantics を先行確定しそうになる
- canonical docs 間で主語固定に矛盾が出る

## 11. Follow-up Waves

1. rule 3 層の physical format 設計
2. `veil-lint.py` の fail / warning / observe 実装
3. current default profile の seed / rule migration
4. domain profile の layout 設計
