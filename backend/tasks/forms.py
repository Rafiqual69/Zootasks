from django import forms

from .models import TaskClaim


class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model = TaskClaim
        fields = ["proof"]
        widgets = {
            "proof": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Describe your completed work and provide proof..."
                }
            )
        }
