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

Detects English terms, coined terms, and abbreviations from AI conversation. At task close / conversation boundary, records to the SQLite canonical as the close operation for the current phase, then updates the HTML and sync targets.

**Installation paths**

| Tool | Path |
|------|------|
| Claude Code | `skills/claude-code/veil-capture.md` |
| Codex | `skills/codex/veil-capture/SKILL.md` |

**Behavior**

1. Extract candidate terms from conversation or target text
2. Prefer state terms, judgment terms, structural terms, operational labels over bare verbs
3. Use `shared/runtime/veil-normalize.py` as needed to collapse variants and cross-check existing rules
4. Classify each term: keep as proper noun / translate as common term / fix as defined term / drop as prohibited / skip
5. Adopt high-demand, high-impact, and VEIL-core terms first
6. Skip low-frequency, context-dependent, and unresolved project-specific terms
7. On user confirmation of adopted terms, record to `~/.veil/veil.db` canonical in the current phase
8. Regenerate `~/.veil/veil.html` via `shared/tools/veil-db.py export-html`
9. Run `shared/runtime/veil-sync.py` for immediate sync

Guardrail: VEIL-generated outputs and sync targets must not live under this repo's `common/` or `archive/` directories. Use `~/.veil/` as the canonical output area and `workspace/` only for repo-local temporary verification artifacts.

### 3-2. shared/runtime/veil-sync.py

Prioritizes the SQLite canonical and applies rules directly to AI tool configuration files.

**Authority**

- reads: `~/.veil/veil.db`, `~/.veil/targets.json`, `~/.veil/config.json`
- writes: sync target files

**Behavior**

1. Read active rules from DB canonical
2. Combine vocabulary rules and behavior description
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

First-pass helper for free-form capture text or chat transcript JSON before `/veil-capture` commits to candidate selection.

**Authority**

- reads: optional `~/.veil/veil.db` to downgrade already registered terms
- non-authority: provisional term labels and reasons

**Behavior**

1. Extract likely terms from free-form text
2. Label each as `industry_term / coined_or_shortened / file_config_identifier / other / unknown`
3. Prefer dropping false positives over over-registering

```
Reference rules: rules

Existing matches:
- current state → present state

New candidates:
- implementation plan x3 → i.md
```

**Commands**

```bash
python shared/runtime/veil-normalize.py --stdin
python shared/runtime/veil-normalize.py --text "current state"
python shared/runtime/veil-normalize.py --json
```

### 3-4. shared/runtime/veil-lint.py

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

### 3-5. shared/runtime/veil-status.py

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

### 3-6. Profile support tools

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

**Modifying a registered term via HTML**

`export-html` is the recommended route for reviewing terms and preparing chat-side updates without touching raw files:

1. Run `python shared/tools/veil-db.py export-html` to regenerate `~/.veil/veil.html`
2. Open `~/.veil/veil.html` in a browser
3. The HTML localizes its UI at view time from the viewer's browser language (currently English, Japanese, Korean, Simplified Chinese, Traditional Chinese, and Arabic)
4. Click **Copy** on a candidate cell (label is locale-aware) — this copies a locale-aware AI instruction to the clipboard (e.g. `Change '{term}' to '{candidate}'`)
5. Paste into the AI chat so the updated preferred form is recorded
6. After registration: run `export-html` and `veil-sync.py` to propagate the change

**Registering a new term via HTML**

1. Paste the source sentence into the `Draft Capture` panel
2. Run `Analyze Draft`
3. Click a preview line to load the registration form
4. Use `Copy Registration Request` for the normal chat-side workflow
5. Use `Copy Commands` only when a manual CLI fallback is needed

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

### 3-7. Package import structure

`shared/__init__.py`, `shared/runtime/__init__.py`, and `shared/tools/__init__.py` are empty but intentionally present. They enable the `from shared.tools.veil_rule_store import ...` package import path. With project root added to `sys.path`, the `try: from shared.tools... except ModuleNotFoundError: from veil_rule_store...` fallback pattern depends on them. Do not delete these files.

---

## 4. Data format

Rules are stored in SQLite canonical rows and may be exported as `rules.json` for profile packs.

On new entry: confirm preferred, record to canonical DB, then regenerate HTML.

Candidate semantics:

| Field | Meaning |
|-------|---------|
| p1 | Adopted term. Enters the canonical DB and is synced to sync targets |
| p2 | Candidate 2. Retained but not synced |
| p3 | Candidate 3. Retained but not synced |

Only candidate 1 is synced to AI tool configuration files.

---

## 5. Classification order

