"""Fail-closed validation for the ZooTasks read/write security policy.

This module validates the policy contract without granting authorization by
itself. Runtime authorization must still be enforced at protected operations.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


BASE_DIR = Path(__file__).resolve().parents[1]
POLICY_PATH = BASE_DIR / "docs" / "security" / "read_write_policy.json"
SCHEMA_PATH = BASE_DIR / "docs" / "security" / "read_write_policy.schema.json"

SUPPORTED_POLICY_MAJOR = 1
SUPPORTED_SCHEMA_MAJOR = 1
FINANCIAL_ACTIONS = {"create", "update", "delete", "approve", "reject", "pay"}
SECRET_MARKERS = {
    "password",
    "secret",
    "token",
    "api_key",
    "api_secret",
    "session_cookie",
    "otp_secret",
    "private_key",
    "bank_account_number",
    "webauthn_challenge",
}


class SecurityPolicyError(ValueError):
    """Raised when the policy cannot be trusted as a security contract."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SecurityPolicyError(f"security policy load failure: {path.name}") from exc

    if not isinstance(value, dict):
        raise SecurityPolicyError(f"{path.name} must contain a JSON object")
    return value


def _major(version: str, field: str) -> int:
    try:
        return int(version.split(".", 1)[0])
    except (AttributeError, ValueError) as exc:
        raise SecurityPolicyError(f"invalid {field}") from exc


def validate_policy(
    policy: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Validate JSON Schema plus security invariants.

    Any validation failure raises SecurityPolicyError. No caller should treat
    an invalid policy as an implicit allow.
    """
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(policy)
    except Exception as exc:  # jsonschema exposes several validation errors
        raise SecurityPolicyError("policy schema validation failed") from exc

    if _major(policy["policy_version"], "policy_version") != SUPPORTED_POLICY_MAJOR:
        raise SecurityPolicyError("unsupported policy major version")
    if _major(policy["schema_version"], "schema_version") != SUPPORTED_SCHEMA_MAJOR:
        raise SecurityPolicyError("unsupported schema major version")

    enforcement = policy["enforcement"]
    required_denials = {
        "default_decision": "deny",
        "unknown_actor": "deny",
        "unknown_resource": "deny",
        "unknown_action": "deny",
        "unknown_scope": "deny",
        "policy_parse_failure": "deny",
        "policy_conflict": "deny",
        "client_assertion_is_authority": False,
    }
    if any(enforcement.get(key) != value for key, value in required_denials.items()):
        raise SecurityPolicyError("fail-closed enforcement invariant violated")

    actors = set(policy["actors"])
    actions = set(policy["actions"])
    scopes = set(policy["scopes"])
    resources = {item["resource"]: item for item in policy["resources"]}

    if len(resources) != len(policy["resources"]):
        raise SecurityPolicyError("duplicate resource declaration")

    rule_ids: set[str] = set()
    decisions: dict[tuple[str, str, str, str], set[str]] = {}

    for rule in policy["rules"]:
        rule_id = rule["rule_id"]
        if rule_id in rule_ids:
            raise SecurityPolicyError("duplicate rule_id")
        rule_ids.add(rule_id)

        if rule["actor"] not in actors:
            raise SecurityPolicyError("rule references unknown actor")
        if rule["action"] not in actions:
            raise SecurityPolicyError("rule references unknown action")
        if rule["scope"] not in scopes:
            raise SecurityPolicyError("rule references unknown scope")
        if rule["resource"] not in resources:
            raise SecurityPolicyError("rule references unknown resource")

        key = (rule["actor"], rule["resource"], rule["action"], rule["scope"])
        decisions.setdefault(key, set()).add(rule["decision"])

        if (
            rule["actor"] == "ai"
            and resources[rule["resource"]]["financial_effect"]
            and rule["action"] in FINANCIAL_ACTIONS
            and rule["decision"] == "allow"
        ):
            raise SecurityPolicyError("AI financial write authority is forbidden")

    if any(len(values) > 1 for values in decisions.values()):
        raise SecurityPolicyError("conflicting allow/deny rules")

    for name, fields in policy["protected_fields"].items():
        if name not in resources:
            raise SecurityPolicyError("protected_fields references unknown resource")
        for field in fields:
            lowered = field.casefold()
            if any(marker in lowered for marker in SECRET_MARKERS):
                raise SecurityPolicyError("secret-like field appears in policy")

    financial_classes = {"financial_critical"}
    for resource in resources.values():
        if resource["classification"] in financial_classes and not resource["financial_effect"]:
            raise SecurityPolicyError("financial resource missing financial_effect")

    return copy.deepcopy(policy)


def load_and_validate_policy() -> dict[str, Any]:
    """Load the repository policy and fail closed on any validation error."""
    policy = _load_json(POLICY_PATH)
    schema = _load_json(SCHEMA_PATH)
    return validate_policy(policy, schema)
