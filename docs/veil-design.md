# VEIL Design Reference

Detailed specification for the runtime and support components. Entry point: [README.md](../README.md).

---

## 1. Design principles

- **Local-only**: runs on Python standard library alone
- **Zero dependencies**: no `pip install` required
- **Pre-emptive control**: inject vocabulary rules before AI output rather than correcting after
- **Fixed main route**: `capture → normalize → sync → lint` is the complete operational loop
- **Fixed scope**: VEIL is a terminology guardrail for AI-assisted technical writing
- **Selective enforcement**: enforce tightly only at the flow and high-impact terms; do not control the full natural text

VEIL mainline is complete when all of the following stay true:

- capture classification is fixed
- sync reads adopted rules from `~/.veil/veil.db` and updates registered targets
- lint rejects registered source terms while accepting preferred forms
- `shared/runtime/veil-status.py --check` reports no setup errors for a healthy install
- `shared/tools/veil-db.py export-html` regenerates `~/.veil/veil.html`

---

## 2. Data locations

| Data | Location | Role |
|------|----------|------|
| Vocabulary rule canonical | `~/.veil/veil.db` | canonical source of truth |
| Vocabulary review HTML | `~/.veil/veil.html` | Browser review and modification surface |
| Sync target list | `~/.veil/targets.json` | list of sync target file paths |
| Tool config | `~/.veil/config.json` | written by `install.sh` / `install.ps1` and `--add`; keys: `sync_script`, `veil_root`, `lang` |

`~/.veil/` is fixed to the user home directory. In the current phase, canonical is SQLite and HTML is the review surface.

---

## 3. Component details

### 3-1. veil-capture skill

Resolves vocabulary consistency at task close or a conversation boundary while keeping routine analysis off the user's critical path.

**Installation paths**

| Tool | Path |
|------|------|
| Claude Code | `skills/claude-code/veil-capture.md` |
| Codex | `skills/codex/veil-capture/SKILL.md` |

**Behavior**

1. The runtime instruction in each registered sync target starts the installed capture workflow automatically once at a substantive task close or conversation boundary. Manual invocation remains an on-demand check and recovery route.
2. The host AI extracts evidence-backed semantic decision frames from the
   supplied text or current conversation, then performs a separate critic pass
   for missed durable decisions, spurious frames, unsupported evidence, and
   unresolved mappings.
3. Pass the exact source text and an isolated contract v2 frame JSON file to
   `veil-classify.py --outcomes --semantic-frames <path> --json`. Local VEIL
   validates the untrusted evidence and classifies each validated frame into
   exactly one of `exclude`, `observe`, `existing-match`, or `exception`.
4. Keep `exclude`, `observe`, and `existing-match` in the background. An automatically triggered normal session adds no VEIL-specific output and requires zero user judgments.
5. Batch every `exception` into one short question. Never ask one question per term and never show a numbered candidate table.
6. If the invoking request already supplies an exact preferred form and explicit registration instruction, do not ask the same question again.
7. Never create a canonical rule from repetition alone.
8. After acceptance, record only accepted exceptions to `~/.veil/veil.db` as one atomic batch, regenerate `~/.veil/veil.html`, and run `veil-sync.py`.
9. If the atomic write, export, or sync fails, report the exact incomplete stage and never claim completion.

**Decision boundary**

- `exclude`: validated negated, reported, non-authoritative, or critic-rejected wording.
- `observe`: validated temporary, one-off, or low-impact unclear wording; retained only for analysis.
- `existing-match`: an exact canonical match; this is an automatic successful result and is not an exclusion.
- `exception`: an affirmed durable adoption, rename, definition, conflict,
  high-impact uncertainty, or material extractor/critic disagreement.

The host AI uses `unclear` rather than guessing. Validated low-impact unclear
recurrence stays `observe`; unresolved durable or high-impact evidence becomes
one combined `exception`, never a silent exclusion.

Guardrail: VEIL-generated outputs and sync targets must not live under this repo's `common/` or `archive/` directories. Use `~/.veil/` as the canonical output area and `workspace/` only for repo-local temporary verification artifacts.

### 3-2. shared/runtime/veil-sync.py

Prioritizes the SQLite canonical and applies rules directly to AI tool configuration files.

**Authority**

- reads: `~/.veil/veil.db`, `~/.veil/targets.json`, `~/.veil/config.json`
- writes: sync target files

