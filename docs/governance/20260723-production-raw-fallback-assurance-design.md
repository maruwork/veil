# VEIL production raw-fallback assurance and next-holdout design

**Status:** active implementation design. v10 is closed immutable evidence and
is never an execution target for this work.

## Objective

Make the production evaluator's `zero_raw_text_fallback` gate a measured claim
rather than an untouched counter. Complete that proof before creating a fresh
v11 source lineage. The goal is not to repair, rerun, or reinterpret v10.

## Fixed boundary

- Do not change anything under `20260723-real-conversation-ux-v10/frozen/`.
- Do not reuse v10 source, review, runtime input, generated payload, manifest,
  or result as v11 material.
- All test fixtures are disposable and use synthetic rows only.
- The production evaluator continues to call real v4 `score_prevalidated` and
  never calls legacy `v4 main()`.

## P1 — production hook

1. Extract a v11-local `RuntimeAudit` context with two deny capabilities:
   canonical DB connect and raw-text fallback.
2. Give every evaluator-side fallback-capable boundary an explicit injected
   callback. The default callback raises; no fallback may silently reconstruct
   evidence from `source_text`.
3. Install the callback around the real-core invocation. A callback invocation
   increments `raw_text_fallback_attempts` before raising.
4. Terminal `scored` manifests derive the raw gate from that counter; terminal
   `runtime-error` manifests retain the counter and error type/message.

## P2 — acceptance matrix

| Fixture | Injection | Required result |
| --- | --- | --- |
| normal real-core score | no forbidden route | terminal `scored`, raw counter 0 |
| DB route | real-core invoked dependency calls `sqlite3.connect` | terminal `runtime-error`, DB counter >=1 |
| raw fallback route | production-wired callback is invoked from the real-core execution boundary | terminal `runtime-error`, raw counter >=1 |
| post-start exception | raise after `runtime-started` | terminal `runtime-error` with error details |
| source change | mutate declared disposable inventory post-start | terminal failure; never a true unchanged gate |

Every case loads the real v4 module, uses no fake core or `main()`, and proves
preflight occurs before reviewed labels or a result directory.

## P3 — verification gate

Before v11 G4 begins: focused P1 tests pass, every changed Python file compiles,
static inspection finds no v4 `.main()` call or fake core, and the VEIL suite
completes in bounded groups. Record a readiness note with exact commands.

## P4 — fresh v11 execution order

Only after P3:

`G4-v11 fresh source -> G5-v11 independent review -> G6-v11 atomic input
fixing -> G7-v11 blind generation once -> G8-v11 evaluation once -> G9-v11
evidence close`.

The v11 frozen inventory records the evaluator with the production raw-fallback
hook. A one-time failure in G6--G8 is preserved and routes to a new recovery
line rather than a retry.
