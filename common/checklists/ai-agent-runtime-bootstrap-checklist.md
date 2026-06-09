# AI Agent Runtime Bootstrap Checklist

**使う場面**: 新しい project で AI 作業環境の入口と境界を決める時に使う。  
**差し替える所**: 採る tool 名、圧縮方法、context 運用、rollback 条件。  
**書かないこと**: その project 固有の正式ルール本文、日々の current 運用。

この checklist は
`../frameworks/project-progression-rule.md`
のうち、主に

- `入口の定義`
- `正本と補助面の分離`
- `current を頭の中だけで持たない`
- `AI がどこへ再接地するか`

を新規プロジェクト立ち上げ時の初期確認として具体化する。

新規プロジェクト立ち上げ時に、AI agent runtime の初期設定として最初に確認する checklist。

## 1. Entry / Boundary

- [ ] root entry file を薄く保つ方針を決めた
  - 必要なら代表例は 1 箇所だけ注記する
- [ ] 詳細は policy / manual / checklist / framework に押し下げる方針を決めた
- [ ] repo-local と user-global の boundary を決めた
- [ ] repo外 runtime config を project SSOT にしないと決めた

## 2. Token Optimization Profile

- [ ] token 最適化を「全部導入」ではなく「選択導入」で進めると決めた
- [ ] 定型CLI圧縮を採るか判定した
- [ ] 広域 context 圧縮を今すぐ採るか deferred にするか判定した
- [ ] 外部知識補助 / repo-wide compression を今すぐ採るか deferred にするか判定した
- [ ] proxy / budget control layer を今すぐ採るか deferred にするか判定した
- [ ] deferred にした項目の理由を記録した

## 3. Search / Context Discipline

- [ ] broad reread より boundary-first / source-first で読む方針を決めた
- [ ] targeted search / narrow read を既定にすると決めた
- [ ] compact / clear / plan の使い分けルールを決めた
- [ ] 1 task / 1 session を既定にするか判定した

## 4. Authority / Safety

- [ ] token 最適化ツールは authority surface ではないと明記した
- [ ] truth / state / verdict / owner / canonical placement は圧縮ツールが決めないと明記した
- [ ] 導入後に誤読が増えた場合の rollback 条件を決めた

## 5. Minimal Measurement

- [ ] 主要 CLI の出力削減率を見る
- [ ] explanation re-pay の減少を見る
- [ ] compact 前後で current facts を落としていないか見る
- [ ] 重要エラーが隠れないかを見る

## 6. Bootstrap Verdict

- [ ] 現時点で採る構成を 1 行で言える
- [ ] deferred 項目を後続 wave に切れる
- [ ] authority boundary を崩さないことを確認した
