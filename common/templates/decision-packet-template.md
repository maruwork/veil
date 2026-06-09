# Decision Packet テンプレート

**使う場面**: 人の最終判断が必要で、今ここで作業を止める時に使う。  
**推奨 file 名**: `YYYYMMDD_<topic>-decision-packet.md`
**差し替える所**: task ID の形式、判断者名、停止後の戻り先、選択肢の数。  
**書かないこと**: 実装 plan 本文、今の状態の正本、project 固有の board 再定義。

この template は停止理由パケットの正本です。
他の gate、theme 文書、board では、この項目群を別 wording で再定義せず、参照または current case への適用に留めます。

branch 完了だけで止まる場合には使わない。人間判断が不要なら、親 task へ再ルーティングして続行する。

`owner 判断が必要か = no` かつ `停止中でも継続できる作業 = yes` の場合も、これを停止宣言として使わず、current surface に必要事項を残して続行する。

停止理由:
なぜここで自律作業を止めるべきか。

必要な判断:
owner が選ぶべき具体的な判断。

選択肢:
A. ...
B. ...
C. ...

推奨:
推奨案と理由。

Decision packet schema:
- task_id:
- review_owner:
- review_target:
- verdict:
- blockers:
- required_fixes:
- human_gate_required:
- approved_execution_scope:
- next_actor:
- beads_execution_gate:
- recommended_option:
- why_recommended:
- alternatives:
- hybrid_option_if_any:
- what_changes_if_user_picks_A:
- stop_before_execution:
- decision_status:
- selected_option:

判断材料:
影響範囲、リスク、戻せるか、コスト、後続タスク。

owner 判断が必要か:
yes / no

owner 判断が必要な場合に決めること:
何を決めれば再開できるか。

owner 判断が不要な場合に次に埋めること:
作業側が次に何を作るか、何を確認するか。

停止中でも継続できる作業:
yes / no

継続できる場合の範囲:
どこまで進めてよいか。

次に必ず編集するファイル:
どの file を次に更新するか。

このターンで最低限埋める範囲:
このターンで少なくともどこまで進めるか。

status報告だけで終了してはいけないか:
yes / no

Spec checkpoint:
fixed:
unknown:
blocked:
non-goal:

Preflight:
precondition check:
read-only verification:
simulate-before-actuate:

判断後の次アクション:
owner が選んだ直後に実行する作業。

handoff:
- next actor:
- reroute target:
- reopen condition:

注意:
- 本命が折衷案なら、純粋案に埋めず独立案として書く
- `what_changes_if_user_picks_A` は、owner が別案を選んだ時に何が変わるかを明示する
- `stop_before_execution` は、判断前に実装へ流してはいけないかを明示する
- `beads_execution_gate: yes` を付けた packet は、`stop_before_execution: yes` かつ `decision_status: resolved` になるまで canonical implementation を止める fail-close gate として扱う
- `selected_option` は owner が選んだ案を記録する。未解決の間は `pending` でよい
- `owner 判断が必要か = no` かつ `停止中でも継続できる作業 = yes` の場合は、`次に必ず編集するファイル`、`このターンで最低限埋める範囲`、`status報告だけで終了してはいけないか: yes` を埋める
