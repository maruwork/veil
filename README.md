# VEIL — Vocabulary Engine for Individual Language

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](shared/runtime/veil-sync.py)

---

## What is VEIL

VEIL is a terminology guardrail for AI-assisted technical writing. It captures vocabulary that drifts in AI output, normalizes it, pushes the rules to AI tool configuration files, and checks that final responses actually follow them.

The problem it solves: AI tools invent English terms, coin abbreviations, or use inconsistent phrasing. You correct it, but the next session starts fresh. Technical documents and explanations keep drifting.

The more AI is in your workflow, the worse this gets. VEIL is not a static style guide — it runs a `capture → normalize → sync → lint` loop to enforce vocabulary consistency. Zero dependencies, fully local.

**The canonical source of truth is `~/.veil/veil.db`. `~/.veil/rules/` is the AI-readable markdown surface and mirror. `CLAUDE.md` / `AGENTS.md` / `.cursorrules` / `.github/copilot-instructions.md` / `GEMINI.md` / `.aider.conf.yml` are sync targets, not storage.**

---

## How it works

```
task close / conversation boundary
        ↓
  /veil-capture (skill)
        ↓
  AI extracts problem terms
        ↓
  prefer state terms, judgment terms, structural terms, operational labels
  over bare verbs
        ↓
  shared/runtime/veil-normalize.py — collapse variants, cross-check existing rules
        ↓
  adopt only high-demand, high-impact terms
        ↓
  record to ~/.veil/veil.db  ← canonical source of truth
        ↓
  generate ~/.veil/rules/{letter}.md  ← mirror / AI-readable surface
        ↓
  shared/runtime/veil-sync.py pushes rules to AI tool config files
        ↓
  CLAUDE.md / AGENTS.md / .cursorrules etc. receive the rules
        ↓
  shared/runtime/veil-lint.py checks the final response before sending
        ↓
next session: AI outputs with consistent vocabulary
```

---

## Term adoption strategy

VEIL is not designed to register everything at once. Add high-demand terms first, a few at a time.

Basic rules:

- **Classify first.** Do not mix identifiers, proper nouns, descriptive terms, and project-specific terms and rush to a translation decision.
- **Adopt high-demand terms first.** Lock in frequently troublesome terms and terms that are core to VEIL operation itself.
- **Skip uncertain terms.** If a term is unclear whether it is a proper noun or common term, if translations conflict, or if the pain level is still low — do not rush to canonicalize.
- **Do not add too many at once.** Run a small set of adopted terms through `sync` and `lint`, confirm they are working, then add the next batch.

Enforce tightly only at the key points, not everywhere:

- **Enforce the flow tightly.** Run `capture` at every task close / conversation boundary, and `lint` before every final response.
- **Enforce high-impact terms tightly.** Prioritize prohibited terms, VEIL core terms, and high-demand terms where drift causes real problems.
- **Do not rush low-frequency or ambiguous terms.** Skip them.
- **Do not enforce the full natural text.** Do not put natural paraphrases, machine-processed terms, and context-dependent terms behind hard gates.

---

## Components

| Component | Role |
|-----------|------|
| `/veil-capture` skill | At task close / conversation boundary: extract problem terms, record to SQLite canonical, generate mirror, run sync |
| `~/.veil/veil.db` | SQLite canonical source of truth |
| `~/.veil/rules/{letter}.md` | AI-readable markdown surface / mirror |
| `shared/runtime/veil-normalize.py` | Normalize candidate terms after capture; return existing matches and new candidates |
| `shared/runtime/veil-sync.py` | Push vocabulary rules to AI tool configuration files |
| `shared/runtime/veil-lint.py` | Check final text for registered source terms before sending |
| `shared/runtime/veil-status.py` | Show canonical / mirror / sync target / skill status and setup diagnostics |
| `shared/tools/veil-profile-audit.py` | Audit rule count and legacy flat rule presence in current profile |
| `shared/tools/veil-profile-export.py` | Export current profile as a domain profile pack |
| `shared/tools/veil-db.py` | SQLite canonical CLI: `init-db / import-rules / readback / upsert-rule / export-mirror / export-html` |