**Behavior**

1. Read active rules from DB canonical
2. Combine the background-capture runtime instruction, vocabulary rules, and behavior description
3. Write the `VEIL_START` / `VEIL_END` block to each registered sync target

**Commands**

```bash
python shared/runtime/veil-sync.py
python shared/runtime/veil-sync.py --add <path>
python shared/runtime/veil-sync.py --list
python shared/runtime/veil-sync.py --remove <path>
python shared/runtime/veil-sync.py --remove <path> --purge
```

### 3-3. shared/runtime/veil-normalize.py

Read-only helper that normalizes a candidate term list after capture and returns cross-check results in two groups.

**Authority**

- reads: `~/.veil/veil.db`
- non-authority: helper output, draft candidate list

**Behavior**

1. Lowercase, absorb space/hyphen/underscore variants, absorb light singular/plural variants
2. Group each normalized cluster with its variants and occurrence count
3. If an existing rule matches, return as `Existing matches:` group with preferred and source_file
4. If no existing rule, return as `New candidates:` group

**Text output format**

### 3-4. shared/runtime/veil-classify.py

Read-only analyzer for free-form text or chat transcript JSON.

**Authority**

- reads: optional `~/.veil/veil.db` for existing matches
- writes: none
- non-authority: classification labels, outcome analysis, and diagnostic candidate modes

**Primary behavior**

`--outcomes --semantic-frames <path>` returns contract version `2` with:

- `analysis_mode=semantic-frames`, `diagnostic_only=false`, and
  `write_allowed=false`;
- `summary.user_action_required`: whether any exception exists
- `summary.question_count`: `0` for normal sessions, otherwise `1` for the combined exception question
- counts for `exclude`, `observe`, `existing-match`, and `exception`
- `exceptions`: the only terms allowed onto the user decision path
- `results`: deterministic policy results traceable to the validated frames

Semantic frames are untrusted input. Local validation requires allowed fields
and enums, exact evidence substrings and occurrence numbers, complete critic
classification, supported rename mappings, unique frame IDs, and conflict
groups with at least two distinct forms. Invalid input returns a structured
error and never falls back to regex for a production decision.

For definitions, corrections, and contrasts, the host frames the primary
lexical target: the wording whose meaning, allowed use, or preferred form is
being decided. Generic predicates and explanatory phrases remain evidence
unless the source independently decides them. Several independent targets may
appear in one session; one definition is not split into a target plus its
explanatory category.

`--outcomes` without `--semantic-frames` remains contract version `1`, marked
`analysis_mode=raw-text-diagnostic`, `diagnostic_only=true`, and
`write_allowed=false`. The label classifier (`industry_term /
coined_or_shortened / file_config_identifier / other / unknown`),
`--preview-only`, `--investigation-only`, and `--adoptable-only` are
compatibility diagnostics, not user-facing adoption semantics.

**Commands**

```bash
python shared/runtime/veil-classify.py --stdin --outcomes --semantic-frames <agent-generated-frame-path> --json
python shared/runtime/veil-classify.py transcript.json --chat-json --outcomes --semantic-frames <agent-generated-frame-path> --json
python shared/runtime/veil-classify.py --text "Use decision boundary consistently." --outcomes --json  # diagnostic only
```

### 3-5. shared/runtime/veil-lint.py

Checks whether registered source terms remain in final text, acting as a pre-response gate.

**Authority**

- reads: `~/.veil/veil.db`
- non-authority: capture report, temporary drafts

**Behavior**

1. Load rules in `- original → preferred` format from SQLite canonical
2. Scan the input text
3. Return any registered source terms found as violation candidates
4. Exclude inline code, fenced code blocks, and indented code blocks from scanning
5. Return registered rule violations as fail-close
6. Return the suggested fix and a first-hit line preview for each violation

**Commands**

```bash
python shared/runtime/veil-lint.py <file>
python shared/runtime/veil-lint.py --stdin
python shared/runtime/veil-lint.py --text "I reviewed the current state"
python shared/runtime/veil-lint.py --json
```

### 3-6. shared/runtime/veil-status.py

Returns VEIL status and setup diagnostics. Without arguments: status summary. With `--check`: setup diagnostics.

**Authority**

- reads: `~/.veil/veil.db`, `~/.veil/veil.html`, `~/.veil/targets.json`, skill files
- writes: nothing

