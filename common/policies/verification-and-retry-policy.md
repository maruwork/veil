# Verification and Retry ポリシー

**目的**: 完了を証明する方法と、失敗が続く場合の扱いを定義する。

最初に覚えることは 3 つだけでよい。

1. `最も強い証拠` を使う
2. 変化を示せる作業では `negative proof -> positive proof` を優先する
3. 同じ失敗を 3 回続けたら、同じやり方をやめる

## 1. 完了には証拠が必要

検証なしに完了を主張しない。

task に対して妥当な範囲で最も強い証拠を使う。

- behavior には test
- 構造には lint または static check
- contract には type check または schema validation
- file topology には generated inventory
- visual work には screenshot または rendered output
- risky automation には dry-run output

single score、単発 benchmark、LLM judge、detector 出力だけで「正しい」と断定しない。

eval signal を使う場合は、少なくとも次を分離する。

- benchmark / judge / detector の結果
- live project 上の read-only verification 結果
- production でまだ未確認の仮説

比較可能性が重要な signal では、tool 名、version、dataset / gold set、threshold、run 回数を残す。

signal が不安定、確率的、または LLM judge 依存なら、可能な限り repeated-run で傾向を見る。1 回の良い結果だけを成功証拠にしない。

検証手段がない場合は、未検証であることと理由を明示する。

benchmark / judge / detector を意思決定に使う場合は、次のどちらかで evidence を残してよい。

- reusable verdict artifact が必要なら
  - `../templates/evaluation-verdict-template.md`
- current / report / register 面へ直接書き戻すなら
  - `strongest_evidence`
  - `verification_result`
  - `unresolved_risk`
  - `retry_change`
  - `writeback_target`

## 2. verification-first

behavior change、bug fix、gate 強化のように「変化前と変化後」を示せる作業では、可能なら **negative proof → positive proof** の順で証拠を取る。

例:

- failing test → passing test
- dry-run mismatch → fixed dry-run
- lint violation → clean result
- broken reference report → clean report

ただし、次を一律に強制しない。

- docs only
- config only
- generated projection の再出力
- inventory / classification / archive-preflight のような read-heavy work

つまり、この policy は `test-first absolutism` は採らない。  
採るのは **verification-first** であり、実作業の型に応じて最も妥当な negative proof を先に確保することを優先する。

## 3. 3回失敗したら変える

同じ失敗操作を無期限に繰り返さない。

同じ command、path、tool、approach で 3 回失敗したら停止し、次を報告する。

- 試したこと
- 失敗したこと
- 試行間で変えたこと
- 最も妥当な代替案
- 人間判断が必要か

## 4. 仮説を変える

失敗後は、少なくとも次のいずれかを変える。

- diagnostic question
- 調査する file または data source
- tool または command
- environment assumption
- proposed fix

新しい仮説なしに同じ操作を繰り返すことは進捗ではない。

## 5. 必要なら巻き戻す

作業経路に混乱した状態が蓄積した場合、最後に確認できた正常点へ戻り、よりきれいな approach を選ぶ。

version control、branch-local changes、logs、generated reports を使って巻き戻し地点を具体化する。user changes や無関係な作業を消さない。

## 6. 残リスクを報告する
この policy を使った結果は、少なくとも次の 5 点が残っていなければならない。

- `strongest_evidence`
  - 今回もっとも強い検証証拠は何か
- `verification_result`
  - 通ったのか、未達なのか、部分通過なのか
- `unresolved_risk`
  - まだ残っている未検証面や運用上の不確実性は何か
- `retry_change`
  - 3 回失敗後に何を変えたか、または次に何を変えるか
- `writeback_target`
  - その結果をどの task / current / packet / register に戻したか

この 5 点が出ていない場合は、検証をしたのではなく、確認途中の観察にとどまる。


検証はリスクゼロを意味しない。確認が一部の挙動しか覆っていない場合は、未確認領域を明示する。