`shared/tools/veil-db.py` initializes, imports, and reads back the SQLite canonical, handles single-rule upsert, generates the markdown mirror, and generates `~/.veil/veil.html` — a browser-based vocabulary list for reviewing and modifying registered terms.

### Core and profile

- **VEIL core**
  - `capture`
  - `normalize`
  - `sync`
  - `lint`
  - `status`
  - classification order skeleton

- **Domain profile**
  - `~/.veil/rules/`
  - prohibited term set
  - high-demand term set
  - how to handle defined terms
  - criteria for keeping proper nouns
  - `lint` enforcement level

The current default profile is for technical writing.

---

## Setup

Requires Python 3.8 or later.

Clone to a fixed location on your machine. VEIL is a global tool, not a per-project dependency.

```bash
# macOS / Linux
git clone https://github.com/fumimaruwork/veil.git ~/tools/veil
cd ~/tools/veil
```

```powershell
# Windows (PowerShell)
git clone https://github.com/fumimaruwork/veil.git $env:USERPROFILE\tools\veil
cd $env:USERPROFILE\tools\veil
```

### 1. Install the skill

Copies skill files to the tool directories and writes `sync_script` and `veil_root` to `~/.veil/config.json`.

```bash
bash install.sh
```

To install manually:

**Claude Code**

```bash
# macOS / Linux
cp skills/claude-code/veil-capture.md ~/.claude/commands/veil-capture.md
```

```powershell
# Windows (PowerShell)
Copy-Item skills\claude-code\veil-capture.md $env:USERPROFILE\.claude\commands\veil-capture.md
```

**Codex**

```bash
# macOS / Linux
cp -r skills/codex/veil-capture ~/.agents/skills/veil-capture
```

```powershell
# Windows (PowerShell)
Copy-Item -Recurse skills\codex\veil-capture $env:USERPROFILE\.agents\skills\veil-capture
```

### 2. Register sync target files

Register the AI tool config files that VEIL should push vocabulary rules into.

```bash
python shared/runtime/veil-sync.py --add /path/to/CLAUDE.md
python shared/runtime/veil-sync.py --add /path/to/AGENTS.md
```

The rules are applied immediately on registration. Supported tools:

| Tool | Config file | Marker format |
|------|-------------|---------------|
| Claude Code | `CLAUDE.md` | `<!-- VEIL_START -->` |
| Codex | `AGENTS.md` | `<!-- VEIL_START -->` |
| Cursor | `.cursorrules` | `<!-- VEIL_START -->` |
| GitHub Copilot | `.github/copilot-instructions.md` | `<!-- VEIL_START -->` |
| Gemini CLI | `GEMINI.md` | `<!-- VEIL_START -->` |
| Aider | `.aider.conf.yml` | `# VEIL_START` |

Files with `.yml` / `.yaml` / `.toml` / `.ini` / `.cfg` extensions use `# VEIL_START` / `# VEIL_END` markers.
---

## Usage

### Capture AI vocabulary (main workflow)

Run at every task close or conversation boundary in Claude Code:

```
/veil-capture
```

Example output:

```
- common asset → shared asset | common resource
- current state → present state | current state (keep)
- validator → validator (keep) | checker

Select current or a candidate.
```

The selected candidate is recorded as `preferred` in the canonical route. `~/.veil/rules/` is regenerated and rules are synced to AI tool config files. Candidates 2 and 3 are stored as alternatives in the DB.

- **Candidate 1**: recommended adopted term
- **Candidate 2**: required alternative displayed alongside
- **Candidate 3**: optional additional candidate

Adoption priority order:

1. High-frequency terms causing active problems
2. Terms core to VEIL operation itself
3. Project-specific terms
4. Low-frequency and boundary-ambiguous terms

