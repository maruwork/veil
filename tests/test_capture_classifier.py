from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from shared.tools.veil_capture_classifier import (
    LABEL_COINED_OR_SHORTENED,
    LABEL_FILE_CONFIG_IDENTIFIER,
    LABEL_INDUSTRY_TERM,
    LABEL_OTHER,
    LABEL_UNKNOWN,
    classify_term,
    extract_adoptable_terms,
    extract_investigation_terms,
    extract_classified_terms,
    extract_classified_term_map,
    extract_preview_terms,
    is_adoptable_classified_term,
)
from shared.tools.veil_capture_taxonomy import capture_taxonomy_payload
from shared.tools.veil_capture_taxonomy import (
    ALL_LABELS,
    ADOPTABLE_OTHER_MULTIWORD_TERMS,
    KNOWN_COINED_TERMS,
    KNOWN_FILE_CONFIG_TERMS,
    KNOWN_INDUSTRY_ACRONYMS,
    KNOWN_INDUSTRY_TERMS,
    KNOWN_OTHER_MULTIWORD_TERMS,
    KNOWN_REPO_DIR_TERMS,
    PREVIEWABLE_GENERIC_SINGLE_TERMS,
    PROPER_NOUN_TERMS,
)
from shared.tools.veil_rule_store import normalize_term
from .helpers import classify_cmd, db_cmd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = Path(__file__).with_name("fixtures") / "veil_capture_chat_seed.json"
CHAT_JSON_FIXTURE_PATH = Path(__file__).with_name("fixtures") / "veil_capture_chat_transcript.json"
ATTACHMENT_LONG_TAIL_FIXTURE_PATH = Path(__file__).with_name("fixtures") / "veil_capture_attachment_long_tail.txt"
ATTACHMENT_CANDIDATES_FIXTURE_PATH = Path(__file__).with_name("fixtures") / "veil_capture_attachment_candidates.txt"
HTML_TEMPLATE_PATH = PROJECT_ROOT / "shared" / "tools" / "veil_review_template.html"
CLASSIFY_RUNTIME_PATH = PROJECT_ROOT / "shared" / "runtime" / "veil-classify.py"
NODE_AUDIT_DIR = PROJECT_ROOT / "workspace" / "audit" / "classifier-node"
_CLASSIFY_RUNTIME_MODULE = None


def _load_classify_runtime_module():
    global _CLASSIFY_RUNTIME_MODULE
    if _CLASSIFY_RUNTIME_MODULE is None:
        spec = importlib.util.spec_from_file_location("veil_classify_runtime_for_tests", CLASSIFY_RUNTIME_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _CLASSIFY_RUNTIME_MODULE = module
    return _CLASSIFY_RUNTIME_MODULE


def _js_capture_runtime() -> str:
    source = HTML_TEMPLATE_PATH.read_text(encoding="utf-8")
    start_marker = "  function simpleSingularizeToken(token) {"
    end_marker = "  function analyzeCaptureInput() {"
    start = source.index(start_marker)
    end = source.index(end_marker)
    return source[start:end]


def _run_node_script(script: str) -> str:
    NODE_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False, dir=NODE_AUDIT_DIR) as handle:
        handle.write(script)
        script_path = handle.name
    try:
        result = subprocess.run(
            ["node", script_path],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        )
        return result.stdout
    finally:
        try:
            os.unlink(script_path)
        except FileNotFoundError:
            pass


def _js_classify_terms(terms: list[str]) -> list[dict[str, str]]:
    script = f"""
const _captureConfig = {json.dumps(capture_taxonomy_payload(), ensure_ascii=False)};
const document = {{ querySelectorAll: () => [] }};
function message(key) {{ return key; }}
{_js_capture_runtime()}
const payload = {json.dumps({"terms": terms}, ensure_ascii=False)};
const results = payload.terms.map((term) => {{
  const item = classifyCaptureTerm(term);
  return {{
  term: item.term,
  normalized: item.normalized,
  label: item.label,
  reason: item.reason
  }};
}});
process.stdout.write(JSON.stringify(results));
"""
    return json.loads(_run_node_script(script))


def _js_extract_capture_candidates(text: str, limit: int = 5) -> list[dict[str, str]]:
    script = f"""
const _captureConfig = {json.dumps(capture_taxonomy_payload(), ensure_ascii=False)};
const document = {{ querySelectorAll: () => [] }};
function message(key) {{ return key; }}
{_js_capture_runtime()}
const payload = {json.dumps({"text": text, "limit": limit}, ensure_ascii=False)};
const results = extractCaptureCandidates(payload.text, payload.limit).map((item) => ({{
  term: item.term,
  normalized: item.normalized,
  label: item.label,
  reason: item.reason
}}));
process.stdout.write(JSON.stringify(results));
"""
    return json.loads(_run_node_script(script))


def _js_extract_capture_preview_terms(text: str, limit: int = 5) -> list[dict[str, str]]:
    script = f"""
const _captureConfig = {json.dumps(capture_taxonomy_payload(), ensure_ascii=False)};
const document = {{ querySelectorAll: () => [] }};
function message(key) {{ return key; }}
{_js_capture_runtime()}
const payload = {json.dumps({"text": text, "limit": limit}, ensure_ascii=False)};
const results = extractCapturePreviewTerms(payload.text, payload.limit).map((item) => ({{
  term: item.term,
  normalized: item.normalized,
  label: item.label,
  reason: item.reason
}}));
process.stdout.write(JSON.stringify(results));
"""
    return json.loads(_run_node_script(script))


def _js_extract_capture_investigation_terms(text: str, limit: int = 8) -> list[dict[str, str]]:
    script = f"""
const _captureConfig = {json.dumps(capture_taxonomy_payload(), ensure_ascii=False)};
const document = {{ querySelectorAll: () => [] }};
function message(key) {{ return key; }}
{_js_capture_runtime()}
const payload = {json.dumps({"text": text, "limit": limit}, ensure_ascii=False)};
const results = extractCaptureInvestigationTerms(payload.text, payload.limit).map((item) => ({{
  term: item.term,
  normalized: item.normalized,
  label: item.label,
  reason: item.reason
}}));
process.stdout.write(JSON.stringify(results));
"""
    return json.loads(_run_node_script(script))


