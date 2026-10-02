"""Provider-neutral AI boundary for ZooTasks.

This module performs no network calls. It defines the fail-closed contract
that any future provider adapter must implement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from django.conf import settings

from .ai_data_boundary import AIDataBoundaryError, build_task_content_projection
from .ai_agent_audit import build_provenance_receipt
from .ai_agent_session import AIAgentSession, validate_agent_session
from .ai_tool_permission import AIToolPermissionError, validate_tool_permission
from .ai_agent_registry import (
    validate_agent_autonomy,
    validate_agent_capability,
    validate_agent_data_class,
)
from .ai_capability_budget import validate_execution_budget, validate_input_budget, validate_output_budget
from .ai_safety_firewall import validate_action_class, validate_autonomy


class AIGatewayError(Exception):
    """Expected failure at the AI trust boundary."""


@dataclass(frozen=True)
class AIRequest:
    agent_id: str
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


def build_task_quality_request(
    *,
    task_title: str,
    task_description: str,
    category: str,
    correlation_id: str,
    agent_id: str = "ZT-AGENT-001",
) -> AIRequest:
    """Build the minimum-data request for AI-SYS-001."""
    if not correlation_id:
        raise AIGatewayError("ai_correlation_id_required")
    try:
        validate_agent_capability(agent_id=agent_id, capability_id="AI-SYS-001")
        validate_agent_data_class(agent_id=agent_id, data_class="task_content_minimal")
        validate_agent_autonomy(agent_id=agent_id, autonomy="suggestion_only")
    except Exception as exc:
        raise AIGatewayError("ai_agent_policy_rejected") from exc

    try:
        values = dict(
            build_task_content_projection(
                title=task_title,
                description=task_description,
                category=category,
            )
        )
    except AIDataBoundaryError as exc:
        raise AIGatewayError(str(exc)) from exc
    if sum(len(value) for value in values.values()) > int(getattr(settings, "AI_MAX_INPUT_CHARS", 12000)):
        raise AIGatewayError("ai_input_too_large")
    try:
        validate_input_budget(capability_id="AI-SYS-001", input_data=values)
    except Exception as exc:
        raise AIGatewayError("ai_input_budget_exceeded") from exc
    return AIRequest(agent_id, "AI-SYS-001", values, correlation_id)


def validate_task_quality_output(output: Any) -> Mapping[str, Any]:
    """Validate a bounded, non-executable suggestion object."""
    if not isinstance(output, Mapping):
        raise AIGatewayError("ai_output_invalid")
    try:
        validate_action_class(capability_id="AI-SYS-001", action_class="suggestion")
        validate_autonomy(capability_id="AI-SYS-001", autonomy="suggestion_only")
    except Exception as exc:
        raise AIGatewayError("ai_safety_policy_rejected") from exc
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
    result = {
        "category_suggestion": category,
        "missing_information": missing,
        "quality_checks": checks,
        "confidence": confidence,
        "rationale": rationale,
    }
    try:
        validate_output_budget(capability_id="AI-SYS-001", output=result)
        validate_execution_budget(capability_id="AI-SYS-001", tool_calls=0, external_side_effects=False)
    except Exception as exc:
        raise AIGatewayError("ai_output_budget_exceeded") from exc
    return result


def validate_production_approval() -> None:
    """Require an explicit release approval before any provider adapter can run."""
    if not bool(getattr(settings, "AI_PRODUCTION_APPROVED", False)):
        raise AIGatewayError("ai_production_not_approved")
    if not str(getattr(settings, "AI_APPROVAL_REFERENCE", "")).strip():
        raise AIGatewayError("ai_approval_reference_required")


def validate_tool_execution(
    *,
    request: AIRequest,
    tool_class: str,
    call_count: int = 0,
    external_side_effects: bool = False,
) -> None:
    """Authorize a future tool execution through the fail-closed tool boundary."""
    try:
        validate_tool_permission(
            agent_id=request.agent_id,
            capability_id=request.capability_id,
            tool_class=tool_class,
            call_count=call_count,
            external_side_effects=external_side_effects,
        )
    except AIToolPermissionError as exc:
        raise AIGatewayError(str(exc)) from exc


def authorize_agent_request(
    *,
    request: AIRequest,
    session: AIAgentSession,
    required_scope: str = "task_quality:suggest",
) -> Mapping[str, str]:
    """Bind session, agent policy and provenance before provider execution."""
    try:
        validate_agent_capability(agent_id=request.agent_id, capability_id=request.capability_id)
        validate_agent_data_class(agent_id=request.agent_id, data_class="task_content_minimal")
        validate_agent_autonomy(agent_id=request.agent_id, autonomy="suggestion_only")
        validate_agent_session(
            session=session,
            expected_agent_id=request.agent_id,
            expected_audience="zootasks-ai-gateway",
            required_scope=required_scope,
        )
        return build_provenance_receipt({
            "agent_id": request.agent_id,
            "capability_id": request.capability_id,
            "correlation_id": request.correlation_id,
            "data_class": "task_content_minimal",
            "policy_version": "1.0",
            "decision": "authorized",
        })
    except Exception as exc:
        raise AIGatewayError("ai_agent_authorization_rejected") from exc


def request_ai(*, request: AIRequest, provider: str, model: str) -> Mapping[str, Any]:
    """Fail closed until an approved provider adapter exists."""
    try:
        validate_agent_capability(agent_id=request.agent_id, capability_id=request.capability_id)
        validate_agent_autonomy(agent_id=request.agent_id, autonomy="suggestion_only")
    except Exception as exc:
        raise AIGatewayError("ai_agent_policy_rejected") from exc
    validate_capability(request.capability_id)
    validate_provider_model(provider, model)
    try:
        validate_execution_budget(capability_id=request.capability_id, tool_calls=0, external_side_effects=False)
    except Exception as exc:
        raise AIGatewayError("ai_execution_budget_rejected") from exc
    validate_production_approval()
    raise AIGatewayError("ai_provider_adapter_not_enabled")
