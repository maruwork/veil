# File Role Consistency Policy

**Purpose**: Define a portable rule for editing long-lived documents without letting the filename, opening declaration, and actual reader role drift apart.

> **Canonical relationship**: This file is the shared baseline for role-consistent file editing. Project-specific document labels, opening metadata, and lint commands may extend it, but should not weaken the minimum anti-misread rules defined here.

This policy mainly targets long-lived documents, governance files, and shared reusable assets.
Legacy or externally fixed filenames may keep their names, but the opening surface should still remove likely role misreads.
For naming rules, see `naming-shelf.md`.
For entry / guide / reference separation, see `entry-guide-reference.md`.

## 1. Decide the Expected Role from the Name First

Before editing the body, decide what role the file name and path already claim.

Common role labels include:

- `manual`
- `guide`
- `runbook`
- `checklist`
- `template`
- `packet`
- `quickstart`
- `bridge`

Project-local prefixes may also imply role or operating lane.

Do not start by rewriting the whole body.
Start by fixing the role the file is supposed to serve.

## 2. Align the Opening Surface First

Before broader edits, read only the opening surface and compare it with the expected role from the name.

For role-bearing documents, keep these four signals aligned:

1. filename
2. title and opening role declaration
3. reading-position statement
4. related-link framing

If these signals disagree, correct the element that best matches the file's real reader role.
If one says `checklist` while another behaves like `manual`, fix the mismatch before refining detail.
AI readers misread role drift earlier than humans do.

## 3. State What the File Is Not

When a file is easy to misread, state its negative boundary near the top.

Typical examples:

- this is not the current source
- this is not the active work board
- this is the template itself, not a working copy
- this is a route document, not the canonical rule

Use only the minimum negative boundary needed to stop likely misreads.

## 4. Separate Nearby Files by Job

When similar files live in the same shelf, make their differences explicit.

Examples:

- one file gives sequence only
- another gives detailed procedure
- another gives quick verification only

Do not let nearby files compete for the same reader job without a stated difference.

## 4.5 Update the Canonical File First

When the same subject appears in more than one file, identify the canonical file first.

Update the canonical file before updating any dependent guide, summary, index, mirror, or reference file.

Do not repair only a dependent file while leaving the canonical source stale.

## 4.6 Recheck Whole-File Consistency After Partial Edits

After a partial edit, recheck the rest of the file for stale headings, tables, examples, summaries, and related links.

Do not treat a local fix as complete if another part of the file still teaches an older rule, route, or boundary.

## 5. Verify After Editing

After role-related edits, recheck:

- links and related references
- nearby documents that name this file
- entry, guide, or index surfaces that route readers here
- any project-provided lint or consistency checks

If the repository provides them, run a diff check, a reference-link lint, and a strict document-consistency lint before closing the change.