def test_classify_term_labels() -> None:
    assert classify_term("migration").label == LABEL_INDUSTRY_TERM
    assert classify_term("tracked file").label == LABEL_INDUSTRY_TERM
    assert classify_term("base url").label == LABEL_INDUSTRY_TERM
    assert classify_term("branch").label == LABEL_INDUSTRY_TERM
    assert classify_term("branch protection").label == LABEL_INDUSTRY_TERM
    assert classify_term("mainline").label == LABEL_INDUSTRY_TERM
    assert classify_term("checkpoint").label == LABEL_INDUSTRY_TERM
    assert classify_term("normalize").label == LABEL_INDUSTRY_TERM
    assert classify_term("workflow").label == LABEL_INDUSTRY_TERM
    assert classify_term("console").label == LABEL_INDUSTRY_TERM
    assert classify_term("scope").label == LABEL_INDUSTRY_TERM
    assert classify_term("dataset").label == LABEL_INDUSTRY_TERM
    assert classify_term("endpoint").label == LABEL_INDUSTRY_TERM
    assert classify_term("readback").label == LABEL_INDUSTRY_TERM
    assert classify_term("release").label == LABEL_INDUSTRY_TERM
    assert classify_term("bootstrap").label == LABEL_INDUSTRY_TERM
    assert classify_term("master").label == LABEL_INDUSTRY_TERM
    assert classify_term("metadata").label == LABEL_INDUSTRY_TERM
    assert classify_term("regression").label == LABEL_INDUSTRY_TERM
    assert classify_term("regulation").label == LABEL_INDUSTRY_TERM
    assert classify_term("checkout").label == LABEL_INDUSTRY_TERM
    assert classify_term("composer").label == LABEL_INDUSTRY_TERM
    assert classify_term("coverage").label == LABEL_INDUSTRY_TERM
    assert classify_term("engine").label == LABEL_INDUSTRY_TERM
    assert classify_term("guardrail").label == LABEL_INDUSTRY_TERM
    assert classify_term("observer").label == LABEL_INDUSTRY_TERM
    assert classify_term("orchestration").label == LABEL_INDUSTRY_TERM
    assert classify_term("playback").label == LABEL_INDUSTRY_TERM
    assert classify_term("renderer").label == LABEL_INDUSTRY_TERM
    assert classify_term("reset").label == LABEL_INDUSTRY_TERM
    assert classify_term("scanning").label == LABEL_INDUSTRY_TERM
    assert classify_term("screening").label == LABEL_INDUSTRY_TERM
    assert classify_term("security").label == LABEL_INDUSTRY_TERM
    assert classify_term("shell").label == LABEL_INDUSTRY_TERM
    assert classify_term("sync").label == LABEL_INDUSTRY_TERM
    assert classify_term("timezone").label == LABEL_INDUSTRY_TERM
    assert classify_term("triage").label == LABEL_INDUSTRY_TERM
    assert classify_term("ruleset").label == LABEL_INDUSTRY_TERM
    assert classify_term("gate").label == LABEL_INDUSTRY_TERM
    assert classify_term("orchestrator").label == LABEL_INDUSTRY_TERM
    assert classify_term("oauth").label == LABEL_INDUSTRY_TERM
    assert classify_term("secret").label == LABEL_INDUSTRY_TERM
    assert classify_term("stdin").label == LABEL_INDUSTRY_TERM
    assert classify_term("token").label == LABEL_INDUSTRY_TERM
    assert classify_term("http").label == LABEL_INDUSTRY_TERM
    assert classify_term("repo").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("repos").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("owner-only").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("dev-only").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("maintainer-only files").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("bounded naturalness").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("repo truth").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("/veil-capture").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("README").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("CI").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("SE").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("adop-pytest").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("adop-pytest-base2").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("adop-pytest-cache").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("candidate intake note").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("compatibility diagnosis").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("dashboard common scope summary").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data dashboard endpoint mode").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data dashboard selected environment").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data dashboard selected environment scope").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data dashboard selected project scope").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data dashboard selected tenant scope").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data environment mode").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data runtime surface id").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data selected environment").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data selected environment scope").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data selected project scope").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("data selected tenant scope").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("export html").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("decision owner").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("Analyze Draft").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("Draft Output").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("file_config_identifier").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("filter reason").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("filter status").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("guided path").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("html path").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("index-local-composed-sample").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("judgment reason").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("judgment-report").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("landing target").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("gitignore").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("56e5981").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("56e5981c05c1413673d58ea6adfba7de824a686c").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("next action").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("pyrightconfig.json").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("preventive action").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("quick-compare").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("quick-trial").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("project profile").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("project local").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("project oriented").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("quick close trial").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("API").label == LABEL_INDUSTRY_TERM
    assert classify_term("JSON").label == LABEL_INDUSTRY_TERM
    assert classify_term("maintainer-only").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("runtime scope readback updated").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("start-trial").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("system dev").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("declared-vs-observed").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("trial-result").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("trial packet").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("writeback target").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("DB").label == LABEL_INDUSTRY_TERM
    assert classify_term("HTML").label == LABEL_INDUSTRY_TERM
    assert classify_term("UI").label == LABEL_INDUSTRY_TERM
    assert classify_term("UX").label == LABEL_INDUSTRY_TERM
    assert classify_term("prompt").label == LABEL_INDUSTRY_TERM
    assert classify_term("read only").label == LABEL_INDUSTRY_TERM
    assert classify_term("package").label == LABEL_INDUSTRY_TERM
    assert classify_term("packaging").label == LABEL_INDUSTRY_TERM
    assert classify_term("append only").label == LABEL_INDUSTRY_TERM
    assert classify_term("use case").label == LABEL_INDUSTRY_TERM
    assert classify_term("worktree").label == LABEL_INDUSTRY_TERM
    assert classify_term("adapter").label == LABEL_INDUSTRY_TERM
    assert classify_term("artifact").label == LABEL_INDUSTRY_TERM
    assert classify_term("assert").label == LABEL_INDUSTRY_TERM
    assert classify_term("audit").label == LABEL_INDUSTRY_TERM
    assert classify_term("backlog").label == LABEL_INDUSTRY_TERM
    assert classify_term("bytecode").label == LABEL_INDUSTRY_TERM
    assert classify_term("commit").label == LABEL_INDUSTRY_TERM
    assert classify_term("contract").label == LABEL_INDUSTRY_TERM
    assert classify_term("control plane").label == LABEL_INDUSTRY_TERM
    assert classify_term("coordinator").label == LABEL_INDUSTRY_TERM
    assert classify_term("coupling").label == LABEL_INDUSTRY_TERM
    assert classify_term("database").label == LABEL_INDUSTRY_TERM
    assert classify_term("drift").label == LABEL_INDUSTRY_TERM
    assert classify_term("execution").label == LABEL_INDUSTRY_TERM
    assert classify_term("fail close").label == LABEL_INDUSTRY_TERM
    assert classify_term("filesystem").label == LABEL_INDUSTRY_TERM
    assert classify_term("generator").label == LABEL_INDUSTRY_TERM
    assert classify_term("grep").label == LABEL_INDUSTRY_TERM
    assert classify_term("healthcheck").label == LABEL_INDUSTRY_TERM
    assert classify_term("hosted gate").label == LABEL_INDUSTRY_TERM
    assert classify_term("gitignored").label == LABEL_INDUSTRY_TERM
    assert classify_term("hook").label == LABEL_INDUSTRY_TERM
    assert classify_term("instrumentation").label == LABEL_INDUSTRY_TERM
    assert classify_term("kernel").label == LABEL_INDUSTRY_TERM
    assert classify_term("linter").label == LABEL_INDUSTRY_TERM
    assert classify_term("mtime").label == LABEL_INDUSTRY_TERM
    assert classify_term("namespace").label == LABEL_INDUSTRY_TERM
    assert classify_term("protocol").label == LABEL_INDUSTRY_TERM
    assert classify_term("push").label == LABEL_INDUSTRY_TERM
    assert classify_term("scan").label == LABEL_INDUSTRY_TERM
    assert classify_term("seed").label == LABEL_INDUSTRY_TERM
    assert classify_term("schema").label == LABEL_INDUSTRY_TERM
    assert classify_term("step").label == LABEL_INDUSTRY_TERM
    assert classify_term("subagent").label == LABEL_INDUSTRY_TERM
    assert classify_term("test").label == LABEL_INDUSTRY_TERM
    assert classify_term("trigger").label == LABEL_INDUSTRY_TERM
    assert classify_term("untracked").label == LABEL_INDUSTRY_TERM
    assert classify_term("validator").label == LABEL_INDUSTRY_TERM
    assert classify_term("writeback").label == LABEL_INDUSTRY_TERM
    assert classify_term("writer").label == LABEL_INDUSTRY_TERM
    assert classify_term("machine readable").label == LABEL_INDUSTRY_TERM
    assert classify_term("veil-capture").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("docs").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("folder").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("generated").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("governance").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("index").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("manifest").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("packet").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("pycache").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("spec").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("template").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("yaml").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("common").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("archive").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("workspace").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("config").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("mirror").label == LABEL_OTHER
    assert classify_term("export").label == LABEL_OTHER
    assert classify_term("import").label == LABEL_OTHER
    assert classify_term("mode").label == LABEL_OTHER
    assert classify_term("flow").label == LABEL_OTHER
    assert classify_term("naming").label == LABEL_OTHER
    assert classify_term("registration").label == LABEL_OTHER
    assert classify_term("deletion").label == LABEL_OTHER
    assert classify_term("version").label == LABEL_OTHER
    assert classify_term("targeted").label == LABEL_OTHER
    assert classify_term("warning").label == LABEL_OTHER
    assert classify_term("AI").label == LABEL_OTHER
    assert classify_term("PROJECT").label == LABEL_OTHER
    assert classify_term("FAIL").label == LABEL_OTHER
    assert classify_term("BLOCKING").label == LABEL_OTHER
    assert classify_term("current").label == LABEL_OTHER
    assert classify_term("consistency").label == LABEL_OTHER
    assert classify_term("detect").label == LABEL_OTHER
    assert classify_term("disabled").label == LABEL_OTHER
    assert classify_term("fixed").label == LABEL_OTHER
    assert classify_term("issue").label == LABEL_OTHER
    assert classify_term("install").label == LABEL_OTHER
    assert classify_term("latest").label == LABEL_OTHER
    assert classify_term("passed").label == LABEL_OTHER
    assert classify_term("report").label == LABEL_OTHER
    assert classify_term("remote").label == LABEL_OTHER
    assert classify_term("status").label == LABEL_OTHER
    assert classify_term("success").label == LABEL_OTHER
    assert classify_term("transcript").label == LABEL_OTHER
    assert classify_term("update").label == LABEL_OTHER
    assert classify_term("draft").label == LABEL_OTHER
    assert classify_term("pending").label == LABEL_OTHER
    assert classify_term("pattern").label == LABEL_OTHER
    assert classify_term("managed").label == LABEL_OTHER
    assert classify_term("closing").label == LABEL_OTHER
    assert classify_term("open").label == LABEL_OTHER
    assert classify_term("path").label == LABEL_OTHER
    assert classify_term("narrow").label == LABEL_OTHER
    assert classify_term("helper").label == LABEL_OTHER
    assert classify_term("ownership").label == LABEL_OTHER
    assert classify_term("transfer").label == LABEL_OTHER
    assert classify_term("local").label == LABEL_OTHER
    assert classify_term("first").label == LABEL_OTHER
    assert classify_term("launch").label == LABEL_OTHER
    assert classify_term("keep").label == LABEL_OTHER
    assert classify_term("baseline").label == LABEL_OTHER
    assert classify_term("readiness").label == LABEL_OTHER
    assert classify_term("matrix").label == LABEL_OTHER
    assert classify_term("framework").label == LABEL_OTHER
    assert classify_term("acceptance").label == LABEL_OTHER
    assert classify_term("architecture").label == LABEL_OTHER
    assert classify_term("preview").label == LABEL_OTHER
    assert classify_term("capture").label == LABEL_OTHER
    assert classify_term("breakdown").label == LABEL_OTHER
    assert classify_term("category").label == LABEL_OTHER
    assert classify_term("compliance").label == LABEL_OTHER
    assert classify_term("context").label == LABEL_OTHER
    assert classify_term("criteria").label == LABEL_OTHER
    assert classify_term("date").label == LABEL_OTHER
    assert classify_term("detail").label == LABEL_OTHER
    assert classify_term("disposition").label == LABEL_OTHER
    assert classify_term("experiment").label == LABEL_OTHER
    assert classify_term("final").label == LABEL_OTHER
    assert classify_term("finding").label == LABEL_OTHER
    assert classify_term("guided").label == LABEL_OTHER
    assert classify_term("heading").label == LABEL_OTHER
    assert classify_term("input").label == LABEL_OTHER
    assert classify_term("integrity").label == LABEL_OTHER
    assert classify_term("inventory").label == LABEL_OTHER
    assert classify_term("label").label == LABEL_OTHER
    assert classify_term("message").label == LABEL_OTHER
    assert classify_term("mutation").label == LABEL_OTHER
    assert classify_term("necessary").label == LABEL_OTHER
    assert classify_term("principle").label == LABEL_OTHER
    assert classify_term("overview").label == LABEL_OTHER
    assert classify_term("preventive").label == LABEL_OTHER
    assert classify_term("production").label == LABEL_OTHER
    assert classify_term("protection").label == LABEL_OTHER
    assert classify_term("proposed").label == LABEL_OTHER
    assert classify_term("purpose").label == LABEL_OTHER
    assert classify_term("role").label == LABEL_OTHER
    assert classify_term("session").label == LABEL_OTHER
    assert classify_term("scene").label == LABEL_OTHER
    assert classify_term("stage").label == LABEL_OTHER
    assert classify_term("target").label == LABEL_OTHER
    assert classify_term("text").label == LABEL_OTHER
    assert classify_term("type").label == LABEL_OTHER
    assert classify_term("done").label == LABEL_OTHER
    assert classify_term("trial").label == LABEL_OTHER
    assert classify_term("tree").label == LABEL_OTHER
    assert classify_term("verification").label == LABEL_OTHER
    assert classify_term("whitelist").label == LABEL_OTHER
    assert classify_term("agent").label == LABEL_OTHER
    assert classify_term("apply").label == LABEL_OTHER
    assert classify_term("anchor").label == LABEL_OTHER
    assert classify_term("backend").label == LABEL_OTHER
    assert classify_term("blocker").label == LABEL_OTHER
    assert classify_term("bound").label == LABEL_OTHER
    assert classify_term("brief").label == LABEL_OTHER
    assert classify_term("cache").label == LABEL_OTHER
    assert classify_term("canonical").label == LABEL_OTHER
    assert classify_term("client").label == LABEL_OTHER
    assert classify_term("cleanup").label == LABEL_OTHER
    assert classify_term("close").label == LABEL_OTHER
    assert classify_term("code").label == LABEL_OTHER
    assert classify_term("command").label == LABEL_OTHER
    assert classify_term("community").label == LABEL_OTHER
    assert classify_term("content").label == LABEL_OTHER
    assert classify_term("control").label == LABEL_OTHER
    assert classify_term("copy").label == LABEL_OTHER
    assert classify_term("coupon").label == LABEL_OTHER
    assert classify_term("daily").label == LABEL_OTHER
    assert classify_term("desktop").label == LABEL_OTHER
    assert classify_term("description").label == LABEL_OTHER
    assert classify_term("domain").label == LABEL_OTHER
    assert classify_term("empty").label == LABEL_OTHER
    assert classify_term("entry").label == LABEL_OTHER
    assert classify_term("error").label == LABEL_OTHER
    assert classify_term("field").label == LABEL_OTHER
    assert classify_term("fallback").label == LABEL_OTHER
    assert classify_term("future").label == LABEL_OTHER
    assert classify_term("goal").label == LABEL_OTHER
    assert classify_term("human").label == LABEL_OTHER
    assert classify_term("immediately").label == LABEL_OTHER
    assert classify_term("investigation").label == LABEL_OTHER
    assert classify_term("limit").label == LABEL_OTHER
    assert classify_term("maintainer").label == LABEL_OTHER
    assert classify_term("manage").label == LABEL_OTHER
    assert classify_term("memory").label == LABEL_OTHER
    assert classify_term("mention").label == LABEL_OTHER
    assert classify_term("multiple").label == LABEL_OTHER
    assert classify_term("only").label == LABEL_OTHER
    assert classify_term("operator").label == LABEL_OTHER
    assert classify_term("owner").label == LABEL_OTHER
    assert classify_term("pass").label == LABEL_OTHER
    assert classify_term("point").label == LABEL_OTHER
    assert classify_term("product").label == LABEL_OTHER
    assert classify_term("plane").label == LABEL_OTHER
    assert classify_term("proof").label == LABEL_OTHER
    assert classify_term("quoting").label == LABEL_OTHER
    assert classify_term("quickstart").label == LABEL_OTHER
    assert classify_term("rate").label == LABEL_OTHER
    assert classify_term("reader").label == LABEL_OTHER
    assert classify_term("record").label == LABEL_OTHER
    assert classify_term("reference").label == LABEL_OTHER
    assert classify_term("register").label == LABEL_OTHER
    assert classify_term("residual").label == LABEL_OTHER
    assert classify_term("residue").label == LABEL_OTHER
    assert classify_term("reusable").label == LABEL_OTHER
    assert classify_term("secondary").label == LABEL_OTHER
    assert classify_term("selected").label == LABEL_OTHER
    assert classify_term("selection").label == LABEL_OTHER
    assert classify_term("setup").label == LABEL_OTHER
    assert classify_term("shelve").label == LABEL_OTHER
    assert classify_term("skill").label == LABEL_OTHER
    assert classify_term("software").label == LABEL_OTHER
    assert classify_term("standalone").label == LABEL_OTHER
    assert classify_term("team").label == LABEL_OTHER
    assert classify_term("this").label == LABEL_OTHER
    assert classify_term("ticket").label == LABEL_OTHER
    assert classify_term("topic").label == LABEL_OTHER
    assert classify_term("treat").label == LABEL_OTHER
    assert classify_term("upper").label == LABEL_OTHER
    assert classify_term("validation").label == LABEL_OTHER
    assert classify_term("validate").label == LABEL_OTHER
    assert classify_term("viewer").label == LABEL_OTHER
    assert classify_term("window").label == LABEL_OTHER
    assert classify_term("without").label == LABEL_OTHER
    assert classify_term("would").label == LABEL_OTHER
    assert classify_term("writable").label == LABEL_OTHER
    assert classify_term("static").label == LABEL_OTHER
    assert classify_term("inside").label == LABEL_OTHER
    assert classify_term("external").label == LABEL_OTHER
    assert classify_term("approved").label == LABEL_OTHER
    assert classify_term("official").label == LABEL_OTHER
    assert classify_term("sandbox").label == LABEL_OTHER
    assert classify_term("connector").label == LABEL_OTHER
    assert classify_term("markdown").label == LABEL_OTHER
    assert classify_term("author").label == LABEL_OTHER
    assert classify_term("committer").label == LABEL_OTHER
    assert classify_term("accessible").label == LABEL_OTHER
    assert classify_term("undocumented").label == LABEL_OTHER
    assert classify_term("cookie").label == LABEL_OTHER
    assert classify_term("arbitrary").label == LABEL_OTHER
    assert classify_term("experimental").label == LABEL_OTHER
    assert classify_term("developer").label == LABEL_OTHER
    assert classify_term("aidev").label == LABEL_OTHER
    assert classify_term("agentic").label == LABEL_OTHER
    assert classify_term("dogfood").label == LABEL_OTHER
    assert classify_term("dogfooding").label == LABEL_OTHER
    assert classify_term("reflection").label == LABEL_OTHER
    assert classify_term("afrayde01").label == LABEL_OTHER
    assert classify_term("saiganakato").label == LABEL_OTHER
    assert classify_term("releas").label == LABEL_OTHER
    assert classify_term("custom").label == LABEL_OTHER
    assert classify_term("research").label == LABEL_OTHER
    assert classify_term("format").label == LABEL_OTHER
    assert classify_term("invocation").label == LABEL_OTHER
    assert classify_term("constitution").label == LABEL_OTHER
    assert classify_term("access").label == LABEL_OTHER
    assert classify_term("acronym").label == LABEL_OTHER
    assert classify_term("adoptable").label == LABEL_OTHER
    assert classify_term("analyzer").label == LABEL_OTHER
    assert classify_term("classification").label == LABEL_OTHER
    assert classify_term("classifier").label == LABEL_OTHER
    assert classify_term("extractor").label == LABEL_OTHER
    assert classify_term("handover").label == LABEL_OTHER
    assert classify_term("locale").label == LABEL_OTHER
    assert classify_term("misclassification").label == LABEL_OTHER
    assert classify_term("patching").label == LABEL_OTHER
    assert classify_term("polishing").label == LABEL_OTHER
    assert classify_term("specialist").label == LABEL_OTHER
    assert classify_term("suite").label == LABEL_OTHER
    assert classify_term("unexpected").label == LABEL_OTHER
    assert classify_term("updated").label == LABEL_OTHER
    assert classify_term("runs").label == LABEL_OTHER
    assert classify_term("shelf").label == LABEL_OTHER
    assert classify_term("sink").label == LABEL_OTHER
    assert classify_term("theme").label == LABEL_OTHER
    assert classify_term("tool").label == LABEL_OTHER
    assert classify_term("Bash").label == LABEL_OTHER
    assert classify_term("Cursor").label == LABEL_OTHER
    assert classify_term("PowerShell").label == LABEL_OTHER
    assert classify_term("Pier").label == LABEL_OTHER
    assert classify_term("AIM").label == LABEL_OTHER
    assert classify_term("ADOP").label == LABEL_OTHER
    assert classify_term("Playwright").label == LABEL_OTHER
    assert classify_term("JavaScript").label == LABEL_OTHER
    assert classify_term("Saiga").label == LABEL_OTHER
    assert classify_term("Symphony").label == LABEL_OTHER
    assert classify_term("Vault").label == LABEL_OTHER
    assert classify_term("mypy").label == LABEL_OTHER
    assert classify_term("parse").label == LABEL_OTHER
    assert classify_term("failure").label == LABEL_OTHER
    assert classify_term("hosted").label == LABEL_OTHER
    assert classify_term("hygiene").label == LABEL_OTHER
    assert classify_term("green").label == LABEL_OTHER
    assert classify_term("dirty").label == LABEL_OTHER
    assert classify_term("clean").label == LABEL_OTHER
    assert classify_term("current state").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("live state").label == LABEL_OTHER
    assert classify_term("branch question").label == LABEL_OTHER
    assert classify_term("current checkpoint").label == LABEL_OTHER
    assert classify_term("current surface").label == LABEL_OTHER
    assert classify_term("launch evidence").label == LABEL_OTHER
    assert classify_term("artifact shelf").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("canonical body").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("current route").label == LABEL_OTHER
    assert classify_term("execution lane").label == LABEL_OTHER
    assert classify_term("generated sink").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("operator view").label == LABEL_OTHER
    assert classify_term("proof blocker").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("read surface").label == LABEL_OTHER
    assert classify_term("shelf class").label == LABEL_OTHER
    assert classify_term("support docs").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("current task register").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("task register").label == LABEL_OTHER
    assert classify_term("failing test").label == LABEL_OTHER
    assert classify_term("parse failure").label == LABEL_OTHER
    assert classify_term("repo hygiene").label == LABEL_OTHER
    assert classify_term("base url").label == LABEL_INDUSTRY_TERM
    assert classify_term("accepted route").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("accepted-route").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("carry-forward").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("manager-copy").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("non-current").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("runtime artifact shelf").label == LABEL_FILE_CONFIG_IDENTIFIER
    assert classify_term("punctuation triple").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("self-describing").label == LABEL_INDUSTRY_TERM
    assert classify_term("unstable wording").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("GitHub standard").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("writable-shelf").label == LABEL_COINED_OR_SHORTENED
    assert classify_term("gitleaks").reason == "proper_noun_non_target"
    assert classify_term("dependabot").reason == "proper_noun_non_target"
    assert classify_term("review").label == LABEL_OTHER
    assert classify_term("GitHub").label == LABEL_OTHER
    assert classify_term("OpenAI").label == LABEL_OTHER
    assert classify_term("Python").label == LABEL_OTHER
    assert classify_term("pytest").label == LABEL_OTHER
    assert classify_term("root").label == LABEL_OTHER
    assert classify_term("ordinary").label == LABEL_OTHER
    assert classify_term("noun").label == LABEL_OTHER
    assert classify_term("multiword").label == LABEL_OTHER
    assert classify_term("first-pass").label == LABEL_OTHER


