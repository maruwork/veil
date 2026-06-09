# Workspace Shelf Cleanup Detailed Design

## Active Keep Set

- `workspace/20260607_workspace_shelf_cleanup_*.md`
- `workspace/20260607_veil_product_design_*.md`
- `workspace/20260607_candidate_rule_decision_sheet.md`
- `workspace/20260607_candidate_rule_decision_sheet_execution_report.md`

## Generated Keep Set

- `workspace/reference/`
- `workspace/profile-exports/`
- `workspace/veil_stage*/`
- `workspace/*smoke*`

## Historical Move Set

- workspace root の `20260607_*.md` のうち active keep set に含まれないもの
- workspace root の dated helper artifact のうち current support でないもの

## Verification

1. move 後に active keep set が残る
2. moved file が `archive/workspace-history/20260607/` に存在する
3. `rg --files workspace` で root clutter が縮小している
4. taxonomy / boundary / current が archive 分離を示す
