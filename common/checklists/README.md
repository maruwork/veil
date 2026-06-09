# 共通チェックリスト

review、implementation、testing、release で再利用できる checklist を置く。

本文は日本語正本とする。severity code、status、Result 欄など、機械処理や横断比較に使う短い code は英語のまま維持してよい。

この棚は
`../frameworks/project-progression-rule.md`
の下にある確認棚として扱う。

最初に進行全体を読む時は、

1. `project-progression-rule.md`
2. `project-progression-rule-integration-audit.md`

を先に読む。

## 本体として前に出す checklist

- [implementation-audit-checklist.md](./implementation-audit-checklist.md)
- [unit-test-checklist.md](./unit-test-checklist.md)
- [integration-test-checklist.md](./integration-test-checklist.md)
- [ai-agent-runtime-bootstrap-checklist.md](./ai-agent-runtime-bootstrap-checklist.md)
- [security-review-checklist.md](./security-review-checklist.md)
- [design-spec-completion-checklist.md](./design-spec-completion-checklist.md)

入口では上の checklist を前に出し、残りは必要時だけ開く。

## そのまま使う所 / 差し替える所

- そのまま使う所
  - 確認観点
  - 判定粒度
  - block すべき問題の考え方
- 差し替える所
  - command 名
  - file 名
  - project 固有の verdict 名
  - project 固有の current surface 名

## 保管資産として残す checklist

- module 作成
- project 固有 source checklist から切り出した補助項目
- 統合済み・削除済み checklist の細目は入口 README に並べず、必要時だけ履歴を確認する

project 固有の source checklist は、別途の置き場所確認が終わるまで元の shelf に残す。
迷ったら `../README.md` に戻る。
