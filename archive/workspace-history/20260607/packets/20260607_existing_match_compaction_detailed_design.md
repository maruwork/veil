# Detailed Design

## 1. Rendering Contract

- `existing-match` item は compact branch を通す
- `new-candidate` item は従来 branch を通す

## 2. Existing-Match Compact Fields

- normalized
- existing_original
- preferred
- level
- source_file
- variant_counts

## 3. Verification Conditions

- existing-match が 3 行程度で収まる
- new-candidate は保留処理や review 目安を含む詳細を維持する
- JSON output は before/after で key contract unchanged
