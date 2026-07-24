# VEIL real-conversation v3 independent evaluation protocol

v3 follows the v2 corpus contract and its candidate-eligibility clarification.
It uses only newly selected anonymized real-conversation excerpts, with no v1
or v2 excerpt reused. The canonical snapshot is read-only and is limited to
active normalized terms. The two reviewers must independently confirm source
fidelity, canonical-registration membership, term completeness, eligibility,
and within-session uniqueness before freeze.

The corpus deliberately includes both explicit definitions or decision-boundary
language and ordinary operational status explanations. A definition or
wording-policy decision is `exception`; a repeatable wording choice with
lexical evidence but no decision request is `observe`; an ordinary work-state,
process, or tool mention is `exclude`.

The blind generator receives only frozen runtime inputs and the semantic-frame
contract. First execution is immutable. All artifacts remain under
`workspace/audit/20260721-real-conversation-ux-v3/` for 30 days. DB, Git,
install, sync, remote, and source implementation writes are prohibited.

## Primary target clarification after v3

For a definition, correction, or contrast, the corpus and blind generator must
select the primary lexical target: the wording whose meaning, allowed use, or
preferred form is being decided. A generic predicate or explanatory phrase is
supporting evidence, not a second target, unless the source independently
decides that phrase. A session may contain multiple independent primary
targets; only duplicate normalized targets are forbidden. This clarification
applies only to a new corpus and does not modify v3 evidence.
