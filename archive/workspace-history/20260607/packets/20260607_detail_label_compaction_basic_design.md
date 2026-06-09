# detail label compaction basic design

## Intent

detail line の本体は hint 値なので、label 自体はもっと短くしてよい。読み手が最初に処理するのは値なので、label は区切り役だけに寄せる。

## Design

1. retention あり:
   - `選別/保留/判別:` を短い label に置換する
2. retention なし:
   - `選別/判別:` を短い label に置換する
3. 値の並び順は変えない
4. JSON 契約は変更しない
5. docs / skills を新 label に追従させる

## Invariants

- `selection_hint`, `retention_hint`, `classification_hint` の順は維持する
- low-priority / existing-match / headline は unchanged
- JSON unchanged
