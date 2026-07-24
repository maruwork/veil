# VEIL v7 blind frame-generation procedure

<!-- VEIL_BLIND_INPUTS: ["generator_procedure", "semantic_frame_schema", "runtime_input"] -->

The blind generator may read only:

1. the frozen `runtime_input` JSONL;
2. this frozen procedure file; and
3. the frozen `semantic_frame_schema` source.

For every runtime row, output exactly one JSON object with only the verbatim
`session_id` and a contract-v2 `payload`. Inspect the source text for each
independent primary lexical target whose definition, adoption, rename,
conflict, required property, allowed-use limit, prohibition, or state
transition is explicitly decided. Supply exact evidence and a complete critic
classification. An empty payload is valid only after determining that none is
present.

Do not read reviewed corpus rows, labels, review reports, canonical snapshot,
evaluation contract, evaluator source, prior holdouts, DB, raw source records,
or unrecorded files. Do not write anything except the reserved generated-frame
JSONL output.
