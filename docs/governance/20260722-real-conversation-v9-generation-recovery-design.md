# VEIL v9 punctuation-fidelity generation recovery

**Status:** G7-R2 and G4-v9 complete. G5-v9 is next and not active. This
document does not authorize freeze, real-holdout generation, evaluation, DB
access, sync, or release actions.

## Fixed v8 boundary

The v8 one-time output is immutable failure evidence. Its JSON transport was
ASCII-safe, but the isolated generator changed full-width equals (`U+FF1D`) to
ASCII equals (`U+003D`) inside semantic evidence. It must not be regenerated,
evaluated, or repaired.

## v9 corrective contract

The v9 generator may still read only procedure, schema, and label-free runtime
input. Before its only output write, it must:

1. decode runtime JSON as UTF-8 and render source text with `ensure_ascii=True`;
2. derive every evidence string as a contiguous substring of the decoded source;
3. preserve every Unicode code point exactly, with no normalization,
   transliteration, punctuation substitution, or visual retyping; and
4. validate each evidence occurrence against the in-memory decoded source
   before serializing one ASCII-only JSONL output.

The generator may inspect its in-memory payload for this self-check. It may
not read a reviewer artifact, label, matrix, evaluator, DB, history, prior
holdout, or its output after writing it. The host's independent validator still
checks the written file before any evaluator may read labels.

## Mandatory disposable rehearsal

Before any v9 source selection or freeze, a newly isolated generator must use
a non-holdout fixture containing full-width punctuation. The fixture requires
both term and intent evidence spanning `U+FF1D`. The rehearsal passes only if:

- the output is ASCII-only JSONL;
- decoded evidence retains `U+FF1D` exactly and passes the shared v9 validator;
- a deliberately substituted `U+003D` output is rejected; and
- no review, canonical snapshot, source history, freeze, or evaluation input
  was exposed to the generator.

The proof passed. G4-v9 then selected one new anonymized source with no session,
text-containment, or shared-12-gram overlap against v1-v8. G5-v9 may now
create an independent two-reviewer corpus, followed by G6-v9, G7-v9, G8-v9,
and G9-v9.