Category 4 does not need to be registered urgently — skip and revisit later.

Classification goes in at least these 5 directions:

1. Keep as a proper noun
2. Translate as a common term
3. Fix as a defined term
4. Drop as a prohibited term
5. Skip if classification is not yet clear

When candidate terms have variants, use the normalization helper before writing:

```bash
python shared/runtime/veil-normalize.py --stdin
python shared/runtime/veil-normalize.py --text "current states\ncurrent_state\nCurrent-State"
```

This helper:

- Collapses case, hyphen, underscore, and light singular/plural variants
- Groups each normalized cluster with its variants and occurrence count
- Cross-checks against existing SQLite canonical / mirror (`Existing matches:` group)
- Suggests mirror target file for terms with no existing match (`New candidates:` group)

Example output:

```
Reference rules: rules

Existing matches:
- current state → present state

New candidates:
- implementation plan x3 → i.md
```

The `Existing matches:` group is treated as already cross-checked — confirm the preferred term. In the `New candidates:` group, review terms with higher `x{N}` counts first. Final adoption decisions rest with the owner.

To analyze external text (e.g. Codex output):

```
/veil-capture <paste target text here>
```

### Review registered terms

Generate a browser-based vocabulary list to see all registered terms and their candidates:

```bash
python shared/tools/veil-db.py export-html   # write ~/.veil/veil.html
```

Open `~/.veil/veil.html` in a browser. Each row shows a registered term alongside its candidates (preferred form, candidate 2, candidate 3). Use the search box to filter. Re-run `export-html` any time the DB changes to keep the list current.

### Modify a registered term

To change the preferred form, use the HTML list:

1. Open `~/.veil/veil.html` (run `export-html` first if needed)
2. Find the term — hover over the target candidate and click **Copy**
3. This copies a ready-to-paste instruction (`Change '{term}' to '{candidate}'`) to the clipboard
4. Paste into the AI chat — this triggers a new capture cycle that records the updated preferred form
5. After capture: run `export-mirror`, `export-html`, and `veil-sync.py` to propagate the change

To update directly without AI:

```bash
python shared/tools/veil-db.py upsert-rule --term "current state" --preferred "present state"
python shared/tools/veil-db.py export-mirror   # regenerate markdown mirror
python shared/tools/veil-db.py export-html     # regenerate HTML list
python shared/runtime/veil-sync.py             # push to sync targets
```

### Inspect raw rule files

The markdown mirror under `~/.veil/rules/` can also be read or edited directly:

```
~/.veil/rules/
├── m.md    # rules for terms starting with m
├── u.md    # rules for terms starting with u
└── ...
```

```markdown
# u

- uncommitted → uncommitted (keep)
- untracked → untracked (keep)
- unstable wording → inconsistent phrasing
- update path → update path (keep)
```

After editing a mirror file directly, run `import-rules` to reload it into the canonical DB, then `export-html` and `veil-sync.py` to propagate.

### Update sync targets manually

```bash
python shared/runtime/veil-sync.py              # update all sync targets
python shared/runtime/veil-sync.py --list       # list registered targets
python shared/runtime/veil-sync.py --add <path> # register a sync target
python shared/runtime/veil-sync.py --remove <path> # unregister a sync target
```

### Check vocabulary before sending

Check that recorded vocabulary is actually present in the text using `shared/runtime/veil-lint.py` before every final response.

```bash
python shared/runtime/veil-lint.py <file>   # check a response file
python shared/runtime/veil-lint.py --stdin  # check from stdin
python shared/runtime/veil-lint.py --text "I organized the current state"  # check a string directly
```

- `CLEAN`: no registered source terms found in the text
- violation: registered source terms remain in the text — check the preferred term and fix
- `SKIP`: no rules in `~/.veil/rules/` — does not exit with error

On a violation, `shared/runtime/veil-lint.py` returns the suggested fix and a line preview. Follow that guidance first; then revise the full sentence if needed.

