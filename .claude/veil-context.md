# VEIL — Session Context

**Repo:** https://github.com/fumimaruwork/veil  
**Primary branch:** main  
**Local path:** C:\Users\f_tan\project\veil (runtime files only on GitHub; local has `.claude/` only)  
**git status:** Not a git repo (no `git init`). All repo ops use `gh api`. Do NOT use agent worktree isolation — it creates empty dirs and fails.  
**gh CLI:** authenticated as fumimaruwork

---

## What VEIL Is

VEIL (Vocabulary Enforcement and Injection Layer) is a personal vocabulary-rule engine for AI-assisted writing. It captures terminology decisions made during AI conversations, stores them in a SQLite database, and syncs the rules back into AI tool configuration files (CLAUDE.md, AGENTS.md, .cursorrules, etc.) so that the AI consistently applies the user's preferred terms.

---

## Full Workflow

```
/veil-capture (Claude Code skill)
    │
    ├─ extract candidate terms from conversation
    ├─ present choices: {term}（現状）→ {cand1}（候補1）| {cand2}（候補2）
    └─ user selects preferred form
         │
         ▼
python shared/tools/veil-db.py upsert-rule
    → write term + candidates to ~/.veil/veil.db (SQLite)
         │
         ▼
python shared/tools/veil-db.py export-mirror
    → regenerate ~/.veil/rules/*.md (markdown mirror by first letter)
         │
         ▼
python shared/tools/veil-db.py export-html
    → regenerate ~/.veil/veil.html (searchable HTML viewer)
         │
         ▼
python shared/runtime/veil-sync.py  (only if config.json has sync_script)
    → inject rules section into registered target files
         │
         ▼
confirmation message output
```

---

## Architecture: Option B Pattern

The data layer returns locale keys (not human-readable strings). The CLI layer translates them with `t()`.

**Data layer** (`veil_rule_store.py`, `veil-db.py` internals):
```python
# Returns a locale key, not a translated string
return {
    "status": "skip",
    "reason": "store.no_rules_dir",   # ← locale key
}
```

**CLI layer** (`veil-db.py` output functions, `veil-sync.py`):
```python
from shared.tools.veil_locale import t

# Translates at the boundary, just before user-facing output
print(t("store.no_rules_dir"))
```

**Why Option B?** The library functions (`upsert_rule`, `export_html_from_db`, etc.) are imported by other tools. If they printed translated text, callers couldn't intercept messages or reformat output. Returning locale keys keeps the library clean and testable; only CLIs call `t()`.

---

## warning_key / warning_args Pattern

Warnings collected inside data-layer functions use a structured dict instead of formatted strings:

```python
warnings.append({
    "file": fname,
    "line": line_no,
    "warning_key": "store.load_failed",    # ← locale key
    "warning_args": {"exc": str(exc)},     # ← format kwargs
})
```

The CLI layer renders these at print time:
```python
for warning in payload["warnings"]:
    msg = t(warning["warning_key"], **warning.get("warning_args", {}))
    print(f"- warning {location}: {msg}")
```

This pattern lets the data layer accumulate warnings across many files without deciding the locale at collection time.

---

## detect_lang() Mechanism

`shared/tools/veil_locale.py` → `detect_lang()` resolves the display language in priority order:

```
1. VEIL_LANG env var          (e.g. VEIL_LANG=ja)
2. ~/.veil/config.json        {"lang": "ja"}
3. OS locale                  locale.getdefaultlocale()[0] → "ja_JP" → "ja"
4. fallback                   "en"
```

`t(key, **kwargs)` is the single public function. It lazy-loads the locale file on first call and falls back to `en.json` if the key is missing in the active language.

Locale files live at `locale/{lang}.json` in the repo root. Current languages: `en`, `ja`.

---

## Locale File Structure

`locale/en.json` and `locale/ja.json` share the same key hierarchy:

```
store.*     ← veil_rule_store.py messages
db.*        ← veil-db.py CLI help/output
sync.*      ← veil-sync.py messages
lint.*      ← veil-lint.py messages
normalize.* ← veil-normalize.py messages
status.*    ← veil-status.py messages
html.*      ← HTML viewer UI strings (passed to export_html_from_db as ui dict)
audit.*     ← veil-profile-audit.py messages
export.*    ← veil-profile-export.py messages
```

The `html.*` section is special: `veil-db.py export-html` reads `t("html.*")` for each key and builds a `ui` dict that is passed directly to `export_html_from_db(ui=ui)`.

---

## Main Files

| File | Role |
|------|------|
| `shared/tools/veil_rule_store.py` | Core library: SQLite schema, `upsert_rule`, `export_html_from_db`, `export_markdown_mirror_from_db`, `load_rules_from_markdown_dir`. Imported by all tools. No `t()` calls — returns locale keys. |
| `shared/tools/veil_locale.py` | `detect_lang()` + `t()`. Loaded once per process; thread-safe via global state. |
| `shared/tools/veil-db.py` | CLI for database operations. Subcommands: `init-db`, `import-rules`, `readback`, `upsert-rule`, `export-mirror`, `export-html`. |
| `shared/runtime/veil-sync.py` | Syncs rules into AI tool config files. Reads `~/.veil/targets.json` for registered target paths. Supports: CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, .github/copilot-instructions.md, .aider.conf.yml |
| `shared/runtime/veil-lint.py` | Checks text/files against registered rules and reports violations. |
| `shared/runtime/veil-normalize.py` | Normalizes candidate terms and shows overlap with existing rules. |
| `shared/runtime/veil-status.py` | Diagnostic: shows DB path, rule count, mirror status, sync targets. |
| `locale/en.json` | English strings for all CLI output and HTML UI. |
| `locale/ja.json` | Japanese strings for all CLI output and HTML UI. |
| `skills/claude-code/veil-capture.md` | Claude Code slash command (`/veil-capture`). Installed to `~/.claude/commands/veil-capture.md` by `install.sh`. |
| `skills/codex/veil-capture/SKILL.md` | Same skill for Codex. Installed to `~/.agents/skills/veil-capture/SKILL.md`. |
| `install.sh` | Copies skill files to appropriate tool directories. |

---

## Runtime Data (not in repo)

| Path | Contents |
|------|----------|
| `~/.veil/veil.db` | SQLite canonical store. Table: `rules` (id, term_original, term_normalized, preferred, preferred_alt_2, preferred_alt_3, status, …) |
| `~/.veil/rules/*.md` | Markdown mirror. One file per first letter (a.md, b.md, …). Format: `- {term} → {preferred}、{alt2}` |
| `~/.veil/veil.html` | Searchable HTML viewer. Open with `file://~/.veil/veil.html`. |
| `~/.veil/config.json` | Optional. Keys: `lang` (override locale), `sync_script` (path to run after upsert). |
| `~/.veil/targets.json` | List of file paths registered as veil-sync targets. |
| `~/.veil/behavior.md` | Free-form behavioral notes injected into sync targets (optional). |

---

## normalize_term() Key Logic

Used to deduplicate rules. Strips leading bullets, lowercases, collapses hyphens/underscores to spaces, and singularizes tokens:

```
"API Endpoints" → "api endpoint"
"error-handling" → "error handling"
"analyses"      → "analysis"
```

Two rules with the same normalized form are considered conflicts; only the first-seen is kept.

---

## Session Rules

- **Files: English. Chat output: Japanese.**
- Do not push files containing Japanese to remote.
- AGENTS.md / CLAUDE.md / docs/veil-product-design.md must stay deleted from the public repo.
- All GitHub operations use `gh api` (no local git clone).
