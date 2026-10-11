from django import forms
import re


_SECRET_LIKE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\b(?:password|passwd|api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|otp[_-]?secret)\s*[:=]", re.IGNORECASE),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)


def _contains_secret_like_material(value: str) -> bool:
    return any(pattern.search(value) for pattern in _SECRET_LIKE_PATTERNS)

from .models import OwnerInputRequest


class OwnerInputRequestForm(forms.ModelForm):
    """Bounded input form; submitted text is queued, never executed inline."""

    class Meta:
        model = OwnerInputRequest
        fields = ("category", "title", "body")
        widgets = {
            "category": forms.Select(attrs={"autocomplete": "off"}),
            "title": forms.TextInput(attrs={"maxlength": 120, "autocomplete": "off"}),
            "body": forms.Textarea(attrs={"maxlength": 5000, "rows": 7}),
        }

    def clean_title(self):
        value = self.cleaned_data["title"].strip()
        if not value:
            raise forms.ValidationError("A short title is required.")
        if _contains_secret_like_material(value):
            raise forms.ValidationError("Do not submit passwords, tokens, keys, or authentication codes.")
        return value

    def clean_body(self):
        value = self.cleaned_data["body"].strip()
        if not value:
            raise forms.ValidationError("Please enter the request details.")
        if _contains_secret_like_material(value):
            raise forms.ValidationError("Sensitive credential-like content was blocked. Remove passwords, tokens, keys, and authentication codes.")
        return value
