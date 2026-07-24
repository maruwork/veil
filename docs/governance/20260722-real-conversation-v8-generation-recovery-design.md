# VEIL v8 blind-generation recovery design

**Status:** G7-R implemented and rehearsed after the fixed v7 G7 failure. This
document does not authorize a v8 source, review, freeze, real-holdout
generation, evaluation, DB write, sync, installation, Git, or release action.

## Fixed v7 boundary

v7 is not repaired. Its frozen package and only generated output remain
failure evidence: the output envelope and session binding were valid, but a
payload `intent_evidence` string did not occur in the frozen runtime input.
No v7 artifact, frozen input, generator procedure, or source recorded in its
manifest may be changed to make that output pass.

## Defect addressed

The v7 contract froze permitted files and checked only the output envelope
before the evaluator. It did not prove that the isolated agent's text display
and text write path preserved non-ASCII exact evidence before spending the
one-time real-holdout generation.

This is a generation-transport defect, not a classifier result and not an
expected-outcome verdict.

## v8 architecture

v8 is a distinct holdout with its own procedure, integrity implementation,
evaluator wrapper, tests, and source-state inventory. It must not import a
mutable v7 implementation as an unrecorded dependency. The v8 inventory may
name a v7 source only when that file is deliberately frozen as a v8 dependency
with its path, hash, and byte count.

The blind generator remains limited to exactly three recorded reads:

1. the v8 generator procedure;
2. the frozen semantic-frame schema source; and
3. the frozen label-free runtime input.

It may write only the reserved v8 `frozen/generated-frames.jsonl`.

### Exact-text transport rule

The v8 procedure must require an ASCII-safe transport without converting the
underlying UTF-8 runtime bytes:

1. decode runtime JSONL as UTF-8 locally;
2. display source fields to the isolated generator only as JSON strings with
   `ensure_ascii=True`;
3. require the generator to write JSONL with `ensure_ascii=True`;
4. parse the resulting JSON as UTF-8 before validation, so escaped code points
   become the original Unicode text; and
5. reject any payload whose evidence does not occur exactly in its runtime
   source text.

The procedure must not rely on a terminal code page, visual copy/paste of raw
non-ASCII text, or a fourth project file to perform this transport.

### Mandatory rehearsal gate

Before any v8 source is selected or frozen, an isolated generator performs a
disposable rehearsal using a non-holdout UTF-8 runtime fixture. The fixture
contains non-ASCII evidence and no expected outcome, reviewer artifact,
canonical snapshot, or production source.

The rehearsal passes only when all of these facts are mechanically proved:

- the generator attests to reading only its procedure, schema, and rehearsal
  runtime input;
- its ASCII-only JSONL has exactly one outer row per runtime session;
- every payload passes contract-v2 semantic-frame validation against the
  decoded UTF-8 runtime text; and
- a deliberate evidence mismatch is rejected by the same validator.

The rehearsal output is not a holdout, is not scored, and cannot be promoted
to a v8 input. A rehearsal failure is retryable because it spends no holdout
generation.

G7-R proved this gate with the v8 procedure,
`workspace/audit/20260722-real-conversation-ux-v8/validate_generated_payloads.py`,
and a one-row non-ASCII fixture. An isolated generator wrote one ASCII-only
rehearsal row; the validator passed with one runtime row, one output row, and
one validated frame. The generated output SHA-256 is
`68ea2f91b15ed54a3952ae281c668dc468c51ff95f23f151e7689eb5ad5d7ab8`.

### v8 validation order

The v8 integrity implementation must expose one shared
`validate_generated_payloads` operation. It validates outer envelope, session
identity, payload field sets, critic coverage, and exact evidence against
runtime input without reading a reviewed corpus or expected label.

- G7 invokes it immediately after its one output write.
- G8 invokes the same operation during preflight before it creates
  `results/first-run/` or reads expected labels.

Thus a payload defect is detected by the same rule in rehearsal, G7, and G8.

## Recovery sequence

`G7-R -> G4-v8 -> G5-v8 -> G6-v8 -> G7-v8 -> G8-v8 -> G9-v8`

1. **G7-R — transport recovery:** implement the v8-only procedure,
   `validate_generated_payloads`, non-ASCII fixture, deliberate-mismatch test,
   and successful isolated rehearsal. No real source or frozen directory.
2. **G4-v8 — fresh-source eligibility:** obtain a new authorized anonymized
   source distinct from v1--v7.
3. **G5-v8 — independent review:** create and mechanically validate a
   two-reviewer corpus without exposing it to the future generator.
4. **G6-v8 — atomic freeze:** freeze the full v8 input set once only.
5. **G7-v8 — blind generation once:** use the rehearsal-proved ASCII-safe
   procedure and validate the generated payload before evaluation.
6. **G8-v8 — evaluation once:** preflight with the shared payload validator,
   then score once only if all preflight checks pass.
7. **G9-v8 — close evidence:** separate procedure validity, generation
   validity, classifier result, and remaining risks.

G7-R, G4-v8, G5-v8, and G6-v8 are complete. G7-v8 is the next unstarted Goal.

## Stop rules

- A failed rehearsal stops G7-R but does not consume a v8 holdout.
- A G7-v8 failure fixes that output and returns to a new authorized holdout;
  it is never regenerated.
- A G8-v8 preflight or score failure fixes the first-run result and is never
  rerun.
- No v7 evidence may be overwritten, relabeled, or reused as a v8 source.
