# Entry / Guide / Reference 分離ポリシー

**目的**: project の入口文書、読む順ガイド、参照棚を混線させず、初見の人や後続 agent が迷わず next step を選べる portable rule を定義する。

このポリシーは project-local の current canonical や governance SSOT を置き換えない。各 project は local rule で canonical path を定義し、その上で本ポリシーを navigation 設計に適用する。

この policy は `読む面の分離` を扱う。

- 棚名や file 名の命名
  - `naming-and-shelf-policy.md`
- file の作成 / 移動 / archive / 処分
  - `file-operation-policy.md`

を正本として参照する。

## 1. 役割分離

project の navigation surface は、少なくとも次の 3 役に分ける。

- `entry`
  - 最初に 1 回だけ開く入口
  - project が何か、今どこを見るか、どの guide に進むかを示す
- `guide`
  - 目的別の読む順だけを示す
  - current work、runtime、first read のように進み方を分ける
- `reference`
  - inventory、generated index、backlog catalog、historical lookup を置く
  - current authoritative source の代替にしない

この 3 役を 1 file に詰め込みすぎると、入口が肥大化し、inventory が current source に見え始める。分離の目的は file 数を増やすことではなく、役割衝突を防ぐことにある。

## 2. Entry Rule

- entry file は 1 つに固定する。
- shelf entry の標準名は `README.md` とする。
- entry file は薄く保ち、少なくとも次の 4 問に答えられる状態にする。
  - この project は何か
  - 今どこを見れば current が分かるか
  - rule / governance の正本はどこか
  - runtime / DB / tool 実体はどこから辿るか
- entry file から guide と canonical surface へのリンクは削らない。
- entry file に inventory table、generated snapshot、長い誤読防止本文、詳細な route 説明を抱え込ませない。
- entry file を更新する時は、追加した導線と同じ粒度の古い導線を残していないか確認する。
- entry file が 2 つ以上の current frame / route frame を持ち始めたら、1 つへ統合する。

## 3. Guide Rule

- guide file は 3 本までを原則とする。
- 推奨する最小構成は次の 3 本である。
  - `guide-first-read.md`
  - `guide-current-work.md`
  - `guide-runtime.md`
- guide は「どの順で読むか」を示す file であり、inventory や current status board を兼ねない。
- 新しい guide を増やしたくなった場合は、まず既存 guide に吸収できないかを確認する。
- 4 本目以降を許可するのは、既存 3 本では role conflict が避けられない場合だけとする。
- guide は reader journey ごとに短く保つ。1 guide が複数 journey を持ち始めたら、まず section 圧縮か既存 guide への再配置を検討する。

## 4. Reference Rule

- reference shelf には inventory、generated index、backlog catalog、historical lookup を置く。
- reference file は、冒頭または file head 付近で少なくとも次を明示する。
  - これは entry ではない
  - これは current authoritative source ではない
  - current を知りたい時の戻り先
- reference file が current progress、active branch、completion posture を独自に要約し始めたら、役割逸脱として扱う。
- 誤読されやすい backlog catalog や pending list は、front surface から下げて reference role に固定する。

## 5. Split Gate

- README を分割する判断は、行数ではなく role conflict を基準に行う。
- 次の条件に当てはまる時は、entry / guide / reference 分離を検討する。
  - 入口、読む順、inventory、誤読防止が同じ file に混在している
  - 初見 reader が next step を選ぶ前に長い説明を読む必要がある
  - backlog catalog や generated index が current source に見える
- 逆に、単に長いからという理由だけで機械的に分割しない。
- 分割時は、削るのではなく destination role を決めて移す。

## 6. Link Preservation Rule

- 重複説明は削ってよいが、導線は削らない。
- entry file には少なくとも次の link class を残す。
  - project overview / concept
  - current canonical
  - governance / rule SSOT
  - runtime / DB / tool surface
- guide に移した内容があっても、entry からその guide へ辿れなければ分離は未完とする。

## 7. Follow-Up Updates

entry / guide / reference の役割を変えたら、少なくとも次を追随させる。

- taxonomy または placement map
- navigation / index
- boundary / disposition register
- generator / script / caller reference

reference shelf を新設または rename した場合は、既存の generated path と link 先を先に確認する。

## 8. Success Criteria

この分離が有効とみなせるのは、少なくとも次を満たす時だけである。

- 初見 reader が entry file だけで next step を選べる
- current work を追う reader が current-work guide へ迷わず着地できる
- runtime / DB / tool 読解の入口が current work guide と混ざらない
- reference file を current authoritative source と誤認しにくい
- 新しい文書を追加する時に、entry / guide / reference / canonical のどこへ置くか判断できる

## 9. Anti-Bloat Rule

entry / guide / reference の整理は、ファイル数を増やすためではなく reader journey を短くするために行う。

- 新しい entry / guide / reference file を作る前に、既存 file の圧縮・置換・pointer 化で足りないか確認する。
- 新しい shelf を作る前に、同じ役割の existing shelf がないか確認する。
- 新しい reference を作る場合は、generated / inventory / historical lookup / current companion のどれかを明示する。
- 役割が曖昧な新規文書は作らず、まず workspace memo や draft として扱い、canonical 化の必要性を後で判定する。
- 追加後に README / guide / reference のどれかが重くなるなら、同じ変更内で古い route note や重複 caution を削る。

## 10. Orientation / Readability Rule

- `Markdown` 本文は、人間の順読みと search / link jump の両方で破綻しない形に保つ。
- 冒頭は「短い役割説明 + 必要最小限の戻り先」に寄せる。
- 同じ file 内で `entry` や `current ではない` という同趣旨の注記を重ねない。
- direct-open reader が誤読しやすい role / authority / next step だけを短く示す。
- `entry / guide / reference / canonical` の役割をまたぐ説明は、最も責務が近い 1 file に寄せ、他は pointer にする。
- 長い caution 羅列、current 値の重複列挙、別 file の navigation の再説明は避ける。
