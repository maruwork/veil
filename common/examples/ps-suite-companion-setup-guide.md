# PS Suite Companion Setup Guide

PS Suite companion script 群を別プロジェクトや外部作業環境で再利用する時の、portable baseline setup guide。

この文書は current project の runtime canonical ではない。  
adopting project 側で script 名、package 名、credential source、execution path を具体化するための reusable example である。

## 1. Purpose

- companion script を初回実行する前提を揃える
- 言語ランタイム、package、credential、検証手順を最低限そろえる
- project 固有 path や local credential store を本文に埋め込まない

## 2. Minimum Setup Cohort

少なくとも次の cohort を定義する。

| cohort | purpose |
|---|---|
| language runtime | script 実行環境 |
| package manager | dependency install |
| browser/runtime tooling | browser validation がある場合 |
| API credential | external API を叩く場合 |
| script inventory | 何の script があるか |
| verification step | setup 後に何を確認するか |

## 3. Baseline Setup Pattern

### Runtime

- Python 3.10+
- Node.js 18+
- npm

### Dependencies

- Python packages は `requirements.txt` または明示 package list で入れる
- browser automation がある場合は browser package と browser binary install を分けて書く

### Credentials

- API key は環境変数優先
- local credential store fallback を使う場合は、source と fallback rule を分けて書く
- project 固有の credential path を baseline 本文に固定しない

### Script Inventory

各 script について最低限次を列挙する。

- script 名
- purpose
- execution example
- required dependency

## 4. Verification Rule

setup 完了と言えるのは、少なくとも次を満たす時だけ。

- runtime version を確認できる
- dependency install 手順がある
- credential source が明示されている
- script inventory がある
- first verification command がある

## 5. Non-Goals

- この文書は特定 project の production rollout manual ではない
- local machine 固有 path や secret location を本文に埋め込まない
- adopting project の runtime boundary rule は別文書に委ねる
