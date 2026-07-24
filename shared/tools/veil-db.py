#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    from shared.tools.veil_rule_store import (
        DEFAULT_BUNDLED_PROFILE_SEED_PATH,
        DEFAULT_DB_PATH,
        DEFAULT_HTML_PATH,
        PROFILE_LEVEL_DEFAULT,
        delete_rule,
        export_html_from_db,
        get_html_ui_for_lang,
        get_protected_repo_dir_name,
        init_db,
        readback_rules,
        replace_rules_from_seed,
        upsert_rule,
        upsert_rules_atomic,
    )
    from shared.tools.veil_locale import detect_lang, t
except ModuleNotFoundError:
    from veil_rule_store import (  # type: ignore[no-redef]
        DEFAULT_BUNDLED_PROFILE_SEED_PATH,
        DEFAULT_DB_PATH,
        DEFAULT_HTML_PATH,
        PROFILE_LEVEL_DEFAULT,
        delete_rule,
        export_html_from_db,
        get_html_ui_for_lang,
        get_protected_repo_dir_name,
        init_db,
        readback_rules,
        replace_rules_from_seed,
        upsert_rule,
        upsert_rules_atomic,
    )
    from veil_locale import detect_lang, t  # type: ignore[no-redef]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=t("db.description"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help=t("db.init_db_help"))
    init_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    init_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    import_seed_parser = subparsers.add_parser("import-seed", help=t("db.import_seed_help"))
    import_seed_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    import_seed_parser.add_argument(
        "--seed-file",
        default=DEFAULT_BUNDLED_PROFILE_SEED_PATH,
        help=t("db.import_seed_file_help"),
    )
    import_seed_parser.add_argument("--yes", action="store_true", help=t("db.import_rules_yes_help"))
    import_seed_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    readback_parser = subparsers.add_parser("readback", help=t("db.readback_help"))
    readback_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    readback_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    upsert_parser = subparsers.add_parser("upsert-rule", help=t("db.upsert_rule_help"))
    upsert_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    upsert_parser.add_argument("--term", required=True, help=t("db.term_help"))
    upsert_parser.add_argument("--preferred", required=True, help=t("db.preferred_help"))
    upsert_parser.add_argument("--preferred-alt-2", help=t("db.preferred_alt_2_help"))
    upsert_parser.add_argument("--preferred-alt-3", help=t("db.preferred_alt_3_help"))
    upsert_parser.add_argument("--status", default="active", help=t("db.status_help"))
    upsert_parser.add_argument("--level", default=PROFILE_LEVEL_DEFAULT, help=argparse.SUPPRESS)
    upsert_parser.add_argument("--category-hint", help=t("db.category_hint_help"))
    upsert_parser.add_argument("--note", help=t("db.note_help"))
    upsert_parser.add_argument("--source-context", help=t("db.source_context_help"))
    upsert_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    upsert_batch_parser = subparsers.add_parser("upsert-batch", help=t("db.upsert_batch_help"))
    upsert_batch_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    upsert_batch_parser.add_argument("--input-json", required=True, help=t("db.upsert_batch_file_help"))
    upsert_batch_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    delete_parser = subparsers.add_parser("delete-rule", help=t("db.delete_rule_help"))
    delete_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    delete_parser.add_argument("--term", required=True, help=t("db.term_help"))
    delete_parser.add_argument("--json", action="store_true", help=t("db.json_help"))

    html_parser = subparsers.add_parser("export-html", help=t("db.export_html_help"))
    html_parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("db.db_help"))
    html_parser.add_argument("--html-path", default=DEFAULT_HTML_PATH, help=t("db.export_html_path_help"))
    html_parser.add_argument("--json", action="store_true", help=t("db.json_help"))
    return parser


def print_import_text(payload: dict[str, Any]) -> None:
    if payload["status"] != "ok":
        tag = "ERROR" if payload["status"] == "error" else "SKIP"
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"{tag}: {t(str(payload['reason']))}{detail}")
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
        if "warning_key" in warning:
            msg = t(warning["warning_key"], **warning.get("warning_args", {}))
        else:
            msg = str(warning.get("warning", ""))
        print(f"- warning {location}: {msg}")


def print_readback_text(payload: dict[str, Any]) -> None:
    if payload["status"] != "ok":
        tag = "ERROR" if payload["status"] == "error" else "SKIP"
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"{tag}: {t(str(payload['reason']))}{detail}")
        return
    summary = payload["summary"]
    print(f"READBACK: db={payload['db_path']}, total={summary['total']}")
    for row in payload["rows"]:
        print(f"- {row['term_original']} -> {row['preferred']} ({row['source_context']})")


def print_upsert_text(payload: dict[str, Any]) -> None:
    if payload["status"] != "ok":
        tag = "ERROR" if payload["status"] == "error" else "SKIP"
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"{tag}: {t(str(payload['reason']))}{detail}")
        return
    row = payload["row"]
    print(
        f"UPSERT: {payload['action']} db={payload['db_path']}"
        f" {row['term_original']} -> {row['preferred']}"
    )


_BATCH_ALLOWED_FIELDS = {
    "term",
    "preferred",
    "preferred_alt_2",
    "preferred_alt_3",
    "status",
    "level",
    "category_hint",
    "note",
    "source_context",
}


