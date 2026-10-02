"""Provider-neutral AI boundary for ZooTasks.

This module performs no network calls. It defines the fail-closed contract
that any future provider adapter must implement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from django.conf import settings


class AIGatewayError(Exception):
    """Expected failure at the AI trust boundary."""


@dataclass(frozen=True)
class AIRequest:
    capability_id: str
    input_data: Mapping[str, Any]
    correlation_id: str


def _csv_setting(name: str) -> frozenset[str]:
    value = getattr(settings, name, "")
    return frozenset(item.strip() for item in value.split(",") if item.strip())


def validate_capability(capability_id: str) -> None:
    if not capability_id or capability_id not in _csv_setting("AI_ALLOWED_CAPABILITIES"):
        raise AIGatewayError("ai_capability_not_allowed")


def validate_provider_model(provider: str, model: str) -> None:
    if not provider or provider not in _csv_setting("AI_ALLOWED_PROVIDERS"):
        raise AIGatewayError("ai_provider_not_allowed")
    if not model or model not in _csv_setting("AI_ALLOWED_MODELS"):
        raise AIGatewayError("ai_model_not_allowed")


def build_task_quality_request(*, task_title: str, task_description: str, category: str, correlation_id: str) -> AIRequest:
    """Build the minimum-data request for AI-SYS-001."""
    if not correlation_id:
        raise AIGatewayError("ai_correlation_id_required")
    values = {"title": (task_title or "").strip(), "description": (task_description or "").strip(), "category": (category or "").strip()}
    if sum(len(value) for value in values.values()) > int(getattr(settings, "AI_MAX_INPUT_CHARS", 12000)):
        raise AIGatewayError("ai_input_too_large")
    if not values["title"] or not values["description"]:
        raise AIGatewayError("ai_task_content_required")
    return AIRequest("AI-SYS-001", values, correlation_id)


def validate_task_quality_output(output: Any) -> Mapping[str, Any]:
    """Validate a bounded, non-executable suggestion object."""
    if not isinstance(output, Mapping):
        raise AIGatewayError("ai_output_invalid")
    allowed = {"category_suggestion", "missing_information", "quality_checks", "confidence", "rationale"}
    if set(output) - allowed:
        raise AIGatewayError("ai_output_fields_not_allowed")
    category = output.get("category_suggestion", "")
    missing = output.get("missing_information", [])
    checks = output.get("quality_checks", [])
    confidence = output.get("confidence")
    rationale = output.get("rationale", "")
    if not isinstance(category, str) or len(category) > 100:
        raise AIGatewayError("ai_output_category_invalid")
    if not isinstance(missing, list) or not all(isinstance(x, str) and len(x) <= 200 for x in missing):
        raise AIGatewayError("ai_output_missing_information_invalid")
    if not isinstance(checks, list) or not all(isinstance(x, str) and len(x) <= 300 for x in checks):
        raise AIGatewayError("ai_output_quality_checks_invalid")
    if confidence is not None and (not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1):
        raise AIGatewayError("ai_output_confidence_invalid")
    if not isinstance(rationale, str) or len(rationale) > 1000:
        raise AIGatewayError("ai_output_rationale_invalid")
    return {"category_suggestion": category, "missing_information": missing, "quality_checks": checks, "confidence": confidence, "rationale": rationale}


def request_ai(*, request: AIRequest, provider: str, model: str) -> Mapping[str, Any]:
    """Fail closed until an approved provider adapter exists."""
    validate_capability(request.capability_id)
    validate_provider_model(provider, model)
    raise AIGatewayError("ai_provider_adapter_not_enabled")
