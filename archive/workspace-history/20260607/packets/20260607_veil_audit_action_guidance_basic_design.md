# VEIL audit action guidance 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 判定結果の意味を変えず、その後に取る軽い手動アクションだけを添える
- helper DB の棚卸し先は既存 UI の delete / upsert 導線に寄せる

## 2. 実装方針

### 2.1 audit result 拡張

- `audit_status()` の返り値を拡張する
- 各 row に以下を追加する
  - `suggested_action`
  - `review_focus`

### 2.2 suggested_action の規則

- `keep`
  - `そのまま維持`
- `review`
  - `候補1・カテゴリ・用途を見直す`
- `drop-candidate`
  - `helper DB からの削除を検討する`

### 2.3 review_focus の生成

- `候補1なし`
- `cat と判別補助がずれる`
- `単語単体で意味が広い`
- `境界が曖昧`
- `project 固有語なので手動判断`

該当しない `keep` は空配列でもよい。

## 3. 文書反映

- README
  - status ごとの処理順を短く追加
- docs/veil-design.md
  - audit 補助の後工程として、UI で delete / upsert する位置づけを追加
- docs/manual.html
  - `drop-candidate` は不要なら ×、`review` は候補1やカテゴリを編集、と記す

## 4. 検証方針

- py_compile
- 仮 DB で text / json を見て、`suggested_action` と `review_focus` を確認
