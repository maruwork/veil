# VEIL Capture Classification

This document defines the first-pass question for free-form capture text:

`What kind of term is this?`

It does **not** decide yet whether VEIL should register the term.
Candidate adoption is a second gate layered on top of this classification.

## Labels

- `industry_term`
  - Industry or specialist term.
  - VEIL still classifies this, but it is a non-target bucket for registration.
- `coined_or_shortened`
  - Project-local coined wording, shorthand, or compressed phrase.
- `file_config_identifier`
  - File name, path, glob, config name, acronym-like identifier, or machine-processed token.
- `other`
  - Ordinary word or phrase that does not look like a useful terminology target.
- `unknown`
  - Still unclear after first-pass rules because the string remains ambiguous or underspecified.

## Current rule direction

- Prefer `file_config_identifier` when the string is clearly mechanical.
- Do not treat an all-caps status or ordinary word as `file_config_identifier` unless it is actually a known acronym-like identifier such as `CI`, `README`, or `SE`.
- Prefer `industry_term` for known specialist terms such as `migration`.
- Prefer known workflow or VCS terms such as `branch`, `mainline`, `checkpoint`, and `normalize` as `industry_term`.
- Treat CI/process-specialist terms such as `workflow` as `industry_term` when they name concrete engineering mechanics rather than just broad status words.
- Treat handoff/runtime engineering terms such as `console`, `scope`, `dataset`, `endpoint`, `readback`, `ruleset`, `OAuth`, `secret`, and `token` as `industry_term`.
- Treat concrete platform/configuration mechanics such as `base URL` and `branch protection` as `industry_term`.
- Do not surface `industry_term` items as VEIL registration candidates just because they are known or repeated.
- Prefer `coined_or_shortened` for project-local phrasing such as `root clutter` or `maintainer-only files`.
- Prefer explicit coined phrase matches over broad suffix or hyphen heuristics, so ordinary bigrams do not get mislabeled.
- Allow a small known list of multiword file/config phrases to be extracted even when they appear as plain words, so schema-like labels such as `guided path` or `trial packet` are not missed.
- Treat known hyphenated local names such as `veil-capture` explicitly instead of treating every hyphenated word as coined wording.
- Strip Markdown link destinations before extraction so `[label](path)` contributes `label` without path-fragment noise.
- Strip `(line 190)`-style reference suffixes before extraction so file references do not leak `line` noise.
- Skip bare one-letter tokens during extraction so outline markers such as `A` or `X` do not survive as fake unknown terms.
- Use `other` for broad ordinary words such as `review`.
- Use `other` for low-signal prose singles such as `this`, `would`, `skill`, `setup`, `selected`, or `validation` so they do not linger as fake unresolved terminology.
- Use `other` for session-log residue such as `sandbox`, `connector`, `markdown`, `agentic`, `dogfooding`, user handles, and similar non-target prose singles.
- Use `other` for VEIL work-session prose residue such as `classification`, `classifier`, `extractor`, `handover`, `locale`, `patching`, and `polishing` when they are being mentioned as conversation wording rather than as terms to register.
- Use `other` for trailing utility prose such as `validate` and `static` when they appear as plain wording rather than product labels or config keys.
- Treat obvious proper nouns such as `GitHub` or `PowerShell` as `other` when they are clearly outside the target categories.
- Use `unknown` only when the first pass still cannot tell what kind of term it is.
- In candidate extraction, require repeated signal before proposing a term. The current default gate is:
  - at least 2 occurrences
  - never propose `file_config_identifier`
  - never propose `industry_term`
  - propose `coined_or_shortened` only for multiword phrases
  - preserve some ordinary multiword `other` phrases for classification, but propose only a smaller allowlist of repeated state or judgment phrases such as `repo hygiene`

- `Draft Capture` investigation is intentionally different from the adoptable gate.
  It is for checking which wording inside a difficult sentence feels suspicious,
  even when the answer may turn out to be “this is a specialist term” or
  “this is just a UI/config label.”
  The current HTML investigation route:
  - can surface single-occurrence coined or internal phrases
  - can surface known multiword UI/config labels such as `Analyze Draft` or `Draft Output`
  - can surface a small allowlist of ambiguous generic singles such as `status`, `preview`, `candidate`, `adoptable`, and `passed`
  - can surface mixed-language unknown singles such as `polishing` when they appear inside Japanese text
  - does not surface single-word specialist terms just because they are known `industry_term` items
  - does not show classification labels to the user in the HTML output

