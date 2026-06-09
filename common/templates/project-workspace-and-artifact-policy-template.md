# Project Workspace and Artifact Policy Template

**使う場面**: workspace、generated、archive の置き場と扱いを決める時に使う。  
**差し替える所**: path、retention、generated の扱い、archive 方針。  
**書かないこと**: 実装 task の細部、今の状態の正本、project 固有の current 運用。

> **用途**:
> workspace / generated output / archive の運用を最初から固定し、repo が途中で scratch dump 化するのを防ぐための reusable template。

> **reading note**: このファイルは fill-in policy form。workspace / cleanup / archive の rule 本文は [`project-structure-governance-starter-pack.md`](./project-structure-governance-starter-pack.md) の cleanup procedure 章で読む。

**project_id**: `project_xxx`
**status**: Draft / Approved
**rulebook**: `project-structure-governance-starter-pack.md`

---

## 1. Purpose

- temporary work の置き場を 1 つに寄せる
- generated output を canonical shelf と混ぜない
- archive と active work を分離する

この template は `workspace / generated / archive の扱い` を決めるためのものであり、

- file type ごとの置き場所決定
- 各棚の class と今の正本性
- project 全体の入口や読む順

を単独で確定する文書ではない。

## 2. Active Workspace

- active workspace root:
  - `{path}`
- allowed contents:
  - `{scratch, temporary exports, one-off analysis, generated review files}`
- prohibited uses:
  - `{placing canonical docs without explicit promotion}`

## 3. Generated Output Shelf

- machine-readable output:
  - `{path}`
- human-readable report output:
  - `{path}`
- retention:
  - `{policy}`
- promotion rule:
  - generated artifact is not canonical until explicitly reviewed and promoted

## 4. Archive Shelf

- archive root:
  - `{path}`
- what belongs here:
  - `{historical docs, retired tools, obsolete exports, one-off completed artifacts}`
- archive note rule:
  - why the file left active topology

## 5. Legacy Compatibility Shelf

- legacy shelf:
  - `{path or none}`
- why it still exists:
  - `{caller / hardcoded path / migration bridge}`
- rule:
  - do not use as new write target

## 5a. Hidden Active Asset Rule

- hidden / ignored active shelf:
  - `{path or none}`
- if active assets live here:
  - `{manifest path}`
  - `{entry-file reference}`
- rule:
  - hidden active asset は「見えないまま運用しない」

## 5b. Runtime / Agent Residue Rule

- residue shelf:
  - `{path or none}`
- class:
  - `generated` / `support`
- cleanup trigger:
  - `{when to delete or rotate}`
- owner:
  - `{who decides retention}`

## 6. Promotion Rule

scratch or generated file を canonical に上げる時は、少なくとも次を通す。

1. role を決める
2. taxonomy に照らして shelf を決める
3. caller / reader 影響を確認する
4. 必要なら boundary register を更新する

## 7. Cleanup Rule

cleanup rules の本文は [`project-structure-governance-starter-pack.md`（rulebook）cleanup procedure 章](./project-structure-governance-starter-pack.md) を参照。

## 8. Completion Rule

- active workspace が 1 つ決まっている
- generated output shelf が決まっている
- archive shelf が決まっている
- compatibility lane があるなら new write target ではないと明記されている
- hidden active asset があるなら visibility rule がある
- runtime / agent residue の retention or cleanup rule がある
- visible support document があるなら front current surface と混線しない
