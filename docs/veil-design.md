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

---

## 2. Data locations

| Data | Location | Role |
|------|----------|------|
| Vocabulary rule canonical | `~/.veil/veil.db` | canonical source of truth |
| Vocabulary rule markdown mirror | `~/.veil/rules/` | AI-readable markdown surface / mirror |
| Sync target list | `~/.veil/targets.json` | list of sync target file paths |
| Sync script path | `~/.veil/config.json` | written automatically on `--add` |

`~/.veil/` is fixed to the user home directory. In the current phase, canonical is SQLite and markdown rules are carried as the mirror.

---

## 3. Component details

### 3-1. veil-capture skill

Detects English terms, coined terms, and abbreviations from AI conversation. At task close / conversation boundary, records to the SQLite canonical as the close operation for the current phase, then updates the markdown mirror.

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
8. Regenerate `~/.veil/rules/` mirror via `shared/tools/veil-db.py export-mirror`
9. Run `shared/runtime/veil-sync.py` for immediate sync

### 3-2. shared/runtime/veil-sync.py

Prioritizes the SQLite canonical; regenerates the `~/.veil/rules/` markdown mirror when needed; then applies rules to AI tool configuration files.

**Authority**

- reads: `~/.veil/veil.db`, `~/.veil/rules/*.md`, `~/.veil/targets.json`, `~/.veil/config.json`
- writes: sync target files

**Behavior**

1. If DB canonical exists in the current phase, regenerate `~/.veil/rules/` mirror
2. Read all `.md` files under `~/.veil/rules/`
3. Combine vocabulary rules and behavior description
4. Write the `VEIL_START` / `VEIL_END` block to each registered sync target

**Commands**

```bash
python shared/runtime/veil-sync.py
python shared/runtime/veil-sync.py --add <path>
python shared/runtime/veil-sync.py --list
python shared/runtime/veil-sync.py --remove <path>
```

### 3-3. shared/runtime/veil-normalize.py

Read-only helper that normalizes a candidate term list after capture and returns cross-check results in two groups.

**Authority**

- reads: `~/.veil/veil.db` or `~/.veil/rules/*.md`
- non-authority: helper output, draft candidate list

**Behavior**

1. Lowercase, absorb space/hyphen/underscore variants, absorb light singular/plural variants
2. Group each normalized cluster with its variants and occurrence count
3. If an existing rule matches, return as `Existing matches:` group with preferred and source_file
4. If no existing rule, return as `New candidates:` group with suggested target_file

**Text output format**

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

- reads: `~/.veil/veil.db` or `~/.veil/rules/*.md`
- non-authority: capture report, temporary drafts

**Behavior**

1. Load rules in `- original → preferred` format from SQLite canonical or `~/.veil/rules/*.md` mirror
2. Scan the input text
3. Return any registered source terms found as violation candidates
4. Exclude inline code and code blocks from scanning
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

- reads: `~/.veil/veil.db`, `~/.veil/rules/`, `~/.veil/targets.json`, skill files
- writes: nothing

**Behavior (no arguments)**

1. Show canonical DB existence and rule count
2. Show mirror last-updated timestamp
3. Show sync target count and existence check
4. Always exit 0

**Behavior (--check)**

1. Check existence of DB, rules/, targets.json, each sync target, and skill files
2. Return each item as `[OK]` / `[WARN]` / `[ERROR]`
3. Exit 1 if any ERROR; otherwise exit 0

**Commands**

```bash
python shared/runtime/veil-status.py
python shared/runtime/veil-status.py --check
python shared/runtime/veil-status.py --json
```

### 3-6. Profile support tools

`shared/tools/veil-profile-audit.py`, `shared/tools/veil-profile-export.py`, `shared/tools/veil-db.py`, and `shared/tools/veil_rule_store.py` are support runtime, not mainline runtime. `veil-db.py` and `veil_rule_store.py` assist with SQLite canonical schema / import / readback / upsert / mirror export. `veil-profile-audit.py`, `veil-normalize.py`, and `veil-lint.py` all accept `--db` to read from a SQLite source.

**Authority**

- reads: `~/.veil/veil.db`, `~/.veil/rules/*.md`
- writes:
  - `veil-profile-audit.py`: nothing
  - `veil-profile-export.py`: export output directory only
  - `veil-db.py`: specified SQLite DB path, specified mirror directory
  - `veil_rule_store.py`: SQLite DB / mirror directory as a helper

**Usage**