def test_taxonomy_known_term_sets_classify_to_expected_labels() -> None:
    for term in KNOWN_COINED_TERMS:
        assert classify_term(term).label == LABEL_COINED_OR_SHORTENED, term
    for term in KNOWN_INDUSTRY_TERMS:
        assert classify_term(term).label == LABEL_INDUSTRY_TERM, term
    for term in KNOWN_FILE_CONFIG_TERMS:
        assert classify_term(term).label == LABEL_FILE_CONFIG_IDENTIFIER, term
    for term in KNOWN_REPO_DIR_TERMS:
        assert classify_term(term).label == LABEL_FILE_CONFIG_IDENTIFIER, term
    for term in KNOWN_OTHER_MULTIWORD_TERMS:
        assert classify_term(term).label == LABEL_OTHER, term
    for term in PROPER_NOUN_TERMS:
        assert classify_term(term).label == LABEL_OTHER, term
    for term in KNOWN_INDUSTRY_ACRONYMS:
        assert classify_term(term.upper()).label == LABEL_INDUSTRY_TERM, term


def test_taxonomy_sets_are_normalization_unique() -> None:
    groups = {
        "proper_noun_terms": PROPER_NOUN_TERMS,
        "known_industry_terms": KNOWN_INDUSTRY_TERMS,
        "known_file_config_terms": KNOWN_FILE_CONFIG_TERMS,
        "known_repo_dir_terms": KNOWN_REPO_DIR_TERMS,
        "known_coined_terms": KNOWN_COINED_TERMS,
        "known_other_multiword_terms": KNOWN_OTHER_MULTIWORD_TERMS,
        "adoptable_other_multiword_terms": ADOPTABLE_OTHER_MULTIWORD_TERMS,
    }
    for group_name, terms in groups.items():
        normalized_terms: dict[str, list[str]] = {}
        for term in terms:
            normalized_terms.setdefault(normalize_term(term), []).append(term)
        collisions = {
            normalized: originals
            for normalized, originals in normalized_terms.items()
            if len(originals) > 1
        }
        assert collisions == {}, group_name


