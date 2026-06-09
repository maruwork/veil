# UI 実機確認 基本設計

## 1. 方針

- verification-first で進める。
- 既存 `vocab.db` をそのまま使い、現在の現物 UI で棚卸し導線を確認する。
- destructive な操作は preview / confirm の範囲までを基本とし、必要な変更は最小に留める。

## 2. 確認順

1. localhost 起動確認
2. 初期表示確認
3. `要見直し` button 動作確認
4. current review 表示の維持・解除確認
5. `削除候補` 一括削除 confirm 確認
6. sort / filter の見え方確認

## 3. 記録

- 実機で見た挙動を workspace に記録する。
- 不整合があれば、再現手順・期待・実際の差を残す。
