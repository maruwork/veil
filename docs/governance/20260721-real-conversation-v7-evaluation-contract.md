# VEIL next real-conversation evaluation: reviewed-label contract

**Status:** G1 complete. This is the reviewed-label contract for the next
real-conversation holdout. It does not create that holdout or authorize source
collection, freeze, blind generation, evaluation, DB access, sync,
installation, Git, remote, or release actions.

## Authority and scope

This contract applies the fixed contract-v2 outcome policy; it does not amend
it. Its authorities are:

- `docs/veil-design.md` sections 3-1, 3-4, and 5;
- `shared/tools/veil_decision_frames.py`, especially `_frame_outcome()`;
- `docs/governance/20260721-real-conversation-v2-corpus-contract.md` for
  exact-context, canonical-snapshot, and two-reviewer requirements.

Each reviewer derives an expected outcome from one valid, exact-evidence
semantic frame for one independent primary lexical target. A label is not a
judgment that a phrase is interesting, common, technical, or worth recording.
It is the result of applying the following order to the reviewed frame.

## Outcome matrix

Use the first matching row. `exception` means one combined user question for a
session; every other outcome remains automatic and invisible in the normal
flow.

| Order | Validated frame condition | Required expected outcome | Runtime reason or policy effect |
| --- | --- | --- | --- |
| 1 | Critic rejects the frame as spurious | `exclude` | critic-rejected wording is non-authoritative |
| 2 | Extractor/critic material disagreement, or critic leaves a durable or high-impact frame unresolved | `exception` | fail closed; the user must resolve it once per session |
| 3 | `polarity` is `negated` or `reported`, or `persistence` is `none` | `exclude` | non-durable or non-authoritative frame |
| 4 | The normalized target is in the frozen canonical snapshot, intent is `mention` or `adopt`, and no different preferred form is requested | `existing-match` | exact registered use is already resolved |
| 5 | `persistence` is `temporary` or `scope` is `one-off` | `observe` | temporary or one-off frame |
| 6 | An affirmed durable `adopt`, `rename`, or `conflict` frame remains | `exception` | affirmed wording decision |
| 7 | An affirmed `define` frame has `persistence=durable` or `impact=high` | `exception` | durable or high-impact definition |
| 8 | An affirmed `define` frame remains but is neither durable nor high impact | `observe` | unclear non-high-impact definition |
| 9 | An affirmed `mention` frame remains, has `persistence=unclear`, and lacks high confidence | `observe` | unclear mention |
| 10 | Any other affirmed `mention` frame remains | `exclude` | mention without a wording decision |

Reviewer instructions must use the policy meaning in the matrix even where a
runtime reason string is more specific. In particular, an affirmed durable
definition, adoption, rename, or conflict must never be relabeled `observe`
to preserve a no-question test session.

## Primary-target and evidence rules

1. Review one natural, complete term for one independently decided concept in
   one exact context. Do not use a substring, identifier fragment, generic
   actor, predicate, explanatory phrase, or duplicate concept as a target.
2. For a definition, correction, or contrast, select the wording whose
   meaning, permitted use, or preferred form is independently decided. Keep
   generic predicates and explanatory categories as evidence unless they are
   separately decided in the source.
3. Preserve the exact context, term evidence, intent evidence, and occurrence
   positions needed to validate the frame. Do not infer an intent or preferred
   form absent from the source.
4. A row can use `existing-match` only when its exact normalized target is in
   the read-only frozen canonical snapshot. Otherwise `registered_terms` is
   `[]`.
5. Within a session, use each normalized concept once unless distinct contexts
   are explicitly explained. Conflicting expected outcomes for one concept are
   a single `exception`, not competing rows.
6. Reviewer B independently verifies source fidelity, snapshot membership,
   primary target, and the matrix-derived outcome. Agreement means agreement
   with the matrix, not agreement with a prior outcome count.

The expected question count is `0` only when the session contains no expected
`exception`; otherwise it is exactly `1`, regardless of the number of
exceptions. The evaluator's `unexpected_exception_count` is not an
outcome-exactness gate: a generated exception matched to a reviewed row can
still contradict that row's incorrect expected label.

## Why v6 labels cannot be reused

The v6 first-run result is preserved at
`workspace/audit/20260721-real-conversation-ux-v6/frozen/results/first-run/`.
Its four reviewed rows expected `observe`, but the frozen generated payload
validated each matching target and produced these matrix outcomes:

| v6 case ID | Old expected label | Frozen actual outcome | Reason the old label is unusable |
| --- | --- | --- | --- |
| `real-v6-01-stop-conditions` | `observe` | `exception` | An affirmed durable definition satisfies row 7. |
| `real-v6-01-primary-root` | `observe` | `exception` | An affirmed durable definition satisfies row 7. |
| `real-v6-01-common-deduplication` | `observe` | `exclude` | Its emitted frame was a negated `mention`, which satisfies row 3. |
| `real-v6-01-dedicated-collision-rejection` | `observe` | `exception` | An affirmed adoption satisfies row 6. |

Therefore none of the v6 expected labels may be copied into the next corpus.
The next reviewers must derive labels afresh from the next source and this
matrix. This conclusion does not repair, rerun, or change the v6 frozen
artifacts.

## G1 acceptance evidence

- The matrix reproduces the fixed classifier order, including automatic
  `exclude`, `observe`, and `existing-match` routes and the single combined
  `exception` question route.
- The v6 four-case comparison records both the former reviewed label and the
  preserved first-run outcome, with a specific matrix rule for each mismatch.
- The document changes no runtime source, canonical DB, sync target, or
  frozen v6 artifact.

## Next boundary

G1 is complete. G2 may now define how the next manifest, attestation, blind
generator procedure, and evaluator will freeze and verify every allowed input.
It must not create a source row or holdout directory until its own contract is
complete.