`veil-capture` handles extraction, recording, and sync. `shared/runtime/veil-lint.py` handles pre-response checking. Keep these roles separate.

`lint` is not for enforcing the entire prose — it is a gate for registered high-impact terms and prohibited terms.

### Check VEIL status

Check canonical DB rule count, mirror last-updated timestamp, and sync target state:

```bash
python shared/runtime/veil-status.py
```

Run setup diagnostics when something seems wrong:

```bash
python shared/runtime/veil-status.py --check
```

`[ERROR]` exits with code 1. `[WARN]` only exits with code 0 and is safe to continue.

### Audit the current profile

Check rule count and any remaining legacy flat rules in `~/.veil/rules/` using `shared/tools/veil-profile-audit.py`:

```bash
python shared/tools/veil-profile-audit.py
python shared/tools/veil-profile-audit.py --json
python shared/tools/veil-profile-audit.py --db workspace/veil_stage1_smoke.db
```

`audit`, `normalize`, and `lint` all accept `--db` to read from a SQLite source. `veil-normalize.py` maintains the existing-match return format and allows distinguishing the source via `source_type` and `source` in JSON output. `veil-lint.py` keeps `rules-dir` compatibility and maintains the `violation / clean / skip` return contract and exit codes.

### SQLite support route

The SQLite canonical support CLI is `shared/tools/veil-db.py`. To verify with a workspace fixture:

```bash
python shared/tools/veil-db.py init-db --db workspace/veil_stage1_smoke.db
python shared/tools/veil-db.py import-rules --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_rules_fixture
python shared/tools/veil-db.py readback --db workspace/veil_stage1_smoke.db --json
python shared/tools/veil-db.py upsert-rule --db workspace/veil_stage1_smoke.db --term "current state" --preferred "present state"
python shared/tools/veil-db.py export-mirror --db workspace/veil_stage1_smoke.db --rules-dir workspace/veil_stage1_mirror
```

### Export the current profile

To cut the current default profile as a domain profile pack:

```bash
python shared/tools/veil-profile-export.py --profile-name technical-writing-default
python shared/tools/veil-profile-export.py --profile-name finance-guardrail --domain finance --base-profile technical-writing-default
python shared/tools/veil-profile-export.py --profile-name technical-writing-default --output-dir workspace/profile-exports/custom-pack
```

By default, output goes to `workspace/profile-exports/<profile-name>/`:

- `*.md` rule files
- `manifest.json`

This is a read-only export — it does not modify the canonical route or `~/.veil/rules/` mirror. `manifest.json` includes `domain`, `intended_use`, and `base_profile` to preserve the branching contract.

To branch from an existing pack:

```bash
python shared/tools/veil-profile-export.py --base-manifest workspace/profile-exports/technical-writing-default/manifest.json --profile-name medical-guardrail --domain medical
```

---

## File structure

```
veil/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── install.sh                            # skill file deploy script
├── locale/                              # locale strings
│   ├── en.json
│   └── ja.json
├── shared/runtime/veil-normalize.py     # candidate term normalization and cross-check
├── shared/runtime/veil-sync.py          # rule sync script (core tool)
├── shared/runtime/veil-lint.py          # pre-response vocabulary check (core tool)
├── shared/runtime/veil-status.py        # canonical / mirror / sync target status
├── shared/tools/veil-profile-audit.py   # profile audit helper
├── shared/tools/veil-profile-export.py  # profile export helper
├── shared/tools/veil-db.py              # SQLite canonical support CLI
├── shared/tools/veil_locale.py          # locale detection and t() lookup
├── shared/tools/veil_rule_store.py      # SQLite schema / upsert / mirror export shared helper
├── skills/                 # skill templates
│   ├── claude-code/
│   │   └── veil-capture.md
│   └── codex/
│       └── veil-capture/
│           └── SKILL.md
└── docs/
    └── veil-design.md      # design reference
```

---

## License

[MIT License](LICENSE)
