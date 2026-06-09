# VEIL Capture Rule Section Alignment Basic Design

## 1. Current Gap

- normalize は level を提案できる
- lint は section heading を解釈できる
- capture の書き込み手順だけが flat format 前提

## 2. Target Flow

1. normalize 出力で `suggested_level` を見る
2. user が level を最終判断する
3. file path と section heading を確定する
4. section がなければ作る
5. その section 内で rule line を整列する

## 3. Compatibility Rule

- heading のない既存 rule line は `必須` とみなす
- 既存 flat file に section を導入する場合は
  - `# {letter}` を残す
  - 既存 rule line 群を `## 必須` の下へ整理する

## 4. Documentation Direction

- skill に section-aware write 手順を入れる
- README / design は必要最小限の補足だけ足す
