"""Deterministic data-classification and redaction boundary for AI inputs.

Only explicitly approved projections may cross toward an AI provider. Redaction
is deterministic and provider-independent; unknown data classes fail closed.
"""

from __future__ import annotations

import re
from typing import Mapping


class AIDataBoundaryError(Exception):
    """Expected failure at the AI data boundary."""


TASK_CONTENT_DATA_CLASS = "task_content_minimal"
DATA_BOUNDARY_VERSION = "1.0"

_ALLOWED_TASK_FIELDS = frozenset({"title", "description", "category"})

_PATTERNS = (
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{8,}"), "[REDACTED:BEARER]"),
    (re.compile(r"(?i)\b(?:api[_-]?key|api[_-]?secret|access[_-]?token|password)\s*[:=]\s*[^\s,;]+"), "[REDACTED:CREDENTIAL]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED:EMAIL]"),
    (re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"), "[REDACTED:PHONE]"),
)


def _redact(value: str) -> str:
    result = value
    for pattern, replacement in _PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def build_task_content_projection(
    *,
    title: str,
    description: str,
    category: str,
    data_class: str = TASK_CONTENT_DATA_CLASS,
) -> Mapping[str, str]:
    """Return the only task fields permitted for AI-SYS-001 provider input."""
    if data_class != TASK_CONTENT_DATA_CLASS:
        raise AIDataBoundaryError("ai_data_class_not_allowed")

    values = {
        "title": str(title or "").strip(),
        "description": str(description or "").strip(),
        "category": str(category or "").strip(),
    }
    if not values["title"] or not values["description"]:
        raise AIDataBoundaryError("ai_task_content_required")

    return {field: _redact(values[field]) for field in _ALLOWED_TASK_FIELDS}