**Behavior (no arguments)**

1. Show canonical DB existence and rule count
2. Show HTML last-updated timestamp
3. Show sync target count and existence check
4. Always exit 0

**Behavior (--check)**

1. Check the canonical DB, generated HTML, targets configuration, each sync
   target, and installed Skills.
2. Return a machine-readable `items[]` list. Every item has a stable `level`
   value. Required delivery members use exactly `OK`, `STALE`, `MISSING`, or
   `ERROR`; sync-target diagnostics may use non-failing `WARN`.
3. `OK` means present, readable, and derived from the declared current inputs.
   `STALE` means present/readable but derived from different source or canonical
   data. `MISSING` means absent where required. `ERROR` means unreadable,
   malformed, corrupt, or internally inconsistent.
4. Exit 1 when a required delivery member is `STALE`, `MISSING`, or `ERROR`.
   A separately configured or non-required target warning does not change the
   exit status.
5. Without `--check`, retain the human-readable summary and exit 0. With
   `--json`, preserve the same state values rather than translating them.

**Commands**

```bash
python shared/runtime/veil-status.py
python shared/runtime/veil-status.py --check
python shared/runtime/veil-status.py --json
```

### 3-7. Profile support tools

`shared/tools/veil-profile-audit.py`, `shared/tools/veil-profile-export.py`, `shared/tools/veil-db.py`, and `shared/tools/veil_rule_store.py` are support runtime, not mainline runtime. `veil-db.py` and `veil_rule_store.py` assist with SQLite canonical schema / import / readback / upsert / HTML export. `veil-profile-audit.py`, `veil-normalize.py`, and `veil-lint.py` read from a SQLite source.

**Authority**

- reads: `~/.veil/veil.db` or exported `rules.json`
- writes:
  - `veil-profile-audit.py`: nothing
  - `veil-profile-export.py`: export output directory only
  - `veil-db.py`: specified SQLite DB path and HTML output path
  - `veil_rule_store.py`: SQLite DB / support serialization helper

**Usage**

1. `shared/tools/veil-profile-audit.py`
   - Visualize level distribution and legacy flat rule presence
   - Supports `--db` for SQLite source reading
2. `shared/runtime/veil-normalize.py`
   - Supports `--db` for SQLite source reading
3. `shared/runtime/veil-lint.py`
   - Supports `--db` for SQLite source reading
4. `shared/tools/veil-profile-export.py`
   - Export current default profile as a JSON domain profile pack
5. `shared/tools/veil-db.py`
   - Handle SQLite canonical `init-db / import-seed / readback / upsert-rule / export-html`
   - `export-html` writes `~/.veil/veil.html`: a searchable browser list of all registered terms with copy buttons

**Review and modification via HTML**

`export-html` is the browser review route:

1. Regenerate `~/.veil/veil.html`.
2. Open it in a browser; the UI localizes to English, Japanese, Korean, Simplified Chinese, Traditional Chinese, or Arabic.
3. Normal task-close review runs in the installed Skill. The HTML is an
   optional recovery surface, not the semantic decision engine.
4. Paste the exact text and use **Copy complete AI review request** as the main
   route. It sends the complete text to the installed semantic-frame workflow
   and remains one user action regardless of term count.
5. **Run local diagnostic preview** is optional. It is contract v1 regex output
   and may miss or misclassify decisions. Zero preview entries must never be
   presented as proof that no vocabulary decision exists.
6. The copied request requires contract v2 frames, a separate critic pass,
   exact evidence, at most one combined question, and no write before acceptance.
7. After the user accepts the combined proposal, the chat-side Skill records
   all accepted mappings through one validated JSON batch. User text is data
   and must not be interpolated into shell commands.
8. Selecting an individual diagnostic item is an optional fine-tuning route;
   it must be verified through AI review before saving.
9. Registered rows use `Preferred`, `Alternative 1`, and `Alternative 2`. Alternatives are optional.
10. **Advanced: copy commands** is a recovery route, not the normal workflow.

The static browser file never writes directly to the canonical DB. Accepted chat-side registration must regenerate HTML and sync before it is called complete.

**Commands**

