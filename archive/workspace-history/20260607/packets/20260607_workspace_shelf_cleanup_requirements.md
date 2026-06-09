# Workspace Shelf Cleanup Requirements

## Goal

`veil` の file / folder 配置を `common` の `current / support / generated / historical` 分離へ戻し、`workspace/` に historical packet 群が滞留した状態を解消する。

## Scope

- `workspace/` root の dated packet / report / stray artifact を分類する
- active に残す packet を最小限へ絞る
- historical 扱いの wave artifact を `archive/` へ退避する
- `index/project-current-work.md`、`index/project-file-taxonomy.md`、`index/project-boundary-register.md` を整理後状態へ揃える

## Out Of Scope

- runtime behavior change
- rule threshold の再設計
- `common/` の内容変更
- hidden helper shelf の整理

## Acceptance

1. `workspace/` root が active packet と少数の current support artifact だけに減る
2. historical wave artifact が `archive/` へ分離される
3. taxonomy / boundary / current が同じ shelf class を指す
4. 削除ではなく非破壊移動で整理する