def test_extract_classified_terms_from_user_example() -> None:
    text = """
    次に進めるなら、優先順位はこれです。
    root clutter を減らす設計見直し
    maintainer-only files を「公開 repo には残すが、ユーザー配布からは外す」方針の導入
    本当に不要な tracked file が後から増えないよう、review ルールを README か CI に固定
    GitHub standard と REPO_CONTENT_CLASSIFICATION.md も確認する
    """
    term_map = extract_classified_term_map(text)

    assert term_map["root clutter"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["maintainer only file"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["tracked file"].label == LABEL_INDUSTRY_TERM
    assert term_map["repo"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["review"].label == LABEL_OTHER
    assert term_map["readme"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["ci"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["github"].label == LABEL_OTHER
    assert term_map["repo content classification.md"].label == LABEL_FILE_CONFIG_IDENTIFIER


def test_extract_classified_terms_handles_slash_command_and_generic_ops() -> None:
    text = "/veil-capture mirror export import root clutter"
    term_map = extract_classified_term_map(text)

    assert term_map["/veil capture"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["mirror"].label == LABEL_OTHER
    assert term_map["export"].label == LABEL_OTHER
    assert term_map["import"].label == LABEL_OTHER
    assert term_map["root clutter"].label == LABEL_COINED_OR_SHORTENED
    assert "veil capture root" not in term_map


def test_extract_classified_terms_keeps_generic_multiword_phrases() -> None:
    text = "current state current issue unstable wording GitHub standard"
    term_map = extract_classified_term_map(text)

    assert term_map["current state"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["current issue"].label == LABEL_OTHER
    assert term_map["unstable wording"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["github standard"].label == LABEL_COINED_OR_SHORTENED
    assert "current" not in term_map
    assert "state" not in term_map


def test_extract_classified_terms_avoids_duplicate_mask_artifact() -> None:
    text = "developer support maintainer/developer support"
    term_map = extract_classified_term_map(text)

    assert "support support" not in term_map


def test_extract_classified_terms_avoids_overeager_generic_phrase_coining() -> None:
    text = "standard file naming packaging policy support"
    term_map = extract_classified_term_map(text)

    assert "standard file" not in term_map
    assert "naming packaging" not in term_map
    assert "packaging policy" not in term_map
    assert "policy support" not in term_map


def test_extract_classified_terms_avoids_generic_hyphenated_phrase_coining() -> None:
    text = "first-pass proper maintainer-only veil-capture Python worktree root ordinary noun multiword"
    term_map = extract_classified_term_map(text)

    assert term_map["first pass"].label == LABEL_OTHER
    assert "first pass proper" not in term_map
    assert term_map["maintainer only"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["veil capture"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["python"].label == LABEL_OTHER
    assert term_map["worktree"].label == LABEL_INDUSTRY_TERM
    assert term_map["root"].label == LABEL_OTHER
    assert term_map["ordinary"].label == LABEL_OTHER
    assert term_map["noun"].label == LABEL_OTHER
    assert term_map["multiword"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_sanitizes_markdown_and_code_noise() -> None:
    text = """
    root clutter review
    ```powershell
    rtk python shared\\runtime\\veil-classify.py --db $HOME\\.veil\\veil.db
    ```
    `README`
    FOO=bar
    """
    term_map = extract_classified_term_map(text)

    assert term_map["root clutter"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["review"].label == LABEL_OTHER
    assert "powershell" not in term_map
    assert "python" not in term_map
    assert "readme" not in term_map
    assert "home" not in term_map


def test_extract_classified_terms_strips_line_reference_noise_and_handoff_terms() -> None:
    text = """
    [index.html (line 190)](/tmp/index.html:190) と [console.spec.js (line 430)](/tmp/console.spec.js:430)
    で workflow parse failure、hosted gate、branch protection、repo hygiene、Playwright、
    runtime endpoint、scope readback、OAuth token、secret、Vault を確認した。
    """
    term_map = extract_classified_term_map(text)

    assert "line" not in term_map
    assert term_map["index.html"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["console.spec.j"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["workflow"].label == LABEL_INDUSTRY_TERM
    assert term_map["parse failure"].label == LABEL_OTHER
    assert term_map["hosted gate"].label == LABEL_INDUSTRY_TERM
    assert term_map["branch protection"].label == LABEL_INDUSTRY_TERM
    assert term_map["repo hygiene"].label == LABEL_OTHER
    assert term_map["playwright"].label == LABEL_OTHER
    assert term_map["runtime"].label == LABEL_INDUSTRY_TERM
    assert term_map["endpoint"].label == LABEL_INDUSTRY_TERM
    assert term_map["scope"].label == LABEL_INDUSTRY_TERM
    assert term_map["readback"].label == LABEL_INDUSTRY_TERM
    assert term_map["oauth"].label == LABEL_INDUSTRY_TERM
    assert term_map["token"].label == LABEL_INDUSTRY_TERM
    assert term_map["secret"].label == LABEL_INDUSTRY_TERM
    assert term_map["vault"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_markdown_governance_status_text() -> None:
    text = """
    [AIM_STATUS.md](/C:/Users/f_tan/project/aim/docs/AIM_STATUS.md) では、live state を
    「first round_2 branch は promote 済み」に統一し、current mainline matches N-297 を
    current branch question から外しました。N-289 / N-297 は「completed first branch の historical
    launch evidence」として扱う形に直し、stale だった caution も「normalize 前」ではなく、
    PowerShell の表示文字化けに関する注意へ差し替えています。あわせて current checkpoint も
    next bounded naturalness branch declaration / status: pending に更新しました。
    [project-current-work.md](/C:/Users/f_tan/project/aim/docs/governance/project-current-work.md) も同様に、
    top の current surface を next bounded naturalness branch declaration pending に合わせ、
    下段の設計部に残っていた current mainline first round_2 block matches N-297 と未解決 branch
    question を削除しました。そこは「historical launch comparison for the completed first branch」に
    置き換えて、今の repo truth が promote 済み mainline であることを一本化しています。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["aim status.md"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["project current work.md"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["live state"].label == LABEL_OTHER
    assert term_map["branch"].label == LABEL_INDUSTRY_TERM
    assert term_map["mainline"].label == LABEL_INDUSTRY_TERM
    assert term_map["normalize"].label == LABEL_INDUSTRY_TERM
    assert term_map["powershell"].label == LABEL_OTHER
    assert term_map["current checkpoint"].label == LABEL_OTHER
    assert term_map["bounded naturalness"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["status"].label == LABEL_OTHER
    assert term_map["pending"].label == LABEL_OTHER
    assert term_map["current surface"].label == LABEL_OTHER
    assert term_map["repo truth"].label == LABEL_COINED_OR_SHORTENED
    assert "/c" not in term_map
    assert "/users/f tan" not in term_map
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_local_exitstack_pattern_text() -> None:
    text = """
    ACI-W3-B1 をさらに 1 pattern 進めました。今回は managed = closing(open(path));
    stack.enter_context(managed) を managed とみなすようにして、[ci_22.py](/C:/Users/f_tan/project/aci/shared/python/detectors/ci_22.py)
    に narrow な認識を追加しました。これは helper ownership transfer ではなく、同一関数内で
    closing(open(path)) を一度ローカル変数に束縛してから ExitStack に登録するだけの local pattern です。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["aci"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["w3 b1"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["pattern"].label == LABEL_OTHER
    assert term_map["managed"].label == LABEL_OTHER
    assert term_map["closing"].label == LABEL_OTHER
    assert term_map["open"].label == LABEL_OTHER
    assert term_map["path"].label == LABEL_OTHER
    assert term_map["stack.enter context"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["ci 22.py"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["narrow"].label == LABEL_OTHER
    assert term_map["helper"].label == LABEL_OTHER
    assert term_map["ownership"].label == LABEL_OTHER
    assert term_map["transfer"].label == LABEL_OTHER
    assert term_map["exitstack"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["local"].label == LABEL_OTHER
    assert "/c" not in term_map
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_ci_completion_evidence_text() -> None:
    text = """
    一番大きかったのは、証明不足と CI 契約の崩れだった点でした。完成条件を固定して、
    workflow parse failure、hosted black-box、HTML 導線、repo hygiene の証拠を順番に回収しました。
    GitHub 上で job が走って green になるまで見届けないと完了とは言えませんでした。
    dirty worktree の中で続けると論点が広がるので、clean worktree を切って CI 修正だけ隔離しました。
    結果として、mypy の import 契約崩れと pre-commit --all-files のスコープ不整合を閉じられました。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["ci"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["workflow"].label == LABEL_INDUSTRY_TERM
    assert term_map["parse failure"].label == LABEL_OTHER
    assert term_map["hosted"].label == LABEL_OTHER
    assert term_map["black box"].label == LABEL_OTHER
    assert term_map["html"].label == LABEL_INDUSTRY_TERM
    assert term_map["repo hygiene"].label == LABEL_OTHER
    assert term_map["repo"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["github"].label == LABEL_OTHER
    assert term_map["green"].label == LABEL_OTHER
    assert term_map["dirty"].label == LABEL_OTHER
    assert term_map["worktree"].label == LABEL_INDUSTRY_TERM
    assert term_map["clean"].label == LABEL_OTHER
    assert term_map["mypy"].label == LABEL_OTHER
    assert term_map["import"].label == LABEL_OTHER
    assert term_map["pre commit"].label == LABEL_OTHER
    assert term_map["all file"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_public_audit_excerpt() -> None:
    text = """
    対象は GitHub 上の maruwork/github-optimization、current master = 56e5981c05c1413673d58ea6adfba7de824a686c、
    latest release/tag = v1.2.10 です。README / SHELF_VERSION / CHANGELOG / release tag は 1.2.10 で揃っています。
    CI と CodeQL も 56e5981 で success でした。secret_scanning / secret_scanning_push_protection /
    dependabot_security_updates は disabled です。distribution bootstrap 例が古い version を示している。
    remote bootstrap 例は v1.1.0 を tag/push する例のままです。validate-regulation-index.ps1 PASS、
    check-gitignore-consistency.ps1 PASS。制限: この side 環境では gitleaks が PATH に無く、直接 gitleaks detect は
    実行できませんでした。GitHub CI 側では gitleaks install 後の regression が成功しています。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["master"].label == LABEL_INDUSTRY_TERM
    assert term_map["latest"].label == LABEL_OTHER
    assert term_map["release"].label == LABEL_INDUSTRY_TERM
    assert term_map["success"].label == LABEL_OTHER
    assert term_map["disabled"].label == LABEL_OTHER
    assert term_map["distribution"].label == LABEL_INDUSTRY_TERM
    assert term_map["bootstrap"].label == LABEL_INDUSTRY_TERM
    assert term_map["remote"].label == LABEL_OTHER
    assert term_map["detect"].label == LABEL_OTHER
    assert term_map["install"].label == LABEL_OTHER
    assert term_map["regression"].label == LABEL_INDUSTRY_TERM
    assert term_map["gitleak"].reason == "proper_noun_non_target"
    assert term_map["56e5981"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["56e5981c05c1413673d58ea6adfba7de824a686c"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_filtered_session_excerpt() -> None:
    text = """
    This skill would immediately apply sync guidance in the shell window.
    Checkout reset guardrail coverage.
    Selected setup command memory validation viewer wording.
    """
    term_map = extract_classified_term_map(text)

    assert term_map["this"].label == LABEL_OTHER
    assert term_map["skill"].label == LABEL_OTHER
    assert term_map["would"].label == LABEL_OTHER
    assert term_map["immediately"].label == LABEL_OTHER
    assert term_map["apply"].label == LABEL_OTHER
    assert term_map["sync"].label == LABEL_INDUSTRY_TERM
    assert term_map["shell"].label == LABEL_INDUSTRY_TERM
    assert term_map["window"].label == LABEL_OTHER
    assert term_map["checkout"].label == LABEL_INDUSTRY_TERM
    assert term_map["reset"].label == LABEL_INDUSTRY_TERM
    assert term_map["guardrail"].label == LABEL_INDUSTRY_TERM
    assert term_map["coverage"].label == LABEL_INDUSTRY_TERM
    assert term_map["selected"].label == LABEL_OTHER
    assert term_map["setup"].label == LABEL_OTHER
    assert term_map["command"].label == LABEL_OTHER
    assert term_map["memory"].label == LABEL_OTHER
    assert term_map["validation"].label == LABEL_OTHER
    assert term_map["viewer"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_session_long_tail_misc_words() -> None:
    text = """
    Inside the external sandbox connector, the markdown form stays official.
    Aidev agentic dogfooding reflection remains ordinary here, and afrayde01 with saiganakato
    should stay non-target. Author committer cookie releas override publish history are also ordinary.
    """
    term_map = extract_classified_term_map(text)

    assert term_map["inside"].label == LABEL_OTHER
    assert term_map["external"].label == LABEL_OTHER
    assert term_map["sandbox"].label == LABEL_OTHER
    assert term_map["connector"].label == LABEL_OTHER
    assert term_map["markdown"].label == LABEL_OTHER
    assert term_map["official"].label == LABEL_OTHER
    assert term_map["aidev"].label == LABEL_OTHER
    assert term_map["agentic"].label == LABEL_OTHER
    assert term_map["dogfooding"].label == LABEL_OTHER
    assert term_map["reflection"].label == LABEL_OTHER
    assert term_map["afrayde01"].label == LABEL_OTHER
    assert term_map["saiganakato"].label == LABEL_OTHER
    assert term_map["author"].label == LABEL_OTHER
    assert term_map["committer"].label == LABEL_OTHER
    assert term_map["cookie"].label == LABEL_OTHER
    assert term_map["releas"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_final_session_residue_words() -> None:
    text = """
    Custom research format repeat invocation and constitution should also remain ordinary.
    """
    term_map = extract_classified_term_map(text)

    assert term_map["custom"].label == LABEL_OTHER
    assert term_map["research"].label == LABEL_OTHER
    assert term_map["format"].label == LABEL_OTHER
    assert term_map["repeat"].label == LABEL_OTHER
    assert term_map["invocation"].label == LABEL_OTHER
    assert term_map["constitution"].label == LABEL_OTHER
    assert term_map["should"].label == LABEL_OTHER
    assert term_map["also"].label == LABEL_OTHER
    assert term_map["remain"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_final_veil_related_pair() -> None:
    text = "validate static"
    term_map = extract_classified_term_map(text)

    assert term_map["validate"].label == LABEL_OTHER
    assert term_map["static"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_veil_session_long_tail_batch() -> None:
    terms = [
        "access", "acronym", "added", "adding", "adopt", "adoptable", "against", "already", "analyze",
        "analyzer", "applying", "around", "assistant", "attachment", "awkward", "back", "before", "blow",
        "both", "broad", "broader", "came", "candidate1", "cas", "chat", "checked", "checking",
        "classification", "classified", "classifier", "classify", "cleanly", "closer", "coined", "composed",
        "concrete", "confirm", "consistent", "corpus", "currently", "dashboard", "deciding", "decoded",
        "denied", "detector", "didn", "directory", "does", "doing", "drop", "dropped", "e5981", "either",
        "embedded", "encoding", "entrypoint", "exactly", "expectation", "explain", "explicit", "extract",
        "extracting", "extraction", "extractor", "fake", "fall", "fenced", "focused", "found", "fragment",
        "handling", "handover", "healthy", "industry", "inline", "interesting", "internally", "join", "kind",
        "know", "landing", "left", "like", "likely", "locale", "lock", "logic", "look", "looking", "making",
        "meaningful", "mechanical", "misclassification", "more", "most", "mostly", "noise", "noisy", "nothing",
        "observed", "oriented", "outside", "part", "pasted", "patch", "patching", "phrase", "pick", "polishing",
        "present", "protected", "pulling", "rather", "real", "registered", "related", "remained", "remaining",
        "resolve", "right", "ripple", "running", "safer", "sanitiz", "sanitization", "scoped", "scoring",
        "segment", "shed", "single", "skeleton", "small", "smallest", "specialist", "stepping", "store",
        "suite", "surfaced", "system", "than", "there", "through", "together", "tracing", "true", "turn",
        "tweak", "unexpected", "unlink", "untouched", "updated", "value", "warned", "whether", "which", "while",
        "word",
    ]
    assert all(classify_term(term).label == LABEL_OTHER for term in terms)


def test_extract_classified_terms_handles_attachment_repo_language_and_skips_single_letter_noise() -> None:
    text = """
    Pier では index が current control plane、shared は canonical body、
    generated sink、docs / governance / generated / template / packet / spec は shelf class として読む。
    validator / hook / healthcheck / audit / execution / test / schema / artifact / drift を確認し、
    task register、support docs、artifact shelf、execution lane、proof blocker、operator view を見る。
    A X C は見出しノイズであり、単独語としては拾わない。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["pier"].label == LABEL_OTHER
    assert term_map["index"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["control plane"].label == LABEL_INDUSTRY_TERM
    assert term_map["canonical body"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["docs"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["governance"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["generated"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["template"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["packet"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["spec"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["shelf class"].label == LABEL_OTHER
    assert term_map["validator"].label == LABEL_INDUSTRY_TERM
    assert term_map["hook"].label == LABEL_INDUSTRY_TERM
    assert term_map["healthcheck"].label == LABEL_INDUSTRY_TERM
    assert term_map["audit"].label == LABEL_INDUSTRY_TERM
    assert term_map["execution"].label == LABEL_INDUSTRY_TERM
    assert term_map["test"].label == LABEL_INDUSTRY_TERM
    assert term_map["schema"].label == LABEL_INDUSTRY_TERM
    assert term_map["artifact"].label == LABEL_INDUSTRY_TERM
    assert term_map["drift"].label == LABEL_INDUSTRY_TERM
    assert term_map["canonical body"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["generated sink"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["task register"].label == LABEL_OTHER
    assert term_map["support docs"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["artifact shelf"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["execution lane"].label == LABEL_OTHER
    assert term_map["proof blocker"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["operator view"].label == LABEL_OTHER
    assert "a" not in term_map
    assert "x" not in term_map
    assert "c" not in term_map
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_remaining_attachment_workflow_words() -> None:
    text = """
    keep baseline readiness matrix framework manager process board glossary profile asset summary
    snapshot source output write known still closed rename worker guide material
    """
    term_map = extract_classified_term_map(text)

    assert term_map["keep"].label == LABEL_OTHER
    assert term_map["baseline"].label == LABEL_OTHER
    assert term_map["readiness"].label == LABEL_OTHER
    assert term_map["matrix"].label == LABEL_OTHER
    assert term_map["framework"].label == LABEL_OTHER
    assert term_map["manager"].label == LABEL_OTHER
    assert term_map["process"].label == LABEL_OTHER
    assert term_map["board"].label == LABEL_OTHER
    assert term_map["glossary"].label == LABEL_OTHER
    assert term_map["profile"].label == LABEL_OTHER
    assert term_map["asset"].label == LABEL_OTHER
    assert term_map["summary"].label == LABEL_OTHER
    assert term_map["snapshot"].label == LABEL_OTHER
    assert term_map["source"].label == LABEL_OTHER
    assert term_map["output"].label == LABEL_OTHER


def test_extract_classified_terms_handles_runtime_artifact_shelf_phrase() -> None:
    text = "shared/runtime は runtime artifact shelf であり canonical body ではない"
    term_map = extract_classified_term_map(text)

    assert term_map["runtime artifact shelf"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["canonical body"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_remaining_attachment_unknown_heads() -> None:
    text = """
    trigger tree disposition proposed seed pycache symphony cursor scan trial scene backlog
    setting synthetic evaluation whitelist manifest management forbidden overview kernel adapter
    protocol verify reviewer auditor engineer bash mtime yaml untracked verification
    """
    term_map = extract_classified_term_map(text)

    assert term_map["trigger"].label == LABEL_INDUSTRY_TERM
    assert term_map["tree"].label == LABEL_OTHER
    assert term_map["disposition"].label == LABEL_OTHER
    assert term_map["proposed"].label == LABEL_OTHER
    assert term_map["seed"].label == LABEL_INDUSTRY_TERM
    assert term_map["pycache"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["symphony"].label == LABEL_OTHER
    assert term_map["cursor"].label == LABEL_OTHER
    assert term_map["scan"].label == LABEL_INDUSTRY_TERM
    assert term_map["trial"].label == LABEL_OTHER
    assert term_map["scene"].label == LABEL_OTHER
    assert term_map["backlog"].label == LABEL_INDUSTRY_TERM
    assert term_map["setting"].label == LABEL_OTHER
    assert term_map["synthetic"].label == LABEL_OTHER
    assert term_map["evaluation"].label == LABEL_OTHER
    assert term_map["whitelist"].label == LABEL_OTHER
    assert term_map["manifest"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["management"].label == LABEL_OTHER
    assert term_map["forbidden"].label == LABEL_OTHER
    assert term_map["overview"].label == LABEL_OTHER
    assert term_map["kernel"].label == LABEL_INDUSTRY_TERM
    assert term_map["adapter"].label == LABEL_INDUSTRY_TERM
    assert term_map["protocol"].label == LABEL_INDUSTRY_TERM
    assert term_map["verify"].label == LABEL_OTHER
    assert term_map["reviewer"].label == LABEL_OTHER
    assert term_map["auditor"].label == LABEL_OTHER
    assert term_map["engineer"].label == LABEL_OTHER
    assert term_map["bash"].label == LABEL_OTHER
    assert term_map["mtime"].label == LABEL_INDUSTRY_TERM
    assert term_map["yaml"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["untracked"].label == LABEL_INDUSTRY_TERM
    assert term_map["verification"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_second_wave_attachment_unknown_heads() -> None:
    text = """
    principle authority broken link discovery fixture bundle role reroute aggregate condition
    quality stage reading order delegation expected capture visible rulebook companion inventory
    label defense living autonomous overall warn missing batch creation text node saiga
    """
    term_map = extract_classified_term_map(text)

    assert term_map["principle"].label == LABEL_OTHER
    assert term_map["authority"].label == LABEL_OTHER
    assert term_map["broken"].label == LABEL_OTHER
    assert term_map["link"].label == LABEL_OTHER
    assert term_map["discovery"].label == LABEL_OTHER
    assert term_map["fixture"].label == LABEL_OTHER
    assert term_map["bundle"].label == LABEL_OTHER
    assert term_map["role"].label == LABEL_OTHER
    assert term_map["reroute"].label == LABEL_OTHER
    assert term_map["aggregate"].label == LABEL_OTHER
    assert term_map["condition"].label == LABEL_OTHER
    assert term_map["quality"].label == LABEL_OTHER
    assert term_map["stage"].label == LABEL_OTHER
    assert term_map["reading"].label == LABEL_OTHER
    assert term_map["order"].label == LABEL_OTHER
    assert term_map["delegation"].label == LABEL_OTHER
    assert term_map["expected"].label == LABEL_OTHER
    assert term_map["capture"].label == LABEL_OTHER
    assert term_map["visible"].label == LABEL_OTHER
    assert term_map["rulebook"].label == LABEL_OTHER
    assert term_map["companion"].label == LABEL_OTHER
    assert term_map["inventory"].label == LABEL_OTHER
    assert term_map["label"].label == LABEL_OTHER
    assert term_map["defense"].label == LABEL_OTHER
    assert term_map["living"].label == LABEL_OTHER
    assert term_map["autonomous"].label == LABEL_OTHER
    assert term_map["overall"].label == LABEL_OTHER
    assert term_map["warn"].label == LABEL_OTHER
    assert term_map["missing"].label == LABEL_OTHER
    assert term_map["batch"].label == LABEL_OTHER
    assert term_map["creation"].label == LABEL_OTHER
    assert term_map["text"].label == LABEL_OTHER
    assert term_map["node"].label == LABEL_OTHER
    assert term_map["saiga"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_third_wave_attachment_unknown_heads() -> None:
    text = """
    assert coupling guided breakdown done date finding commit detail target script filesystem
    generator semantic namespace linter message push hold session subagent coordinator writer
    """
    term_map = extract_classified_term_map(text)

    assert term_map["assert"].label == LABEL_INDUSTRY_TERM
    assert term_map["coupling"].label == LABEL_INDUSTRY_TERM
    assert term_map["guided"].label == LABEL_OTHER
    assert term_map["breakdown"].label == LABEL_OTHER
    assert term_map["done"].label == LABEL_OTHER
    assert term_map["date"].label == LABEL_OTHER
    assert term_map["finding"].label == LABEL_OTHER
    assert term_map["commit"].label == LABEL_INDUSTRY_TERM
    assert term_map["detail"].label == LABEL_OTHER
    assert term_map["target"].label == LABEL_OTHER
    assert term_map["script"].label == LABEL_OTHER
    assert term_map["filesystem"].label == LABEL_INDUSTRY_TERM
    assert term_map["generator"].label == LABEL_INDUSTRY_TERM
    assert term_map["semantic"].label == LABEL_OTHER
    assert term_map["namespace"].label == LABEL_INDUSTRY_TERM
    assert term_map["linter"].label == LABEL_INDUSTRY_TERM
    assert term_map["message"].label == LABEL_OTHER
    assert term_map["push"].label == LABEL_INDUSTRY_TERM
    assert term_map["hold"].label == LABEL_OTHER
    assert term_map["session"].label == LABEL_OTHER
    assert term_map["subagent"].label == LABEL_INDUSTRY_TERM
    assert term_map["coordinator"].label == LABEL_INDUSTRY_TERM
    assert term_map["writer"].label == LABEL_INDUSTRY_TERM
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_fourth_wave_attachment_unknown_heads() -> None:
    text = """
    necessary mojibake loop runner instrumentation phase hardening compliance dual evaluator
    step4 context injection expiry signal promotion stub purpose placeholder criteria silent
    input escalation result final acceptance architecture database philosophy marker integrity
    protection addendum experiment production sqlite copilot anthropic aider
    """
    term_map = extract_classified_term_map(text)

    assert term_map["necessary"].label == LABEL_OTHER
    assert term_map["mojibake"].label == LABEL_OTHER
    assert term_map["loop"].label == LABEL_OTHER
    assert term_map["runner"].label == LABEL_OTHER
    assert term_map["instrumentation"].label == LABEL_INDUSTRY_TERM
    assert term_map["phase"].label == LABEL_OTHER
    assert term_map["hardening"].label == LABEL_OTHER
    assert term_map["compliance"].label == LABEL_OTHER
    assert term_map["dual"].label == LABEL_OTHER
    assert term_map["evaluator"].label == LABEL_OTHER
    assert term_map["step4"].label == LABEL_OTHER
    assert term_map["context"].label == LABEL_OTHER
    assert term_map["injection"].label == LABEL_OTHER
    assert term_map["expiry"].label == LABEL_OTHER
    assert term_map["signal"].label == LABEL_OTHER
    assert term_map["promotion"].label == LABEL_OTHER
    assert term_map["stub"].label == LABEL_OTHER
    assert term_map["purpose"].label == LABEL_OTHER
    assert term_map["placeholder"].label == LABEL_OTHER
    assert term_map["criteria"].label == LABEL_OTHER
    assert term_map["silent"].label == LABEL_OTHER
    assert term_map["input"].label == LABEL_OTHER
    assert term_map["escalation"].label == LABEL_OTHER
    assert term_map["result"].label == LABEL_OTHER
    assert term_map["final"].label == LABEL_OTHER
    assert term_map["acceptance"].label == LABEL_OTHER
    assert term_map["architecture"].label == LABEL_OTHER
    assert term_map["database"].label == LABEL_INDUSTRY_TERM
    assert term_map["philosophy"].label == LABEL_OTHER
    assert term_map["marker"].label == LABEL_OTHER
    assert term_map["integrity"].label == LABEL_OTHER
    assert term_map["protection"].label == LABEL_OTHER
    assert term_map["addendum"].label == LABEL_OTHER
    assert term_map["experiment"].label == LABEL_OTHER
    assert term_map["production"].label == LABEL_OTHER
    assert term_map["sqlite"].label == LABEL_OTHER
    assert term_map["copilot"].label == LABEL_OTHER
    assert term_map["anthropic"].label == LABEL_OTHER
    assert term_map["aider"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_fifth_wave_attachment_unknown_heads() -> None:
    text = """
    dual shortcut coupled cogitated coding mismatch creating cannot directly wrote edit confirmed
    thematic fragmentation partial unresolved critical safety hint crossref expanded counted resolved absence
    """
    term_map = extract_classified_term_map(text)

    assert term_map["dual"].label == LABEL_OTHER
    assert term_map["shortcut"].label == LABEL_OTHER
    assert term_map["coupled"].label == LABEL_OTHER
    assert term_map["cogitated"].label == LABEL_OTHER
    assert term_map["coding"].label == LABEL_OTHER
    assert term_map["mismatch"].label == LABEL_OTHER
    assert term_map["creating"].label == LABEL_OTHER
    assert term_map["cannot"].label == LABEL_OTHER
    assert term_map["directly"].label == LABEL_OTHER
    assert term_map["wrote"].label == LABEL_OTHER
    assert term_map["edit"].label == LABEL_OTHER
    assert term_map["confirmed"].label == LABEL_OTHER
    assert term_map["thematic"].label == LABEL_OTHER
    assert term_map["fragmentation"].label == LABEL_OTHER
    assert term_map["partial"].label == LABEL_OTHER
    assert term_map["unresolved"].label == LABEL_OTHER
    assert term_map["critical"].label == LABEL_OTHER
    assert term_map["safety"].label == LABEL_OTHER
    assert term_map["hint"].label == LABEL_OTHER
    assert term_map["crossref"].label == LABEL_OTHER
    assert term_map["expanded"].label == LABEL_OTHER
    assert term_map["counted"].label == LABEL_OTHER
    assert term_map["resolved"].label == LABEL_OTHER
    assert term_map["absence"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_sixth_wave_attachment_unknown_heads() -> None:
    text = """
    fork optional short carried side conversation payload localhost server private practical guidance
    recording public name filename stable sweep declared item couple recorded platform license cost
    credential compatibility diagnosis filter reason candidate basetemp reachability category preventive
    """
    term_map = extract_classified_term_map(text)

    assert term_map["fork"].label == LABEL_OTHER
    assert term_map["optional"].label == LABEL_OTHER
    assert term_map["short"].label == LABEL_OTHER
    assert term_map["carried"].label == LABEL_OTHER
    assert term_map["side"].label == LABEL_OTHER
    assert term_map["conversation"].label == LABEL_OTHER
    assert term_map["payload"].label == LABEL_OTHER
    assert term_map["localhost"].label == LABEL_OTHER
    assert term_map["server"].label == LABEL_OTHER
    assert term_map["private"].label == LABEL_OTHER
    assert term_map["practical"].label == LABEL_OTHER
    assert term_map["guidance"].label == LABEL_OTHER
    assert term_map["recording"].label == LABEL_OTHER
    assert term_map["public"].label == LABEL_OTHER
    assert term_map["name"].label == LABEL_OTHER
    assert term_map["filename"].label == LABEL_OTHER
    assert term_map["stable"].label == LABEL_OTHER
    assert term_map["sweep"].label == LABEL_OTHER
    assert term_map["declared"].label == LABEL_OTHER
    assert term_map["item"].label == LABEL_OTHER
    assert term_map["couple"].label == LABEL_OTHER
    assert term_map["recorded"].label == LABEL_OTHER
    assert term_map["platform"].label == LABEL_OTHER
    assert term_map["license"].label == LABEL_OTHER
    assert term_map["cost"].label == LABEL_OTHER
    assert term_map["category"].label == LABEL_OTHER
    assert term_map["credential"].label == LABEL_OTHER
    assert term_map["compatibility"].label == LABEL_OTHER
    assert term_map["diagnosis"].label == LABEL_OTHER
    assert term_map["filter"].label == LABEL_OTHER
    assert term_map["preventive"].label == LABEL_OTHER
    assert term_map["reason"].label == LABEL_OTHER
    assert term_map["candidate"].label == LABEL_OTHER
    assert term_map["basetemp"].label == LABEL_OTHER
    assert term_map["reachability"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_verification_report_terms() -> None:
    text = """
    検証は python shared/python/adop_cli.py --version、python -m py_compile shared/python/adop_cli.py、
    pytest の targeted 2件 test_init_fallback_overlay_still_matches_contract
    test_scan_record_writes_canonical_coupling_note を通しています。pytest は .pytest_cache
    への書き込み拒否 warning が1件出ていますが、実行自体は成功です。GitHub CI の再実行までは
    このターンではしていません。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["python"].label == LABEL_OTHER
    assert term_map["shared/python/adop cli.py"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["version"].label == LABEL_OTHER
    assert term_map["pytest"].label == LABEL_OTHER
    assert term_map["targeted"].label == LABEL_OTHER
    assert term_map["test init fallback overlay still match contract"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["test scan record write canonical coupling note"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["pytest cache"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["warning"].label == LABEL_OTHER
    assert term_map["github"].label == LABEL_OTHER
    assert term_map["ci"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_export_html_command_flags() -> None:
    text = """
    rtk python shared/tools/veil-db.py export-html --db $HOME/.veil/veil.db
    --html-path workspace/veil.html --json を回して確認した。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["shared/tools/veil db.py"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["export html"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["html path"].label == LABEL_FILE_CONFIG_IDENTIFIER


def test_extract_classified_terms_handles_hyphenated_technical_phrases() -> None:
    text = """
    owner と read-only 監査役の区別を固定し、append-only の運用原則と
    machine-readable な landing_target を要求する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["read only"].label == LABEL_INDUSTRY_TERM
    assert term_map["append only"].label == LABEL_INDUSTRY_TERM
    assert term_map["machine readable"].label == LABEL_INDUSTRY_TERM
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_schema_and_subcommand_terms() -> None:
    text = """
    candidate-intake-note へ属性を記録し、quick-close-trial では既定文を避ける。
    landing_target と writeback_target は machine-readable に固定し、
    guided path と trial packet の契約も確認する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["candidate intake note"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["guided path"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["quick close trial"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["landing target"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["trial packet"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["writeback target"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["machine readable"].label == LABEL_INDUSTRY_TERM
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_schema_field_terms() -> None:
    text = """
    decision owner と project profile を確認し、compatibility diagnosis、
    filter status、filter reason、judgment reason、next action、preventive action を記録する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["decision owner"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["project profile"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["compatibility diagnosis"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["filter status"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["filter reason"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["judgment reason"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["next action"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["preventive action"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_use_case_and_system_dev_terms() -> None:
    text = """
    1 use-case に 1 本の採用レーンを回し、system-dev の棚配置も見直す。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["use case"].label == LABEL_INDUSTRY_TERM
    assert term_map["system dev"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_data_attribute_and_event_terms() -> None:
    text = """
    #dashboard-common-scope-summary を確認し、data-runtime-surface-id、
    data-environment-mode、data-selected-environment、data-selected-project-scope、data-selected-tenant-scope、
    data-selected-environment-scope を同期する。最後に pier:runtime-scope-readback-updated を dispatch する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["dashboard common scope summary"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data runtime surface id"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data environment mode"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data selected environment"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data selected project scope"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data selected tenant scope"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data selected environment scope"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["runtime scope readback updated"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_dashboard_specific_data_attributes() -> None:
    text = """
    data-dashboard-selected-project-scope、data-dashboard-selected-tenant-scope、
    data-dashboard-selected-environment-scope、data-dashboard-endpoint-mode、
    data-dashboard-selected-environment を確認する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["data dashboard selected project scope"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data dashboard selected tenant scope"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data dashboard selected environment scope"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data dashboard endpoint mode"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["data dashboard selected environment"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_machine_readable_flow_labels() -> None:
    text = """
    preset:index-local-composed-sample の場合は、trial-result and judgment-report を使う。
    quick-compare と quick-trial では declared-vs-observed drift も確認する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["index local composed sample"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["trial result"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["judgment report"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["quick compare"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["quick trial"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["declared vs observed"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_internal_visibility_and_start_trial_labels() -> None:
    text = """
    判断自体は owner-only なので未確定のまま維持しつつ、
    dev-only / 内部向け棚を見直す。quick-trial / start-trial で入力を固定する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["owner only"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["dev only"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["quick trial"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["start trial"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_workspace_temp_names_and_punctuation_label() -> None:
    text = """
    adop-pytest と adop-pytest-cache を使い、
    adop-pytest-base2 で検証した。punctuation-triple closure だった。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["adop pytest"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["adop pytest cache"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["adop pytest base2"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["punctuation triple"].label == LABEL_COINED_OR_SHORTENED
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_internal_shorthand_labels() -> None:
    text = """
    T-04(writable-shelf) と O6 carry-forward は未解決で、
    governance 保護には manager-copy が必要。Theme 2 は parked non-current 扱い。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["writable shelf"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["carry forward"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["manager copy"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["non current"].label == LABEL_COINED_OR_SHORTENED
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_self_describing_phrase() -> None:
    text = "shared/ 自体を self-describing に作り直すこと"
    term_map = extract_classified_term_map(text)

    assert term_map["self describing"].label == LABEL_INDUSTRY_TERM
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_fail_close_and_project_labels() -> None:
    text = """
    lint を fail-close に寄せ、project-local settings と project-oriented templates
    の棚ラベルも整理する。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["fail close"].label == LABEL_INDUSTRY_TERM
    assert term_map["project local"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["project oriented"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_extract_classified_terms_handles_current_task_register_label() -> None:
    text = """
    shared/docs/tasks/ の current 面は current-task-register と execution を置く。
    """
    term_map = extract_classified_term_map(text)

    assert term_map["current task register"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["execution"].label == LABEL_INDUSTRY_TERM
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_attachment_long_tail_fixture_has_no_unknown_terms() -> None:
    term_map = extract_classified_term_map(ATTACHMENT_LONG_TAIL_FIXTURE_PATH.read_text(encoding="utf-8"))

    assert term_map["database"].label == LABEL_INDUSTRY_TERM
    assert term_map["trigger"].label == LABEL_INDUSTRY_TERM
    assert term_map["indexcurrent"].label == LABEL_OTHER
    assert term_map["mojibake"].label == LABEL_OTHER
    assert term_map["coordinator"].label == LABEL_INDUSTRY_TERM
    assert term_map["writeback"].label == LABEL_INDUSTRY_TERM
    assert term_map["instrumentation"].label == LABEL_INDUSTRY_TERM
    assert term_map["runner"].label == LABEL_OTHER
    assert term_map["subagent"].label == LABEL_INDUSTRY_TERM
    assert term_map["dual"].label == LABEL_OTHER
    assert term_map["payload"].label == LABEL_OTHER
    assert term_map["localhost"].label == LABEL_OTHER
    assert term_map["platform"].label == LABEL_OTHER
    assert term_map["credential"].label == LABEL_OTHER
    assert term_map["compatibility"].label == LABEL_OTHER
    assert term_map["preventive"].label == LABEL_OTHER
    assert term_map["reachability"].label == LABEL_OTHER
    assert term_map["basetemp"].label == LABEL_OTHER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_python_and_js_capture_classification_stay_in_lockstep() -> None:
    terms = [
        "database",
        "instrumentation",
        "writeback",
        "root clutter",
        "maintainer-only files",
        "/veil-capture",
        "README",
        "CI",
        "SE",
        "adop-pytest",
        "adop-pytest-base2",
        "adop-pytest-cache",
        "API",
        "JSON",
        "candidate intake note",
        "decision owner",
        "project profile",
        "project local",
        "project oriented",
        "compatibility diagnosis",
        "dashboard common scope summary",
        "data dashboard endpoint mode",
        "data dashboard selected environment",
        "data dashboard selected environment scope",
        "data dashboard selected project scope",
        "data dashboard selected tenant scope",
        "data runtime surface id",
        "data environment mode",
        "data selected environment",
        "data selected project scope",
        "data selected tenant scope",
        "data selected environment scope",
        "judgment reason",
        "next action",
        "preventive action",
        "guided path",
        "index-local-composed-sample",
        "use case",
        "GitHub",
        "AI",
        "PROJECT",
        "FAIL",
        "BLOCKING",
        "payload",
        "localhost",
        "platform",
        "compatibility",
        "fail close",
        "preventive",
        "branch protection",
        "hosted gate",
        "repo hygiene",
        "runtime scope readback updated",
        "carry-forward",
        "declared-vs-observed",
        "indexcurrent",
        "judgment-report",
        "maintainer-only",
        "manager-copy",
        "mojibake",
        "non-current",
        "punctuation-triple",
        "proof-blocker",
        "quick-compare",
        "quick-trial",
        "self-describing",
        "subagent",
        "start-trial",
        "system dev",
        "trial-result",
        "trial packet",
        "writable-shelf",
        "worktree",
    ]
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in (classify_term(term) for term in terms)
    ]
    js_results = _js_classify_terms(terms)

    assert js_results == py_results


def test_python_and_js_taxonomy_known_term_sets_stay_in_lockstep() -> None:
    terms = (
        sorted(KNOWN_COINED_TERMS)
        + sorted(KNOWN_INDUSTRY_TERMS)
        + [term.upper() for term in sorted(KNOWN_INDUSTRY_ACRONYMS)]
        + sorted(KNOWN_FILE_CONFIG_TERMS)
        + sorted(KNOWN_REPO_DIR_TERMS)
        + sorted(KNOWN_OTHER_MULTIWORD_TERMS)
        + sorted(PROPER_NOUN_TERMS)
    )
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in (classify_term(term) for term in terms)
    ]
    js_results = _js_classify_terms(terms)

    assert js_results == py_results


def test_is_adoptable_classified_term_requires_signal() -> None:
    text = "\n".join(
        [
            "root clutter root clutter",
            "workflow workflow",
            "repo hygiene repo hygiene",
            "current issue current issue current issue",
            "README README",
            "stable stable",
            "public public",
        ]
    )
    term_map = extract_classified_term_map(text)

    assert is_adoptable_classified_term(term_map["root clutter"]) is True
    assert is_adoptable_classified_term(term_map["workflow"]) is False
    assert is_adoptable_classified_term(term_map["repo hygiene"]) is True
    assert is_adoptable_classified_term(term_map["current issue"]) is False
    assert is_adoptable_classified_term(term_map["readme"]) is False
    assert is_adoptable_classified_term(term_map["stable"]) is False
    assert is_adoptable_classified_term(term_map["public"]) is False


def test_extract_adoptable_terms_filters_out_non_candidates() -> None:
    text = "\n".join(
        [
            "root clutter root clutter",
            "workflow workflow workflow",
            "repo hygiene repo hygiene",
            "current issue current issue current issue",
            "README README README",
            "stable stable stable",
            "public public public",
        ]
    )
    results = extract_adoptable_terms(text)
    normalized = [item.normalized for item in results]

    assert normalized == ["root clutter", "repo hygiene"]


def test_extract_adoptable_terms_excludes_repeated_multiword_industry_phrases() -> None:
    text = "\n".join(
        [
            "base url base url base url",
            "control plane control plane",
            "README README README",
            "review review review",
        ]
    )
    results = extract_adoptable_terms(text, limit=10)
    normalized = [item.normalized for item in results]

    assert normalized == []


def test_attachment_candidate_fixture_excludes_industry_heavy_terms() -> None:
    text = ATTACHMENT_CANDIDATES_FIXTURE_PATH.read_text(encoding="utf-8")
    results = extract_adoptable_terms(text)
    normalized = [item.normalized for item in results]

    assert normalized == []


def test_python_and_js_capture_candidates_stay_in_lockstep() -> None:
    text = "\n".join(
        [
            "root clutter root clutter",
            "workflow workflow workflow",
            "repo hygiene repo hygiene",
            "README README README",
            "stable stable stable",
            "public public public",
        ]
    )
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_adoptable_terms(text)
    ]
    js_results = _js_extract_capture_candidates(text)

    assert js_results == py_results


def test_python_and_js_candidate_gate_excludes_non_adoptable_other_phrase() -> None:
    text = "\n".join(
        [
            "current issue current issue current issue",
            "repo hygiene repo hygiene",
        ]
    )
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_adoptable_terms(text)
    ]
    js_results = _js_extract_capture_candidates(text)

    assert py_results == [
        {
            "term": "repo hygiene",
            "normalized": "repo hygiene",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        }
    ]
    assert js_results == py_results


def test_other_multiword_phrase_boundary_sets_are_disjoint_from_industry_terms() -> None:
    assert KNOWN_OTHER_MULTIWORD_TERMS.isdisjoint(KNOWN_INDUSTRY_TERMS)


def test_industry_and_file_config_term_sets_are_disjoint() -> None:
    assert KNOWN_INDUSTRY_TERMS.isdisjoint(KNOWN_FILE_CONFIG_TERMS)


def test_known_coined_terms_have_stable_candidate_boundaries() -> None:
    text = "\n".join(f"{term} {term}" for term in sorted(KNOWN_COINED_TERMS))
    term_map = extract_classified_term_map(text)
    py_results = {item.normalized for item in extract_adoptable_terms(text, limit=100)}
    js_results = {item["normalized"] for item in _js_extract_capture_candidates(text, limit=100)}
    expected_candidates = {
        term
        for term in KNOWN_COINED_TERMS
        if not any(other.startswith(term + " ") for other in KNOWN_COINED_TERMS if other != term)
    }

    assert {classify_term(term).label for term in KNOWN_COINED_TERMS} == {LABEL_COINED_OR_SHORTENED}
    assert {term_map[term].label for term in expected_candidates} == {LABEL_COINED_OR_SHORTENED}
    assert py_results == expected_candidates
    assert js_results == expected_candidates


def test_industry_single_terms_never_become_candidates() -> None:
    industry_single_terms = {term for term in KNOWN_INDUSTRY_TERMS if " " not in term}
    text = "\n".join(f"{term} {term}" for term in sorted(industry_single_terms))
    py_results = {
        item.normalized
        for item in extract_adoptable_terms(text, limit=100)
        if item.label == LABEL_INDUSTRY_TERM and " " not in item.normalized
    }
    js_results = {
        item["normalized"]
        for item in _js_extract_capture_candidates(text, limit=100)
        if item["label"] == LABEL_INDUSTRY_TERM and " " not in item["normalized"]
    }

    assert {classify_term(term).label for term in industry_single_terms} == {LABEL_INDUSTRY_TERM}
    assert py_results == set()
    assert js_results == set()


def test_known_industry_multiword_terms_have_stable_candidate_boundaries() -> None:
    multiword_terms = {term for term in KNOWN_INDUSTRY_TERMS if " " in term}
    text = "\n".join(f"{term} {term}" for term in sorted(multiword_terms))
    term_map = extract_classified_term_map(text)
    py_results = {
        item.normalized
        for item in extract_adoptable_terms(text, limit=100)
        if item.label == LABEL_INDUSTRY_TERM and " " in item.normalized
    }
    js_results = {
        item["normalized"]
        for item in _js_extract_capture_candidates(text, limit=100)
        if item["label"] == LABEL_INDUSTRY_TERM and " " in item["normalized"]
    }

    assert {term_map[term].label for term in multiword_terms} == {LABEL_INDUSTRY_TERM}
    assert py_results == set()
    assert js_results == set()


def test_known_other_multiword_phrases_have_stable_candidate_boundaries() -> None:
    text = "\n".join(f"{term} {term}" for term in sorted(KNOWN_OTHER_MULTIWORD_TERMS))
    term_map = extract_classified_term_map(text)
    py_results = {
        item.normalized
        for item in extract_adoptable_terms(text, limit=50)
        if item.label == LABEL_OTHER
    }
    js_results = {
        item["normalized"]
        for item in _js_extract_capture_candidates(text, limit=50)
        if item["label"] == LABEL_OTHER
    }

    assert {term_map[term].label for term in KNOWN_OTHER_MULTIWORD_TERMS} == {LABEL_OTHER}
    assert py_results == ADOPTABLE_OTHER_MULTIWORD_TERMS
    assert js_results == ADOPTABLE_OTHER_MULTIWORD_TERMS


def test_file_config_and_repo_dir_terms_never_become_candidates() -> None:
    terms = sorted(KNOWN_FILE_CONFIG_TERMS | KNOWN_REPO_DIR_TERMS)
    text = "\n".join(f"{term} {term}" for term in terms)
    py_results = {
        item.normalized
        for item in extract_adoptable_terms(text, limit=200)
    }
    js_results = {
        item["normalized"]
        for item in _js_extract_capture_candidates(text, limit=200)
    }

    assert {
        classify_term(term).label
        for term in KNOWN_FILE_CONFIG_TERMS | KNOWN_REPO_DIR_TERMS
    } == {LABEL_FILE_CONFIG_IDENTIFIER}
    assert py_results & (KNOWN_FILE_CONFIG_TERMS | KNOWN_REPO_DIR_TERMS) == set()
    assert js_results & (KNOWN_FILE_CONFIG_TERMS | KNOWN_REPO_DIR_TERMS) == set()


def test_proper_noun_terms_never_become_candidates() -> None:
    text = "\n".join(f"{term} {term}" for term in sorted(PROPER_NOUN_TERMS))
    py_results = {
        item.normalized
        for item in extract_adoptable_terms(text, limit=100)
    }
    js_results = {
        item["normalized"]
        for item in _js_extract_capture_candidates(text, limit=100)
    }

    assert py_results == set()
    assert js_results == set()


def test_python_and_js_attachment_candidate_fixture_stay_in_lockstep() -> None:
    text = ATTACHMENT_CANDIDATES_FIXTURE_PATH.read_text(encoding="utf-8")
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_adoptable_terms(text)
    ]
    js_results = _js_extract_capture_candidates(text)

    assert js_results == py_results


def test_python_and_js_preview_terms_include_single_occurrence_high_signal_terms() -> None:
    text = "\n".join(
        [
            "current state",
            "github standard",
            "current issue",
            "source term",
            "preferred term",
            "status",
            "preview",
            "candidate",
            "README",
            "review",
        ]
    )
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_preview_terms(text)
    ]
    js_results = _js_extract_capture_preview_terms(text)

    assert py_results == [
        {
            "term": "github standard",
            "normalized": "github standard",
            "label": LABEL_COINED_OR_SHORTENED,
            "reason": "known_coined_phrase",
        },
        {
            "term": "current state",
            "normalized": "current state",
            "label": LABEL_COINED_OR_SHORTENED,
            "reason": "known_coined_phrase",
        },
        {
            "term": "preferred term",
            "normalized": "preferred term",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        },
        {
            "term": "current issue",
            "normalized": "current issue",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        },
        {
            "term": "source term",
            "normalized": "source term",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        },
    ]
    assert js_results == py_results


def test_python_and_js_preview_terms_pick_ui_labels_from_natural_sentence() -> None:
    text = "source term と preferred term と status と preview と candidate の意味が曖昧です。"
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_preview_terms(text)
    ]
    js_results = _js_extract_capture_preview_terms(text)

    assert py_results == [
        {
            "term": "preferred term",
            "normalized": "preferred term",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        },
        {
            "term": "source term",
            "normalized": "source term",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        },
        {
            "term": "candidate",
            "normalized": "candidate",
            "label": LABEL_OTHER,
            "reason": "generic_single_word",
        },
        {
            "term": "preview",
            "normalized": "preview",
            "label": LABEL_OTHER,
            "reason": "generic_single_word",
        },
        {
            "term": "status",
            "normalized": "status",
            "label": LABEL_OTHER,
            "reason": "generic_single_word",
        },
    ]
    assert js_results == py_results


def test_python_and_js_preview_terms_pick_status_from_ui_update_sentence() -> None:
    text = "実行系でも Analyze Draft が Draft Output と status を更新するところまで確認しました。"
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_preview_terms(text)
    ]
    js_results = _js_extract_capture_preview_terms(text)

    assert py_results == [
        {
            "term": "Analyze Draft",
            "normalized": "analyze draft",
            "label": LABEL_FILE_CONFIG_IDENTIFIER,
            "reason": "config_term",
        },
        {
            "term": "Draft Output",
            "normalized": "draft output",
            "label": LABEL_FILE_CONFIG_IDENTIFIER,
            "reason": "config_term",
        },
        {
            "term": "status",
            "normalized": "status",
            "label": LABEL_OTHER,
            "reason": "generic_single_word",
        },
    ]
    assert js_results == py_results


def test_python_and_js_investigation_terms_pick_ui_labels_without_showing_classification_noise() -> None:
    text = "実行系でも Analyze Draft が Draft Output と status を更新するところまで確認しました。"
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_investigation_terms(text)
    ]
    js_results = _js_extract_capture_investigation_terms(text)

    assert py_results == [
        {
            "term": "Analyze Draft",
            "normalized": "analyze draft",
            "label": LABEL_FILE_CONFIG_IDENTIFIER,
            "reason": "config_term",
        },
        {
            "term": "Draft Output",
            "normalized": "draft output",
            "label": LABEL_FILE_CONFIG_IDENTIFIER,
            "reason": "config_term",
        },
        {
            "term": "status",
            "normalized": "status",
            "label": LABEL_OTHER,
            "reason": "generic_single_word",
        },
    ]
    assert js_results == py_results


def test_python_and_js_investigation_terms_pick_mixed_language_unknown_single() -> None:
    text = "まだ polishing の余地はある"
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_investigation_terms(text)
    ]
    js_results = _js_extract_capture_investigation_terms(text)

    assert py_results == [
        {
            "term": "polishing",
            "normalized": "polishing",
            "label": LABEL_OTHER,
            "reason": "generic_single_word",
        }
    ]
    assert js_results == py_results


def test_python_and_js_investigation_terms_pick_operational_english_from_japanese_explanation() -> None:
    text = "こちらで把握している不整合と failing test は解消され、179 passed です。worktree には本件以外の差分もあるので"
    py_results = [
        {
            "term": item.term,
            "normalized": item.normalized,
            "label": item.label,
            "reason": item.reason,
        }
        for item in extract_investigation_terms(text)
    ]
    js_results = _js_extract_capture_investigation_terms(text)

    assert py_results == [
        {
            "term": "failing test",
            "normalized": "failing test",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        },
        {
            "term": "passed",
            "normalized": "passed",
            "label": LABEL_OTHER,
            "reason": "generic_single_word",
        },
    ]
    assert js_results == py_results


def test_registered_term_keeps_type_and_marks_registered() -> None:
    registered_terms = {"tracked file"}
    classified = classify_term("tracked file", registered_terms=registered_terms)
    assert classified.label == LABEL_INDUSTRY_TERM
    assert classified.registered is True


def test_classify_cli_json_output() -> None:
    result = classify_cmd(
        "--text",
        "root clutter migration review README CI GitHub",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    assert '"root clutter"' in result.stdout
    assert '"migration"' in result.stdout
    assert '"review"' in result.stdout


def test_classify_cli_chat_json_input() -> None:
    result = classify_cmd(
        str(CHAT_JSON_FIXTURE_PATH),
        "--chat-json",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    labels = {item["normalized"]: item["label"] for item in payload["results"]}

    assert labels["root clutter"] == LABEL_COINED_OR_SHORTENED
    assert labels["maintainer only file"] == LABEL_COINED_OR_SHORTENED
    assert labels["tracked file"] == LABEL_INDUSTRY_TERM
    assert labels["repo"] == LABEL_COINED_OR_SHORTENED
    assert labels["/veil capture"] == LABEL_FILE_CONFIG_IDENTIFIER
    assert labels["mirror"] == LABEL_OTHER
    assert labels["export"] == LABEL_OTHER
    assert labels["review"] == LABEL_OTHER
    assert labels["readme"] == LABEL_FILE_CONFIG_IDENTIFIER
    assert labels["ci"] == LABEL_FILE_CONFIG_IDENTIFIER
    assert labels["github"] == LABEL_OTHER


def test_classify_cli_adoptable_only_json_output() -> None:
    result = classify_cmd(
        "--text",
        "\n".join(
            [
                "root clutter root clutter",
                "workflow workflow workflow",
                "repo hygiene repo hygiene",
                "README README README",
                "review review review",
            ]
        ),
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == ["root clutter", "repo hygiene"]


def test_classify_cli_preview_only_json_output() -> None:
    result = classify_cmd(
        "--text",
        "\n".join(
            [
                "current state",
                "github standard",
                "current issue",
                "source term",
                "preferred term",
                "status",
                "README",
                "review",
            ]
        ),
        "--preview-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == ["github standard", "current state", "preferred term", "current issue", "source term"]


def test_classify_cli_preview_only_picks_ui_labels_from_natural_sentence() -> None:
    result = classify_cmd(
        "--text",
        "source term と preferred term と status と preview と candidate の意味が曖昧です。",
        "--preview-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == ["preferred term", "source term", "candidate", "preview", "status"]


def test_classify_cli_preview_only_picks_status_from_ui_update_sentence() -> None:
    result = classify_cmd(
        "--text",
        "実行系でも Analyze Draft が Draft Output と status を更新するところまで確認しました。",
        "--preview-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == ["analyze draft", "draft output", "status"]


def test_classify_cli_investigation_only_picks_ui_labels_from_natural_sentence() -> None:
    result = classify_cmd(
        "--text",
        "実行系でも Analyze Draft が Draft Output と status を更新するところまで確認しました。",
        "--investigation-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == ["analyze draft", "draft output", "status"]


def test_classify_cli_investigation_only_picks_mixed_language_unknown_single() -> None:
    result = classify_cmd(
        "--text",
        "まだ polishing の余地はある",
        "--investigation-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == ["polishing"]


def test_classify_cli_investigation_only_picks_operational_english_from_japanese_explanation() -> None:
    result = classify_cmd(
        "--text",
        "こちらで把握している不整合と failing test は解消され、179 passed です。worktree には本件以外の差分もあるので",
        "--investigation-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == ["failing test", "passed"]


def test_classify_cli_adoptable_only_chat_json_input() -> None:
    payload = {
        "messages": [
            {"text": "root clutter root clutter"},
            {"text": "workflow workflow workflow"},
            {"text": "README README README"},
            {"text": "review review review"},
        ]
    }
    result = classify_cmd(
        "--stdin",
        "--chat-json",
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
        "--json",
        input=json.dumps(payload, ensure_ascii=False),
    )
    output = json.loads(result.stdout)
    normalized = [item["normalized"] for item in output["results"]]

    assert normalized == ["root clutter"]


def test_classify_cli_adoptable_only_chat_json_excludes_non_adoptable_other_phrase() -> None:
    payload = {
        "messages": [
            {"text": "current issue current issue current issue"},
            {"text": "repo hygiene repo hygiene"},
        ]
    }
    result = classify_cmd(
        "--stdin",
        "--chat-json",
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
        "--json",
        input=json.dumps(payload, ensure_ascii=False),
    )
    output = json.loads(result.stdout)
    results = [
        {
            "normalized": item["normalized"],
            "label": item["label"],
            "reason": item["reason"],
        }
        for item in output["results"]
    ]

    assert results == [
        {
            "normalized": "repo hygiene",
            "label": LABEL_OTHER,
            "reason": "ordinary_multiword_phrase",
        }
    ]


def test_classify_cli_attachment_long_tail_fixture_has_no_unknown_terms() -> None:
    result = classify_cmd(
        str(ATTACHMENT_LONG_TAIL_FIXTURE_PATH),
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)

    assert all(item["label"] != LABEL_UNKNOWN for item in payload["results"])


def test_classify_cli_attachment_candidate_fixture_excludes_industry_heavy_terms() -> None:
    result = classify_cmd(
        str(ATTACHMENT_CANDIDATES_FIXTURE_PATH),
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)
    normalized = [item["normalized"] for item in payload["results"]]

    assert normalized == []


def test_capture_candidate_registration_round_trip() -> None:
    text = "\n".join(
        [
            "root clutter root clutter root clutter",
            "README README README",
        ]
    )
    tmpdir = Path(tempfile.mkdtemp(dir="workspace"))
    db_path = tmpdir / "roundtrip.db"
    html_path = tmpdir / "veil-round-trip.html"
    try:
        db_cmd("init-db", "--db", str(db_path))

        initial = classify_cmd(
            "--text",
            text,
            "--adoptable-only",
            "--db",
            str(db_path),
            "--json",
        )
        initial_payload = json.loads(initial.stdout)
        initial_normalized = [item["normalized"] for item in initial_payload["results"]]

        assert initial_normalized == ["root clutter"]

        upsert = db_cmd(
            "upsert-rule",
            "--db",
            str(db_path),
            "--term",
            "root clutter",
            "--preferred",
            "current state clutter",
            "--json",
        )
        upsert_payload = json.loads(upsert.stdout)
        assert upsert_payload["status"] == "ok"
        assert upsert_payload["row"]["term_normalized"] == "root clutter"

        follow_up = classify_cmd(
            "--text",
            text,
            "--adoptable-only",
            "--db",
            str(db_path),
            "--json",
        )
        follow_up_payload = json.loads(follow_up.stdout)
        follow_up_normalized = [item["normalized"] for item in follow_up_payload["results"]]

        assert follow_up_normalized == []

        readback = db_cmd("readback", "--db", str(db_path), "--json")
        readback_payload = json.loads(readback.stdout)
        rows = {row["term_normalized"]: row for row in readback_payload["rows"]}

        assert rows["root clutter"]["preferred"] == "current state clutter"

        exported = db_cmd("export-html", "--db", str(db_path), "--html-path", str(html_path), "--json")
        exported_payload = json.loads(exported.stdout)

        assert exported_payload["status"] == "ok"
        content = html_path.read_text(encoding="utf-8")
        assert "root clutter" in content
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_classify_cli_chat_transcript_fixture_produces_no_adoptable_terms() -> None:
    result = classify_cmd(
        str(CHAT_JSON_FIXTURE_PATH),
        "--chat-json",
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)

    assert payload["results"] == []


def test_classify_cli_chat_json_preserves_identical_segments_before_candidate_gate() -> None:
    payload = {
        "messages": [
            {"text": "root clutter"},
            {"text": "root clutter"},
        ]
    }
    result = classify_cmd(
        "--stdin",
        "--chat-json",
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
        "--json",
        input=json.dumps(payload, ensure_ascii=False),
    )
    output = json.loads(result.stdout)

    assert [item["normalized"] for item in output["results"]] == ["root clutter"]


def test_classify_cli_chat_json_accepts_nested_textual_keys() -> None:
    payload = {
        "conversation": [
            {"parts": [{"text": "root clutter root clutter"}]},
            {"turns": [{"message": "workflow workflow workflow"}]},
            {"items": [{"body": "README README README"}]},
        ]
    }
    result = classify_cmd(
        "--stdin",
        "--chat-json",
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
        "--json",
        input=json.dumps(payload, ensure_ascii=False),
    )
    output = json.loads(result.stdout)
    normalized = [item["normalized"] for item in output["results"]]

    assert normalized == ["root clutter"]


def test_extract_text_from_chat_json_preserves_occurrences_and_input_order() -> None:
    runtime = _load_classify_runtime_module()
    payload = {
        "conversation": [
            {"parts": [{"text": " first "}], "message": "first"},
            {"turns": [{"content": "second"}]},
            {"items": [{"body": "third"}, {"value": "second"}]},
            {"messages": [{"text": "third"}, {"text": "fourth"}]},
        ]
    }

    assert runtime.extract_text_from_chat_json(json.dumps(payload, ensure_ascii=False)) == (
        "first\nfirst\nsecond\nthird\nsecond\nthird\nfourth"
    )


def test_extract_text_from_chat_json_returns_empty_string_for_non_textual_payload() -> None:
    runtime = _load_classify_runtime_module()

    assert runtime.extract_text_from_chat_json(json.dumps({"messages": [{"meta": 1}, {"parts": [None, 3]}]})) == ""


def test_read_input_prefers_inline_text_over_path_or_stdin() -> None:
    runtime = _load_classify_runtime_module()
    args = argparse.Namespace(text="inline text", stdin=False, path="ignored.txt")

    assert runtime.read_input(args) == "inline text"


def test_load_registered_terms_returns_empty_set_for_missing_or_corrupt_db(tmp_path: Path) -> None:
    runtime = _load_classify_runtime_module()
    missing_db = tmp_path / "missing.db"
    corrupt_db = tmp_path / "corrupt.db"
    corrupt_db.write_text("not a sqlite db", encoding="utf-8")

    assert runtime.load_registered_terms(str(missing_db)) == set()
    assert runtime.load_registered_terms(str(corrupt_db)) == set()
    corrupt_db.unlink()
    assert not corrupt_db.exists()


def test_load_registered_terms_returns_normalized_keys(tmp_db: str) -> None:
    runtime = _load_classify_runtime_module()
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "Current State", "--preferred", "Present State")

    assert runtime.load_registered_terms(tmp_db) == {"current state"}


def test_classify_cli_adoptable_only_without_json_prints_no_terms() -> None:
    result = classify_cmd(
        str(CHAT_JSON_FIXTURE_PATH),
        "--chat-json",
        "--adoptable-only",
        "--db",
        "does-not-exist.db",
    )

    assert result.stdout.strip() == "NO-TERMS"


def test_classify_cli_invalid_chat_json_reports_error() -> None:
    result = classify_cmd(
        "--stdin",
        "--chat-json",
        "--db",
        "does-not-exist.db",
        check=False,
        input="{",
    )

    assert result.returncode == 1
    assert "ERROR: Invalid chat JSON:" in result.stderr


def test_classify_cli_without_input_reports_error() -> None:
    result = classify_cmd("--json", "--db", "does-not-exist.db", check=False)

    assert result.returncode == 1
    assert "ERROR: No input text provided." in result.stderr


def test_chat_seed_fixture_labels() -> None:
    samples = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    for sample in samples:
        classified = classify_term(sample["term"])
        assert classified.label == sample["label"], sample["term"]


def test_capture_taxonomy_payload_exposes_other_phrase_boundaries() -> None:
    payload = capture_taxonomy_payload()

    assert "passed" in payload["previewable_generic_single_terms"]
    assert "status" in payload["previewable_generic_single_terms"]
    assert "current issue" in payload["known_other_multiword_terms"]
    assert "current issue" not in payload["adoptable_other_multiword_terms"]
    assert "failing test" in payload["known_other_multiword_terms"]
    assert "failing test" not in payload["adoptable_other_multiword_terms"]
    assert "source term" in payload["known_other_multiword_terms"]
    assert "repo hygiene" in payload["known_other_multiword_terms"]
    assert "repo hygiene" in payload["adoptable_other_multiword_terms"]


def test_capture_taxonomy_payload_schema_is_fixed() -> None:
    payload = capture_taxonomy_payload()

    assert set(payload.keys()) == {
        "labels",
        "proper_noun_terms",
        "known_industry_terms",
        "known_industry_acronyms",
        "known_repo_dir_terms",
        "known_file_config_terms",
        "shortened_terms",
        "generic_single_words",
        "phrase_weak_tokens",
        "coined_head_tokens",
        "known_coined_terms",
        "known_other_multiword_terms",
        "adoptable_other_multiword_terms",
        "previewable_generic_single_terms",
        "identifier_token_pattern",
        "word_token_pattern",
    }
    assert set(payload["labels"].values()) == set(ALL_LABELS)


def test_capture_taxonomy_payload_mirrors_source_sets() -> None:
    payload = capture_taxonomy_payload()

    assert payload["proper_noun_terms"] == sorted(PROPER_NOUN_TERMS)
    assert payload["known_industry_terms"] == sorted(KNOWN_INDUSTRY_TERMS)
    assert payload["known_file_config_terms"] == sorted(KNOWN_FILE_CONFIG_TERMS)
    assert payload["known_repo_dir_terms"] == sorted(KNOWN_REPO_DIR_TERMS)
    assert payload["known_coined_terms"] == sorted(KNOWN_COINED_TERMS)
    assert payload["known_other_multiword_terms"] == sorted(KNOWN_OTHER_MULTIWORD_TERMS)
    assert payload["adoptable_other_multiword_terms"] == sorted(ADOPTABLE_OTHER_MULTIWORD_TERMS)
    assert payload["previewable_generic_single_terms"] == sorted(PREVIEWABLE_GENERIC_SINGLE_TERMS)


def test_taxonomy_overlaps_are_only_intentional_adoptable_subsets() -> None:
    assert ADOPTABLE_OTHER_MULTIWORD_TERMS <= KNOWN_OTHER_MULTIWORD_TERMS
    assert KNOWN_COINED_TERMS.isdisjoint(KNOWN_INDUSTRY_TERMS)
    assert KNOWN_COINED_TERMS.isdisjoint(KNOWN_FILE_CONFIG_TERMS)
    assert KNOWN_COINED_TERMS.isdisjoint(KNOWN_OTHER_MULTIWORD_TERMS)
    assert KNOWN_INDUSTRY_TERMS.isdisjoint(KNOWN_FILE_CONFIG_TERMS)
    assert KNOWN_OTHER_MULTIWORD_TERMS.isdisjoint(KNOWN_INDUSTRY_TERMS)
    assert KNOWN_FILE_CONFIG_TERMS.isdisjoint(PROPER_NOUN_TERMS)


def test_chat_transcript_fixture_keeps_expected_labels() -> None:
    payload = json.loads(CHAT_JSON_FIXTURE_PATH.read_text(encoding="utf-8"))
    text = "\n".join(
        str(message.get("content", "") or message.get("text", ""))
        for message in payload.get("messages", [])
    )
    term_map = extract_classified_term_map(text)

    assert term_map["root clutter"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["maintainer only file"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["tracked file"].label == LABEL_INDUSTRY_TERM
    assert term_map["repo"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["review"].label == LABEL_OTHER
    assert term_map["readme"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["ci"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert term_map["github"].label == LABEL_OTHER
    assert term_map["github standard"].label == LABEL_COINED_OR_SHORTENED
    assert term_map["repo content classification.md"].label == LABEL_FILE_CONFIG_IDENTIFIER
    assert all(item.label != LABEL_UNKNOWN for item in term_map.values())


def test_chat_transcript_fixture_produces_no_adoptable_terms() -> None:
    payload = json.loads(CHAT_JSON_FIXTURE_PATH.read_text(encoding="utf-8"))
    text = "\n".join(
        str(message.get("content", "") or message.get("text", ""))
        for message in payload.get("messages", [])
    )

    assert extract_adoptable_terms(text, limit=20) == []
