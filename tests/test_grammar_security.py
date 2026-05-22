#!/usr/bin/env python3
"""Grammar Security Hardening Tests — verify fix blocks known chaos vectors.

Runs attack payloads against the hardened grammar engine. All must be
rejected with ValidationError or SecurityError.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for 'grammar' import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from grammar.security_hardening import (
    ValidationError,
    SecurityError,
    RuleProvenance,
    create_rule,
    create_rule_from_dict,
    validate_rule_name,
    validate_tagline,
    validate_condition,
    validate_exec_field,
    evaluate_condition,
    sandboxed_exec,
    batch_create_rules,
    compute_checksum,
    build_provenance,
    audit_rule,
)


# ── 1. Rule Name Validation ────────────────────────────────────────

def test_rule_name_alphanumeric_underscore_only() -> None:
    assert validate_rule_name("safe_rule_123") == "safe_rule_123"


def test_rule_name_rejects_hyphen() -> None:
    with pytest.raises(SecurityError):
        validate_rule_name("unsafe-rule")


def test_rule_name_rejects_dot() -> None:
    with pytest.raises(SecurityError):
        validate_rule_name("unsafe.rule")


def test_rule_name_rejects_slash() -> None:
    with pytest.raises(SecurityError):
        validate_rule_name("unsafe/rule")


def test_rule_name_rejects_backslash() -> None:
    with pytest.raises(SecurityError):
        validate_rule_name("unsafe\\rule")


def test_rule_name_rejects_path_traversal() -> None:
    with pytest.raises(SecurityError):
        validate_rule_name("../../../etc/passwd")


def test_rule_name_rejects_too_long() -> None:
    with pytest.raises(ValidationError):
        validate_rule_name("a" * 65)


def test_rule_name_rejects_empty() -> None:
    with pytest.raises(ValidationError):
        validate_rule_name("")


def test_rule_name_rejects_non_string() -> None:
    with pytest.raises(ValidationError):
        validate_rule_name(12345)  # type: ignore[arg-type]


# ── 2. Tagline Validation ──────────────────────────────────────────

def test_tagline_strips_html() -> None:
    assert validate_tagline("<b>bold</b>") == "bold"


def test_tagline_escapes_ampersand() -> None:
    assert "&amp;" in validate_tagline("Tom & Jerry")


def test_tagline_blocks_script_tag() -> None:
    with pytest.raises(SecurityError):
        validate_tagline("<script>alert(1)</script>")


def test_tagline_blocks_iframe() -> None:
    with pytest.raises(SecurityError):
        validate_tagline("<iframe src='evil.com'></iframe>")


def test_tagline_blocks_javascript_protocol() -> None:
    with pytest.raises(SecurityError):
        validate_tagline("javascript:alert(1)")


def test_tagline_blocks_event_handler() -> None:
    with pytest.raises(SecurityError):
        validate_tagline("<img onerror=alert(1)>")


def test_tagline_rejects_too_long() -> None:
    with pytest.raises(ValidationError):
        validate_tagline("x" * 257)


# ── 3. Condition Validation ──────────────────────────────────────

def test_condition_allows_safe_expression() -> None:
    assert validate_condition("thermal_headroom > 5") == "thermal_headroom > 5"


def test_condition_blocks_sql_drop() -> None:
    with pytest.raises(SecurityError):
        validate_condition("'; DROP TABLE rules; --")


def test_condition_blocks_sql_delete() -> None:
    with pytest.raises(SecurityError):
        validate_condition("x > 0; DELETE FROM rules")


def test_condition_blocks_sql_union() -> None:
    with pytest.raises(SecurityError):
        validate_condition("x UNION SELECT * FROM users")


def test_condition_blocks_semicolon() -> None:
    with pytest.raises(SecurityError):
        validate_condition("a > 1; b < 2")


def test_condition_blocks_comment_dash() -> None:
    with pytest.raises(SecurityError):
        validate_condition("x > 0 -- comment")


def test_condition_rejects_too_long() -> None:
    with pytest.raises(ValidationError):
        validate_condition("x > 0" + " " * 1020)


# ── 4. Exec Field Sandboxing ─────────────────────────────────────

def test_exec_allows_dict_literal() -> None:
    assert validate_exec_field("{'key': 'value'}") == "{'key': 'value'}"


def test_exec_allows_list_literal() -> None:
    assert validate_exec_field("[1, 2, 3]") == "[1, 2, 3]"


def test_exec_allows_safe_string() -> None:
    assert validate_exec_field("'hello world'") == "'hello world'"


def test_exec_blocks_import() -> None:
    with pytest.raises(SecurityError):
        validate_exec_field("__import__('os').system('rm -rf /')")


def test_exec_blocks_eval_call() -> None:
    with pytest.raises(SecurityError):
        validate_exec_field("eval('1+1')")


def test_exec_blocks_exec_call() -> None:
    with pytest.raises(SecurityError):
        validate_exec_field("exec('print(1)')")


def test_exec_blocks_lambda() -> None:
    with pytest.raises(SecurityError):
        validate_exec_field("lambda x: x + 1")


def test_exec_blocks_function_def() -> None:
    # Function definitions are invalid in 'eval' mode — caught as syntax error
    with pytest.raises(ValidationError):
        validate_exec_field("def evil(): pass")


def test_exec_rejects_too_long() -> None:
    with pytest.raises(ValidationError):
        validate_exec_field("x" * 513)


def test_exec_allows_none() -> None:
    assert validate_exec_field(None) is None


# ── 5. Sandboxed Exec Evaluation ─────────────────────────────────

def test_sandboxed_exec_returns_dict() -> None:
    result = sandboxed_exec("{'a': 1, 'b': 2}")
    assert result == {"a": 1, "b": 2}


def test_sandboxed_exec_returns_none() -> None:
    assert sandboxed_exec(None) is None


def test_sandboxed_exec_rejects_import() -> None:
    with pytest.raises(SecurityError):
        sandboxed_exec("__import__('os')")


# ── 6. Condition Evaluation ──────────────────────────────────────

def test_evaluate_condition_simple_comparison() -> None:
    assert evaluate_condition("x > 5", {"x": 10}) is True
    assert evaluate_condition("x > 5", {"x": 3}) is False


def test_evaluate_condition_boolean_logic() -> None:
    assert evaluate_condition("x > 5 and y < 10", {"x": 10, "y": 5}) is True
    assert evaluate_condition("x > 5 or y > 10", {"x": 3, "y": 12}) is True


def test_evaluate_condition_empty_returns_true() -> None:
    assert evaluate_condition("", {}) is True


def test_evaluate_condition_unknown_metric() -> None:
    with pytest.raises(ValidationError):
        evaluate_condition("z > 5", {"x": 10})


def test_evaluate_condition_rejects_unsafe_ast() -> None:
    # Attempt to use attribute access (not in whitelist)
    with pytest.raises(SecurityError):
        evaluate_condition("__import__('os').system('ls')", {})


# ── 7. Full Rule Creation ─────────────────────────────────────────

def test_create_rule_success() -> None:
    rule = create_rule(name="thermal_guard", tagline="Watch thermal headroom", condition="temp > 80")
    assert rule.name == "thermal_guard"
    assert rule.production.tagline == "Watch thermal headroom"
    assert rule.production.condition == "temp > 80"
    assert rule.provenance is not None
    assert len(rule.provenance.history) == 1
    assert rule.provenance.history[0]["event"] == "created"


def test_create_rule_rejects_bad_name() -> None:
    with pytest.raises(SecurityError):
        create_rule(name="bad-name", tagline="ok", condition="ok")


def test_create_rule_rejects_bad_tagline() -> None:
    with pytest.raises(SecurityError):
        create_rule(name="ok", tagline="<script>evil</script>", condition="ok")


def test_create_rule_rejects_bad_condition() -> None:
    with pytest.raises(SecurityError):
        create_rule(name="ok", tagline="ok", condition="DROP TABLE rules")


def test_create_rule_rejects_bad_exec() -> None:
    with pytest.raises(SecurityError):
        create_rule(name="ok", tagline="ok", condition="ok", exec_field="__import__('os')")


# ── 8. Rule Ingestion from Dict ──────────────────────────────────

def test_create_rule_from_dict_builds_provenance() -> None:
    data = {
        "name": "ingested_rule",
        "production": {
            "tagline": "Test rule",
            "condition": "x > 0",
            "exec": "{'foo': 'bar'}",
        },
    }
    rule = create_rule_from_dict(data, source="test_api", ingested_by="agent_1")
    assert rule.name == "ingested_rule"
    assert rule.provenance.source == "test_api"
    assert rule.provenance.ingested_by == "agent_1"
    assert rule.provenance.checksum is not None


def test_create_rule_from_dict_rejects_path_traversal_name() -> None:
    data = {
        "name": "../../../etc/passwd",
        "production": {"tagline": "", "condition": ""},
    }
    with pytest.raises(SecurityError):
        create_rule_from_dict(data)


def test_create_rule_from_dict_rejects_xss_tagline() -> None:
    data = {
        "name": "safe_rule",
        "production": {"tagline": "<script>alert(1)</script>", "condition": ""},
    }
    with pytest.raises(SecurityError):
        create_rule_from_dict(data)


def test_create_rule_from_dict_rejects_sqli_condition() -> None:
    data = {
        "name": "safe_rule",
        "production": {"tagline": "", "condition": "'; DROP TABLE rules; --"},
    }
    with pytest.raises(SecurityError):
        create_rule_from_dict(data)


def test_create_rule_from_dict_rejects_code_injection_exec() -> None:
    data = {
        "name": "safe_rule",
        "production": {
            "tagline": "",
            "condition": "",
            "exec": "__import__('os').system('rm -rf /')",
        },
    }
    with pytest.raises(SecurityError):
        create_rule_from_dict(data)


# ── 9. Batch Operations ──────────────────────────────────────────

def test_batch_create_rules_mixed() -> None:
    rule_dicts = [
        {"name": "good_1", "production": {"tagline": "ok", "condition": "x > 0"}},
        {"name": "bad-name", "production": {"tagline": "ok", "condition": "ok"}},
        {"name": "good_2", "production": {"tagline": "ok", "condition": "y < 10"}},
    ]
    rules, errors = batch_create_rules(rule_dicts, source="batch_test")
    assert len(rules) == 2
    assert len(errors) == 1
    assert errors[0].index == 1  # type: ignore[attr-defined]


# ── 10. Provenance & Audit ───────────────────────────────────────

def test_provenance_history_events() -> None:
    prov = RuleProvenance(source="manual")
    assert prov.history == []
    prov.add_event("reviewed", detail="passed initial scan")
    assert len(prov.history) == 1
    assert prov.history[0]["event"] == "reviewed"
    assert prov.history[0]["detail"] == "passed initial scan"


def test_checksum_stable() -> None:
    data = {"name": "test", "production": {"tagline": "hi", "condition": "x > 0"}}
    c1 = compute_checksum(data)
    c2 = compute_checksum(data)
    assert c1 == c2
    assert len(c1) == 64  # SHA-256 hex length


def test_audit_rule_structure() -> None:
    rule = create_rule(name="audit_me", tagline="test", condition="x > 0")
    audit = audit_rule(rule)
    assert audit["name"] == "audit_me"
    assert audit["checksum"] is not None
    assert audit["event_count"] == 1
    assert audit["has_exec"] is False


# ── 11. Chaos Vectors (April 22 Audit) ───────────────────────────

CHAOS_VECTORS = [
    {
        "name": "../../../etc/passwd",
        "production": {"tagline": "", "condition": ""},
        "attack": "Path Traversal",
    },
    {
        "name": "safe_rule",
        "production": {"tagline": "<script>alert(1)</script>", "condition": ""},
        "attack": "XSS",
    },
    {
        "name": "safe_rule",
        "production": {"tagline": "", "condition": "'; DROP TABLE rules; --"},
        "attack": "SQL Injection",
    },
    {
        "name": "safe_rule",
        "production": {
            "tagline": "",
            "condition": "",
            "exec": "__import__('os').system('rm -rf /')",
        },
        "attack": "Code Injection",
    },
]


@pytest.mark.parametrize("payload", CHAOS_VECTORS, ids=lambda p: p["attack"])
def test_chaos_vector_blocked(payload: dict) -> None:
    """Each chaos vector must be blocked at ingestion time."""
    with pytest.raises((ValidationError, SecurityError)):
        create_rule_from_dict(payload)


def run_all_standalone() -> bool:
    """Standalone runner for manual execution without pytest."""
    print("=" * 70)
    print("Grammar Security Hardening — Chaos Vector Validation")
    print("=" * 70)
    blocked = 0
    for payload in CHAOS_VECTORS:
        try:
            create_rule_from_dict(payload)
            print(f"  ❌ {payload['attack']} — RULE CREATED UNSAFELY")
        except (ValidationError, SecurityError) as exc:
            print(f"  ✅ {payload['attack']} — BLOCKED: {exc}")
            blocked += 1
    print("=" * 70)
    ok = blocked == len(CHAOS_VECTORS)
    print("✅ ALL BLOCKED" if ok else "❌ SOME VECTORS PASSED")
    return ok


if __name__ == "__main__":
    ok = run_all_standalone()
    sys.exit(0 if ok else 1)
