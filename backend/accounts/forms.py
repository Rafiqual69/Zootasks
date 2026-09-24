from django import forms
from django_otp.forms import OTPAuthenticationForm
from django.contrib.auth.models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("Passwords do not match.")

        return cleaned

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists.")

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()

        return user


class OwnerOTPAuthenticationForm(OTPAuthenticationForm):
    """Password + TOTP authentication restricted to the configured Owner."""

    def confirm_login_allowed(self, user):
        from django.conf import settings
        from django.core.exceptions import ValidationError
        from django_otp.plugins.otp_totp.models import TOTPDevice

        super().confirm_login_allowed(user)

        owner_username = getattr(settings, "OWNER_USERNAME", "").strip()
        if not owner_username or user.username.casefold() != owner_username.casefold():
            raise ValidationError(
                "This authentication endpoint is restricted to the Owner account."
            )

        if not user.is_staff or not user.is_superuser:
            raise ValidationError(
                "This account is not authorized for Owner access."
            )

        if not TOTPDevice.objects.filter(user=user, confirmed=True).exists():
            raise ValidationError(
                "Owner MFA is not enrolled. Owner access is currently unavailable."
            )
