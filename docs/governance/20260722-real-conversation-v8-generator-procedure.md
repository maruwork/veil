# VEIL v8 blind frame-generation procedure

<!-- VEIL_BLIND_INPUTS: ["generator_procedure", "semantic_frame_schema", "runtime_input"] -->

The blind generator may read only this procedure, the frozen semantic-frame
schema source, and the frozen label-free runtime-input JSONL. The host assigns
one output path; write only that path and do not discover it by reading another
file.

## ASCII-safe exact-text transport

Read the runtime JSONL as UTF-8. When inspecting any `source_text`, render it
as an ASCII JSON string with `ensure_ascii=True`; do not copy non-ASCII text
through a terminal display or rely on its code page. Treat JSON `\uXXXX`
escapes as the exact decoded Unicode source text.

Write each output object as one ASCII-only JSONL line using
`ensure_ascii=True`. The object must contain exactly the verbatim
`session_id` and one contract-v2 `payload`. Evidence text inside the payload
must use the same decoded characters as the runtime source; JSON escaping is
required in the file but does not change the decoded evidence.

For every runtime session, identify each independent primary lexical target
whose definition, adoption, rename, conflict, required property, allowed-use
limit, prohibition, or state transition is explicitly decided. Supply exact
evidence and a complete critic classification. An empty payload is valid only
after determining that no such target exists.

Do not read a reviewed corpus, expected outcome, review report, canonical
snapshot, evaluation matrix, evaluator source, prior holdout, DB, raw source
record, or any unrecorded file. Do not write prose, a report, or a second
output file.
