# VEIL v9 blind frame-generation procedure

<!-- VEIL_BLIND_INPUTS: ["generator_procedure", "semantic_frame_schema", "runtime_input"] -->

Read only this procedure, the frozen semantic-frame schema, and the frozen
label-free runtime JSONL. Write only the host-assigned output path.

## Exact Unicode evidence rule

Decode runtime JSONL as UTF-8. Render `source_text` only with
`json.dumps(source_text, ensure_ascii=True)`. Treat every decoded code point as
data: do not normalize Unicode, transliterate, substitute punctuation, or
retype a visually similar character. In particular, `\uff1d` is not `=`.

For each frame, select `term_evidence.text` and every `intent_evidence[].text`
by extracting a contiguous substring from the decoded `source_text`. Before
writing, perform this in-memory check for each evidence object: its 1-based
occurrence must exist in that same decoded source. If it does not, correct the
in-memory payload before the single output write; never write then repair an
output file.

Write one ASCII-only JSONL object per runtime session using `ensure_ascii=True`.
Each object has exactly `session_id` and a contract-v2 `payload`. The session
ID is copied verbatim. Do not read review artifacts, labels, snapshots,
evaluation matrices, evaluators, source history, DBs, prior holdouts, or any
other file. Do not write a report or second output.
