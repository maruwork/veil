# VEIL v10 adapter/core compatibility recovery design

**Status:** R1--R5 acceptance complete. The real-core suite passed: 11 focused
v10 tests, Python compilation, static no-fake-core inspection, and 346 VEIL
project tests. G4-v10 fresh-source eligibility and G5-v10 independent review
are complete. G6-v10 production integrity tooling and regression tests are now
active; v10 one-time operations remain prohibited until that tooling is
implemented and verified.

## 1. Fixed evidence and objective

v9 is closed immutable `requires-revision` evidence. Its frozen input,
generated output, and terminal runtime-error remain read-only and are neither
modified, rerun, nor used as v10 input. The v9 failure proves only that its
adapter called the legacy v4 `main()` lifecycle incompatibly; it does not prove
or disprove classifier behavior, questions, DB safety, raw fallback safety, or
any scored gate.

The v10 prerequisite is to prove that a v10 adapter can use the real v4
scoring implementation after v10 strict preflight and `runtime-started`, then
produce one terminal scored result with all ten v10 gates. Only that proof
enables a fresh G4-v10 source lineage.

## 2. Architecture decision

The v10 adapter must never call `v4_module.main()` and must never provide a
v10 manifest to the v4 legacy preflight. That path owns a legacy result
directory lifecycle and requires `host_generation.output`, both incompatible
with the v10 contract.

Instead, extract a side-effect-free `score_prevalidated(...)` callable from
the actual v4 core. It receives already parsed, schema-valid runtime rows,
generated rows, and reviewed corpus rows; returns case results and the seven
core score gates plus summary metrics; and performs no path resolution,
manifest validation, result-directory creation, result-manifest write, DB
open, or raw-text fallback. Refactor v4 `main()` to call this callable without
changing its existing v4 CLI behavior. The v10 adapter dynamically loads that
real module and calls this callable exactly once.

The v10 adapter exclusively owns:

1. strict v10 manifest/attestation, source-state, exact-six-argument, and
   blind-payload preflight;
2. creation of `runtime-started` after preflight;
3. label parsing only after runtime start;
4. DB/raw-fallback deny hooks and measured counters;
5. post-run source-state recomputation; and
6. exact terminal scored or runtime-error manifests.

The v10 manifest retains its v10 `host_generation.input_records` contract. No
compatibility-only `host_generation.output` field is added, because the real
core callable receives generated rows directly and never reads a manifest.

## 3. Acceptance-first implementation order

| Unit | Owned writes | Completion fact | Prohibited action |
| --- | --- | --- | --- |
| R1 core extraction | v4 core function plus focused equivalence tests | legacy `main()` behavior is preserved and `score_prevalidated` is callable | call v10 source/review/freeze tooling |
| R2 v10 adapter | v10-local adapter and tests | adapter calls the real module callable, never `main()` | use a fake/SimpleNamespace core |
| R3 disposable integration | disposable fixtures only | one full v10-shaped score reaches exact terminal scored manifest and ten gates | create a real v10 artifact |
| R4 failure integration | disposable fixtures only | DB, raw fallback, source state, and post-start errors are terminal and measured through the real core callable | weaken a gate or fixed manifest contract |
| R5 readiness close | recovery design, execution, and acceptance record | focused/full/static evidence is complete | start G4-v10 before R1--R4 pass |

## 4. Mandatory real-core fixture

The integration fixture loads
`workspace/audit/20260721-independent-semantic-holdout-v4/evaluate_semantic_holdout.py`
from disk. It must assert that the loaded object is the real module, invoke
`score_prevalidated`, and fail if `main()` is called. A `SimpleNamespace`,
synthetic scoring function, or direct terminal-manifest construction is not
an acceptance substitute.

The disposable fixture contains a v10-shaped manifest/attestation, one
label-free runtime row, one contract-valid generated row, and one reviewed
corpus row. It executes this exact order:

`v10 strict preflight -> runtime-started -> real v4 score_prevalidated -> post-run source-state -> terminal scored manifest`

It must prove all ten gates, exact terminal and summary field sets, case
results, and source-state-before/after equality. The test does not use a
real-conversation source and writes only a disposable directory.

## 5. Failure acceptance matrix

Each case uses the real loaded v4 module and the v10 adapter path.

| Case | Injection point | Required evidence |
| --- | --- | --- |
| legacy lifecycle guard | replace real module `main()` with a failure sentinel | scored fixture still passes; sentinel is never called |
| DB denial | make the real core's invoked analyzer dependency call `sqlite3.connect` | terminal `runtime-error`; DB counter is one or more; raw counter is zero |
| raw fallback denial | make that same real-core execution dependency call the adapter raw-fallback hook | terminal `runtime-error`; raw counter is one or more |
| source-state change | alter a declared execution source after `runtime-started` | terminal runtime-error or scored failed result; no `source_state_unchanged: true` claim |
| post-start exception | raise from the real callable after runtime start | exact terminal `runtime-error` with type/message |
| core score mismatch | give the real callable a disposable mismatching generated payload | terminal scored result with the relevant false score gate, never a fabricated pass |

The successful fixture and every failure fixture must show that v10 preflight
runs before reviewed labels are parsed and before a result directory exists.

## 6. Verification and readiness record

R5 records exact commands and outputs for:

- all v10 focused acceptance tests, including the real-core fixture;
- legacy-v4 equivalence tests for the extracted callable;
- the full VEIL project suite;
- Python compilation of every new/changed v10 file;
- VEIL lint of changed Markdown; and
- static inspection of ignored or untracked v10 files, not only `git diff`.

The v10 freeze source inventory includes the new adapter, its integrity helper,
the extracted v4 core, the semantic-frame implementation, normalization source,
payload validator, and generator procedure. Any change after a v10 freeze is
a source-state failure, not a reason to mutate or retry that package.

## 7. Entry, exit, and stop rules

R1--R5 must pass before G4-v10. Then, and only then, the order is:

`G4-v10 fresh source -> G5-v10 independent two-reviewer corpus -> G6-v10 one input-fixed package -> G7-v10 one blind generation -> G8-v10 one evaluation -> G9-v10 close`.

The v10 source must be fresh from every prior holdout, including v9. No v9
corpus, runtime input, generated frame, result, manifest, or source text is
eligible for v10 reuse. If R1--R5 fail, record the disposable failure and
return to this recovery design; do not start G4-v10. If a future G6--G8 v10
one-time operation fails, preserve its evidence and create a new recovery line
instead of retrying it.
