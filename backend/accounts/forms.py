import re

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


class WhatsAppPhoneForm(forms.Form):
    phone_number = forms.CharField(max_length=24, strip=True)

    def clean_phone_number(self):
        value = re.sub(r"[\s().-]", "", self.cleaned_data["phone_number"])
        if value.startswith("00"):
            value = "+" + value[2:]
        elif re.fullmatch(r"01[3-9][0-9]{8}", value):
            value = "+880" + value[1:]
        elif re.fullmatch(r"8801[3-9][0-9]{8}", value):
            value = "+" + value

        if not re.fullmatch(r"\+[1-9][0-9]{7,14}", value):
            raise forms.ValidationError(
                "Enter a valid phone number with country code, e.g. +8801XXXXXXXXX."
            )
        return value


class WhatsAppOTPVerifyForm(forms.Form):
    code = forms.CharField(
        min_length=6,
        max_length=6,
        strip=True,
        widget=forms.PasswordInput(attrs={"inputmode": "numeric", "autocomplete": "one-time-code"}),
    )

    def clean_code(self):
        value = self.cleaned_data["code"]
        if not value.isascii() or not value.isdigit():
            raise forms.ValidationError("Enter the six-digit verification code.")
        return value


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
