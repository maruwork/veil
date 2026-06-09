# detail label surface repair basic design

## Intent

wave 48 の code 契約はすでに `review:` へ切り替わっているので、今回は surface 残留だけを修復する。

## Design

1. `README.md` の旧 detail label 説明を `review:` 契約へ置換する
2. `index/project-current-work.md` を新 repair bundle に切り替える
3. code / docs / skills の再変更は行わない

## Invariants

- runtime unchanged
- docs/skills unchanged if already aligned
- JSON unchanged
