from django import forms

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
        return value

    def clean_body(self):
        value = self.cleaned_data["body"].strip()
        if not value:
            raise forms.ValidationError("Please enter the request details.")
        return value