```bash
python shared/tools/veil-profile-audit.py
python shared/tools/veil-profile-audit.py --db /tmp/veil_smoke.db
python shared/tools/veil-profile-audit.py --seed-file /tmp/exported_rules.json
python shared/runtime/veil-normalize.py --text "current state" --db /tmp/veil_smoke.db --json
python shared/runtime/veil-lint.py --text "current state" --db /tmp/veil_smoke.db
python shared/tools/veil-db.py init-db --db /tmp/veil_smoke.db
python shared/tools/veil-db.py import-seed --db /tmp/veil_smoke.db --seed-file shared/default-profile/technical-writing-default.json --yes
python shared/tools/veil-db.py readback --db /tmp/veil_smoke.db --json
python shared/tools/veil-db.py upsert-rule --db /tmp/veil_smoke.db --term "current state" --preferred "present state"
python shared/tools/veil-db.py export-html
```

### 3-8. Package import structure

`shared/__init__.py`, `shared/runtime/__init__.py`, and `shared/tools/__init__.py` are empty but intentionally present. They enable the `from shared.tools.veil_rule_store import ...` package import path. With project root added to `sys.path`, the `try: from shared.tools... except ModuleNotFoundError: from veil_rule_store...` fallback pattern depends on them. Do not delete these files.

---

## 4. Data format

Rules are stored in SQLite canonical rows and may be exported as `rules.json` for profile packs.

On a new entry, confirm one preferred form, record it to the canonical DB, then regenerate HTML.

Stored wording fields:

| Field | Meaning |
|-------|---------|
| `preferred` | The enforced form synced to targets |
| `preferred_alt_2` | Optional alternative retained for review, not synced |
| `preferred_alt_3` | Optional second alternative retained for review, not synced |

Alternatives are optional. VEIL must not invent alternatives or expose numbered candidate slots merely to fill the schema. Only `preferred` is synced to AI tool configuration files.

---

## 5. Exclusion-first outcome order

After exact evidence and the critic result have been validated, assign outcomes
in this order:

1. Material critic disagreement -> `exception`.
2. Negated, reported, or non-authoritative frame -> `exclude`.
3. Exact canonical use without rename, conflict, or a requested wording change -> `existing-match`.
4. Temporary or one-off frame -> `observe`.
5. Affirmed durable adoption, rename, definition, or conflict -> `exception`.
6. Low-impact unclear recurrence -> `observe`.

The order is fail-closed for writes: only an accepted `exception` may create a
rule. Repetition, fixture membership, label classification, or a raw-text regex
match is never sufficient authorization to register.

Success gates:

- normal session: zero user judgments
- exception session: at most one combined judgment
- high-impact false exclusion: zero in the release evaluation set
- `existing-match` precision: at least 99%
- no candidate table, candidate numbering, or manual command sequence in the normal flow

---

## 6. Core and profile

### VEIL core

- `veil-capture`
- `shared/runtime/veil-normalize.py`
- `shared/runtime/veil-sync.py`
- `shared/runtime/veil-lint.py`
- `shared/runtime/veil-status.py`
- `capture → normalize → sync → lint` fixed operational loop
- fixed classification order

### Domain profile

- `~/.veil/veil.db`
- `~/.veil/veil.html`
- prohibited term set
- high-demand term set
- how to handle defined terms
- criteria for keeping proper nouns
- `lint` enforcement level

The current default profile is for technical writing.
The bundled seed for that profile lives at `shared/default-profile/technical-writing-default.json`.

To distribute the current default profile outside the repo or as a separate bundle, use `shared/tools/veil-profile-export.py` to create a profile pack. This is a support route for domain profile separation — it does not change the mainline `capture → normalize → sync → lint` flow.
For local reset or first-install seeding, import `shared/default-profile/technical-writing-default.json` into the canonical DB.

The export manifest carries `domain`, `intended_use`, and `base_profile` as the minimal contract for branching from the technical writing default to an industry-specific profile.

---

## 7. Operational loop

- Have the AI produce evidence-backed semantic frames and run its critic pass
  automatically at every substantive task close or conversation boundary; do
  not require the user to start the normal flow.
- Keep a no-decision automatic run silent.
- Keep `exclude`, `observe`, and `existing-match` automatic and invisible in normal output.
- Ask once only when one or more `exception` results exist.
- Sync only after accepted wording is recorded.
- Lint before every final response; fix and re-check violations.
- If a registered source term must remain intentionally, record the reason.

`veil-normalize.py` remains a read-only diagnostic for variants. Its `Existing matches` and `New candidates` groups do not authorize registration and do not define the user interaction.