After capture, classify each candidate in at least this order:

1. Keep as a proper noun
2. Translate as a common term
3. Fix as a defined term
4. Drop as a prohibited term
5. Skip

This classification order is a guide for what to check first — it is not a final decision gate.

Terms to enforce loosely:

- Low-frequency terms
- Highly context-dependent terms
- Unresolved project-specific terms
- Machine-processed terms: code identifiers, file names, paths, CLI options

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

- Capture at every task close / conversation boundary
- Sync after recording
- Lint before every final response
- Fix and re-check on lint violation
- If a source term must remain intentionally, note the reason explicitly

In capture, present adoption options as `- term (current) → candidate1 (candidate 1) | candidate2 (candidate 2)` and complete `sync` after the user selects.

In normalize output, treat the `Existing matches:` group as already cross-checked — confirm the preferred term. In the `New candidates:` group, review terms with higher `x{N}` counts first.

Use `shared/runtime/veil-status.py` for current state. Run `--check` if setup issues are suspected.

Use `shared/tools/veil-profile-audit.py` for auditing the current default profile. It is read-only and visualizes level distribution and remaining legacy flat rules.

To distribute a domain profile as a separate unit, use `shared/tools/veil-profile-export.py` to pack the current default profile before tuning or branching.

---

## 8. Current migration design lock

**Status:** conditionally design locked. M1 foundation implementation may
proceed only after all of the following are decided and recorded:

- M1/M2 ownership for every mixed hunk;
- the release treatment of the G/C/R categories; and
- the exact exporter-owned HTML freshness manifest inputs and fields.

The dated migration ledger records the current decisions. The contracts in
sections 8-2 through 8-5 remain the decision frame and prevent M2 or deferred
UX work from being folded into M1 foundation implementation.

This section owns the completion boundary for the current SQLite-canonical and
capture-classification migration. It does not change VEIL's normal operational
loop or authorize unrelated UX work.

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

### 8-3. Migration work boundaries

The current worktree must be classified before implementation resumes:

- `M1 - canonical and delivery migration`: SQLite store, DB CLI, sync, lint,
  normalize, status, installer, profile import/export/audit, and their tests.
- `M2 - capture classification and review`: classifier, taxonomy, capture
  preview, generated HTML review behavior, capture skills, fixtures, and their
  tests.
- M2 depends on M1. M1 exposes canonical read, export, and delivery contracts;
  M2 must not define a second canonical, installer, freshness, or sync path.
- `G - active governance and entry surfaces`: project routing, authority, and
  operating configuration are not M1 or M2 release content and require their
  own release decision.
- `C - excluded PJ Framework material`: PJ Framework-derived content requires
  its own owner and release boundary.
- `R - retained residue`: archives and migration residue are neither runtime
  release content nor current governance.

Every tracked changed hunk and every untracked file must be assigned to exactly
one of M1, M2, G, C, R, or a separately recorded proposal before a commit,
installer run, generated-output refresh, or new UX feature. Mixed M1/M2 files
require a hunk ledger and cannot be assigned by filename alone.

### 8-4. Completion conditions

The migration is complete only when all of the following are true:

1. Every worktree change is owned by M1, M2, G, C, R, or a separately recorded
   proposal; no unclassified files remain in the release scope.
2. M1 and M2 have an explicit dependency boundary; a change is not split into
   a separately released unit if it cannot pass its declared verification.
3. The full test suite and compilation checks pass in an isolated temporary
   directory.
4. A clean installation or update verifies the delivery set, and `veil-status`
   reports the appropriate freshness state for every member.
5. The review HTML, both installed skills, source documentation, and the
   current runtime describe the same supported flow.

Mixed-line-ending cleanup in a mixed implementation file is a hunk-review
condition, not a standalone formatting pass. It must be assigned to the M1 or
M2 owner of each affected hunk before normalization; do not apply a broad
mechanical rewrite while ownership remains unresolved.

### 8-5. Deferred work

The following are not part of M1 or M2:

- making Candidate 2 optional;
- adding a semantic-generation or referent-table gate;
- direct browser writes to the canonical DB;
- visual simplification beyond work needed to complete the current migration.

These remain follow-up proposals after the migration delivery set is fixed.

### 8-6. Lock exit

This is a temporary migration section. On completion, retain the permanent
canonical, delivery, and freshness requirements by integrating them into the
ordinary component sections of this document. Move M1/M2/G/C/R classification
and the completion snapshot to a dated audit record, then remove this temporary
section. Do not leave an open-ended "current migration" rule in the design
authority.
