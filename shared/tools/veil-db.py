#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

try:
    from shared.tools.veil_rule_store import (
        DEFAULT_DB_PATH,
        DEFAULT_HTML_PATH,
        DEFAULT_RULES_DIR,
        export_html_from_db,
        export_markdown_mirror_from_db,
        init_db,
        readback_rules,
        replace_rules_from_markdown,
        upsert_rule,
    )
    from shared.tools.veil_locale import t
except ModuleNotFoundError:
    from veil_rule_store import (  # type: ignore[no-redef]
        DEFAULT_DB_PATH,
        DEFAULT_HTML_PATH,
        DEFAULT_RULES_DIR,
        export_html_from_db,
        export_markdown_mirror_from_db,
        init_db,
        readback_rules,
        replace_rules_from_markdown,
        upsert_rule,
    )
    from veil_locale import t  # type: ignore[no-redef]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VEIL SQLite Stage 1 support CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help=t("db.init_db_help"))
    init_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    init_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    import_parser = subparsers.add_parser("import-rules", help=t("db.import_rules_help"))
    import_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    import_parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help=t("db.import_rules_dir_help"),
    )
    import_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    readback_parser = subparsers.add_parser("readback", help=t("db.readback_help"))
    readback_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    readback_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    upsert_parser = subparsers.add_parser("upsert-rule", help=t("db.upsert_rule_help"))
    upsert_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    upsert_parser.add_argument("--term", required=True, help="original term.")
    upsert_parser.add_argument("--preferred", required=True, help="preferred term.")
    upsert_parser.add_argument("--preferred-alt-2", help=t("db.preferred_alt_2_help"))
    upsert_parser.add_argument("--preferred-alt-3", help=t("db.preferred_alt_3_help"))
    upsert_parser.add_argument("--status", default="active", help=t("db.status_help"))
    upsert_parser.add_argument("--category-hint", help="category hint.")
    upsert_parser.add_argument("--note", help="note.")
    upsert_parser.add_argument("--source-context", help="source context.")
    upsert_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    export_parser = subparsers.add_parser("export-mirror", help=t("db.export_mirror_help"))
    export_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    export_parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help=t("db.export_rules_dir_help"),
    )
    export_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    html_parser = subparsers.add_parser("export-html", help=t("db.export_html_help"))
    html_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    html_parser.add_argument("--html-path", default=DEFAULT_HTML_PATH, help=t("db.export_html_path_help"))
    html_parser.add_argument("--json", action="store_true", help=t("db.json_help"))
    return parser


def print_import_text(payload: dict[str, object]) -> None:
    if payload["status"] != "ok":
        print(f"SKIP: {payload['reason']}")
        return
    print(
        "IMPORTED:"
        f" db={payload['db_path']}, files={payload['files_seen']}, rows={payload['imported_count']},"
        f" conflicts={len(payload['conflicts'])}, warnings={len(payload['warnings'])}"
    )
    for conflict in payload["conflicts"]:
        selected = conflict["selected"]
        ignored = ", ".join(
            f"{entry['term_original']} -> {entry['preferred']} ({entry['source_context']})"
            for entry in conflict["ignored"]
        )
        print(
            f"- conflict [{conflict['normalized']}]: "
            f"selected {selected['term_original']} -> {selected['preferred']} "
            f"({selected['source_context']}), ignored {ignored}"
        )
    for warning in payload["warnings"]:
        location = f"{warning.get('file', '?')}:{warning.get('line', 0)}"
        print(f"- warning {location}: {warning['warning']}")


def print_readback_text(payload: dict[str, object]) -> None:
    if payload["status"] != "ok":
        print(f"SKIP: {payload['reason']}")
        return
    summary = payload["summary"]
    print(f"READBACK: db={payload['db_path']}, total={summary['total']}")
    for row in payload["rows"]:
        print(f"- {row['term_original']} -> {row['preferred']} ({row['source_context']})")


def print_upsert_text(payload: dict[str, object]) -> None:
    if payload["status"] != "ok":
        print(f"SKIP: {payload['reason']}")
        return
    row = payload["row"]
    print(f"UPSERT: {payload['action']} db={payload['db_path']} {row['term_original']} -> {row['preferred']}")


def print_export_text(payload: dict[str, object]) -> None:
    if payload["status"] != "ok":
        print(f"SKIP: {payload['reason']}")
        return
    print(
        "EXPORT-MIRROR:"
        f" db={payload['db_path']}, rules_dir={payload['rules_dir']},"
        f" rows={payload['row_count']}, written={len(payload['written_files'])},"  # type: ignore[arg-type]
        f" removed={len(payload['removed_files'])}"  # type: ignore[arg-type]
    )
    for filename in payload["written_files"]:  # type: ignore[union-attr]
        print(f"- wrote {filename}")
    for filename in payload["removed_files"]:  # type: ignore[union-attr]
        print(f"- removed {filename}")


def print_export_html_text(payload: dict[str, object]) -> None:
    if payload["status"] != "ok":
        print(f"SKIP: {payload['reason']}")
        return
    print(f"EXPORT-HTML: db={payload['db_path']}, html={payload['html_path']}, rows={payload['row_count']}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        init_db(args.db)
        payload = {"status": "ok", "db_path": args.db}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"INIT-DB: {args.db}")
        return 0

    if args.command == "import-rules":
        payload = replace_rules_from_markdown(args.db, args.rules_dir)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_import_text(payload)
        return 0 if payload["status"] == "ok" else 1

    if args.command == "readback":
        payload = readback_rules(args.db)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_readback_text(payload)
        return 0 if payload["status"] == "ok" else 1

    if args.command == "upsert-rule":
        payload = upsert_rule(
            args.db,
            term_original=args.term,
            preferred=args.preferred,
            preferred_alt_2=args.preferred_alt_2,
            preferred_alt_3=args.preferred_alt_3,
            status=args.status,
            category_hint=args.category_hint,
            note=args.note,
            source_context=args.source_context,
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_upsert_text(payload)
        return 0 if payload["status"] == "ok" else 1

    if args.command == "export-mirror":
        payload = export_markdown_mirror_from_db(args.db, args.rules_dir)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_export_text(payload)
        return 0 if payload["status"] == "ok" else 1

    if args.command == "export-html":
        payload = export_html_from_db(args.db, args.html_path)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_export_html_text(payload)
        return 0 if payload["status"] == "ok" else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