## Chat seed input

`shared/runtime/veil-classify.py` can also read chat transcript JSON with `--chat-json`.
That lets VEIL reuse a conversation export directly instead of requiring manual copy-by-copy term entry first.

The chat-json reader accepts nested transcript shapes through keys such as
`messages`, `conversation`, `turns`, `items`, and `parts`, then reads textual
content from keys such as `text`, `content`, `value`, `message`, and `body`.
Blank segments are dropped, but textual segments remain in input order and keep
their repeated occurrences before classification.

The same CLI also exposes narrower modes:

- `--preview-only`
  - returns local undefined-wording preview results, including single-occurrence internal labels
- `--investigation-only`
  - returns the broader HTML-style investigation results for difficult sentences
- `--adoptable-only`
  - returns only repeated terms that VEIL would currently consider viable registration candidates

`tests/fixtures/veil_capture_attachment_long_tail.txt` is the compact regression corpus for attachment-derived long-tail wording that previously fell into `unknown`.
`tests/fixtures/veil_capture_attachment_candidates.txt` is the compact candidate-gate corpus for attachment-derived wording that should keep only the current high-signal adoptable set while excluding repeated noise such as proper nouns, file identifiers, and generic phrases.
`tests/fixtures/veil_capture_chat_transcript.json` is the chat-shaped regression corpus for transcript ingestion. It should keep the expected coined / industry / file-config boundaries without leaking any adoptable candidates.

## Classification Fixed

VEIL can treat capture classification as fixed when all of the following stay true:

- The attachment long-tail regression corpus produces no `unknown` terms.
- Python classification, HTML/JS classification, and CLI output stay in lockstep.
- Known taxonomy sets remain normalization-unique and free of accidental cross-category overlap.
- Candidate extraction boundaries are explicit:
  - known coined phrases that survive prefix suppression remain candidates
  - industry terms do not become candidates even if they repeat
  - only the allowlisted `other` multiword phrases become repeated `other` candidates
  - file/config terms, repo-directory terms, and proper nouns do not become candidates just because they repeat

At that point, new edge words should no longer drive routine rule expansion.
Anything still outside the boundary should default to `other` or remain intentionally unresolved rather than reopening broad taxonomy growth.

The fixed-state regression loop is:

- `rtk python -m pytest tests -q`
- `rtk python shared\tools\veil-db.py export-html --db $HOME\.veil\veil.db --html-path workspace\veil.html --json`

## Seed examples

