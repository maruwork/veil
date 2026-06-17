# VEIL — Vocabulary Engine for Individual Language

[![CI](https://github.com/maruwork/veil/actions/workflows/ci.yml/badge.svg)](https://github.com/maruwork/veil/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](shared/runtime/veil-sync.py)

---

**For developers and technical writers** who use AI tools (Claude Code, Codex, Cursor, Copilot, Gemini CLI, Aider) and need vocabulary to stay consistent across sessions.

## What is VEIL

AI tools invent English terms, coin abbreviations, and use inconsistent phrasing. You correct it once, but the next session starts fresh and the same terms drift again.

**Before VEIL:** AI uses "current state" in a response. You correct it to "present state". Next session, the AI uses "current state" again. Every session requires the same correction.

**After VEIL:** "present state" is registered as the preferred form. VEIL syncs the rule to `CLAUDE.md` / `AGENTS.md`. The next session, the AI reads the rule and outputs "present state" from the start.

**Success condition:** once a term is registered, it does not require re-explanation or correction across sessions or AI tools.

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

The Python scripts (veil-sync, veil-lint, veil-normalize, etc.) are CLI tools invoked from the terminal or by the skill. The `/veil-capture` skill installs as 2 files — one for Claude Code (`~/.claude/commands/veil-capture.md`) and one for Codex (`~/.agents/skills/veil-capture/SKILL.md`).

`shared/tools/veil-db.py` initializes, imports, and reads back the SQLite canonical, handles single-rule upsert, generates the markdown mirror, and generates `~/.veil/veil.html` — a browser-based vocabulary list for reviewing and modifying registered terms.

### AI behavior rules

`~/.veil/behavior.md` is an optional plain-text file. When present, its content is appended to every sync target alongside vocabulary rules. Use it to enforce output behavior that is not term-specific: tone, code style, response format, language constraints.

Example:

```
Do not use compound English words mixed into Japanese sentences.
Respond to Japanese prompts in Japanese.
```

Create the file manually — VEIL reads it automatically during sync. Vocabulary rules in `~/.veil/rules/` and behavior rules in `~/.veil/behavior.md` are kept separate so each can evolve independently.

---

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

Requires Python 3.8 or later and Git.

### One-liner install

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/maruwork/veil/main/get-veil.sh | bash
```

```powershell
# Windows (PowerShell)
irm https://raw.githubusercontent.com/maruwork/veil/main/get-veil.ps1 | iex
```

Clones the repo to `~/tools/veil` (macOS/Linux) or `%USERPROFILE%\tools\veil` (Windows), then runs the installer. Re-running updates the existing install via `git pull`.

To use a different location:

```bash
VEIL_REPO=~/dev/veil bash <(curl -fsSL https://raw.githubusercontent.com/maruwork/veil/main/get-veil.sh)
```

```powershell
$env:VEIL_REPO = "$env:USERPROFILE\dev\veil"
irm https://raw.githubusercontent.com/maruwork/veil/main/get-veil.ps1 | iex
```

### Manual install

Clone to a fixed location, then run the installer:

```bash
# macOS / Linux
git clone https://github.com/maruwork/veil.git ~/tools/veil
bash ~/tools/veil/install.sh
```

```powershell
# Windows (PowerShell)
git clone https://github.com/maruwork/veil.git $env:USERPROFILE\tools\veil
& "$env:USERPROFILE\tools\veil\install.ps1"
```

The installer copies skill files to the tool directories, writes `sync_script`, `veil_root`, and `lang` to `~/.veil/config.json`, initializes `~/.veil/veil.db`, and auto-registers AI config files found in `~/.claude/` and the current directory as sync targets.

To install skill files only without the installer:

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

`install.sh` automatically registers AI config files found in `~/.claude/` and the directory it is run from. To register additional files:

```bash
python shared/runtime/veil-sync.py --add /path/to/CLAUDE.md
```

Siblings in the same directory (AGENTS.md, GEMINI.md, .cursorrules, etc.) are auto-registered alongside the given file. The rules are applied immediately on registration. Supported tools:

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
- common asset (current) → shared asset (candidate 1) | common resource (candidate 2)
- current state (current) → present state (candidate 1) | current state (keep)
- validator (current) → validator (keep) | checker (candidate 2)

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
python shared/tools/veil-db.py upsert-rule --term "current state" --preferred "present state" --level required
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

## 必須

- uncommitted → uncommitted (keep)
- untracked → untracked (keep)

## 推奨

- unstable wording → inconsistent phrasing

## 観察

- update path → update path (keep)
```

After editing a mirror file directly, run `import-rules` to reload it into the canonical DB, then `export-html` and `veil-sync.py` to propagate. **`import-rules` replaces all existing rules in the DB** — a warning is printed before execution.

### Update sync targets manually

```bash
python shared/runtime/veil-sync.py              # update all sync targets
python shared/runtime/veil-sync.py --list       # list registered targets
python shared/runtime/veil-sync.py --add <path> # register a sync target
python shared/runtime/veil-sync.py --remove <path>          # unregister a sync target
python shared/runtime/veil-sync.py --remove <path> --purge  # unregister and remove VEIL block from file
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
python shared/tools/veil-profile-audit.py --db ~/.veil/veil.db
```

`audit`, `normalize`, and `lint` all accept `--db` to read from a SQLite source. `veil-normalize.py` maintains the existing-match return format and allows distinguishing the source via `source_type` and `source` in JSON output. `veil-lint.py` keeps `rules-dir` compatibility and maintains the `violation / clean / skip / error` return contract and exit codes. If the DB file exists but is unreadable, the CLI returns a structured error instead of a traceback.

### SQLite support route

The SQLite canonical support CLI is `shared/tools/veil-db.py`. Common operations:

```bash
python shared/tools/veil-db.py init-db                        # initialize ~/.veil/veil.db
python shared/tools/veil-db.py upsert-rule --term "foo" --preferred "bar" --level required
python shared/tools/veil-db.py readback --json
python shared/tools/veil-db.py export-mirror                  # regenerate ~/.veil/rules/
python shared/tools/veil-db.py export-html                    # regenerate ~/.veil/veil.html
```

### Export the current profile

To cut the current default profile as a domain profile pack:

```bash
python shared/tools/veil-profile-export.py --profile-name technical-writing-default
python shared/tools/veil-profile-export.py --profile-name finance-guardrail --domain finance --base-profile technical-writing-default
python shared/tools/veil-profile-export.py --profile-name technical-writing-default --output-dir ~/my-exports/custom-pack
```

By default, output goes to `~/.veil/profile-exports/<profile-name>/`:

- `*.md` rule files
- `manifest.json`

This is a read-only export — it does not modify the canonical route or `~/.veil/rules/` mirror. `manifest.json` includes `domain`, `intended_use`, and `base_profile` to preserve the branching contract.

To branch from an existing pack:

```bash
python shared/tools/veil-profile-export.py --base-manifest ~/.veil/profile-exports/technical-writing-default/manifest.json --profile-name medical-guardrail --domain medical
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

## File structure

```
veil/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── get-veil.sh                           # one-liner installer (macOS / Linux)
├── get-veil.ps1                          # one-liner installer (Windows)
├── install.sh                            # installer: skills + config + init-db (macOS / Linux)
├── install.ps1                           # installer: skills + config + init-db (Windows)
├── pytest.ini                            # pytest configuration
├── pyrightconfig.json                    # Pyright type-check configuration
├── locale/                              # locale strings
│   ├── en.json
│   └── ja.json
├── shared/
│   ├── runtime/
│   │   ├── veil-normalize.py             # candidate term normalization and cross-check
│   │   ├── veil-sync.py                  # rule sync script (core tool)
│   │   ├── veil-lint.py                  # pre-response vocabulary check (core tool)
│   │   └── veil-status.py               # canonical / mirror / sync target status
│   └── tools/
│       ├── veil-profile-audit.py         # profile audit helper
│       ├── veil-profile-export.py        # profile export helper
│       ├── veil-db.py                    # SQLite canonical support CLI
│       ├── veil_locale.py                # locale detection and t() lookup
│       └── veil_rule_store.py            # SQLite schema / upsert / mirror export shared helper
├── skills/                              # skill templates
│   ├── claude-code/
│   │   └── veil-capture.md              # Claude Code slash command
│   └── codex/
│       └── veil-capture/
│           └── SKILL.md                 # Codex skill
├── tests/                               # pytest suite
│   ├── conftest.py
│   ├── helpers.py
│   ├── test_db.py
│   ├── test_lint.py
│   ├── test_locale.py
│   ├── test_normalize.py
│   ├── test_profile.py
│   ├── test_status.py
│   └── test_sync.py
└── docs/
    └── veil-design.md                   # design reference
```

---

## Community

| File | Purpose |
| --- | --- |
| [SUPPORT.md](SUPPORT.md) | Documentation pointers, issue routing, scope |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution flow and PR expectations |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

---

## License

[MIT License](LICENSE)