1. `shared/tools/veil-profile-audit.py`
   - Visualize level distribution and legacy flat rule presence
   - Supports `--db` for SQLite source reading
2. `shared/runtime/veil-normalize.py`
   - Supports `--db` for SQLite source reading
3. `shared/runtime/veil-lint.py`
   - Supports `--db` for SQLite source reading
4. `shared/tools/veil-profile-export.py`
   - Export current default profile as a section-aware domain profile pack
5. `shared/tools/veil-db.py`
   - Handle SQLite canonical `init-db / import-rules / readback / upsert-rule / export-mirror / export-html`
   - `export-html` writes `~/.veil/veil.html`: a searchable browser list of all registered terms with copy buttons

**Modifying a registered term via HTML**

`export-html` is the recommended route for reviewing and changing preferred forms without touching raw files:

1. Run `python shared/tools/veil-db.py export-html` to regenerate `~/.veil/veil.html`
2. Open `~/.veil/veil.html` in a browser
3. Hover over a candidate cell and click **Copy** (label is locale-aware) — copies a locale-aware AI instruction to the clipboard (e.g. `Change '{term}' to '{candidate}'`)
4. Paste into the AI chat; this triggers a new capture cycle that records the updated preferred form
5. After capture: run `export-mirror`, `export-html`, and `veil-sync.py` to propagate the change

**Commands**

```bash
python shared/tools/veil-profile-audit.py
python shared/tools/veil-profile-audit.py --db workspace/veil_stage1_smoke.db
python shared/runtime/veil-normalize.py --text "current state" --db workspace/veil_stage1_smoke.db --json
python shared/runtime/veil-lint.py --text "current state" --db workspace/veil_stage1_smoke.db
python shared/tools/veil-db.py init-db --db workspace/veil_stage1_smoke.db
python shared/tools/veil-db.py import-rules --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_rules_fixture
python shared/tools/veil-db.py readback --db workspace/veil_stage1_smoke.db --json
python shared/tools/veil-db.py upsert-rule --db workspace/veil_stage1_smoke.db --term "current state" --preferred "present state"
python shared/tools/veil-db.py export-mirror --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_mirror
python shared/tools/veil-db.py export-html
```

### 3-7. Package import structure

`shared/__init__.py`, `shared/runtime/__init__.py`, and `shared/tools/__init__.py` are empty but intentionally present. They enable the `from shared.tools.veil_rule_store import ...` package import path. With project root added to `sys.path`, the `try: from shared.tools... except ModuleNotFoundError: from veil_rule_store...` fallback pattern depends on them. Do not delete these files.

---

## 4. Data format

Rules are stored as:

```md
# c

- current state → present state
- current issue → current problem
```

On new entry: confirm preferred, record to canonical DB, then regenerate mirror.

Candidate semantics:

| Field | Meaning |
|-------|---------|
| p1 | Adopted term. Enters canonical route; in current phase also synced to mirror and sync targets |
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
- `capture → normalize → sync → lint` operational skeleton
- classification order skeleton

### Domain profile

- `~/.veil/veil.db`
- `~/.veil/rules/` mirror
- prohibited term set
- high-demand term set
- how to handle defined terms
- criteria for keeping proper nouns
- `lint` enforcement level

The current default profile is for technical writing.

To distribute the current default profile outside the repo or as a separate bundle, use `shared/tools/veil-profile-export.py` to create a profile pack. This is a support route for domain profile separation — it does not change the mainline `capture → normalize → sync → lint` flow.

The export manifest carries `domain`, `intended_use`, and `base_profile` as the minimal contract for branching from the technical writing default to an industry-specific profile.

---

## 7. Operational loop

- Capture at every task close / conversation boundary
- Sync after recording
- Lint before every final response
- Fix and re-check on lint violation
- If a source term must remain intentionally, note the reason explicitly

In capture, present adoption options as `- term (current) → candidate1 (candidate1) | candidate2 (candidate2)` and complete `sync` after the user selects.

In normalize output, treat the `Existing matches:` group as already cross-checked — confirm the preferred term. In the `New candidates:` group, review terms with higher `x{N}` counts first.

Use `shared/runtime/veil-status.py` for current state. Run `--check` if setup issues are suspected.

Use `shared/tools/veil-profile-audit.py` for auditing the current default profile. It is read-only and visualizes level distribution and remaining legacy flat rules.

To distribute a domain profile as a separate unit, use `shared/tools/veil-profile-export.py` to pack the current default profile before tuning or branching.