Use `shared/runtime/veil-status.py --check` for delivery health. Use `veil-profile-audit.py` for read-only profile auditing. Use `veil-profile-export.py` only for explicitly authorized profile distribution.

---

## 8. Delivery freshness contract

The SQLite-canonical and delivery-reliability migration completed on 2026-07-20. The following requirements are permanent runtime and release contracts, not an active migration lock.

### 8-1. Canonical and delivery contract

- `~/.veil/veil.db` is the canonical vocabulary store.
- The repository is the source of the runtime, generated review HTML, and the
  Codex and Claude Code capture skills.
- The delivery set is one unit:
  1. source runtime and skill templates in the repository;
  2. generated `~/.veil/veil.html`;
  3. installed `~/.agents/skills/veil-capture/SKILL.md`;
  4. installed `~/.claude/commands/veil-capture.md`.
- A delivery set is not healthy merely because its files exist. Each member
  must match its configured source and declared inputs, or be reported as
  stale, missing, or erroneous.

### 8-2. Freshness states

`veil-status` must distinguish the following states for each generated or
installed delivery member:

- `OK`: present, readable, and derived from the current declared inputs.
- `STALE`: present and readable, but derived from different source content or
  older canonical data.
- `MISSING`: absent where the configured installation expects it.
- `ERROR`: unreadable, corrupt, internally inconsistent, or unable to verify.

For `veil-status --check`, any `STALE`, `MISSING`, or `ERROR` result on a
required delivery member must produce a non-zero exit status. A warning about a
non-required or separately configured sync target does not change this delivery
result.

### 8-2a. Freshness inputs and legacy outputs

- HTML freshness is calculated from an exporter-owned manifest, not from a
  whole SQLite file hash. The manifest is an `application/json` script element
  in the generated HTML and has these required fields:

  - `format`: the manifest schema version;
  - `template_sha256`: UTF-8 bytes of `_HTML_TEMPLATE`;
  - `i18n_sha256`: canonical JSON of the full embedded `_HTML_UI_BY_LANG`
    payload;
  - `capture_taxonomy_sha256`: canonical JSON of
    `capture_taxonomy_payload()`;
  - `active_rules_sha256`: canonical JSON of the normalized, sorted active
    rows rendered into the table. Each row contains only `term_original`,
    `term_normalized`, `preferred`, `preferred_alt_2`, and `preferred_alt_3`;
  - `settings_sha256`: canonical JSON of the embedded `default_lang`,
    `db_cli_path`, `db_path`, and `html_path`; and
  - `content_sha256`: the final document fingerprint with this field's value
    replaced by its empty placeholder.

  Canonical JSON means UTF-8, sorted object keys, and compact separators. A
  generation timestamp may be present for diagnosis, but is not a freshness
  input.

  `veil-status` recomputes the first five fingerprints from the configured
  source and validates `content_sha256` against the installed document. A
  mismatch in any required field is `STALE`; an unreadable, malformed, or
  internally inconsistent manifest is `ERROR`.
- A Codex or Claude Code skill is fresh exactly when
  `fingerprint(installed bytes) == fingerprint(source bytes)` for its
  corresponding source template. Skills do not require an embedded manifest.
- A generated HTML file without a valid exporter-owned freshness manifest is
  `STALE`, not implicitly `OK`.
- A failed manifest read, invalid fingerprint, corrupt DB, or unreadable
  delivery member is `ERROR`.

The SHA-256 encoding and canonical serialization above are the freshness
contract. Implementations may add diagnostic fields, but must not treat file
existence as freshness or weaken the required comparisons.

### 8-3. Release gates

A UX release is complete only when all of the following are true in the same source state:

1. classifier, outcome, locale, DB, Skill, and HTML tests pass;
2. stratified evaluation meets the outcome success gates in section 5;
3. browser E2E confirms the normal no-decision route, existing-match auto-resolution, the one-combined-decision route for multiple exceptions, locale switching, and optional registration-form handoff;
4. `veil-status --check --json` reports every required delivery member `OK` after installation;
5. hosted checks pass for the merged source revision.

Generating or detecting a delivery member is not enough: source, generated HTML, installed Skills, and declared inputs must be fresh as one delivery set. Installation, distribution, commit, merge, and push remain explicit release actions and are not implied by read-only UX evaluation.
