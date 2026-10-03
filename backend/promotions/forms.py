from decimal import Decimal

from django import forms

from .models import Promotion


class AdvertiserPromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ["title", "description", "reward", "budget", "max_workers"]

    def clean(self):
        cleaned = super().clean()
        reward = cleaned.get("reward")
        budget = cleaned.get("budget")
        max_workers = cleaned.get("max_workers")
        if reward is not None and budget is not None and max_workers is not None:
            if budget < reward * Decimal(max_workers):
                raise forms.ValidationError(
                    "Budget must cover the maximum possible worker rewards."
                )
        return cleaned
