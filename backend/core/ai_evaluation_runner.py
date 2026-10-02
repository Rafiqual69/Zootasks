"""Deterministic evidence runner for AI-SYS-001.

No network/provider calls are made. The runner validates the local AI boundary
and emits machine-readable evidence suitable for CI artifact retention.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.test import override_settings

from core.ai_evaluation_cases import CASES, EVALUATION_DATASET_VERSION
from core.ai_evaluation_integrity import evidence_sha256, sha256_json
from core.ai_agent_registry import validate_agent_capability, validate_agent_data_class, validate_agent_autonomy
from core.ai_gateway import AIGatewayError, build_task_quality_request, validate_task_quality_output

RUNNER_VERSION = "1.2"
AGENT_ID = "ZT-AGENT-001"
SCHEMA_VERSION = "1.0"


def _case_result(case_id, group, expected, status, checks, error=None):
    result = {"case_id": case_id, "group": group, "expected": expected, "status": status, "checks": checks}
    if error:
        result["error"] = error
    return result


def _git_commit() -> str:
    value = os.environ.get("GITHUB_SHA") or os.environ.get("ZOOTASKS_GIT_COMMIT")
    if value:
        return value
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _source_revision_digest() -> str:
    files = (Path(__file__), Path(__file__).with_name("ai_evaluation_cases.py"), Path(__file__).with_name("ai_gateway.py"), Path(__file__).with_name("ai_agent_registry.py"))
    payload = {path.name: path.read_bytes().hex() for path in files}
    return sha256_json(payload)


def run_evaluation() -> dict:
    results = []
    for case in CASES:
        checks, status, error = [], "PASS", None
        try:
            request = build_task_quality_request(
                task_title="Evaluation task",
                task_description=case["input"],
                category="Evaluation",
                correlation_id=f"eval-{case['id']}",
                agent_id=AGENT_ID,
            )
            checks.append({"name": "input_boundary", "status": "PASS", "fields": sorted(request.input_data.keys())})
            if case["group"] in {"financial_boundary", "secret_disclosure", "identity_privacy"}:
                forbidden = {"wallet", "withdrawal", "payment", "password", "token", "secret", "api_key"}
                leaked_fields = forbidden.intersection(request.input_data.keys())
                if leaked_fields:
                    raise AssertionError(f"forbidden_fields_present:{sorted(leaked_fields)}")
                checks.append({"name": "protected_data_boundary", "status": "PASS"})
            if case["group"] == "malformed_output":
                try:
                    validate_task_quality_output({"category_suggestion": "Evaluation", "action": {"type": "approve_withdrawal"}})
                except AIGatewayError:
                    checks.append({"name": "malformed_output_rejected", "status": "PASS"})
                else:
                    raise AssertionError("malformed_output_was_accepted")
            if case["group"] == "provider_failure":
                try:
                    from core.ai_gateway import request_ai
                    with override_settings(
                        AI_ALLOWED_CAPABILITIES="AI-SYS-001",
                        AI_ALLOWED_PROVIDERS="test-provider",
                        AI_ALLOWED_MODELS="test-model-v1",
                        AI_PRODUCTION_APPROVED=True,
                        AI_APPROVAL_REFERENCE="AI-EVAL-REL-001",
                    ):
                        request_ai(request=request, provider="test-provider", model="test-model-v1")
                except AIGatewayError as exc:
                    if str(exc) != "ai_provider_adapter_not_enabled":
                        raise AssertionError(f"unexpected_provider_failure:{exc}")
                    checks.append({"name": "provider_failure_is_fail_closed", "status": "PASS"})
                else:
                    raise AssertionError("provider_adapter_unexpectedly_invoked")
            if case["group"] in {"prompt_injection", "financial_boundary"}:
                try:
                    validate_task_quality_output({"category_suggestion": "Evaluation", "privileged_action": "blocked"})
                except AIGatewayError:
                    checks.append({"name": "privileged_action_field_rejected", "status": "PASS"})
                else:
                    raise AssertionError("privileged_action_field_was_accepted")
            if case["group"] == "secret_disclosure":
                try:
                    validate_task_quality_output({"category_suggestion": "Evaluation", "secret": "blocked"})
                except AIGatewayError:
                    checks.append({"name": "secret_field_rejected", "status": "PASS"})
                else:
                    raise AssertionError("secret_field_was_accepted")
            if case["group"] == "identity_privacy":
                try:
                    validate_task_quality_output({"category_suggestion": "Evaluation", "private_identity": "blocked"})
                except AIGatewayError:
                    checks.append({"name": "private_identity_field_rejected", "status": "PASS"})
                else:
                    raise AssertionError("private_identity_field_was_accepted")
        except Exception as exc:
            status, error = "FAIL", str(exc)
        results.append(_case_result(case["id"], case["group"], case["expected"], status, checks, error))

    passed = sum(item["status"] == "PASS" for item in results)
    failed = len(results) - passed
    evidence = {
        "evidence_type": "zootasks.ai.security_evaluation",
        "schema_version": SCHEMA_VERSION,
        "system_id": "AI-SYS-001",
        "agent_id": AGENT_ID,
        "capability": "Task Classification & Quality Assistance",
        "evaluation_dataset_version": EVALUATION_DATASET_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "django_settings": os.environ.get("DJANGO_SETTINGS_MODULE", "")},
        "production_provider_invoked": False,
        "summary": {"total": len(results), "passed": passed, "failed": failed, "status": "PASS" if failed == 0 else "FAIL"},
        "cases": results,
        "provenance": {
            "git_commit": _git_commit(),
            "runner_version": RUNNER_VERSION,
            "source_revision_digest": _source_revision_digest(),
            "dataset_version": EVALUATION_DATASET_VERSION,
            "dataset_sha256": sha256_json(list(CASES)),
            "schema_version": SCHEMA_VERSION,
        },
    }
    evidence["integrity"] = {"algorithm": "sha256", "evidence_sha256": evidence_sha256(evidence)}
    return evidence


def write_evidence(output_path: str | Path) -> dict:
    evidence = run_evaluation()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    output = sys.argv[1] if len(sys.argv) > 1 else "artifacts/ai/AI-SYS-001-evidence.json"
    evidence = write_evidence(output)
    print(json.dumps(evidence["summary"], sort_keys=True))
    print(json.dumps(evidence["integrity"], sort_keys=True))
    raise SystemExit(0 if evidence["summary"]["status"] == "PASS" else 1)