- `migration` -> `industry_term`
- `tracked file` -> `industry_term`
- `API` -> `industry_term`
- `JSON` -> `industry_term`
- `base url` -> `industry_term`
- `branch` -> `industry_term`
- `branch protection` -> `industry_term`
- `read only` -> `industry_term`
- `append only` -> `industry_term`
- `fail close` -> `industry_term`
- `machine readable` -> `industry_term`
- `mainline` -> `industry_term`
- `use case` -> `industry_term`
- `checkpoint` -> `industry_term`
- `workflow` -> `industry_term`
- `console` -> `industry_term`
- `scope` -> `industry_term`
- `dataset` -> `industry_term`
- `endpoint` -> `industry_term`
- `readback` -> `industry_term`
- `ruleset` -> `industry_term`
- `OAuth` -> `industry_term`
- `secret` -> `industry_term`
- `token` -> `industry_term`
- `DB` -> `industry_term`
- `UI` -> `industry_term`
- `UX` -> `industry_term`
- `HTML` -> `industry_term`
- `normalize` -> `industry_term`
- `prompt` -> `industry_term`
- `package` -> `industry_term`
- `packaging` -> `industry_term`
- `release` -> `industry_term`
- `security` -> `industry_term`
- `sync` -> `industry_term`
- `checkout` -> `industry_term`
- `reset` -> `industry_term`
- `guardrail` -> `industry_term`
- `worktree` -> `industry_term`
- `adapter` -> `industry_term`
- `artifact` -> `industry_term`
- `audit` -> `industry_term`
- `backlog` -> `industry_term`
- `bytecode` -> `industry_term`
- `commit` -> `industry_term`
- `contract` -> `industry_term`
- `control plane` -> `industry_term`
- `coordinator` -> `industry_term`
- `coupling` -> `industry_term`
- `database` -> `industry_term`
- `drift` -> `industry_term`
- `execution` -> `industry_term`
- `filesystem` -> `industry_term`
- `grep` -> `industry_term`
- `generator` -> `industry_term`
- `healthcheck` -> `industry_term`
- `hook` -> `industry_term`
- `instrumentation` -> `industry_term`
- `kernel` -> `industry_term`
- `linter` -> `industry_term`
- `mtime` -> `industry_term`
- `namespace` -> `industry_term`
- `protocol` -> `industry_term`
- `push` -> `industry_term`
- `scan` -> `industry_term`
- `seed` -> `industry_term`
- `self-describing` -> `industry_term`
- `schema` -> `industry_term`
- `step` -> `industry_term`
- `subagent` -> `industry_term`
- `test` -> `industry_term`
- `trigger` -> `industry_term`
- `untracked` -> `industry_term`
- `validator` -> `industry_term`
- `writeback` -> `industry_term`
- `writer` -> `industry_term`
- `accepted-route` -> `coined_or_shortened`
- `bounded naturalness` -> `coined_or_shortened`
- `carry-forward` -> `coined_or_shortened`
- `current state` -> `coined_or_shortened`
- `dev-only` -> `coined_or_shortened`
- `maintainer-only` -> `coined_or_shortened`
- `manager-copy` -> `coined_or_shortened`
- `non-current` -> `coined_or_shortened`
- `punctuation-triple` -> `coined_or_shortened`
- `proof-blocker` -> `coined_or_shortened`
- `root clutter` -> `coined_or_shortened`
- `maintainer-only files` -> `coined_or_shortened`
- `owner-only` -> `coined_or_shortened`
- `repo` -> `coined_or_shortened`
- `repos` -> `coined_or_shortened`
- `repo truth` -> `coined_or_shortened`
- `veil-capture` -> `coined_or_shortened`
- `writable-shelf` -> `coined_or_shortened`
- `index` -> `file_config_identifier`
- `docs` -> `file_config_identifier`
- `governance` -> `file_config_identifier`
- `generated` -> `file_config_identifier`
- `template` -> `file_config_identifier`
- `packet` -> `file_config_identifier`
- `pycache` -> `file_config_identifier`
- `spec` -> `file_config_identifier`
- `folder` -> `file_config_identifier`
- `manifest` -> `file_config_identifier`
- `yaml` -> `file_config_identifier`
- `/veil-capture` -> `file_config_identifier`
- `AIM_STATUS.md` -> `file_config_identifier`
- `README` -> `file_config_identifier`
- `CI` -> `file_config_identifier`
- `SE` -> `file_config_identifier`
- `adop-pytest` -> `file_config_identifier`
- `adop-pytest-base2` -> `file_config_identifier`
- `adop-pytest-cache` -> `file_config_identifier`
- `artifact shelf` -> `file_config_identifier`
- `candidate intake note` -> `file_config_identifier`
- `compatibility diagnosis` -> `file_config_identifier`
- `dashboard common scope summary` -> `file_config_identifier`
- `data dashboard endpoint mode` -> `file_config_identifier`
- `data dashboard selected environment` -> `file_config_identifier`
- `data dashboard selected environment scope` -> `file_config_identifier`
- `data dashboard selected project scope` -> `file_config_identifier`
- `data dashboard selected tenant scope` -> `file_config_identifier`
- `data environment mode` -> `file_config_identifier`
- `data runtime surface id` -> `file_config_identifier`
- `data selected environment` -> `file_config_identifier`
- `data selected environment scope` -> `file_config_identifier`
- `data selected project scope` -> `file_config_identifier`
- `data selected tenant scope` -> `file_config_identifier`
- `decision owner` -> `file_config_identifier`
- `export html` -> `file_config_identifier`
- `filter reason` -> `file_config_identifier`
- `filter status` -> `file_config_identifier`
- `guided path` -> `file_config_identifier`
- `html path` -> `file_config_identifier`
- `index-local-composed-sample` -> `file_config_identifier`
- `judgment reason` -> `file_config_identifier`
- `judgment-report` -> `file_config_identifier`
- `landing target` -> `file_config_identifier`
- `next action` -> `file_config_identifier`
- `preventive action` -> `file_config_identifier`
- `project local` -> `file_config_identifier`
- `project oriented` -> `file_config_identifier`
- `project profile` -> `file_config_identifier`
- `quick close trial` -> `file_config_identifier`
- `quick-compare` -> `file_config_identifier`
- `quick-trial` -> `file_config_identifier`
- `declared-vs-observed` -> `file_config_identifier`
- `runtime artifact shelf` -> `file_config_identifier`
- `runtime scope readback updated` -> `file_config_identifier`
- `support docs` -> `file_config_identifier`
- `start-trial` -> `file_config_identifier`
- `URL` -> `file_config_identifier`
- `MD` -> `file_config_identifier`
- `system dev` -> `file_config_identifier`
- `trial-result` -> `file_config_identifier`
- `trial packet` -> `file_config_identifier`
- `writeback target` -> `file_config_identifier`
- `config` -> `file_config_identifier`
- `common` -> `file_config_identifier`
- `archive` -> `file_config_identifier`
- `workspace` -> `file_config_identifier`
- `mirror` -> `other`
- `skill` -> `other`
- `setup` -> `other`
- `selected` -> `other`
- `validation` -> `other`
- `sandbox` -> `other`
- `connector` -> `other`
- `markdown` -> `other`
- `dogfooding` -> `other`
- `export` -> `other`
- `import` -> `other`
- `mode` -> `other`
- `flow` -> `other`
- `naming` -> `other`
- `registration` -> `other`
- `deletion` -> `other`
- `version` -> `other`
- `targeted` -> `other`
- `warning` -> `other`
- `AI` -> `other`
- `PROJECT` -> `other`
- `FAIL` -> `other`
- `BLOCKING` -> `other`
- `current` -> `other`
- `latest` -> `other`
- `disabled` -> `other`
- `success` -> `other`
- `passed` -> `other`
- `status` -> `other`
- `pending` -> `other`
- `pattern` -> `other`
- `managed` -> `other`
- `closing` -> `other`
- `open` -> `other`
- `path` -> `other`
- `narrow` -> `other`
- `helper` -> `other`
- `ownership` -> `other`
- `transfer` -> `other`
- `local` -> `other`
- `PowerShell` -> `other`
- `Anthropic` -> `other`
- `Copilot` -> `other`
- `Pier` -> `other`
- `AIM` -> `other`
- `ADOP` -> `other`
- `Playwright` -> `other`
- `JavaScript` -> `other`
- `Vault` -> `other`
- `mypy` -> `other`
- `parse` -> `other`
- `failure` -> `other`
- `hosted` -> `other`
- `hygiene` -> `other`
- `green` -> `other`
- `dirty` -> `other`
- `clean` -> `other`
- `live state` -> `other`
- `branch question` -> `other`
- `current checkpoint` -> `other`
- `current surface` -> `other`
- `launch evidence` -> `other`
- `parse failure` -> `other`
- `repo hygiene` -> `other`
- `canonical body` -> `file_config_identifier`
- `current route` -> `other`
- `execution lane` -> `other`
- `generated sink` -> `file_config_identifier`
- `GitHub standard` -> `coined_or_shortened`
- `operator view` -> `other`
- `read surface` -> `other`
- `shelf class` -> `other`
- `current task register` -> `file_config_identifier`
- `task register` -> `other`
- `hosted gate` -> `industry_term`
- `punctuation triple` -> `other`
- `current issue` -> `other`
- `failing test` -> `other`
- `current issue` remains classifiable as `other`, but repetition alone does not make it a registration candidate.
- `gitleaks` -> proper-noun exclusion (`proper_noun_non_target`)
- `dependabot` -> proper-noun exclusion (`proper_noun_non_target`)
- `unstable wording` -> `coined_or_shortened`
- `review` -> `other`
- `keep` -> `other`
- `baseline` -> `other`
- `readiness` -> `other`
- `matrix` -> `other`
- `framework` -> `other`
- `capture` -> `other`
- `tree` -> `other`
- `disposition` -> `other`
- `inventory` -> `other`
- `principle` -> `other`
- `proposed` -> `other`
- `role` -> `other`
- `scene` -> `other`
- `stage` -> `other`
- `text` -> `other`
- `trial` -> `other`
- `verification` -> `other`
- `overview` -> `other`
- `whitelist` -> `other`
- `reviewer` -> `other`
- `auditor` -> `other`
- `engineer` -> `other`
- `Bash` -> `other`
- `Cursor` -> `other`
- `SQLite` -> `other`
- `Saiga` -> `other`
- `Symphony` -> `other`
- `server` -> `other`
- `payload` -> `other`
- `platform` -> `other`
- `license` -> `other`
- `reason` -> `other`
- `GitHub` -> `other`
- `Python` -> `other`
- `pytest` -> `other`
- `root` -> `other`
- `ordinary` -> `other`
- `noun` -> `other`
- `multiword` -> `other`
- `first-pass` -> `other`
