# VEIL Vocabulary Cleanup Basic Design

## 1. Strategy

- file 名・script 名・CLI option は識別子なので維持する
- 識別子の説明文と出力文言を日本語へ寄せる
- `index/` は今回の主対象から外し、VEIL の主運用面を先に clean にする

## 2. Output Policy

- stdout / stderr の人向け文言は日本語優先
- JSON key は今回は互換優先で維持可

## 3. Exceptions

- `veil-lint.py`, `veil-normalize.py` の script 名
- JSON field 名
- 最低限の技術識別子