def load_upsert_batch(path: str) -> list[dict[str, str | None]]:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read batch JSON: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("contract_version") != "1":
        raise ValueError("batch JSON must be an object with contract_version '1'")
    rules = raw.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("batch JSON rules must be a non-empty array")
    if len(rules) > 100:
        raise ValueError("batch JSON may contain at most 100 rules")

    validated: list[dict[str, str | None]] = []
    for index, item in enumerate(rules):
        if not isinstance(item, dict):
            raise ValueError(f"rules[{index}] must be an object")
        unknown = sorted(set(item) - _BATCH_ALLOWED_FIELDS)
        if unknown:
            raise ValueError(f"rules[{index}] has unsupported fields: {', '.join(unknown)}")
        normalized: dict[str, str | None] = {}
        for key in _BATCH_ALLOWED_FIELDS:
            value = item.get(key)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"rules[{index}].{key} must be a string or null")
            normalized[key] = value.strip() if isinstance(value, str) else None
        for required in ("term", "preferred"):
            if not normalized[required]:
                raise ValueError(f"rules[{index}].{required} must be a non-empty string")
        if "|" in str(normalized["preferred"]):
            raise ValueError(f"rules[{index}].preferred must contain one preferred form")
        validated.append(normalized)
    return validated


def upsert_batch(db_path: str, input_json: str) -> dict[str, Any]:
    try:
        rules = load_upsert_batch(input_json)
    except ValueError as exc:
        return {
            "status": "error",
            "reason": "invalid_batch_payload",
            "db_path": db_path,
            "input_json": input_json,
            "error": str(exc),
            "processed_count": 0,
            "results": [],
        }

    payload = upsert_rules_atomic(db_path, rules)
    payload["input_json"] = input_json
    payload["atomic"] = True
    return payload


def print_upsert_batch_text(payload: dict[str, Any]) -> None:
    if payload["status"] != "ok":
        reason = str(payload.get("reason") or "store.batch_write_failed")
        print(f"ERROR: {t(reason)} ({payload.get('error', 'batch write failed')})")
        return
    print(f"UPSERT-BATCH: db={payload['db_path']} rows={payload['processed_count']}")


def print_delete_text(payload: dict[str, Any]) -> None:
    if payload["status"] != "ok":
        tag = "ERROR" if payload["status"] == "error" else "SKIP"
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"{tag}: {t(str(payload['reason']))}{detail}")
        return
    row = payload["row"]
    print(f"DELETE: {payload['action']} db={payload['db_path']} {row['term_original']}")


def print_export_html_text(payload: dict[str, Any]) -> None:
    if payload["status"] != "ok":
        tag = "ERROR" if payload["status"] == "error" else "SKIP"
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"{tag}: {t(str(payload['reason']))}{detail}")
        return
    source = payload.get("source_type", "db")
    warning = ""
    if payload.get("warning_reason"):
        warning_detail = t(str(payload["warning_reason"]))
        warning = f", warning={warning_detail}"
    print(
        f"EXPORT-HTML: db={payload['db_path']}, html={payload['html_path']}, rows={payload['row_count']},"
        f" source={source}{warning}"
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init-db":
        if get_protected_repo_dir_name(args.db) is not None:
            payload = {
                "status": "error",
                "reason": "store.protected_output_path",
                "db_path": args.db,
                "error": args.db,
            }
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(f"ERROR: {t(str(payload['reason']))} ({payload['error']})")
            return 1
        try:
            init_db(args.db)
            payload = {"status": "ok", "db_path": args.db}
        except Exception as exc:
            payload = {"status": "error", "reason": "store.db_unreadable", "db_path": args.db, "error": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            if payload["status"] == "ok":
                print(f"INIT-DB: {args.db}")
            else:
                print(f"ERROR: {t(str(payload['reason']))} ({payload['error']})")
        return 0 if payload["status"] == "ok" else 1

    if args.command == "import-seed":
        if not args.yes:
            print(t("db.import_rules_confirm", db=args.db), file=sys.stderr)
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                print(t("db.import_rules_aborted"), file=sys.stderr)
                return 1
        payload = replace_rules_from_seed(args.db, args.seed_file)
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
        preferred_val = args.preferred
        alt2_val = args.preferred_alt_2
        alt3_val = args.preferred_alt_3
        if "|" in preferred_val:
            parts = [p.strip() for p in preferred_val.split("|") if p.strip()]
            if parts:
                preferred_val = parts[0]
                if alt2_val is None and len(parts) > 1:
                    alt2_val = parts[1]
                if alt3_val is None and len(parts) > 2:
                    alt3_val = parts[2]
        payload = upsert_rule(
            args.db,
            term_original=args.term,
            preferred=preferred_val,
            preferred_alt_2=alt2_val,
            preferred_alt_3=alt3_val,
            status=args.status,
            profile_level=args.level,
            category_hint=args.category_hint,
            note=args.note,
            source_context=args.source_context,
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_upsert_text(payload)
        return 0 if payload["status"] == "ok" else 1

    if args.command == "upsert-batch":
        payload = upsert_batch(args.db, args.input_json)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_upsert_batch_text(payload)
        return 0 if payload["status"] == "ok" else 1

    if args.command == "delete-rule":
        payload = delete_rule(
            args.db,
            args.term,
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_delete_text(payload)
        return 0 if payload["status"] == "ok" else 1

    if args.command == "export-html":
        lang = detect_lang()
        ui = get_html_ui_for_lang(lang)
        payload = export_html_from_db(args.db, args.html_path, ui=ui)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_export_html_text(payload)
        return 0 if payload["status"] == "ok" else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
