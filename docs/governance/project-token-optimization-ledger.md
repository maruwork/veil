# Project Token Optimization Ledger

## 1. Project identity

- project name: `veil`
- ledger path: `docs/governance/project-token-optimization-ledger.md`
- last reviewed date: `2026-06-25`
- current reviewer: `Codex`

## 2. Active symptom classes

| symptom class | active pressure | basis |
|---|---|---|
| `C1` output-volume reduction | `yes` | Runtime sync, lint, and status work creates repetitive output pressure. |
| `C2` reread / retrieval reduction | `no` | The current first-wave pressure is not document retrieval. |
| `C3` continuity / memory support | `yes` | Thin entrypoint reading and bounded runtime/doc reads are part of the active route. |
| `C4` code-traversal reduction | `no` | No code-understanding index is active in the current route. |

## 3. Active trial table

| symptom class | active trial | canonical status | automation | why active | where referenced |
|---|---|---|---|---|---|
| `C1` | `output compression helper` | `active` | `A2` | RTK-filtered sync, lint, and validation output is the documented default command path. | `README.md`, `docs/governance/ai-agent-runtime-token-optimization.md` |
| `C2` | `none` | `none` | `-` | No retrieval trial is active in the current route. | `none` |
| `C3` | `memory / continuation discipline` | `active` | `A1` | Thin entrypoint reading and bounded reads are part of the default route. | `README.md`, `docs/governance/ai-agent-runtime-token-optimization.md` |
| `C4` | `none` | `none` | `-` | No code-traversal trial is active in the current route. | `none` |

## 4. Current-route contract

- `README.md`
- `common/README.md`
- `docs/governance/ai-agent-runtime-token-optimization.md`
- `docs/veil-design.md`
- `shared/runtime/veil-sync.py`
- `shared/runtime/veil-lint.py`

## 5. Operator contract

- default token-saving route: start from `README.md`, then stay inside bounded `docs/`, `shared/runtime/`, `shared/tools/`, and exact files under change before broader repository scans.
- command-automatic helper: `rtk ...`
- broad-read boundary helper: root `.claudeignore`
- savings delivery mode: `default`
- project-local implementation shelf: `common/pj-token-optimization/`
- savings by default: `C3` savings happen through the bounded route; `C1` savings happen because repetitive sync, lint, and validation commands are expected to run through `rtk ...`; Claude broad reads are further narrowed by root `.claudeignore`.

## 6. Artifact contract

- `none`

## 7. Boundary contract

- root `.claudeignore`
- `docs/governance/ai-agent-runtime-token-optimization.md` excludes archive, workspace, and unrelated hidden support shelves from default reads.

## 8. Overlap status

- status: `compliant`
- overlap exists: `no`
- overlapping symptom class: `none`
- note: `C1` and `C3` each have one active first-wave trial; no same-class duplication is active.

## 9. Replacement status

- status: `none`
- old active trial: `none`
- candidate replacement: `none`
- symptom class: `none`
- old automation class: `-`
- candidate automation class: `-`
- verification path: `none`
- cutover condition: `none`
- impact judgment: `none`

## 10. Measurement snapshot

- measurement date: `2026-06-25`
- measurement scope: `veil` repo-owned files, excluding vendor and tool-internal trees such as `.git/`, `.claude/`, `node_modules/`, `.next/`, `dist/`, `build/`, `.venv/`, `venv/`, and `.pytest_cache/`
- `M1 = 30`
- `M2 = 1078`
- `M3 = 56`
- `M4 = 4`
- `M5 = 16`
- `M6 = 31`
- `M7 = true`
- `M8 = 1`
- satisfied signals: `S2`, `S5`
- non-satisfied signals: `S1`, `S3`, `S4`, `S6`
- chosen active automatic trial: `output compression helper`
- chosen active route discipline: `memory / continuation discipline`
- excluded overlapping trials: `repo-wide compression pack`, `Headroom`
- escalation beyond Layer 2: `none`
- deferred additional trial: `none`
- reason for deferral: the current measured pressure is output-heavy but does not yet justify retrieval, code-index, or integrated runtime escalation beyond the compatibility-preserving first-wave route.
