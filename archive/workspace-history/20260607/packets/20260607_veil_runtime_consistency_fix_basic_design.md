# VEIL Runtime Consistency Fix Basic Design

## 1. app.py Migration

- current schema と完全一致しない時でも、`vocab_old` に存在する列だけを選ぶ
- 欠けている列は SQL literal default で補う
- known column projection で rebuild する

## 2. UI Re-render

- `loadVocab()` 後の compare refresh で `renderUnmatched()` も再実行する
- `popRevert()` では `renderCompare()` 単体ではなく compare summary を再計算する

## 3. lint / normalize Alignment

- phrase rule の token-wise optional plural handling を normalize の軽量 singularize と揃える
- false positive を抑えつつ、少なくとも normalize 済み cluster が lint でも検出可能になることを優先する

## 4. Rule Conflict Visibility

- canonicalized key が重複したら silent overwrite / silent keep をしない
- helper output に conflict list を含める
- lint は conflict を stderr warning で出す
- normalize は result payload に conflict info を含める

## 5. targets.json Hardening

- `load_targets()` で JSON decode / type error を吸収
- caller に empty list だけ返すと原因不明になるため、warning を出せる形にする

## 6. Doc Reflection

- runtime semantics が変わる箇所だけ `docs/veil-design.md` に補足する
